from symbolic import apply_all_laws
from llm import haiku_message

expr = "(x and y) or (x and y)"
laws_tuple = apply_all_laws(expr, do_print=False)
counter = 1

llm_message = f"""
original input expression: {expr}
Choose one of the following that you think will best help you solve if this statement is a tautology.
Generate thoughts about which logical law helps you most, then output 1 row, where the row is a selection of what law is best.
"""

for law, expressions in laws_tuple.items():
    for expression in expressions:
        llm_message += f"#{counter}., '{law}', '{expression}'\n"
        counter += 1

print(llm_message)
print("---------------------\n")
haiku_res = haiku_message(llm_message)
print(haiku_res.content[0].text)