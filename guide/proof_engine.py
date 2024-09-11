import json
import argparse
from functools import partial
import random

from llm import llm_api_call
from symbolic import symbolic_deduce, simplify, apply_bi_imp, is_reduced
from prompts import value_prompt, deduction_prompt
from utils import create_propose_prompt, get_llm_choice, get_llm_value, get_greedy_choice
    
def get_value(expr, expr_history):
    prompt = value_prompt.format(expr=expr, expr_history=expr_history)
    llm_res = llm(message=prompt)
    value = get_llm_value(llm_res, prompt, llm)
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
    if proof_history[-1] == "(1)":
        proof_steps.append(f"TAUTOLOGY")
    else:
        proof_steps.append(f"NOT TAUTOLOGY")
    formatted_proof = "Proof:\n" + "\n≡ ".join(proof_steps)
    print(formatted_proof)
    return formatted_proof

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

def clean_expression(expr):
    expr = expr.strip()
    if expr[0] != "(" and expr[-1] != ")":
        expr = "(" + expr + ")"
    return expr

def initialize_queue(expr, ckpt, ckpt_file, verbose):
    """Initialize the BFS queue from checkpoint or scratch."""
    if ckpt:
        with open(ckpt_file, 'r') as file:
            for line in file:
                current_list = eval(line.strip())
                prev_q = current_list
            return prev_q
    else:
        # start new ckpt file
        with open(ckpt_file, 'w'): 
            pass
        
        # check and apply implication/biconditional
        res = apply_bi_imp(expr, verbose) # returns (law, simplified_expr)
        if res != (None, None):
            return [((res[1]), [expr, res[1]], [res[0]])] # BFS queue [(expr, expr_history, law_history)]
        else:
            return [(expr, [expr], [])]                   # BFS queue [(expr, expr_history, law_history)]

# ---------------solver---------------

def proof_engine(expr, K, T, B): 
    """
    psuedo code params from paper:

    expr = expression to start evaluating on
    T    = step limit (tree depth)
    B    = breadth limit (generates B candidates for the next thought step)
    K    = size limit of level (for level-wise pruning)

    If you're using Chain of Thought (--cot): B=1 and K=1
    """
    unique_proofs = [] # to store finished proofs in (expr, expr_history, law_history) format 
    expr = clean_expression(expr)
    q = initialize_queue(expr, ckpt, ckpt_file, verbose) # create q from checkpoint or scratch

    for t in range(T): # step limit (tree depth)
        print(f"-------------------------------\n[TREE DEPTH]: {t+1}/{T}")
        new_q = [] # stores nodes for next level

        for item in q: # go through each node on this level
            expr_i, expr_history, law_history = item
            
            # generate list of deduction
            if pure_llm: expr_deductions = llm_symbolic_deduce(expr_i, verbose) # pure llm symbolic deductions
            else: expr_deductions = symbolic_deduce(expr_i, verbose) # normal symbolic engine
            
            if not expr_deductions:
                can_simplify = simplify(expr=expr_i, item_history=item)

                if can_simplify and is_reduced(can_simplify[0]):
                    res = check_proof(can_simplify, unique_proofs, q, done=False)
                    if early_stop and res != (None, None):
                        return res

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
                    if random_select:
                        choice_number = str(random.randint(0, len(choice_dict) - 1))
                        new_expr, new_law = choice_dict[choice_number]
                    elif greedy:
                        choice_number, new_expr, new_law = get_greedy_choice(choice_dict)  
                    else:
                        choice_number, new_expr, new_law = get_llm_choice(llm_res, choice_dict, llm_message, llm) 
                    
                    # update structures and add node to BFS queue
                    if del_choice:
                        del expr_deductions[new_law]
                    expr_history_new = expr_history + [new_expr]
                    law_history_new = law_history + [new_law]
                    item = (new_expr, expr_history_new, law_history_new)

                    # simplify if possible                    
                    item = simplify(expr=new_expr, item_history=item, verbose=verbose) or item

                    if verbose: 
                        print(f"[NEW NODE (T={t+1},B=({i+1}/{B})]: new_expr={item[0]}, {new_law=}, {expr_history=}, {law_history=}")

                    res = check_proof(item, unique_proofs, q)

                    if early_stop and res != (None, None):
                        return res

                    new_q.append(item) 
        
        if not random_select:
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

    return formatted_proof

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Prompt engine CLI args")
    parser.add_argument("--expr", type=str, default="(x and x) or (x and x)", help="The expression to evaluate")
    parser.add_argument("--num_steps", type=int, default=5, help="Number of proof steps")
    parser.add_argument("--debug", action='store_true', help="Print debug statements")
    parser.add_argument("--verbose", action='store_true', help="Print out states at each step")
    parser.add_argument("--cot", action='store_true', help="Use Chain of Thought")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Specify a model to use")
    parser.add_argument("--T",  type=int, default=5, help="ToT tree depth")
    parser.add_argument("--B",  type=int, default=3, help="ToT branching factor")
    parser.add_argument("--K",  type=int, default=5, help="ToT max number of nodes per level")
    parser.add_argument("--early_stop", action='store_true', help="Return on first proof found")
    parser.add_argument("--pure_llm", action='store_true', help="Evaluate all expressions through llm instead of symbolic engine")
    parser.add_argument("--del_choice", action='store_true', help="Delete law option after LLM choice")
    parser.add_argument("--ckpt", action='store_true', help="Resume from last q in guide/ckpt.txt")
    parser.add_argument("--random", action='store_true', help="Randomly select expression")
    parser.add_argument("--greedy", action='store_true', help="Greedy select shortest expression")

    args = parser.parse_args()
    
    global T, B, K, early_stop, llm, pure_llm, del_choice, ckpt, ckpt_file, verbose, random_select, greedy
    T = args.T
    B = args.B
    K = args.K
    early_stop = args.early_stop
    pure_llm = args.pure_llm
    del_choice = args.del_choice
    ckpt = args.ckpt
    ckpt_file = "guide/ckpt.txt"
    verbose = args.verbose 
    model = args.model
    random_select = args.random
    greedy = args.greedy

    if args.cot: # chain of thought
        B = 1 # single thread of thought
        K = 1
    
    llm = partial(llm_api_call, model=model) # initialize llm

    print(f"\nSOLVING: '{args.expr}'")
    print(f"LLM: {model}")
    print(f"PARAMS: {T=}, {B=}, {K=}, {early_stop=}, {pure_llm=}, {del_choice=}, {ckpt=}")

    if pure_llm: 
        print("ENGINE: pure llm **WARNING: Not using symbolic engine, proof may have hallucinations**")
    elif random_select:
        print("ENGINE: random selection")
    elif greedy:
        print("ENGINE: greedy selection")
    else:
        print("ENGINE: symbolic")

    if args.cot: 
        print("METHOD: chain of thoughts")
    else: 
        print("METHOD: tree of thoughts")

    print("----------------------------")
    proof_engine(expr=args.expr, T=T, B=B, K=K)