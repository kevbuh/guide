# symbolic logic task
import os
DATA_PATH = os.path.join(os.path.dirname(__file__))

class Task:
    def __init__(self):
        pass

    def __len__(self) -> int:
        pass

    def get_input(self, idx: int) -> str:
        pass

    def test_output(self, idx: int, output: str):
        pass
    
    # extra methods
    @staticmethod
    def standard_prompt_wrap():
        pass
    
    @staticmethod
    def cot_prompt_wrap():
        pass
    
    @staticmethod
    def propose_prompt_wrap():
        pass
    
    @staticmethod
    def value_prompt_wrap():
        pass
    
    @staticmethod
    def value_outputs_unwrap():
        pass

    
# BFS

def get_value():
    pass

def get_values():
    pass

def get_votes():
    pass

def get_proposals():
    pass

def get_samples():
    pass

def solve(expr, args, idx, to_print=True): # tot solver
    print("expr=", expr)
    ys = [''] # current output candidates
    infos = []

    for step in range(args.steps):
        print(f"step: {step}")

        # generation
        if args.method_generate == 'propose':
            new_ys = [get_proposals(expr, y) for y in ys]
        elif args.method_generate == 'sample':
            pass


def naive_solve(): # cot solver
    pass