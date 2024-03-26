import ast
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
        match self.tree:
            # Match for bi-conditional
            case str(x) if "<->" in x: 
                p, q = self.tree.split('<->')
                p, q = p.strip(), q.strip()
                newtree = "(" + p + " and " + q + ") or (not(" + p + ") and not(" + q + "))"
                self.astTree = newtree
            # Match for implication
            case str(x) if "->" in x:
                p, q = self.tree.split('->')
                p, q = p.strip(), q.strip()
                newtree = "not(" + p + ") or " + q
                self.astTree = newtree
            # No matches
            case _:
                self.astTree = self.tree

    def parse_tree(self) -> ast:
       """
       Return AST parse tree of the input logic
       """
       self.parseTree = ast.parse(self.astTree, mode='eval')
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
            modules_.append(type(node))
        return modules_
