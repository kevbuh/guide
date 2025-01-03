import re
import ast
import regex
from collections import deque
from dataclasses import dataclass

from prompts import propose_prompt, propose_prompt_long

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
                case _:
                    pass
        
        if success == 1:
            self.__post_init__()
        else:
            if "<->" in str(self.tree):
                p, q = self.tree.split('<->', 1)
                p, q = p.strip(), q.strip()
                self.tree = "(" + p + " and " + q + ") or (not(" + p + ") and not(" + q + "))"
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
    
def create_propose_prompt(expr, expr_deductions):
    """output law and expression in a numbered list and create prompt"""
    choices_list = []
    choice_dict = {} # Tracks the possible choices to choose from
    counter = 0

    for law, expressions in expr_deductions.items():
        for expression in expressions:
            choice = f"#{counter}. '{law}', '{expression}'\n"
            choices_list.append(choice)
            choice_dict[str(counter)] = (expression, law)
            counter += 1

    choices = "".join(choices_list)
    llm_message = f"{expr=}\n{choices=}{propose_prompt}"

    # TODO: experiment with other prompts
    # llm_message = propose_prompt_long.format(expr=expr, choices=choices)
    # print("LLM_MESSAGE",llm_message)

    return llm_message, choice_dict

def get_llm_choice(llm_text, choice_dict, llm_message, llm):
    """search for LLM choice selection and send choice back to symbolic engine"""
    pattern = r"LLM CHOICE: #(\d+)\."
    match = re.search(pattern, llm_text)
    retries = 0
    MAX_RETRIES = 3

    while retries < MAX_RETRIES:
        if match:
            choice_number = match.group(1)
            if choice_number in choice_dict:
                new_expr, new_law = choice_dict[choice_number]
                return choice_number, new_expr, new_law
            else:
                print(f"WARNING: Choice number {choice_number} not in choice_dict. Retrying...{choice_dict=}")
        else:
            print("Couldn't find LLM choice...retrying")
        
        llm_res = llm(message=llm_message)  # Send message to LLM and collect its text response
        match = re.search(pattern, llm_res)
        retries += 1

    raise ValueError("ERROR: Valid choice number not found after maximum retries")

def get_llm_value(llm_text, llm_message, llm):
    """search for LLM value and send choice back"""
    match = re.search(r'\d+', llm_text)
    retries = 0

    MAX_RETRIES = 2
    while not match and retries < MAX_RETRIES:
        print("Couldn't find number...retrying")
        llm_res = llm(message=llm_message)  # send message to llm and collect its text response
        match = re.search(r'\d+', llm_res)
        retries += 1

    if match:
        value = int(match.group(0))
        return value
    else:
        raise ValueError("ERROR: Choice number not found after maximum retries")
    
def get_greedy_choice(choice_dict):
    shortest = float("inf")
    choice_number, new_expr, new_law = "", "", ""
    for key, (expr, law) in choice_dict.items():
        cur_len = len(choice_dict)
        if cur_len < shortest:
            shortest = cur_len
            choice_number, new_expr, new_law = key, expr, law
    return choice_number, new_expr, new_law