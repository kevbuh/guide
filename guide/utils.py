import ast
import re
import regex
from collections import deque
from dataclasses import dataclass

@dataclass
class booleanTree:
    """
    Define a Python dataclass corresponding to the AST representation of the input logic 
    Input:
        tree: A string of the input boolean logic
    Symbols:
        0:   False          : Constant(value=False)
        1:   True           : Constant(value=True)
        and: AND            : op=And()
        or:  OR             : op=Or()
        not: NOT            : op=Not()
        ->:  Implication    
        <->: Bi-Conditional
    Output:
        AST representation of the input logic
    """
    tree: str
    astTree: ast = None
    parseTree: ast = None

    def __post_init__(self):
        """
        Post init method using structural pattern matching to match bi-conditional and implication operations
        Matches:
            p <-> q (bi-conditional): (p and q) or ((not p) and (not q))
            p -> q  (implication)   : (not p) or q 
        """
        success = 0
        groups = regex.search(r"(?<rec> \( (?: [^()]++ | (?&rec) )* \) )", str(self.tree), flags=regex.VERBOSE)
        group_matches = groups.captures('rec')
        for items in group_matches:
            match items:
                case str(x) if "<->" in x: 
                    success = 1
                    p, q = items[1:-1].split('<->', 1)
                    p, q = p.strip(), q.strip()
                    partial_step = "(" + p + " and " + q + ") or (not(" + p + ") and not(" + q + "))"
                    self.tree = self.tree.replace(items, partial_step)
                case str(x) if "->" in x:
                    success = 1
                    p, q = items[1:-1].split('->', 1)
                    p, q = p.strip(), q.strip()
                    partial_step = "(not(" + p + ") or " + q + ")"
                    self.tree = self.tree.replace(items, partial_step)
                case _:
                    pass
        
        if success == 1:
            self.__post_init__()
        else:
            if "<->" in str(self.tree):
                p, q = self.tree.split('<->', 1)
                p, q = p.strip(), q.strip()
                self.tree = "(" + p + " and " + q + ") or (not(" + p + ") and not(" + q + "))"
            elif "->" in str(self.tree):
                p, q = self.tree.split('->', 1)
                p, q = p.strip(), q.strip()
                self.tree = "not(" + p + ") or " + q
            self.astTree = self.tree

    def parse_tree(self, astTree=None) -> ast:
        """
        Return AST parse tree of the input logic
        """
        if astTree is None:
           self.parseTree = ast.parse(self.astTree, mode='eval')
        else:
           self.parseTree = astTree
        return ast.dump(self.parseTree, indent=4)

    def bfs_traversal(self, node):
        """
        Perform BFS traversal of the AST tree created using Deque operator
        """
        queue = deque([node])
        # Maintain a Queue for BFS
        while queue:
            current_node = queue.popleft()
            yield current_node
            # Check if current node can be parsed
            if isinstance(current_node, ast.AST):          
                for _, child_node in ast.iter_fields(current_node):
                    if isinstance(child_node, list):       # Check for list assoc in child node
                        for child in child_node:
                            if isinstance(child, ast.AST):
                                queue.append(child)
                    elif isinstance(child_node, ast.AST):  # Check for AST assoc in child node
                        queue.append(child_node)
    
    def do_traversal(self) -> list:
        """
        Returns the list of modules after a BFS traversal on the input logic
        """
        modules_ = []
        for node in self.bfs_traversal(self.parseTree):
            node_name = type(node).__name__
            if node_name != "Expression" and node_name != "Load":
                modules_.append(node_name)
        return modules_


class helpers:
    """
    Helper class which contains all the important functions
    """
    def are_subtrees_equivalent(self, node1, node2):
        """
        Recursively check if two subtrees are equivalent
        """
        if node1 is None and node2 is None:
            return True
        if node1 is None or node2 is None:
            return False
        
        if type(node1) != type(node2):
            return False
        
        if isinstance(node1, ast.AST):
            for attr in node1._fields:
                if not self.are_subtrees_equivalent(getattr(node1, attr), getattr(node2, attr)):
                    return False
        elif isinstance(node1, list):
            if len(node1) != len(node2):
                return False
            for n1, n2 in zip(node1, node2):
                if not self.are_subtrees_equivalent(n1, n2):
                    return False
        else:
            if node1 != node2:
                return False
        return True
