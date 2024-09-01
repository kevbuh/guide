import random
import ast
import astor
from copy import deepcopy
from utils import booleanTree, helpers
from ast import BoolOp, Or, And, UnaryOp, Not, Name, Constant, walk, Gt, Compare
from symbolic import ReplaceVisitor

def print_mirror(transformations):
    for expr, law in transformations:
        print(f"{expr:35} {law}")

def symbolic_mirror(expr, iterations=5, verbose=False):
    """
    Generates a logical expression into a longer tautological expression

    Input:  simple symbolic expression (e.g., "1")    <class 'str'>
    Output: expanded expression                       <class 'str'>

    Example output
    ...
    input  : 1
    output : ((1 or a) or b) and (1 or (a or b))
    """

    if expr[0] != "(" and expr[-1] != ")": expr = "(" + expr + ")"

    # ----------CREATE AST-----------
    bTree = booleanTree(expr)
    t_util = helpers()
    bTree.parse_tree()
    parsed_code = bTree.parseTree
    parsed_code_deepcopy = deepcopy(bTree.parseTree)
    assert ast.dump(ast.parse(parsed_code), indent=4) == bTree.parse_tree()

    laws = [
        "Associative Law OR",
        "Associative Law AND",
        "Distributive Law AND",
        "Distributive Law OR",
        "Identity Law 1",
        "Identity Law 2",
        "Identity Law 3",
        "Negation Law OR",
        "Idempotent Law OR",
        "Idempotent Law AND",
        "Absorption Law OR",
        "Absorption Law AND",
        "DeMorgan Law 1",
        "DeMorgan Law 2",
        "DeMorgan Law 3",
        "DeMorgan Law 4",
        "Implication Law 1",
        "Implication Law 2",
        "Commutative Law OR",
        "Commutative Law AND"
    ]

    parsed_code = deepcopy(parsed_code_deepcopy)

    i = 0
    transformations = []
    print(expr)
    while i < iterations:
        law = random.choice(laws)
        parsed_code = deepcopy(parsed_code)

        if law == "Associative Law OR": # (a or b) or c = a or (b or c)
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])]):
                        new_node = BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Associative Law AND": # (a and b) and c = a and (b and c)
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])]):
                        new_node = BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Distributive Law AND": # (a and b) or (a and c) = a and (b or c)
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[x, c])]):
                        new_node = BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Distributive Law OR": # (a or b) and (a or c) = a or (b and c)
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a1, b]), BoolOp(op=Or(), values=[a2, c])]):
                        new_node = BoolOp(op=Or(), values=[a1, BoolOp(op=And(), values=[b, c])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Identity Law 1": # a or 1 = 1
            for node in walk(parsed_code):
                match node:
                    case Constant(value=1):
                        new_node = BoolOp(op=Or(), values=[Name(id='a'), Constant(value=1)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Identity Law 2": # a = a and 1
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):  # Changed 'a' to 'id'
                        new_node = BoolOp(op=And(), values=[Name(id=a), Constant(value=1)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Identity Law 3": # a = a or 0
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=Or(), values=[Name(id=a), Constant(value=0)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Negation Law OR": # 1 = a or not a
            for node in walk(parsed_code):
                match node:
                    case Constant(value=1):
                        a = Name(id='a')
                        new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Idempotent Law OR": # a = a or a
            for node in walk(parsed_code): 
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=Or(), values=[Name(id=a), Name(id=a)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Idempotent Law AND": # a = a and a
            for node in walk(parsed_code): 
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=And(), values=[Name(id=a), Name(id=a)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Absorption Law OR": # a = a or (a and b)
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=Or(), values=[Name(id=a), BoolOp(op=And(), values=[Name(id=a), Name(id='b')])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Absorption Law AND": # a = a and (a or b)
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=And(), values=[Name(id=a), BoolOp(op=Or(), values=[Name(id=a), Name(id='b')])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "DeMorgan Law 1": # not a and not b = not (a or b)
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)]):
                        new_node = UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b]))
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break
        
        elif law == "DeMorgan Law 2": # not (a or b) = not a and not b
            for node in walk(parsed_code):
                match node:
                    case UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b])):
                        new_node = BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "DeMorgan Law 3": # not a or not b = not (a and b)
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)]):
                        new_node = UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b]))
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break
        
        elif law == "DeMorgan Law 4": # not (a and b) = not a or not b
            for node in walk(parsed_code): 
                match node:
                    case UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b])):
                        new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Implication Law 1": # not a or b = a -> b 
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), b]):
                        new_node = Compare(left=a, ops=[Gt()], comparators=[b])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Implication Law 2": # a -> b = not a or b
            for node in walk(parsed_code): 
                match node:
                    case Compare(left=a, ops=[Gt()], comparators=[b]):
                        new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), b])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Commutative Law OR": # a or b = b or a
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=Or(), values=[a, b]):
                        new_node = BoolOp(op=Or(), values=[b, a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code) 
                        modified_code = astor.to_source(parsed_code)                    
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

        elif law == "Commutative Law AND": # a and b = b and a
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=And(), values=[a, b]):
                        new_node = BoolOp(op=And(), values=[b, a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        i += 1
                        if verbose: transformations.append((modified_code[:-1], law))
                        break

    if verbose: print_mirror(transformations)
    return astor.to_source(parsed_code).strip()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Symbolic mirror CLI args")
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    args = parser.parse_args()
    expr = args.expr if args.expr else "1"
    expr = expr.strip()

    expanded_expr = symbolic_mirror(expr, iterations=10, verbose=True)