"""
SYMBOLIC ENGINE

parses the boolean logic which is provided as input into AST and uses pattern matching
in python to identify which condition the current tree falls into. Once it identifies
the condition, it manipulates the tree into the new logical condition and returns all 
unparsed trees.

example expressions:
# exp = "((not(x or y) and z) or True) <-> z"
exp = "(a -> (f -> c)) -> d"
# exp = "((a <-> (p <-> q)) <-> c) <-> d"
# exp = "p -> (a -> b)"
# exp = "(p -> b) -> a"
# exp = "(p -> b) <-> a"
# exp = "(not(b) and (a -> b)) <-> not(a)"
# exp = "(not(x and not(y)) or ((not(y) and z))) and z"
# exp = "(x and y) or (x and y)"
# exp = "((not x or not not not y) or z)"
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
from utils import booleanTree, helpers
from ast import BoolOp, Or, And, UnaryOp, Not, Name, Constant, walk, NodeTransformer

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
    
def simplify(expr, item_history=None, verbose=False):
    """
    Simplify Boolean expressions 

    Parameters:
    expr (str): Boolean expression to simplify.
    item_history (tuple, optional): Contains previous expressions and laws used.
    verbose (bool, optional): Print verbose debugging information.
    """
    if type(expr) == str:
        parseTree = ast.parse(expr, mode='eval')
    else:
        raise Exception(f"Expr {expr} should be string")
        
    tree = parseTree
    law_code_tuples = []

    # TODO: do unit tests to test simplifications

    for node in walk(tree): 
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=Or(), values=[Constant(value=0), a]): # a or 0 = a | 0 or a = a
                new_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, new_node).visit(tree)
                modified_code = astor.to_source(replaced_tree)
                law_code_tuples.append(("Simplification Law", modified_code[:-1])) 

            case BoolOp(op=Or(), values=[a, Constant(value=1)]) | BoolOp(op=Or(), values=[Constant(value=1), a]): # a or 1 = a | 1 or a = a
                new_node = Name(id=a)
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

    if verbose: print(f"SIMPLIFICATION OUTPUT {expr=}: {law_code_tuples}")

    # update with new expr and law
    if law_code_tuples != []:
        _, expr_history, law_history = item_history
        assert len(law_code_tuples) == 1, f"simplify() has too many simplifications"
        expr_history_new = expr_history + [law_code_tuples[0][1]]
        law_history_new = law_history + [law_code_tuples[0][0]] 
        return (law_code_tuples[0][1], expr_history_new, law_history_new)
    else:
        return None
    
def apply_bi_imp(expr, verbose=False):
    bTree = booleanTree(expr)
    bTree.parse_tree()
    parsed_code = bTree.parseTree
    assert ast.dump(ast.parse(parsed_code), indent=4) == bTree.parse_tree()

    simplified_expr = astor.to_source(parsed_code)[:-1]
    if simplified_expr != expr:
        if "<->" in expr and "->" in expr:
            if verbose: print("SIMPLIFY: implication/biconditional law applied")
            return ("Implication/Biconditional Law", simplified_expr)
        elif "<->" in expr:
            if verbose: print("SIMPLIFY: biconditional law applied")
            return ("Biconditional Law", simplified_expr)
        elif "->" in expr:
            if verbose: print("SIMPLIFY: implication law applied")
            return ("Implication Law", simplified_expr)
    return (None, None)

def symbolic_deduce(expr, verbose=False):
    """
    Creates logical expressions for each logical law 

    Input:  symbolic expression                                         <class 'str'>
    Output: key-item pairs of law and list of its possible deductions   <class 'dict_items'>

    Example output:
    ...
    input  : (x and y) or (x and y)
    detail :
    - Applying Commutative Law: (x and y) or (x and y) = (x and y or x and y)
    - Applying Commutative Law: (x and y) or (x and y) = (y and x or x and y)
    - Applying Commutative Law: (x and y) or (x and y) = (y and x or y and x)
    - Applying Distributive Law 2: (x and y) or (x and y) = ((y and x or y) and (y and x or x))
    output : defaultdict(<class 'list'>, {'Commutative Law': ['(x and y or x and y)', '(y and x or x and y)', '(y and x or y and x)'], 'Distributive Law': ['((y and x or y) and (y and x or x))']})
    """

    # ----------CREATE AST-----------

    bTree = booleanTree(expr)
    t_util = helpers()
    bTree.parse_tree()
    parsed_code = bTree.parseTree
    parsed_code_deepcopy = deepcopy(bTree.parseTree)
    assert ast.dump(ast.parse(parsed_code), indent=4) == bTree.parse_tree()

    new_expressions = defaultdict(list)

    if verbose: print("SYMBOLIC ENGINE input :", expr)
    if verbose: print("SYMBOLIC ENGINE detail:")

    # ----------APPLIES LAWS ONTO AST ONE AT A TIME-----------

    # Commutative Law
    for node in walk(parsed_code): # BFS traversal of the tree
        match node:
            case BoolOp(op=Or(), values=[a, b]):
                new_node = BoolOp(op=Or(), values=[b, a])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Commutative Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Applying Commutative Law OR: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, b]):
                new_node = BoolOp(op=And(), values=[b, a])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                #   print("REPLACED TREE", ast.dump(replaced_tree))
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Commutative Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Applying Commutative Law AND: {expr} = {modified_code[:-1]}")

    # Associative Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c]):
                new_node = BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Associative Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Applying Associative Law: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c]):
                new_node = BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Associative Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Applying Associative Law 2: {expr} = {modified_code[:-1]}")

    # Distributive Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])]):
                n_node = BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[a, c])])
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Distributive Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Applying Distributive Law AND: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[b, c])]):
                n_node = BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a, b]), BoolOp(op=Or(), values=[a, c])])
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Distributive Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Applying Distributive Law OR: {expr} = {modified_code[:-1]}")

    # Identity Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=And(), values=[a, Constant(value=1)]):
                new_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Identity Law"].append(modified_code[:-1]) # -1 to get rid of new line
                if verbose: print(f" - Applying Identity Law: {expr} = {modified_code[:-1]}")

    # Double Negation Law 
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case UnaryOp(op=Not(), operand=UnaryOp(op=Not(), operand=a)):
                n_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Double Negation Law "].append(modified_code[:-1])
                if verbose: print(f" - Applying Double Negation Law : {expr} = {modified_code[:-1]}")
    
    # Negation Law: not(a) and a = 0 | a and not(a) = 0
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), b]) | BoolOp(op=And(), values=[b, UnaryOp(op=Not(), operand=a)]):
                if t_util.are_subtrees_equivalent(a, b):
                    n_node = Constant(value=0)
                    replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Negation Law AND"].append(modified_code[:-1]) # -1 to get rid of new line
                    if verbose: print(f" - Applying Negation Law AND: {expr} = {modified_code[:-1]}")
    
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=b), a]) | BoolOp(op=Or(), values=[a, UnaryOp(op=Not(), operand=b)]):
                if t_util.are_subtrees_equivalent(a, b):
                    n_node = Name(id=a)
                    replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Negation Law OR"].append(modified_code[:-1]) # -1 to get rid of new line
                    if verbose: print(f" - Applying Negation Law OR: {expr} = {modified_code[:-1]}")

    # Idempotent Law
    parsed_code = deepcopy(parsed_code_deepcopy)  
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[*objects]):
                if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                    new_node = objects[0]
                    #   print("NEW NODE", ast.dump(new_node))
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Idempotent Law OR"].append(modified_code[:-1])
                    if verbose: print(f" - Applying Idempotent Law OR: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[*objects]):
                if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                    new_node = objects[0]
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Idempotent Law AND"].append(modified_code[:-1])
                    if verbose: print(f" - Applying Idempotent Law AND: {expr} = {modified_code[:-1]}")

    # Absorption Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[*objects])]) | BoolOp(op=Or(), values=[BoolOp(op=And(), values=[*objects]), a]):
                if t_util.are_subtrees_equivalent(a, objects[0]): 
                    new_node = Name(id=a)
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code) # replace node with new_node
                    modified_code = astor.to_source(replaced_tree) # re-evalaluate
                    new_expressions["Absorption Law 1"].append(modified_code[:-1])
                    if verbose: print(f" - Applying Absorption Law 1: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[*objects])]) | BoolOp(op=And(), values=[BoolOp(op=Or(), values=[*objects]), a]):
                if t_util.are_subtrees_equivalent(a, objects[0]): 
                    new_node = Name(id=a)
                    replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                    modified_code = astor.to_source(replaced_tree)
                    new_expressions["Absorption Law 2"].append(modified_code[:-1])
                    if verbose: print(f" - Applying Absorption Law 2: {expr} = {modified_code[:-1]}")

    # Domination Law
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=Or(), values=[a, Constant(value=1)]):
                new_node = Constant(value=1)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Domination Law OR"].append(modified_code[:-1])
                if verbose: print(f" - Applying Domination Law: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case BoolOp(op=And(), values=[a, Constant(value=0)]):
                new_node = Constant(value=0)
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["Domination Law AND"].append(modified_code[:-1])
                if verbose: print(f" - Applying Domination Law 2: {expr} = {modified_code[:-1]}")

    # DeMorgan's Law 
    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code):
        match node:
            case UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b])):
                new_node = BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["DeMorgan Law 1"].append(modified_code[:-1])
                if verbose: print(f" - Applying DeMorgan's Law 1: {expr} = {modified_code[:-1]}")

    parsed_code = deepcopy(parsed_code_deepcopy)
    for node in walk(parsed_code): 
        match node:
            case UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b])):
                new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
                replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                modified_code = astor.to_source(replaced_tree)
                new_expressions["DeMorgan Law 2"].append(modified_code[:-1])
                if verbose: print(f" - Applying DeMorgan's Law 2: {expr} = {modified_code[:-1]}")

    if verbose: print("SYMBOLIC ENGINE OUTPUT:", new_expressions)
    return new_expressions

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Symbolic engine CLI args")
    parser.add_argument("--expr", type=str, help="The expression to evaluate")
    args = parser.parse_args()
    expr = args.expr if args.expr else "(x and x) or (x and x)"
    expr = expr.strip()
    symbolic_deduce(expr, verbose=True)