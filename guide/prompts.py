propose_prompt = """ORIGINAL INPUT EXPRESSION: {expr}
Choose one of the following that you think will best help you solve if this statement is a tautology. Generate thoughts about which logical law helps you most, then output 1 row, where the row is a selection of what law is best.
"""

output_prompt = """Respond with your best output like this at the VERY end:
LLM CHOICE: #?. (? law)"""

# we find proposals, LLM doesn't for our approach
# propose_prompt = '''Input: 2 8 8 14
# Possible next steps:
# 2 + 8 = 10 (left: 8 10 14)
# 8 / 2 = 4 (left: 4 8 14)
# 14 + 2 = 16 (left: 8 8 16)
# 2 * 8 = 16 (left: 8 14 16)
# 8 - 2 = 6 (left: 6 8 14)
# 14 - 8 = 6 (left: 2 6 8)
# 14 /  2 = 7 (left: 7 8 8)
# 14 - 2 = 12 (left: 8 8 12)
# Input: {input}
# Possible next steps:
# '''