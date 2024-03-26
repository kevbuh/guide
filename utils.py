from dataclasses import dataclass
import ast

@dataclass
class BooleanTree:
    tree: ast.AST

print("x or y:", ast.dump(ast.parse('x or y', mode='eval'), indent=4))

