# propose_prompt = """ORIGINAL INPUT EXPRESSION: {expr}
# Choose ONE of the following that you think will best help you solve if this statement is a tautology. Look at all of the laws. Generate thoughts about which logical is best, then output the selection of what law is best. Be concise.
# """

propose_prompt = """
ORIGINAL INPUT EXPRESSION: {expr}
Choose ONE of the following that you think will best help you solve if this statement is a tautology. Look at all of the laws. Generate thoughts about which logical is best, then output the selection of what law is best. Be concise.
Choices:
{choices}
Respond with your best output like this at the VERY end:
LLM CHOICE: #?. (? law)"""

propose_prompt_short = """Respond with your best output like this at the VERY end:
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

deduction_prompt = """
ORIGINAL INPUT EXPRESSION: {expr}

Create a Python dictionary with keys representing symbolic logic laws, and values being lists of possible expressions immediately after applying that law to the original input expression.

Example response format:
\\{{
    "Law Name": ["expression1", "expression2", ...],
    "Another Law": ["expression3", "expression4", ...],
    ...
\\}}

Notes:
- Only include laws that result in a valid change to the original expression.
- Enclose the law names with double quotes as dictionary keys.
- If the original expression remains unchanged after applying a law, do not include that law or expression.
- Ensure that the expressions in the value lists are valid symbolic logic expressions.
- Only include unique expressions per law

RESPOND LIKE THIS:
LLM DICT: \\{{ /* your dictionary response here */ \\}}
"""
