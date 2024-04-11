llm_prompt = """ORIGINAL INPUT EXPRESSION: {expr}
Choose one of the following that you think will best help you solve if this statement is a tautology. Generate thoughts about which logical law helps you most, then output 1 row, where the row is a selection of what law is best.
"""

output_prompt = """Respond with your best output like this at the VERY end:
My choice: #?. (? law)"""