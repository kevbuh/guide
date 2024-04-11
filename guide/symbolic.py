"""
SYMBOLIC ENGINE

parses the boolean logic which is provided as input into AST and uses pattern matching
in python to identify which condition the current tree falls into. Once it identifies
the condition, it manipulates the tree into the new logical condition and returns all 
unparsed trees.
"""

import astor
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
    
def apply_all_laws(expr, to_print=False):
  """
  Collects all logical prompts for each logical law 

  Input: Binary Expression                                            <class 'str'>
  Output: Key item pairs of law and list of its possible deductions   <class 'dict_items'>

  Example:
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
  nodes = bTree.parse_tree() # NOTE: don't delete this line or else everything breaks
  parsed_code = bTree.parseTree
  new_expressions = defaultdict(list)

  if to_print: print("input  :", expr)
  if to_print: print("detail :")

  # ----------APPLY LAWS ONTO AST ONE AT A TIME-----------

  # Identity Law
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[a, Constant(value=0)]) | BoolOp(op=And(), values=[a, Constant(value=1)]):     
              new_node = Name(id=a)
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Identity Law"].append(modified_code[:-1]) # -1 to get rid of new line
              if to_print: print(f" - Applying Identity Law: {expr} = {modified_code[:-1]}")
              
  # Domination Law
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[a, Constant(value=1)]):                                                        
              new_node = Constant(value=1)
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Domination Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Domination Law: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[a, Constant(value=0)]):                                                       
              new_node = Constant(value=0)
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Domination Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Domination Law 2: {expr} = {modified_code[:-1]}")

  # Double Negation Law 
  for node in walk(parsed_code): 
      match node:
          case UnaryOp(op=Not(), operand=UnaryOp(op=Not(), operand=a)):                                               
              new_node = Name(id=a)
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Double Negation Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Double Negation Law: {expr} = {modified_code[:-1]}")

  # Commutative Law
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[a, b]):                                                                        
              new_node = BoolOp(op=Or(), values=[b, a])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Commutative Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Commutative Law: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[a, b]):                                                                       
              new_node = BoolOp(op=And(), values=[b, a])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Commutative Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Commutative Law: {expr} = {modified_code[:-1]}")

  # Associative Law
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[a, b]), c]):                                           
              new_node = BoolOp(op=Or(), values=[a, BoolOp(op=Or(), values=[b, c])])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Associative Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Associative Law: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[BoolOp(op=And(), values=[a, b]), c]):                                         
              new_node = BoolOp(op=And(), values=[a, BoolOp(op=And(), values=[b, c])])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Associative Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Associative Law 2: {expr} = {modified_code[:-1]}")

  # Distributive Law
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[b, c])]):                                          
              new_node = BoolOp(op=Or(), values=[BoolOp(op=And(), values=[a, b]), BoolOp(op=And(), values=[a, c])])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Distributive Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Distributive Law: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[b, c])]):                                          
              new_node = BoolOp(op=And(), values=[BoolOp(op=Or(), values=[a, b]), BoolOp(op=Or(), values=[a, c])])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["Distributive Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying Distributive Law 2: {expr} = {modified_code[:-1]}")

  # DeMorgan's Law 
  for node in walk(parsed_code): 
      match node:
          case UnaryOp(op=Not(), operand=BoolOp(op=Or(), values=[a, b])):                                             
              new_node = BoolOp(op=And(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["DeMorgan Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying DeMorgan's Law 1: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case UnaryOp(op=Not(), operand=BoolOp(op=And(), values=[a, b])):                                            
              new_node = BoolOp(op=Or(), values=[UnaryOp(op=Not(), operand=a), UnaryOp(op=Not(), operand=b)])
              replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
              modified_code = astor.to_source(replaced_tree)
              new_expressions["DeMorgan Law"].append(modified_code[:-1])
              if to_print: print(f" - Applying DeMorgan's Law 2: {expr} = {modified_code[:-1]}")

  # Absorption Law, NOTE: doesn't work for (a and (a or b))
  for node in walk(parsed_code):
      match node:
          case BoolOp(op=Or(), values=[a, BoolOp(op=And(), values=[*objects])]):                                      
              if t_util.are_subtrees_equivalent(a, objects[0]): 
                  new_node = Name(id=a)
                  replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                  modified_code = astor.to_source(replaced_tree)
                  new_expressions["Absorption Law"].append(modified_code[:-1])
                  if to_print: print(f" - Applying Absorption Law: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[a, BoolOp(op=Or(), values=[*objects])]):                                      
              if t_util.are_subtrees_equivalent(a, objects[0]): 
                  new_node = Name(id=a)
                  replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                  modified_code = astor.to_source(replaced_tree)
                  new_expressions["Absorption Law"].append(modified_code[:-1])
                  if to_print: print(f" - Applying Absorption Law 2: {expr} = {modified_code[:-1]}")

  # Idempotent Law - NOTE: doesn't work for ((x and y) or (x and y)). should reduce to (x and y)
  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=Or(), values=[*objects]):                                                                    
              if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                  new_node = objects[0]
                  new_ast = parsed_code
                  replaced_tree = ReplaceVisitor(node, new_node).visit(new_ast)
                  modified_code = astor.to_source(replaced_tree)
                  new_expressions["Idempotent Law"].append(modified_code[:-1])
                  if to_print: print(f" - Applying Idempotent Law OR: {expr} = {modified_code[:-1]}")

  for node in walk(parsed_code): 
      match node:
          case BoolOp(op=And(), values=[*objects]):                                                                    
              if t_util.are_subtrees_equivalent(objects[0], objects[1]):
                  new_node = objects[0]
                  replaced_tree = ReplaceVisitor(node, new_node).visit(parsed_code)
                  modified_code = astor.to_source(replaced_tree)
                  new_expressions["Idempotent Law"].append(modified_code[:-1])
                  if to_print: print(f" - Applying Idempotent Law AND: {expr} = {modified_code[:-1]}")

  if to_print: print("output :",new_expressions)
  return new_expressions

if __name__ == '__main__':  
  import argparse
  parser = argparse.ArgumentParser(description="Symbolic engine CLI args")
  parser.add_argument("--expr", type=str, help="The expression to evaluate")
  args = parser.parse_args()
  expr = args.expr if args.expr else "(x and x) or (x and x)"
  apply_all_laws(expr, to_print=True)
    