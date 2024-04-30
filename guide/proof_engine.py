import re
import json
import argparse
from functools import partial

from llm import llm_api_call
from symbolic import symbolic_deduce, simplify, apply_bi_imp, is_reduced
from prompts import propose_prompt, propose_prompt_short, value_prompt, deduction_prompt

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
    llm_message = f"{expr=}\n{choices=}{propose_prompt_short}"

    # TODO: experiment with other prompts
    # llm_message = propose_prompt.format(expr=expr, choices=choices)
    # print("LLM_MESSAGE",llm_message)

    return llm_message, choice_dict

def get_llm_choice(llm_text, choice_dict, llm_message):
    """search for LLM choice selection and send choice back to symbolic engine"""
    pattern = r"LLM CHOICE: #(\d+)\."
    match = re.search(pattern, llm_text)
    retries = 0
    MAX_RETRIES = 3

    while retries < MAX_RETRIES:
        if match:
            choice_number = match.group(1)
            if choice_number in choice_dict:
                new_expr, new_law = choice_dict[choice_number]
                return choice_number, new_expr, new_law
            else:
                print(f"WARNING: Choice number {choice_number} not in choice_dict. Retrying...{choice_dict=}")
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
    if num > 1: print(f"----------FINAL PROOF #{num}----------")
    else: print("----------FINAL PROOF----------")
    proof_steps = []
    proof_steps.append(proof_history[0]) # add last step (e.g. simply just 'x')
    for i, (proof, law) in enumerate(zip(proof_history[1:], law_history)):
        proof_steps.append(f"{proof:35} {law}")
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

        # if expr.replace("(","").replace(")","") in TERMINAL_VALUES: # to determine if tautology or not
        if is_reduced(expr=expr.replace("(","").replace(")","")):
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

def check_proof(item, unique_proofs, q, done=False):
    """ check if proof is done """
    a, b, c = item
    if len(a) == 1 or done or is_reduced(a):
        if item not in unique_proofs:
            print(f"FULLY REDUCED EXPR, PROOF DONE.")
            unique_proofs.append(item)

            # early stop for first proof found
            if early_stop:
                print("EARLY STOPPING, FOUND FIRST PROOF...")
                for i, (a, b, c) in enumerate(unique_proofs):
                    formatted_proof = get_formatted_proof(b, c, num=i+1)
                    return q, formatted_proof
        else:
            print("REMOVING NON-UNIQUE PROOF...")
    return (None, None)

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
    # stores finished proofs in (expr, expr_history, law_history) format 
    unique_proofs = [] 

    # preprocess expression
    expr = expr.strip()
    if expr[0] != "(" and expr[-1] != ")": expr = "(" + expr + ")"
    
    # create q from checkpoint or scratch
    if ckpt:
        with open(ckpt_file, 'r') as file:
            for line in file:
                current_list = eval(line.strip())
                prev_q = current_list
            q = prev_q
    else:
        # start new ckpt file
        with open(ckpt_file, 'w'): 
            pass
        
        # check and apply implication/biconditional
        res = apply_bi_imp(expr, verbose) # returns (law, simplified_expr)
        if res != (None, None):
            q = [((res[1]), [expr, res[1]], [res[0]])] # BFS queue [(expr, expr_history, law_history)]
        else:
            q = [(expr, [expr], [])]                   # BFS queue [(expr, expr_history, law_history)]

    for t in range(T): # step limit (tree depth)
        print(f"\nTREE DEPTH:{t+1}/{T}")
        new_q = [] # stores nodes for next level

        for item in q: # go through each node on this level
            expr_i, expr_history, law_history = item
            
            # generate list of deduction
            if pure_llm: expr_deductions = llm_symbolic_deduce(expr_i, verbose) # pure llm symbolic deductions
            else: expr_deductions = symbolic_deduce(expr_i, verbose) # normal symbolic engine
            
            if not expr_deductions:
                can_simplify = simplify(expr=expr, item_history=item)
                if can_simplify:
                    new_q.append(can_simplify)
                else:
                    check_proof(item, unique_proofs, q, done=False)
                continue

            # generate B new thoughts per node
            for i in range(B):
                llm_message, choice_dict = create_propose_prompt(expr_i, expr_deductions) # output law and expression in a numbered list and create prompt
                llm_res = llm(message=llm_message) # send message to llm and collect its text response
                if choice_dict:
                    # TODO: make it with *respect to the probabilities* and have it print values
                    choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict, llm_message) 
                    
                    # update structures and add node to BFS queue
                    if del_choice:
                        del expr_deductions[new_law]
                    expr_history_new = expr_history + [new_expr]
                    law_history_new = law_history + [new_law]
                    item = (new_expr, expr_history_new, law_history_new)

                    # simplify if possible                    
                    item = simplify(expr=new_expr, item_history=item, verbose=verbose) or item

                    if verbose: print(f"NEW NODE [level:{t+1} ({i+1}/{B})]: new_expr={item[0]}, {new_law=}, {expr_history=}, {law_history=}")

                    res = check_proof(item, unique_proofs, q)

                    if early_stop and res != (None, None):
                        return res

                    new_q.append(item) 
        
        # evaluate and select top nodes
        values = evaluate_tree(new_q) # rates each node on scale of 1-10
        q = prune_tree(values, new_q, K) # level-wise pruning
        
        # write to guide/ckpt.txt
        print("writing q to file...")
        with open(ckpt_file, 'a') as file:
            file.write(f"{q}\n")

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
    parser = argparse.ArgumentParser(description="Prompt engine CLI args")
    parser.add_argument("--expr", type=str, default="(x and x) or (x and x)", help="The expression to evaluate")
    parser.add_argument("--num_steps", type=int, default=5, help="Number of proof steps")
    parser.add_argument("--debug", action='store_true', help="Print debug statements")
    parser.add_argument("--verbose", action='store_true', help="Print out states at each step")
    parser.add_argument("--cot", action='store_true', help="Use Chain of Thought")
    parser.add_argument("--claude", action='store_true', help="Use Claude-3-Haiku")
    parser.add_argument("--T",  type=int, default=5, help="ToT tree depth")
    parser.add_argument("--B",  type=int, default=3, help="ToT branching factor")
    parser.add_argument("--K",  type=int, default=5, help="ToT max number of nodes per level")
    parser.add_argument("--early_stop", action='store_true', help="Return on first proof found")
    parser.add_argument("--pure_llm", action='store_true', help="Evaluate all expressions through llm instead of symbolic engine")
    parser.add_argument("--del_choice", action='store_true', help="Delete law option after LLM choice")
    parser.add_argument("--ckpt", action='store_true', help="Resume from last q in guide/ckpt.txt")
    args = parser.parse_args()
    
    global T, B, K, early_stop, llm, pure_llm, del_choice, ckpt, ckpt_file
    T = args.T
    B = args.B
    K = args.K
    early_stop = args.early_stop
    pure_llm = args.pure_llm
    del_choice = args.del_choice
    ckpt = args.ckpt
    ckpt_file = "guide/ckpt.txt"

    if args.claude: model_name = "claude-3-haiku"
    else: model_name = "gpt-3.5-turbo"
    llm = partial(llm_api_call, model=model_name)

    print(f"\nSOLVING: '{args.expr}'")
    print(f"LLM: {model_name}")
    print(f"PARAMS: {T=}, {B=}, {K=}, {early_stop=}, {pure_llm=}, {del_choice=}, {ckpt=}")
    if pure_llm: 
        print("ENGINE: pure llm **WARNING: Not using symbolic engine, proof may have hallucinations**")
    else:
        print("ENGINE: symbolic")
    if args.cot: print("METHOD: chain of thoughts")
    else: print("METHOD: tree of thoughts")
    print("----------------------------")

    proof_engine(args.expr, max_num_steps=args.num_steps, verbose=args.verbose, debug=args.debug, naive=args.cot)


