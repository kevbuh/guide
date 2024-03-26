# from utils import booleanTree
# from ast import BoolOp, Or

# # exp = "((not(x or y) and z) or True) <-> z"
# exp = "not(x or y)"
# bTree = booleanTree(exp)
# nodes = bTree.parse_tree()
# print("nodes", nodes)

# ------------------WORK IN PROGRESS-------------------

import re
import argparse

def remove_outer_parens(expr):
  if expr.startswith('(') and expr.endswith(')'):
    return expr[1:-1]
  return expr

def split_operands(expr):
  tokens = re.split(r'([\(\)\¬∧∨⊕⇒⇔⊙])', expr)
  print("tokens     :", tokens)
  operands = []
  operators = []
  for token in tokens:
    if token:
      if token in '()¬∧∨⊕⇒⇔⊙':
        operators.append(token)
      else:
        operands.append(token)
  operands = [remove_outer_parens(op) for op in operands]
  return operands, operators

def apply_law(law=1, expr="A∧(B∨C)"):
    operands, operators = split_operands(expr)
    print("operands   :", operands)
    print("operators  :", operators)

    if law == 1:  # Commutative Law
        if '∧' in operators:
            return f"{operands[1]} ∧ {operands[0]}"
        elif '∨' in operators:
            return f"{operands[1]} ∨ {operands[0]}"
    elif law == 2:  # Associative Law
        if len(operands) == 3:
            if '∧' in operators:
                return f"({operands[0]} ∧ {operands[1]}) ∧ {operands[2]}"
            elif '∨' in operators:
                return f"({operands[0]} ∨ {operands[1]}) ∨ {operands[2]}"
    elif law == 3:  # Distributive Law
        if '∧' in operators and '∨' in operators:
            if operators.index('∧') < operators.index('∨'):
                return f"({operands[0]} ∧ {operands[1]}) ∨ ({operands[0]} ∧ {operands[2]})"
            else:
                return f"({operands[0]} ∨ {operands[1]}) ∧ ({operands[0]} ∨ {operands[2]})"
    elif law == 4:  # Identity Law
        if '∧' in operators:
            if '1' in operands:
                return operands[1 - operands.index('1')]
            elif '0' in operands:
                return '0'
        elif '∨' in operators:
            if '0' in operands:
                return operands[1 - operands.index('0')]
            elif '1' in operands:
                return '1'
    elif law == 5:  # Negation Law
        if '∧' in operators and '¬' in expr:
            negated_op = '¬' + operands[1 - operators.index('∧')]
            if negated_op in operands:
                return '0'
        elif '∨' in operators and '¬' in expr:
            negated_op = '¬' + operands[1 - operators.index('∨')]
            if negated_op in operands:
                return '1'
    elif law == 6:  # Idempotent Law
        if '∧' in operators and operands[0] == operands[1]:
            return operands[0]
        elif '∨' in operators and operands[0] == operands[1]:
            return operands[0]
    elif law == 7:  # Zero and One Law
        if '∧' in operators and '0' in operands:
            return '0'
        elif '∨' in operators and '1' in operands:
            return '1'
    elif law == 8:  # Absorption Law
        if '∧' in operators and '∨' in operators:
            if operators.index('∧') < operators.index('∨'):
                return operands[0]
            else:
                return operands[0]
    elif law == 9:  # De Morgan's Theorem
        if '¬' in expr and '∧' in expr:
            operand1 = operands[operators.index('∧')]
            operand2 = operands[operators.index('∧') + 1]
            return f"¬{operand1} ∨ ¬{operand2}"
        elif '¬' in expr and '∨' in expr:
            operand1 = operands[operators.index('∨')]
            operand2 = operands[operators.index('∨') + 1]
            return f"¬{operand1} ∧ ¬{operand2}"
    elif law == 10:  # Double Negation (Involution) Law
        if '¬¬' in expr:
            return expr.replace('¬¬', '')
    elif law == 11:  # Exclusive OR (XOR) Properties
        if '⊕' in operators:
            operand1 = operands[operators.index('⊕')]
            operand2 = operands[operators.index('⊕') + 1]
            return f"({operand1} ∧ ¬{operand2}) ∨ (¬{operand1} ∧ {operand2})"
    elif law == 12:  # Implication Transformation
        if '⇒' in operators:
            operand1 = operands[operators.index('⇒')]
            operand2 = operands[operators.index('⇒') + 1]
            return f"¬{operand1} ∨ {operand2}"
    elif law == 13:  # NAND and NOR Laws
        if '∧' in operators:
            return f"¬({operands[0]} ∧ {operands[1]})"
        elif '∨' in operators:
            return f"¬({operands[0]} ∨ {operands[1]})"
    elif law == 14:  # Exclusive NOR (XNOR) Properties
        if '⊕¬' in expr:
            operands, operators = split_operands(expr.replace('⊕¬', '⊕'))
            operand1 = operands[operators.index('⊕')]
            operand2 = operands[operators.index('⊕') + 1]
            return f"¬({operand1} ⊕ {operand2})"
        elif '⊙' in operators:
            operand1 = operands[operators.index('⊙')]
            operand2 = operands[operators.index('⊙') + 1]
            return f"({operand1} ∧ {operand2}) ∨ (¬{operand1} ∧ ¬{operand2})"
    elif law == 16:  # Consensus Theorem
        if len(operands) == 3 and '∧' in operators and '∨' in operators:
            return f"({operands[0]} ∧ {operands[1]}) ∨ (¬{operands[0]} ∧ {operands[2]})"
    elif law == 17:  # Consensus Law
        if len(operands) == 3 and '∧' in operators and '∨' in operators:
            return f"({operands[0]} ∧ {operands[1]}) ∨ (¬{operands[1]} ∧ {operands[2]})"
    elif law == 18:  # Adjacency Law
        if '∧' in operators and len(operands) == 2 and '¬' in operands[1]:
            return operands[0]
    elif law == 19:  # Simplification Law
        if '∧' in operators and '∨' in operators and len(operands) == 2 and '¬' in operands[1]:
            return operands[0]
    elif law == 20:  # Implication Laws
        if '⇒' in operators:
            operand1 = operands[operators.index('⇒')]
            operand2 = operands[operators.index('⇒') + 1]
            return f"¬{operand1} ∨ {operand2}"
        elif '¬⇒' in expr:
            operands, operators = split_operands(expr.replace('¬⇒', '⇒'))
            operand1 = operands[operators.index('⇒')]
            operand2 = operands[operators.index('⇒') + 1]
            return f"{operand1} ∧ ¬{operand2}"
    elif law == 21:  # Biconditional (iff) Laws
        if '⇔' in operators:
            operand1 = operands[operators.index('⇔')]
            operand2 = operands[operators.index('⇔') + 1]
            return f"({operand1} ∧ {operand2}) ∨ (¬{operand1} ∧ ¬{operand2})"
        elif '¬⇔' in expr:
            operands, operators = split_operands(expr.replace('¬⇔', '⇔'))
            operand1 = operands[operators.index('⇔')]
            operand2 = operands[operators.index('⇔') + 1]
            return f"{operand1} ⊕ {operand2}"
    return expr

