import re
from llm import llm_api_call
from symbolic import apply_all_laws
from prompts import llm_message_v1

def prompt_engine_loop(og_expr, max_num_steps=3, do_print=True, debug=False):
    expr = og_expr
    proof_history=[og_expr]
    law_history = []
    
    for i in range(max_num_steps):
        if do_print:
            print(f"\n----------PROOF STEP #{i+1}----------\n")
            print(f"CURRENT EXPR: {expr}")

        if expr in ["True", "False", "1", "0", "x", "y"]: # can determine if tautology or not
            print(f"Expression '{expr}' cannot be further applied onto laws\n")
            break
        
        all_laws_applied = apply_all_laws(expr, do_print=False)
    
        # output law and expression in a numbered list
        choices = ""
        choice_dict = {} # tracks the possible choices to choose from
        counter = 0
        for law, expressions in all_laws_applied.items():
            for expression in expressions:
                choices += f"#{counter}., '{law}', '{expression}'\n"
                choice_dict[str(counter)] = (expression, law)
                counter += 1

        # set up prompt
        llm_message = llm_message_v1.format(expr=expr)
        llm_message += choices
        llm_message += """Respond with your best output like this at the VERY end:
My choice: #?. (? law)"""

        # sent message to haiku and collect its text response
        haiku_res = llm_api_call(llm_message)
        haiku_text = haiku_res.content[0].text

        if do_print:
            print("\nPrompt:")
            print("'''" + llm_message + "'''")
            print("\nLLM Response:")
            print("'''" + haiku_text + "'''")

        # search for choice selection
        pattern = r"My choice: #(\d+)\."
        match = re.search(pattern, haiku_text)
        if match:
            choice_number = match.group(1) # just select what the LLM chose and not the one from the example
        else:
            print("ERROR: Choice number not found in the response.")
            exit(0)

        # send choice back to symbolic engine
        assert choice_number, "ERROR: Choice number not found"
        new_expr = choice_dict[choice_number][0]
        new_law = choice_dict[choice_number][1]

        if debug:
            print(f"{choice_dict=}")
            print(f"{choice_number=}")
            print(f"{choice_dict[choice_number]=}")
            print(f"{new_expr=}")

        expr = new_expr
        proof_history.append(new_expr) 
        law_history.append(new_law)

    if do_print:
        print("----------FINAL PROOF----------")
        if debug: print(f"{proof_history=}")
        proof_steps = []
        for i, (proof, law) in enumerate(zip(proof_history, law_history)):
            if i == 0: proof_steps.append(f"{proof:35}   {law}")
            else: proof_steps.append(f"{proof:35} {law}")
        proof_steps.append(proof_history[-1]) # add last step (e.g. simply just 'x')
        formatted_proof = "Proof:\n" + "\n≡ ".join(proof_steps)
        print(formatted_proof)

    return proof_history

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Prompt engine CLI args")
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    parser.add_argument("--num_steps", type=str, help="Num of proof steps")
    parser.add_argument("--debug", action='store_true', help="Boolean to print debug statement")
    args = parser.parse_args()

    # TODO: these should be test cases
    # CK's examples
    # expr = "(a or (a and b)) -> a"              # TAUTOLOGY
    # expr = "((not b) and (a -> b)) -> (not a)"  # TAUTOLOGY
    # expr = "not((a or (a and b)) -> a)"         # NOT TAUTOLOGY
    # expr = "(((y and x) or x) and y)"           # NOT TAUTOLOGY

    # Simple examples
    # expr = "(x and y) or (x and y)"             # TAUTOLOGY
    # expr = "(x and x) or (x and x)"
    
    expr = args.expr if args.expr else "(x and x) or (x and x)"
    num_steps = int(args.num_steps) if args.num_steps else 5
    debug = bool(args.debug)

    prompt_engine_loop(expr, max_num_steps=num_steps, debug=debug)