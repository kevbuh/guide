"""
SYMBOLIC ENGINE

parses the boolean logic which is provided as input into AST and uses pattern matching
in python to identify which condition the current tree falls into. Once it identifies
the condition, it manipulates the tree into the new logical condition and returns all 
unparsed trees.

example expressions:
# exp = "((not(a or b) and c) or True) <-> c"
exp = "(a -> (f -> c)) -> d"
# exp = "((a <-> (p <-> q)) <-> c) <-> d"
# exp = "p -> (a -> b)"
# exp = "(p -> b) -> a"
# exp = "(p -> b) <-> a"
# exp = "(not(b) and (a -> b)) <-> not(a)"
# exp = "(not(a and not(b)) or ((not(b) and c))) and c"
# exp = "(a and b) or (a and b)"
# exp = "((not a or not not not b) or c)"
# exp = "a or b"
# exp = "(a and b) and c"
# exp = "a or (b and c)"
# exp = "(a or b) or ((a or b) and q)"

# exp = "(not(b) and (a -> b)) -> not(a)"
# exp = "(not (not b and not a or not b and b) or not a)"
# exp = "((not b and not not a or b) or not a)"
# exp = "(not a or (b or a and not b))"
# exp = "((b or not b and a) or not a)"
"""

import ast
import astor
from copy import deepcopy
from collections import defaultdict
from .utils import booleanTree, helpers
from ast import BoolOp, Or, And, UnaryOp, Not, Name, Constant, walk, NodeTransformer, Gt, Compare

class ReplaceVisitor(NodeTransformer):
    def __init__(self, original_node, replacement_node):
        self.original_node = original_node
        self.replacement_node = replacement_node

    def visit_UnaryOp(self, node):
        if node == self.original_node:
            return self.replacement_node
        return self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        if node == self.original_node:
            return self.replacement_node
        return self.generic_visit(node)
    
    def visit_Compare(self, node):
        if node == self.original_node:
            return self.replacement_node
        return self.generic_visit(node)
    
def simplify(expr, item_history=None, verbose=False):
    """
    Simplify Boolean expressions 

    Parameters:
    expr (str): Boolean expression to simplify.
    item_history (tuple, optional): Contains previous expressions and laws used.
    verbose (bool, optional): Print verbose debugging information.
    """
    if expr[0] != "(" and expr[-1] != ")": expr = "(" + expr + ")"

    if type(expr) == str:
        parseTree = ast.parse(expr, mode='eval')
    else:
        raise Exception(f"Expr {expr} should be string")
    
    tree = parseTree
    law_code_tuples = []

    for node in walk(tree):
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=Or(), values=[Constant(value=0), a]): # a or 0 = a | 0 or a = a
                new_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            case BoolOp(op=Or(), values=[a, Constant(value=1)]) | BoolOp(op=Or(), values=[Constant(value=1), a]): # a or 1 = 1 | 1 or a = 1
                new_node = Constant(value=1)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            case BoolOp(op=And(), values=[a, Constant(value=1)]) | BoolOp(op=And(), values=[Constant(value=1), a]): # a and 1 = a |  1 and a = a
                new_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1]))

            case BoolOp(op=And(), values=[a, Constant(value=0)]) | BoolOp(op=And(), values=[Constant(value=0), a]): # a and 0 = 0 | 0 and a = 0
                new_node = Constant(value=0)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            # not 0 = 1
            case UnaryOp(op=Not(), operand=Constant(value=0)):
                new_node = Constant(value=1)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            # not 1 = 0
            case UnaryOp(op=Not(), operand=Constant(value=1)):
                new_node = Constant(value=0)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            # Double Negation Law 
            case UnaryOp(op=Not(), operand=UnaryOp(op=Not(), operand=a)):
                n_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, n_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law (Double Negation)", modified_code[:-1]))

    if verbose and law_code_tuples != []: print(f"[SIMPLIFICATION OUTPUT] {expr=}: {law_code_tuples}")

    # update with new expr and law
    if law_code_tuples != []:
        _, expr_history, law_history = item_history
        final_expr = None
        for law,code in law_code_tuples:
            expr_history = expr_history + [code]
            law_history = law_history + [law]
            final_expr = code
        return (final_expr, expr_history, law_history)
    else:
        return None
    