# law number to law name
num2name = {
    1: "Commutative Law",
    2: "Associative Law",
    3: "Distributive Law",
    4: "Identity Law",
    5: " Negation Law",
    6: "Idempotent Law",
    7: "Zero and One Law",
    8: "Absorption Law",
    9: "De Morgan's Theorem",
    10: "Double Negation (Involution) Law",
    11: "Exclusive OR (XOR) Properties",
    12: "Implication Transformation",
    13: "NAND and NOR Laws",
    14: "Exclusive NOR (XNOR) Properties",
    16: "Consensus Theorem",
    17: "Consensus Law",
    18: "Adjacency Law",
    19: "Simplification Law",
    20: "Implication Laws",
    21:"Biconditional (iff)"
}


# ------Example-------
# set up parser
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('--law', type=int, help='Determines which law to apply')
parser.add_argument('--expression', type=int, help='A boolean expression to apply laws on')
args = parser.parse_args()
print("args       :", args)

# capute expression from command line or default
if args.expression: expression = args.expression
else: expression = "A∧(B∨C)"

# capute law number from command line or default
if args.law: law = args.law
else: law = 1

# Example usage
print("expression :", expression)
simplified = apply_law(law, expression)  # Apply Distributive Law
print("\nDetail:")
print(f"applying law #{law}: '{num2name[law]}' to expression of {expression}")
print(f"{num2name[law]} --> {expression} = {simplified}")
print("\noutput:")
print(simplified)  # Output: (A ∧ B) ∨ (A ∧ C)
