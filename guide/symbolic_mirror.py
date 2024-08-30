import random
import ast
import astor
from copy import deepcopy
from utils import booleanTree, helpers
from ast import BoolOp, Or, And, UnaryOp, Not, Name, Constant, walk, Gt, Compare
from symbolic import ReplaceVisitor

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

    if verbose: print("[SYMBOLIC MIRROR INPUT] :", expr)

    laws = [
        "Associative Law OR",
        "Associative Law AND",
        "Distributive Law AND",
        "Distributive Law OR",
        "Identity Law",
        "Negation Law OR",
        "Idempotent Law OR",
        "Idempotent Law AND",
        "Absorption Law OR",
        "Absorption Law AND",
        "DeMorgan Law 1",
        "DeMorgan Law 2",
        "Implication Law",
        "Commutative Law OR",
        "Commutative Law AND"
    ]

    parsed_code = deepcopy(parsed_code_deepcopy)

    i = 0
    while i < iterations:
        law = random.choice(laws)
        if verbose: print(f"iteration: {i + 1}: {law}")
        parsed_code = deepcopy(parsed_code)

        if law == "Associative Law OR":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])]):
                        new_node = BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Associative Law AND":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])]):
                        new_node = BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Distributive Law AND":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[x, c])]):
                        new_node = BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Distributive Law OR":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a1, b]), BoolOp(op=Or(), values=[a2, c])]):
                        new_node = BoolOp(op=Or(), values=[a1, BoolOp(op=And(), values=[b, c])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Identity Law":
            for node in walk(parsed_code):
                match node:
                    case Constant(value=1):
                        new_node = BoolOp(op=Or(), values=[Name(id='a'), Constant(value=1)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Negation Law OR":
            for node in walk(parsed_code):
                match node:
                    case Constant(value=1):
                        a = Name(id='a')
                        new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Idempotent Law OR":
            for node in walk(parsed_code): 
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=Or(), values=[Name(id=a), Name(id=a)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Idempotent Law AND":
            for node in walk(parsed_code): 
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=And(), values=[Name(id=a), Name(id=a)])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Absorption Law OR":
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=Or(), values=[Name(id=a), BoolOp(op=And(), values=[Name(id=a), Name(id='b')])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Absorption Law AND":
            for node in walk(parsed_code):
                match node:
                    case Name(id=a):
                        new_node = BoolOp(op=And(), values=[Name(id=a), BoolOp(op=Or(), values=[Name(id=a), Name(id='b')])])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "DeMorgan Law 1":
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)]):
                        new_node = UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b]))
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "DeMorgan Law 2":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)]):
                        new_node = UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b]))
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Implication Law":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), b]):
                        new_node = Compare(left=a, ops=[Gt()], comparators=[b])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f"iteration {i + 1}: {modified_code[:-1]} ({law})")
                        i += 1
                        break

        elif law == "Commutative Law OR":
            for node in walk(parsed_code):
                match node:
                    case BoolOp(op=Or(), values=[a, b]):
                        new_node = BoolOp(op=Or(), values=[b, a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code) 
                        modified_code = astor.to_source(parsed_code)                    
                        if verbose: print(f" - Applying {law}: {modified_code[:-1]}") 
                        i += 1
                        break
            
        elif law == "Commutative Law AND":
            for node in walk(parsed_code): 
                match node:
                    case BoolOp(op=And(), values=[a, b]):
                        new_node = BoolOp(op=And(), values=[b, a])
                        parsed_code = ReplaceVisitor(node, new_node).visit(parsed_code)
                        modified_code = astor.to_source(parsed_code)
                        if verbose: print(f" - Applying {law}: {modified_code[:-1]}")
                        i += 1
                        break

    return astor.to_source(parsed_code).strip()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Symbolic mirror CLI args")
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    args = parser.parse_args()
    expr = args.expr if args.expr else "1"
    expr = expr.strip()

    expanded_expr = symbolic_mirror(expr, iterations=10, verbose=True)
    print(f"\nFinal expanded expression: {expanded_expr}")