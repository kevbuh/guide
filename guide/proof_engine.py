import re
from llm import llm_api_call
from symbolic import symbolic_deduce
from prompts import propose_prompt, output_prompt, value_prompt
from functools import partial

terminal_values = set(["True", "False", "1", "0", "x", "y"])

def create_propose_prompt(expr, expr_deductions):
    """output law and expression in a numbered list and create prompt"""
    choices_list = []
    choice_dict = {} # Tracks the possible choices to choose from
    counter = 0

    for law, expressions in expr_deductions.items():
        for expression in expressions:
            choice = f"#{counter}. '{law}', '{expression}'\n"
            choices_list.append(choice)
            choice_dict[str(counter)] = (expression, law)
            counter += 1

    choices = "".join(choices_list)
    llm_message = f"{expr}\n{choices}{output_prompt}"

    return llm_message, choice_dict


def get_llm_choice(llm_text, choice_dict, llm_message):
    """search for LLM choice selection and send choice back to symbolic engine"""
    pattern = r"LLM CHOICE: #(\d+)\."
    match = re.search(pattern, llm_text)
    retries = 0

    MAX_RETRIES = 2
    while not match and retries < MAX_RETRIES:
        print("Couldn't find LLM choice...retrying")
        llm_res = llm(message=llm_message)  # send message to llm and collect its text response
        match = re.search(pattern, llm_res)
        retries += 1

    if match:
        choice_number = match.group(1)
        new_expr = choice_dict[choice_number][0]
        new_law = choice_dict[choice_number][1]
        return choice_number, new_expr, new_law
    else:
        raise ValueError("ERROR: Choice number not found after maximum retries")

def get_llm_value(llm_text, llm_message):
    """search for LLM value and send choice back"""
    match = re.search(r'\d+', llm_text)
    retries = 0

    MAX_RETRIES = 2
    while not match and retries < MAX_RETRIES:
        print("Couldn't find number...retrying")
        llm_res = llm(message=llm_message)  # send message to llm and collect its text response
        match = re.search(r'\d+', llm_res)
        retries += 1

    if match:
        value = int(match.group(0))
        return value
    else:
        raise ValueError("ERROR: Choice number not found after maximum retries")
    
def get_value(expr, expr_history):
    prompt = value_prompt.format(expr=expr, expr_history=expr_history)
    llm_res = llm(message=prompt)
    value = get_llm_value(llm_res, prompt)
    return value

def evaluate_tree(q):
    values = []
    local_value_cache = {}
    for (expr, expr_history, law_history) in q:
        if expr in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:
            value = get_value(expr, expr_history)
            local_value_cache[expr] = value
        values.append(value)
    return values

def prune_tree(values, q, K):
    len_q = len(q)
    if len_q <= K: return q
    print(f"pruning {len_q-K} leaves...")
    sorted_q = [node[1] for node in sorted(zip(values, q), key=lambda x: x[0], reverse=True)][:K]
    return sorted_q

def get_formatted_proof(proof_history, law_history, num=0):
    if num > 1: print(f"----------FINAL PROOF #{num}----------")
    else: print("----------FINAL PROOF----------")
    proof_steps = []
    for i, (proof, law) in enumerate(zip(proof_history, law_history)):
        if i == 0: proof_steps.append(f"{proof:35}   {law}")
        else: proof_steps.append(f"{proof:35} {law}")
    proof_steps.append(proof_history[-1]) # add last step (e.g. simply just 'x')
    formatted_proof = "Proof:\n" + "\n≡ ".join(proof_steps)
    print(formatted_proof)
    return formatted_proof

# ---------------solvers---------------

def solve_cot(og_expr, max_num_steps=3, verbose=True, debug=False):
    # naive chain of thought (CoT) proof solver
    expr = og_expr
    proof_history=[og_expr]
    law_history = []
    for i in range(max_num_steps):
        if verbose:
            print(f"\n----------PROOF STEP #{i+1}----------\n")
            print(f"CURRENT EXPR: {expr}")

        if expr in terminal_values: # to determine if tautology or not
            print(f"Expression '{expr}' cannot be further applied onto laws\n")
            break
        
        expr_deductions = symbolic_deduce(expr, verbose=False) 
        llm_message, choice_dict = create_propose_prompt(expr, expr_deductions) # output law and expression in a numbered list and create prompt
        llm_res = llm(message=llm_message) # send message to llm and collect its text response

        if verbose:
            print("\nPrompt:")
            print("'''" + llm_message + "'''")
            print("\nLLM Response:")
            print("'''" + llm_res + "'''")

        # search for LLM choice selection and send choice back to symbolic engine
        choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict, llm_message)

        if debug:
            print(f"{choice_dict=}")
            print(f"{choice_number=}")
            print(f"{choice_dict[choice_number]=}")
            print(f"{new_expr=}")

        expr = new_expr
        proof_history.append(new_expr) 
        law_history.append(new_law)

    formatted_proof = get_formatted_proof(proof_history, law_history)
    return proof_history, formatted_proof

