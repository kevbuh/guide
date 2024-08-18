import random
from copy import deepcopy
from ast import BoolOp, Load, Or, And, UnaryOp, Not, Name, Constant, UnaryOp, unparse, Load, parse

def symbolic_expand(expr, iterations=5, verbose=False):
    """
    Generates a logical expression into a longer tautological expression

    Input:  simple symbolic expression (e.g., "1")    <class 'str'>
    Output: expanded expression                       <class 'str'>

    Example output
    ...
    input  : 1
    output : ((1 or y) or z) and (1 or (y or z))
    """
    if not expr.strip():
        raise ValueError("Expression cannot be empty")

    current_expr = expr
    expansion_history = [current_expr]

    for i in range(iterations):
        if verbose:
            print(f"iteration: {i + 1}:")

        # choose a random law
        expansion_law = random.choice([
            "identity_law",
            "idempotent_law",
            "commutative_law",
            "associative_law",
            "distributive_law",
            "demorgan_law",
            "double_negation",
        ])

        new_expr = apply_expansion_law(current_expr, expansion_law)

        if new_expr != current_expr:
            current_expr = new_expr
            expansion_history.append(current_expr)
            if verbose:
                print(f"Applied {expansion_law}: {current_expr}")
        else:
            if verbose:
                print(f"No change after applying {expansion_law}")

    if verbose:
        print("\nExpansion history:")
        for step, expr in enumerate(expansion_history):
            print(f"Step {step}: {expr}")

    return current_expr

def apply_expansion_law(expr, law):
    """Apply a specific expansion law to the expression."""
    tree = parse(expr)

    if law == "identity_law": return identity_law(tree)
    elif law == "idempotent_law": return idempotent_law(tree)
    elif law == "commutative_law": return commutative_law(tree)
    elif law == "associative_law": return associative_law(tree)
    elif law == "distributive_law": return distributive_law(tree)
    elif law == "demorgan_law": return demorgan_law(tree)
    elif law == "double_negation": return double_negation(tree)
    else: return expr

def identity_law(tree):
    """Expand using identity law: x -> (x or False) or (x and True)"""
    new_tree = BoolOp(
        op=Or(),
        values=[
            BoolOp(op=Or(), values=[tree.body[0].value, Constant(value=False)]),
            BoolOp(op=And(), values=[tree.body[0].value, Constant(value=True)])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def idempotent_law(tree):
    """Expand using idempotent law: x -> (x or x) and (x and x)"""
    new_tree = BoolOp(
        op=And(),
        values=[
            BoolOp(op=Or(), values=[tree.body[0].value, deepcopy(tree.body[0].value)]),
            BoolOp(op=And(), values=[tree.body[0].value, deepcopy(tree.body[0].value)])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def commutative_law(tree):
    """Expand using commutative law: x -> (x and y) or (y and x)"""
    y = Name(id='y', ctx=Load())
    new_tree = BoolOp(
        op=Or(),
        values=[
            BoolOp(op=And(), values=[tree.body[0].value, y]),
            BoolOp(op=And(), values=[y, tree.body[0].value])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def associative_law(tree):
    """Expand using associative law: x -> ((x or y) or z) and (x or (y or z))"""
    y = Name(id='y', ctx=Load())
    z = Name(id='z', ctx=Load())
    new_tree = BoolOp(
        op=And(),
        values=[
            BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[tree.body[0].value, y]), z]),
            BoolOp(op=Or(), values=[tree.body[0].value, BoolOp(op=Or(), values=[y, z])])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def distributive_law(tree):
    """Expand using distributive law: x -> (x and y) or (x and z)"""
    y = Name(id='y', ctx=Load())
    z = Name(id='z', ctx=Load())
    new_tree = BoolOp(
        op=Or(),
        values=[
            BoolOp(op=And(), values=[tree.body[0].value, y]),
            BoolOp(op=And(), values=[tree.body[0].value, z])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def demorgan_law(tree):
    """Expand using De Morgan's law: x -> not(not x and not y)"""
    y = Name(id='y', ctx=Load())
    new_tree = UnaryOp(
        op=Not(),
        operand=BoolOp(
            op=And(),
            values=[
                UnaryOp(op=Not(), operand=tree.body[0].value),
                UnaryOp(op=Not(), operand=y)
            ]
        )
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def double_negation(tree):
    """Expand using double negation: x -> not(not x)"""
    new_tree = UnaryOp(
        op=Not(),
        operand=UnaryOp(op=Not(), operand=tree.body[0].value)
    )
    tree.body[0].value = new_tree
    return unparse(tree)

if __name__ == "__main__":
    initial_expr = "1" # start out with simple tautology
    expanded_expr = symbolic_expand(initial_expr, iterations=5, verbose=True)
    print(f"\nFinal expanded expression: {expanded_expr}")