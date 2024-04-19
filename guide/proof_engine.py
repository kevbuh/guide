import re
import json
from llm import llm_api_call
from functools import partial
from symbolic import symbolic_deduce
from prompts import propose_prompt, propose_prompt_short, value_prompt, deduction_prompt

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
    llm_message = f"{expr}\n{choices}{propose_prompt_short}"

    # TODO: test with other prompts
    # llm_message = propose_prompt.format(expr=expr, choices=choices)
    # print("LLM_MESSAGE",llm_message)

    return llm_message, choice_dict

def get_llm_choice(llm_text, choice_dict, llm_message):
    """search for LLM choice selection and send choice back to symbolic engine"""
    pattern = r"LLM CHOICE: #(\d+)\."
    match = re.search(pattern, llm_text)
    retries = 0
    MAX_RETRIES = 2

    while retries < MAX_RETRIES:
        if match:
            choice_number = match.group(1)
            if choice_number in choice_dict:
                new_expr, new_law = choice_dict[choice_number]
                return choice_number, new_expr, new_law
            else:
                print(f"Warning: Choice number {choice_number} not in choice_dict. Retrying...")
        else:
            print("Couldn't find LLM choice...retrying")
        
        llm_res = llm(message=llm_message)  # Send message to LLM and collect its text response
        match = re.search(pattern, llm_res)
        retries += 1

    raise ValueError("ERROR: Valid choice number not found after maximum retries")

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
    # NOTE: Prunes ENTIRE tree, leaves K remaining nodes. Should this be per node?
    len_q = len(q)
    if len_q <= K: return q
    print(f"pruning {len_q-K} leaves...{K} nodes remain")
    sorted_q = [node[1] for node in sorted(zip(values, q), key=lambda x: x[0], reverse=True)][:K]
    return sorted_q

def get_formatted_proof(proof_history, law_history, num=0):
    # TODO: offset law history by one
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

def is_unique(item, unique_proofs):
    _, expr_history, _ = item
    expr_history_u = set(tuple(proof[1]) for proof in unique_proofs) # just check expr_history
    return tuple(expr_history) not in expr_history_u

def llm_symbolic_deduce(expr_i, verbose=False, num_retries=3):
    prompt = deduction_prompt.format(expr=expr_i)
    attempt = 0

    while attempt < num_retries:
        llm_res = llm(message=prompt)
        if verbose: print(f"Attempt {attempt+1}: llm_symbolic_deduce:", llm_res)
        try:
            json_str = llm_res.split('LLM DICT:')[1].strip()
            json_str = json_str.replace("\n", "").replace(",}","}").replace("'", '"')
            data_dict = json.loads(json_str)
            return data_dict
        except json.JSONDecodeError as e:
            print(f"ERROR on attempt {attempt+1}: trying invalid dict in llm_symbolic_deduce(), {json_str=}")
            attempt += 1
    raise Exception("All attempts failed to parse JSON in llm_symbolic_deduce()")


def solve_tot(expr, K=5, T=5, B=5, bfs=True, verbose=True): 
    """
    psuedo code params from paper:

    expr = expression to start evaluating on
    T    = step limit (tree depth)
    B    = breadth limit (generates B candidates for the next thought step)
    K    = size limit of level (for level-wise pruning)
    """

    q = [(expr, [expr], [])] # BFS queue [(expr, expr_history, law_history)]
    unique_proofs = [] # stores the proofs in (expr, expr_history, law_history) format 

    for t in range(T): # step limit (tree depth)
        print(f"TREE DEPTH:{t+1}/{T}")

        new_q = [] # stores nodes for next level

        for item in q: # go through each thought on level
            expr_i, expr_history, law_history = item

            if expr_i in terminal_values or len(expr_i) == 1: # to determine if tautology or not
                expr, expr_history, law_history = item
                
                # if item not in unique_proofs: # NOTE: is this the same as is_unique?
                if is_unique(item, unique_proofs):
                    print(f"FULLY REDUCED EXPR, PROOF DONE.")
                    unique_proofs.append(item)

                     # early stop for first proof found
                    if early_stop:
                        print("EARLY STOPPING, FOUND FIRST PROOF...")
                        for i, (expr, expr_history, law_history) in enumerate(unique_proofs):
                            formatted_proof = get_formatted_proof(expr_history, law_history, num=i+1)
                            return q, formatted_proof
                else:
                    print("REMOVING NON-UNIQUE PROOF...")
                    
                continue
            
            # generate list of deduction
            if pure_llm: expr_deductions = llm_symbolic_deduce(expr_i, verbose) # pure llm symbolic deductions
            else: expr_deductions = symbolic_deduce(expr_i, verbose) # normal symbolic engine
            if verbose: print("GENERATED LIST OF DEDUCTIONS: ", expr_deductions)

            # generate B new thoughts per node
            for i in range(B): 
                llm_message, choice_dict = create_propose_prompt(expr_i, expr_deductions) # output law and expression in a numbered list and create prompt
                llm_res = llm(message=llm_message) # send message to llm and collect its text response
                choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict, llm_message)

                if verbose: print(f"NODE DETAIL: {new_expr=}, {new_law=}, {expr_history=}, {law_history=}")
                
                # update structures and add node to BFS queue
                expr_history_new = expr_history + [new_expr]
                law_history_new = law_history + [new_law]
                new_q.append((new_expr, expr_history_new, law_history_new)) 
        
        # eval and select top nodes
        values = evaluate_tree(new_q) # rates each node on scale of 1-10
        q = prune_tree(values, new_q, K) # level-wise pruning
        # q = new_q

    if unique_proofs: 
        for i, (expr, expr_history, law_history) in enumerate(unique_proofs):
            formatted_proof = get_formatted_proof(expr_history, law_history, num=i+1)
    else: 
        print("-------------------\nNo unique proofs found.")
        formatted_proof = None

    return q, formatted_proof