def solve_tot(expr, K=5, T=5, B=5, bfs=True, verbose=True): 
    """
    psuedo code params from paper:

    expr = expression to start evaluating on
    K    = size limit
    T    = step limit
    B    = breadth limit
    """

    q = [(expr, [expr], [])] # (expr, expr_history, law_history)
    unique_proofs = []

    for t in range(T): # each level
        print(f"Level:{t+1}/{T}")
        new_q = []
        
        values = evaluate_tree(q)
        q = prune_tree(values, q, K)

        for item in q: # go through each thought on level
            expr_i, expr_history, law_history = item

            if expr_i in terminal_values or len(expr_i) == 1: # to determine if tautology or not
                print(f"Fully reduced expression, proof done.")
                if item not in unique_proofs: 
                    print("Removing non-unique proof")
                    unique_proofs.append(item)
                continue
            
            expr_deductions = symbolic_deduce(expr_i, verbose=False) 

            for i in range(B): 
                llm_message, choice_dict = create_propose_prompt(expr_i, expr_deductions) # output law and expression in a numbered list and create prompt
                llm_res = llm(message=llm_message) # send message to llm and collect its text response
                choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict, llm_message)

                if verbose: print(f"DETAIL: {new_expr=}, {new_law=}, {expr_history=}, {law_history=}")
                
                # update structures
                expr_history_new = expr_history + [new_expr]
                law_history_new = law_history + [new_law]
                new_q.append((new_expr, expr_history_new, law_history_new)) 
       
        q = new_q

    if unique_proofs: 
        for i, (expr, expr_history, law_history) in enumerate(unique_proofs):
            formatted_proof = get_formatted_proof(expr_history, law_history, num=i+1)
    else: 
        print("-------------------\nNo unique proofs found.")
        formatted_proof = None

    return q, formatted_proof

def proof_engine(expr, max_num_steps=3, verbose=True, debug=False, naive=False):
    if naive:
        print("USING CHAIN OF THOUGHT")
        solve_cot(expr, max_num_steps, verbose, debug)
    else: 
        print("USING TREE OF THOUGHT")
        return solve_tot(expr, T=3, B=3, K=3, verbose=verbose)

if __name__ == '__main__':
    # TODO: How should we test these?
    # CK's examples
    # expr = "(a or (a and b)) -> a"              # TAUTOLOGY
    # expr = "((not b) and (a -> b)) -> (not a)"  # TAUTOLOGY
    # expr = "not((a or (a and b)) -> a)"         # NOT TAUTOLOGY
    # expr = "(((y and x) or x) and y)"           # NOT TAUTOLOGY

    # Simple examples
    # expr = "(x and y) or (x and y)"             # TAUTOLOGY
    # expr = "(x and x) or (x and x)"

    import argparse
    parser = argparse.ArgumentParser(description="Prompt engine CLI args")
    parser.add_argument("--expr", type=str, default="(x and x) or (x and x)", help="The expression to evaluate")
    parser.add_argument("--num_steps", type=int, default=5, help="Number of proof steps")
    parser.add_argument("--debug", action='store_true', help="Boolean to print debug statements")
    parser.add_argument("--verbose", action='store_true', help="Print out states at each step")
    parser.add_argument("--cot", action='store_true', help="Boolean to use Chain of Thought")
    parser.add_argument("--claude", action='store_true', help="Boolean to use Claude-3-Haiku")
    args = parser.parse_args()
    
    print(f"\nSOLVING '{args.expr}'...\n")
    
    if args.claude:
        model_name = "claude-3-haiku"
        print("Using Claude-3-Haiku")
    else:
        model_name = "gpt-3.5-turbo"
        print("Using GPT-3.5-Turbo")

    global llm
    llm = partial(llm_api_call, model=model_name)

    proof_engine(args.expr, max_num_steps=args.num_steps, verbose=args.verbose, debug=args.debug, naive=args.cot)