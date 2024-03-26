from dataclasses import dataclass
import ast

# boolean AST
@dataclass
class BooleanTree:
    tree: ast.AST

# pattern matcher

print("x or y:", ast.dump(ast.parse('x or y', mode='eval'), indent=4))

