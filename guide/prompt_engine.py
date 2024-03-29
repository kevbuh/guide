import re
from llm import haiku_message
from symbolic import apply_all_laws

def prompt_engine_loop(og_expr, num_loops=2, do_print=True, debug=False):
    expr = og_expr
    proof_history=[og_expr]
    
    for i in range(num_loops): # TODO: go until tautology?
        if do_print:
            print(f"\n***PROOF STEP #{i+1}***\n")
            print(f"CURRENT EXPR: {expr}")
        laws_tuple = apply_all_laws(expr, do_print=False)
    
        # set up prompt
        llm_message = f"""original input expression: {expr}
        Choose one of the following that you think will best help you solve if this statement is a tautology. Generate thoughts about which logical law helps you most, then output 1 row, where the row is a selection of what law is best."""

        choices = ""
        choice_dict = {} # tracks the possible choices to choose from
        counter = 1
        for law, expressions in laws_tuple.items():
            for expression in expressions:
                choices += f"#{counter}., '{law}', '{expression}'\n"
                choice_dict[str(counter)] = expression
                counter += 1
        llm_message += choices
        best_choice_example = """Respond with your best output like this at the VERY end:
        My choice: #?. (? law)"""
        llm_message += best_choice_example

        # sent message to haiku and collect its text response
        haiku_res = haiku_message(llm_message)
        haiku_text = haiku_res.content[0].text

        if do_print:
            print("\n-------------Prompt-------------")
            print(llm_message)
            print("----------LLM Response-----------\n")
            print(haiku_text)

        # search for choice selection
        pattern = r"My choice: #(\d+)\."
        match = re.search(pattern, haiku_text)
        if match:
            choice_number = match.group(1) # just select what the LLM chose and not the one from the example
            if do_print: print(f"LLM CHOSE OPTION #{choice_number}")
        else:
            print("ERROR: Choice number not found in the response.")
            exit(0)

        # send choice back to symbolic engine
        assert choice_number, "ERROR: Choice number not found"
        new_expr = choice_dict[choice_number]

        if debug:
            print(f"{choice_dict=}")
            print(f"{choice_number=}")
            print(f"{choice_dict[choice_number]=}")
            print(f"{new_expr=}")

        expr = new_expr
        proof_history.append(new_expr) # TODO: track what laws the LLM chose
    if do_print:
        print("***********FINAL PROOF***********")
        if debug: print(f"{proof_history=}")
        formatted_proof = "Proof:\n" + "\n≡ ".join(proof_history)
        print(formatted_proof)
    return proof_history

if __name__ == '__main__':
    expr = "(x and x) or (x and x)"
    num_steps = 2
    prompt_engine_loop(expr, num_loops=num_steps)