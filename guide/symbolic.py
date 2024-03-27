from utils import booleanTree, helpers
from ast import BoolOp, Or, And, UnaryOp, Not, Name, Constant
from ast import walk, unparse, NodeTransformer
import astor

# exp = "((not(x or y) and z) or True) <-> z"
# exp = "(not(x and not(y)) or ((not(y) and z))) and z"
# exp = "(x and y) or (x and y)"
# exp = "((not x or not not not y) or z)"
# exp = "a or b"
# exp = "(a and b) and c"
# exp = "a or (b and c)"
exp = "p or (p and q)"
bTree = booleanTree(exp)
t_util = helpers()
nodes = bTree.parse_tree()
print("Original expression: ", exp)
print(bTree.parse_tree())

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

parsed_code = bTree.parseTree

for node in walk(parsed_code):
    match node:
        case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=And(), values=[a, Constant(value=1)]):      # Identity Law
            n_node = Name(id=a)
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[a, Constant(value=1)]):                                                        # Domination Law
            n_node = Constant(value=1)
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=And(), values=[a, Constant(value=0)]):                                                       # Domination Law
            n_node = Constant(value=0)
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case UnaryOp(op=Not(), operand=UnaryOp(op=Not(), operand=a)):                                               # Double Negation Law 
            n_node = Name(id=a)
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[a, b]):                                                                        # Commutative Law
            n_node = BoolOp(op=Or(), values=[b, a])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=And(), values=[a, b]):                                                                       # Commutative Law
            n_node = BoolOp(op=And(), values=[b, a])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c]):                                           # Associative Law
            n_node = BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c]):                                         # Associative Law
            n_node = BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])]):                                          # Distributive Law
            n_node = BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[a, c])])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[b, c])]):                                          # Distributive Law
            n_node = BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a, b]), BoolOp(op=Or(), values=[a, c])])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[*objects])]):                                      # Absorption Law
            if t_util.are_subtrees_equivalent(a, objects[0]): 
                n_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[*objects])]):                                      # Absorption Law
            if t_util.are_subtrees_equivalent(a, objects[0]): 
                n_node = Name(id=a)
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b])):                                             # DeMorgan's Law 1
            n_node = BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b])):                                            # DeMorgan's Law 2
            n_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
            replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)
        case BoolOp(op=Or(), values=[*objects]) | BoolOp(op=And(), values=[*objects]):                              # Idempotent Law
            if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                n_node = objects[0]
                replaced_tree = ReplaceVisitor(node, n_node).visit(parsed_code)

# Convert the modified AST back to code
# print(bTree.parse_tree(replaced_tree))
modified_code = astor.to_source(bTree.parseTree)
print("\nConverted Expression: ", modified_code)