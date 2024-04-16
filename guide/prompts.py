propose_prompt = """ORIGINAL INPUT EXPRESSION: {expr}
Choose ONE of the following that you think will best help you solve if this statement is a tautology. Look at all of the laws. Generate thoughts about which logical is best, then output the selection of what law is best. Be concise.
"""

output_prompt = """Respond with your best output like this at the VERY end:
LLM CHOICE: #?. (? law)"""

value_prompt_no_history = """Value this expression on a scale from 1-10 based on how easy it is to simplify the expression. Just respond with a number and not a fraction.
Expression to grade: {expr}
Respond like this:
LLM GRADE: ???"""

value_prompt = """Value this expression on a scale from 1-10 based on how easy it is to simplify the expression and take into account the length of the Previous Expression Path. Just respond with a number and not a fraction.
Previous Expression Path: {expr_history}
Expression to grade: {expr}
Respond like this:
LLM GRADE: ???"""