def apply_bi_imp(expr, verbose=False):
    bTree = booleanTree(expr)
    bTree.parse_tree()
    parsed_code = bTree.parseTree
    assert ast.dump(ast.parse(parsed_code), indent=4) == bTree.parse_tree()

    simplified_expr = astor.to_source(parsed_code)[:-1]
    if simplified_expr != expr:
        if "<->" in expr:
            if verbose: print("SIMPLIFY: biconditional law applied")
            return ("Biconditional Law", simplified_expr)
    return (None, None)

def is_reduced(expr):
    """ check if expr is unreducable expression """
    if expr[0] != "(" and expr[-1] != ")": expr = "(" + expr + ")"

    bTree = booleanTree(expr)
    bTree.parse_tree()
    parsed_code = bTree.parseTree

    vartree = []
    for node in walk(parsed_code):
        match node:
            case Name(id=a):
                vartree.append(a)
            case Constant(value=value):
                vartree.append(str(value))

    can_simplify = simplify(expr=expr, item_history=("", [], []))
    has_unique_vars = sorted(list(set(vartree))) == sorted(vartree)

    if can_simplify:
        return False
    
    # TODO: is this the right check?
    if (len(vartree) == 1) or (not can_simplify and has_unique_vars and '0' not in vartree and '1' not in vartree):
        print(f"{expr=} cannot be reduced further...")
        return True
    return False

