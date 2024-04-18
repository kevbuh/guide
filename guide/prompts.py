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

# deduction_prompt = """
# ORIGINAL INPUT EXPRESSION: {expr}

# Possible laws to choose from:

# 1. **Commutative Law**:
#    - $A \land B = B \land A$
#    - $A \lor B = B \lor A$

# 2. **Associative Law**:
#    - $(A \land B) \land C = A \land (B \land C)$
#    - $(A \lor B) \lor C = A \lor (B \lor C)$

# 3. **Distributive Law**:
#    - $A \land (B \lor C) = (A \land B) \lor (A \land C)$
#    - $A \lor (B \land C) = (A \lor B) \land (A \lor C)$

# 4. **Identity Law**:
#    - $A \land 1 = A$; $A \land 0 = 0$
#    - $A \lor 0 = A$; $A \lor 1 = 1$

# 5. **Negation Law**:
#    - $A \land \lnot A = 0$
#    - $A \lor \lnot A = 1$

# 6. **Idempotent Law**:
#    - $A \land A = A$
#    - $A \lor A = A$

# 7. **Zero and One Law**:
#    - $A \land 0 = 0$
#    - $A \lor 1 = 1$

# 8. **Absorption Law**:
#    - $A \land (A \lor B) = A$
#    - $A \lor (A \land B) = A$

# 9. **De Morgan's Theorem**:
#    - $\lnot (A \land B) = \lnot A \lor \lnot B$
#    - $\lnot (A \lor B) = \lnot A \land \lnot B$

# 10. **Double Negation (Involution) Law**:
#     - $\lnot (\lnot A) = A$

# 11. **Implication Transformation**:
#     - $A \Rightarrow B = \lnot A \lor B$

# 12. **Consensus Theorem**:
#     - $(A \land B) \lor (\lnot A \land C) \lor (B \land C) = (A \land B) \lor (\lnot A \land C)$

# 13. **Consensus Law**:
#     - $(A \land B) \lor (\lnot B \land C) \lor (A \land C) = (A \land B) \lor (\lnot B \land C)$

# 14. **Adjacency Law**:
#     - $(A \land B) \lor (A \land \lnot B) = A$

# 15. **Simplification Law**:
#     - $(A \lor B) \land (A \lor \lnot B) = A$

# 16. **Implication Laws**:
#     - $A \Rightarrow B = \lnot A \lor B$
#     - $\lnot (A \Rightarrow B) = A \land \lnot B$

# 17. **Biconditional (iff) Laws**:
#     - $A \Leftrightarrow B = (A \land B) \lor (\lnot A \land \lnot B)$

# Example response format:
# {{"Law Name": ["expression1", "expression2", ...], "Another Law": ["expression3", "expression4", ...], ...}}

# RESPOND LIKE THIS:
# LLM DICT: {{ /* put your custom dictionary response here that you created */ }}

# Try to simplify this expression as much as possible without skipping steps. Create a python dictionary with keys representing symbolic logic laws, and values being lists of possible expressions. You are trying to reduce this down to a terminal value like ["True", "False", "1", "0", "x", "y"].
# - Each expression should logically follow from the original expression.
# - Expressions should be the transformation from IMMEDIATELY applying that law to the original input expression, with no further simplification. 
# - DON'T further simplify the expression after its tranformation e.g. don't go from a complex expression all the way down to x, which shows that it skipped steps. 
# - Only include unique expressions per law.
# - ONLY include laws that result in a VALID change to the original expression.
# - If the original expression remains unchanged after applying a law, do not include that law or expression.
# - ALL property names should be enclosed in DOUBLE quotes, STRICTLY to the format in the EXAMPLE response and use NO NEWLINE CHARACTERS.
# """
