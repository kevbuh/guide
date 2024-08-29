import random
from ast import BoolOp, Load, Or, And, UnaryOp, Not, Name, Constant, UnaryOp, unparse, Load, parse

def symbolic_expand(expr="1", iterations=5, verbose=False):
    """
    Generates a logical expression into a longer tautological expression

    Input:  simple symbolic expression (e.g., "1")    <class 'str'>
    Output: expanded expression                       <class 'str'>

    Example output
    ...
    input  : 1
    output : ((1 or a) or b) and (1 or (a or b))
    """
    if not expr.strip():
        raise ValueError("Expression cannot be empty")

    current_expr = expr
    expansion_history = [current_expr]
    i = 0
    while i < iterations:
        if verbose: print(f"iteration: {i + 1}:")

        # choose a random law
        expansion_law = random.choice([
            "identity_law",
            "idempotent_law_or",
            "idempotent_law_and",
            "commutative_law_and",
            "commutative_law_or",
            "associative_law_and",
            "associative_law_or",
            "distributive_law_or",
            "distributive_law_and",
            # "demorgan_law",
            "double_negation",
        ])

        new_expr = apply_expansion_law(current_expr, expansion_law)

        if new_expr != current_expr:
            current_expr = new_expr
            expansion_history.append(current_expr)
            if verbose: print(f"Applied {expansion_law}: {current_expr}")
        else:
            if verbose: print(f"No change after applying {expansion_law}, retrying...")
            i -= 1
        i += 1

    if verbose:
        print("\nExpansion history:")
        for step, expr in enumerate(expansion_history):
            print(f"Step {step}: {expr}")

    return current_expr

def apply_expansion_law(expr, law):
    """Apply a specific expansion law to the expression."""
    tree = parse(expr)
    if law == "identity_law": return identity_law(tree)
    elif law == "idempotent_law_or": return idempotent_law_or(tree)
    elif law == "idempotent_law_and": return idempotent_law_and(tree)
    elif law == "commutative_law_and": return commutative_law_and(tree)
    elif law == "commutative_law_or": return commutative_law_or(tree)
    elif law == "associative_law_and": return associative_law_and(tree)
    elif law == "associative_law_or": return associative_law_or(tree)
    elif law == "distributive_law_or": return distributive_law_or(tree)
    elif law == "distributive_law_and": return distributive_law_and(tree)
    # elif law == "demorgan_law": return demorgan_law(tree)
    elif law == "double_negation": return double_negation(tree)
    else: return expr

def commutative_law_and(tree):
    """Expand using commutative law: a and b = b and a"""
    if len(tree.body) < 2:
        return unparse(tree)

    new_tree = BoolOp(
        op=And(),
        values=[
            tree.body[1].value, 
            tree.body[0].value
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def commutative_law_or(tree):
    """Expand using commutative law: a or b = b or a"""
    if len(tree.body) < 2:
        return unparse(tree)

    new_tree = BoolOp(
        op=Or(),
        values=[
            tree.body[1].value, 
            tree.body[0].value
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def associative_law_and(tree):
    """Expand using associative law: (a and b) and c = a and (b and c)"""
    if len(tree.body) < 3:
        return unparse(tree)

    new_tree = BoolOp(
        op=And(),
        values=[
            BoolOp(op=And(), values=[tree.body[0].value, tree.body[1].value]),
            tree.body[2].value
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def associative_law_or(tree):
    """Expand using associative law for OR: (a or b) or c = a or (b or c)"""
    if len(tree.body) < 3:
        return unparse(tree)

    new_tree = BoolOp(
        op=Or(),
        values=[
            tree.body[0].value,
            BoolOp(op=Or(), values=[tree.body[1].value, tree.body[2].value])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def distributive_law_and(tree):
    """Expand using distributive law: a and (b or c) = (a and b) or (a and c)"""
    if len(tree.body) < 2:
        return unparse(tree)

    new_tree = BoolOp(
        op=Or(),
        values=[
            BoolOp(op=And(), values=[tree.body[0].value, tree.body[1].value]),
            BoolOp(op=And(), values=[tree.body[0].value, tree.body[2].value])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def distributive_law_or(tree):
    """Expand using distributive law: a or (b and c) = (a or b) and (a or c)"""
    if len(tree.body) < 2:
        return unparse(tree)

    new_tree = BoolOp(
        op=And(),
        values=[
            BoolOp(op=Or(), values=[tree.body[0].value, tree.body[1].value]),
            BoolOp(op=Or(), values=[tree.body[0].value, tree.body[2].value])
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def identity_law(tree):
    """Expand using identity law: 1 = 1 or a"""
    if isinstance(tree.body[0].value, Constant) and tree.body[0].value.value == 1:
        new_tree = BoolOp(
            op=Or(),
            values=[
                Constant(value=True),
                Name(id='a', ctx=Load())
            ]
        )
        tree.body[0].value = new_tree
    return unparse(tree)

def idempotent_law_or(tree):
    """Expand using idempotent law: a = a or a"""
    new_tree = BoolOp(
        op=Or(),
        values=[
            tree.body[0].value,
            tree.body[0].value
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def idempotent_law_and(tree):
    """Expand using idempotent law: a = a and a"""
    new_tree = BoolOp(
        op=And(),
        values=[
            tree.body[0].value,
            tree.body[0].value
        ]
    )
    tree.body[0].value = new_tree
    return unparse(tree)

def negation_law(tree):
    """Expand using negation law: 1 = a or not a"""
    if isinstance(tree.body[0].value, Constant) and tree.body[0].value.value == 1:
        a = Name(id='a', ctx=Load())
        new_tree = BoolOp(
            op=Or(),
            values=[
                a,
                UnaryOp(op=Not(), operand=a)
            ]
        )
        tree.body[0].value = new_tree
    return unparse(tree)

# def demorgan_law(tree):
#     """Expand using De Morgan's law: not (a and b) = not a or not b"""
#     a = tree.body[0].value  # First argument 'a'
#     b = tree.body[1].value  # Second argument 'b'
#     new_tree = BoolOp(
#         op=Or(),
#         values=[
#             UnaryOp(op=Not(), operand=a),
#             UnaryOp(op=Not(), operand=b)
#         ]
#     )
#     tree.body[0].value = UnaryOp(op=Not(), operand=new_tree)
#     return unparse(tree)

def double_negation(tree):
    """Expand using double negation: a = not(not a)"""
    new_tree = UnaryOp(
        op=Not(),
        operand=UnaryOp(op=Not(), operand=tree.body[0].value)
    )
    tree.body[0].value = new_tree
    return unparse(tree)

if __name__ == "__main__":
    expanded_expr = symbolic_expand("1", iterations=5, verbose=True)
    print(f"\nFinal expanded expression: {expanded_expr}")