"""
---------------------------proof_engine outputs------------------------------------------
# TODO: How should we test these? --> assert unique_proofs != []?

CK's EXAMPLES:
------1---------
Proof:
(((not b) and (not a)) -> (not a))
≡ (not (not b and not a) or not a)  Implication Law
≡ ((not not b or not not a) or not a) DeMorgan Law 2
≡ ((b or not not a) or not a)     Simplification Law (Double Negation)
≡ ((b or a) or not a)         Simplification Law (Double Negation)
≡ (b or (a or not a))         Associative Law OR
≡ (b or 1)              Negation Law OR
≡ (1)                 Simplification Law
------2---------
Proof:
not((a or (a and b)) -> a)
≡ (not (not (a or a and b) or a))   Implication Law
≡ (not (a or not (a or a and b)))   Commutative Law OR
≡ (not (a or not a))         Absorption Law 1
≡ (not 1)               Negation Law OR
≡ (0)                 Simplification Law
-----3----------
Proof:
(a or (a and b)) -> a
≡ (not (a or a and b) or a)      Implication Law
≡ (not a or a)            Absorption Law 1
≡ (1)                 Negation Law OR
-----4----------
expr = "(((y and x) or x) and y)" # NOT TAUTOLOGY
Proof:
(((y and x) or x) and y)
≡ (y and (x and y or x))              Commutative Law AND
≡ ((x and y or x) and y)              Commutative Law AND
≡ (x and y)                           Absorption Law 1

------------------------pure llm results---------------------------------------------

Pure llm (no symbolic) results:
python3 guide/proof_engine.py --early_stop  --verbose --expr="(a or (a and b)) -> a"
Proof:
(a or (a and b)) -> a                 Absorption
≡ (a or (a and b)) -> a               Simplification
≡ a -> a                              Identity
≡ a
"""