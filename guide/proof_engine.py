import re
from llm import llm
from symbolic import symbolic_deduce
from prompts import propose_prompt, output_prompt
from copy import copy
# from tot import solve_tot

terminal_values = set(["True", "False", "1", "0", "x", "y"])

def create_propose_prompt(expr, expr_deductions):
    """output law and expression in a numbered list and create prompt"""
    choices = ""
    choice_dict = {} # tracks the possible choices to choose from
    counter = 0
    for law, expressions in expr_deductions.items():
        for expression in expressions:
            choices += f"#{counter}., '{law}', '{expression}'\n"
            choice_dict[str(counter)] = (expression, law)
            counter += 1
    llm_message = propose_prompt.format(expr=expr)
    llm_message += choices
    llm_message += output_prompt
    return llm_message, choice_dict

def get_llm_choice(llm_text, choice_dict):
    """search for LLM choice selection and send choice back to symbolic engine"""
    pattern = r"LLM CHOICE: #(\d+)\."
    match = re.search(pattern, llm_text)
    if match:
        choice_number = match.group(1) # capture the LLM choice 
        assert choice_number, "ERROR: Choice number not found"
        new_expr = choice_dict[choice_number][0]
        new_law = choice_dict[choice_number][1]
        return choice_number, new_expr, new_law 
    else:
        print("ERROR: Choice number not found in the response.")
        # TODO: retry until selection so it doesn't error out
        exit(0)

def get_formatted_proof(proof_history, law_history, num=0):
    print("----------FINAL PROOF----------")
    if num != 0: print(f"#{num}")
    # if debug: print(f"{proof_history=}")
    proof_steps = []
    for i, (proof, law) in enumerate(zip(proof_history, law_history)):
        if i == 0: proof_steps.append(f"{proof:35}   {law}")
        else: proof_steps.append(f"{proof:35} {law}")
    proof_steps.append(proof_history[-1]) # add last step (e.g. simply just 'x')
    formatted_proof = "Proof:\n" + "\n≡ ".join(proof_steps)
    print(formatted_proof)
    return formatted_proof

def solve_cot(og_expr, max_num_steps=3, to_print=True, debug=False, use_claude=True):
    # naive chain of thought (CoT) proof solver
    expr = og_expr
    proof_history=[og_expr]
    law_history = []
    for i in range(max_num_steps):
        if to_print:
            print(f"\n----------PROOF STEP #{i+1}----------\n")
            print(f"CURRENT EXPR: {expr}")

        if expr in terminal_values: # to determine if tautology or not
            print(f"Expression '{expr}' cannot be further applied onto laws\n")
            break
        
        expr_deductions = symbolic_deduce(expr, to_print=False) 
        llm_message, choice_dict = create_propose_prompt(expr, expr_deductions) # output law and expression in a numbered list and create prompt
        llm_res = llm(message=llm_message, claude=use_claude) # send message to llm and collect its text response

        if to_print:
            print("\nPrompt:")
            print("'''" + llm_message + "'''")
            print("\nLLM Response:")
            print("'''" + llm_res + "'''")

        # search for LLM choice selection and send choice back to symbolic engine
        choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict)

        if debug:
            print(f"{choice_dict=}")
            print(f"{choice_number=}")
            print(f"{choice_dict[choice_number]=}")
            print(f"{new_expr=}")

        expr = new_expr
        proof_history.append(new_expr) 
        law_history.append(new_law)

    if to_print: formatted_proof = get_formatted_proof(proof_history, law_history)
    else: formatted_proof = None

    return proof_history, formatted_proof


def solve_tot(expr, K=5, T=5, B=5, bfs=True, to_print=True, use_claude=True): 
    """
    psuedo code params from paper:

    expr = expression to start evaluating on
    K    = size limit
    T    = step limit
    B    = breadth limit
    """

    q = [(expr, [expr], [])] # (expr, expr_history, law_history)
    final_proofs = []

    for t in range(T): # each level
        print(f"T:{t+1}/{T}")
        new_q = []
        for item in q: # go through each thought on level
            expr_i, expr_history, law_history = item

            # TODO: Simplify this
            if expr_i in terminal_values or len(expr_i) == 1 or (expr_history and expr_history[-1] in terminal_values) or (expr_history and expr_history[-1] == "x"): # to determine if tautology or not
                print(f"Expression '{expr_i}' cannot be further applied onto laws\n")
                final_proofs.append(item)
                continue
            
            expr_deductions = symbolic_deduce(expr_i, to_print=False) 

            for i in range(B): # TODO: value each expr_i and prune
                llm_message, choice_dict = create_propose_prompt(expr_i, expr_deductions) # output law and expression in a numbered list and create prompt
                llm_res = llm(message=llm_message, claude=use_claude) # send message to llm and collect its text response
                choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict)

                # print(f"{new_expr=}, {new_law=}, {expr_history=}, {law_history=}")
                
                # update structures
                expr_history_new = expr_history.copy()
                law_history_new = law_history.copy()
                expr_history_new.append(new_expr)
                law_history_new.append(new_law)

                new_item = (new_expr, expr_history_new, law_history_new)
                new_q.append(new_item) 
       
        q = new_q

    if to_print: 
        for i, (expr, expr_history, law_history) in enumerate(final_proofs):
            formatted_proof = get_formatted_proof(expr_history, law_history, num=i)
    else: 
        formatted_proof = None

    return q, formatted_proof

def proof_engine(expr, max_num_steps=3, to_print=True, debug=False, naive=True, use_claude=True):
    if naive: # naive chain of thought 
        print("USING CHAIN OF THOUGHT")
        solve_cot(expr, max_num_steps, to_print, debug, use_claude)
    else: # tree of thoughts
        print("USING TREE OF THOUGHT")
        return solve_tot(expr, T=3, B=3, use_claude=use_claude)

if __name__ == '__main__':
    # TODO: these should be test cases
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
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    parser.add_argument("--num_steps", type=str, help="Num of proof steps")
    parser.add_argument("--debug", action='store_true', help="Boolean to print debug statement")
    parser.add_argument("--tot", action='store_true', help="Boolean to use ToT")
    parser.add_argument("--gpt", action='store_true', help="Boolean to use GPT-3.5-Turbo")

    args = parser.parse_args()

    expr = args.expr if args.expr else "(x and x) or (x and x)"
    num_steps = int(args.num_steps) if args.num_steps else 5
    debug = bool(args.debug)
    tot = bool(args.tot)
    gpt = bool(args.gpt)

    # expr = "(x and x or x)"

    proof_engine(expr, max_num_steps=num_steps, debug=debug, naive=not tot, use_claude=not gpt)