def proof_engine(expr, max_num_steps=3, verbose=True, debug=False, naive=False):
    if naive:
        solve_cot(expr, max_num_steps, verbose, debug)
    else: 
        return solve_tot(expr, T=T, B=B, K=K, verbose=verbose) 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Prompt engine CLI args")
    parser.add_argument("--expr", type=str, default="(x and x) or (x and x)", help="The expression to evaluate")
    parser.add_argument("--num_steps", type=int, default=5, help="Number of proof steps")
    parser.add_argument("--debug", action='store_true', help="Boolean to print debug statements")
    parser.add_argument("--verbose", action='store_true', help="Print out states at each step")
    parser.add_argument("--cot", action='store_true', help="Boolean to use Chain of Thought")
    parser.add_argument("--claude", action='store_true', help="Boolean to use Claude-3-Haiku")
    parser.add_argument("--T",  type=int, default=5, help="ToT tree depth")
    parser.add_argument("--B",  type=int, default=3, help="ToT branching factor")
    parser.add_argument("--K",  type=int, default=5, help="ToT max number of nodes per level")
    parser.add_argument("--early_stop", action='store_true', help="Boolean to return on first proof found")
    parser.add_argument("--pure_llm", action='store_true', help="Boolean to evaluate all expressions through llm instead of symbolic engine")

    args = parser.parse_args()
    
    global T, B, K, early_stop, llm, pure_llm
    T = args.T
    B = args.B
    K = args.K
    early_stop = args.early_stop
    pure_llm = args.pure_llm

    if args.claude: model_name = "claude-3-haiku"
    else: model_name = "gpt-3.5-turbo"
    llm = partial(llm_api_call, model=model_name)

    print(f"\nSOLVING: '{args.expr}'")
    print(f"LLM: {model_name}")
    print(f"PARAMS: {T=}, {B=}, {K=}, {early_stop=}, {pure_llm=}")
    if pure_llm: 
        print("WARNING: Not using symbolic engine, proof may have hallucinations")
        print("ENGINE: PURE LLM")
    else:
        print("ENGINE: SYMBOLIC")
    if args.cot: print("METHOD: Chain of Thought\n")
    else: print("METHOD: Tree of Thought\n")

    proof_engine(args.expr, max_num_steps=args.num_steps, verbose=args.verbose, debug=args.debug, naive=args.cot)


# TODO: How should we test these?
"""
Test expressions:
# CK's examples
# expr = "(a or (a and b)) -> a"              # TAUTOLOGY
# expr = "((not b) and (a -> b)) -> (not a)"  # TAUTOLOGY
# expr = "not((a or (a and b)) -> a)"         # NOT TAUTOLOGY
# expr = "(((y and x) or x) and y)"           # NOT TAUTOLOGY

# Simple examples
# expr = "(x and y) or (x and y)"             # TAUTOLOGY
# expr = "(x and x) or (x and x)"

----------------------------------

Pure LLM did output this
python3 guide/proof_engine.py --early_stop  --verbose --expr="(a or (a and b)) -> a"
Proof:
(a or (a and b)) -> a                 Absorption
≡ (a or (a and b)) -> a               Simplification
≡ a -> a                              Identity
≡ a
"""