def symbolic_deduce(expr, verbose=False):
    """
    Creates logical expressions for each logical law 

    Input:  symbolic expression                                         <class 'str'>
    Output: key-item pairs of law and list of its possible deductions   <class 'dict_items'>

    Example output:
    ...
    input  : (a and b) or (a and b)
    detail :
    - Commutative Law: (a and b) or (a and b) = (a and b or a and b)
    - Commutative Law: (a and b) or (a and b) = (b and a or a and b)
    - Commutative Law: (a and b) or (a and b) = (b and a or b and a)
    - Distributive Law 2: (a and b) or (a and b) = ((b and a or b) and (b and a or a))
    output : defaultdict(<class 'list'>, {'Commutative Law': ['(a and b or a and b)', '(b and a or a and b)', '(b and a or b and a)'], 'Distributive Law': ['((b and a or b) and (b and a or a))']})
    """
    if expr[0] != "(" and expr[-1] != ")": expr = "(" + expr + ")"

    # ----------CREATE AST-----------
    bTree = booleanTree(expr)
    t_util = helpers()
    bTree.parse_tree()
    parsed_code = bTree.parseTree
    parsed_code_deepcopy = deepcopy(bTree.parseTree)
    assert ast.dump(ast.parse(parsed_code), indent=4) == bTree.parse_tree()

    new_expressions = defaultdict(list)

    if verbose: print("[SYMBOLIC ENGINE input] :", expr)
    if verbose: print("[SYMBOLIC ENGINE detail]:")

    # Associative Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c]):
                new_node = BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Associative Law OR"].append(modified_code[:-1]) 
                if verbose: print(f" - Associative Law: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c]):
                new_node = BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Associative Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Associative Law 2: {expr} = {modified_code[:-1]}")

    # Distributive Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])]):
                n_node = BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[a, c])])
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Distributive Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Distributive Law AND: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[b, c])]):
                n_node = BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a, b]), BoolOp(op=Or(), values=[a, c])])
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Distributive Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Distributive Law OR: {expr} = {modified_code[:-1]}")

    # Identity Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=And(), values=[a, Constant(value=1)]):
                new_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Identity Law"].append(modified_code[:-1]) 
                if verbose: print(f" - Identity Law: {expr} = {modified_code[:-1]}")
    
    # Negation Law: not(a) and a = 0 | a and not(a) = 0
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), b]) | BoolOp(op=And(), values=[b, UnaryOp(op=Not(), operand=a)]):
                if t_util.are_subtrees_equivalent(a, b):
                    n_node = Constant(value=0)
                    replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Negation Law AND"].append(modified_code[:-1]) 
                    if verbose: print(f" - Negation Law AND: {expr} = {modified_code[:-1]}")
    
    # Negation Law: not a or a = 1 | a or not a = 1
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=b), a]) | BoolOp(op=Or(), values=[a, UnaryOp(op=Not(), operand=b)]):
                if t_util.are_subtrees_equivalent(a, b):
                    n_node = Constant(value=1)
                    replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Negation Law OR"].append(modified_code[:-1]) 
                    if verbose: print(f" - Negation Law OR: {expr} = {modified_code[:-1]}")

    # Idempotent Law
    parsed_code = deepcopy(parsed_code_deepcopy)  
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[*objects]):
                if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                    new_node = objects[0]
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Idempotent Law OR"].append(modified_code[:-1])
                    if verbose: print(f" - Idempotent Law OR: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[*objects]):
                if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                    new_node = objects[0]
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Idempotent Law AND"].append(modified_code[:-1])
                    if verbose: print(f" - Idempotent Law AND: {expr} = {modified_code[:-1]}")

    # Absorption Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[*objects])]) | BoolOp(op=Or(), values=[BoolOp(op=And(), values=[*objects]), a]):
                if t_util.are_subtrees_equivalent(a, objects[0]): 
                    new_node = Name(id=a)
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree) 
                    new_expressions["Absorption Law 1"].append(modified_code[:-1])
                    if verbose: print(f" - Absorption Law 1: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[*objects])]) | BoolOp(op=And(), values=[BoolOp(op=Or(), values=[*objects]), a]):
                if t_util.are_subtrees_equivalent(a, objects[0]): 
                    new_node = Name(id=a)
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Absorption Law 2"].append(modified_code[:-1])
                    if verbose: print(f" - Absorption Law 2: {expr} = {modified_code[:-1]}")

    # Domination Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=1)]):
                new_node = Constant(value=1)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Domination Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Domination Law: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, Constant(value=0)]):
                new_node = Constant(value=0)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Domination Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Domination Law 2: {expr} = {modified_code[:-1]}")

    # DeMorgan's Law 
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b])):
                new_node = BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["DeMorgan Law 1"].append(modified_code[:-1])
                if verbose: print(f" - DeMorgan's Law 1: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b])):
                new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["DeMorgan Law 2"].append(modified_code[:-1])
                if verbose: print(f" - DeMorgan's Law 2: {expr} = {modified_code[:-1]}")

    # Implication Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case Compare(left=a, ops=[Gt()], comparators=[b]):
                new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), b])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Implication Law"].append(modified_code[:-1]) 
                if verbose: print(f" - Implication Law: {expr} = {modified_code[:-1]}")

    # check if expr is unreducable expression
    can_simplify = simplify(expr=expr, item_history=("", [], []))

    if is_reduced(expr) and not can_simplify:
        return new_expressions

    # ----------APPLIES LAWS ONTO AST ONE AT A TIME-----------

    # Commutative Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[a, b]):
                new_node = BoolOp(op=Or(), values=[b, a])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code) # replace node with new_node
                modified_code = astor.to_source(replaced_tree)                    # re-evalaluate
                new_expressions["Commutative Law OR"].append(modified_code[:-1])  # -1 to get rid of new line
                if verbose: print(f" - Applying Commutative Law OR: {expr} = {modified_code[:-1]}") 
            
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, b]):
                new_node = BoolOp(op=And(), values=[b, a])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Commutative Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Applying Commutative Law AND: {expr} = {modified_code[:-1]}")

    if verbose: print("[SYMBOLIC ENGINE OUTPUT]:", new_expressions)
    return new_expressions

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Symbolic engine CLI args")
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    args = parser.parse_args()
    expr = args.expr if args.expr else "(a and a) or (a and a)"
    expr = expr.strip()
    symbolic_deduce(expr, verbose=True)