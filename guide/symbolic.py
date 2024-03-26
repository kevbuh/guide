from utils import booleanTree
from ast import BoolOp, Or

# exp = "((not(x or y) and z) or True) <-> z"
exp = "not(x or y)"
bTree = booleanTree(exp)
nodes = bTree.parse_tree()
print(nodes)
