# symbolic logic task
from llm import llm
from prompts import value_prompt
from symbolic import symbolic_deduce
from proof_engine import terminal_values, create_propose_prompt, get_llm_choice, get_formatted_proof

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

# def get_value():
#     pass

def get_votes():
    """
    from ToT paper:
    Vote across states: V(p_θ,S)(s) = 1[s = s^*], where a “good” state s* ~ p_θ^vote (s^*|S) is
    voted out based on deliberately comparing different states in S in a vote prompt. When
    problem success is harder to directly value (e.g. passage coherency), it is natural to to instead
    compare different partial solutions and vote for the most promising one. This is similar
    in spirit to a “step-wise” self-consistency strategy, i.e. cast “which state to explore” as a
    multi-choice QA, and use LM samples to vote for it
    """
    pass

def get_values(exprs):
    """
    from ToT paper:
    Value each state independently: V(p_θ , S)(s) ~ p_θ^value (v|s) ∀s ∈ S, where a value
    prompt reasons about the state s to generate a scalar value v (e.g. 1-10) or a classification 
    (e.g. sure/likely/impossible) that could be heuristically turned into a value. The basis
    of such evaluative reasoning can vary across problems and thought steps. In this work, we
    explore evaluation via few lookahead simulations (e.g. quickly confirm that 5, 5, 14 can
    reach 24 via 5 + 5 + 14, or “hot l” can mean “inn” via filling “e” in “ ”) plus commonsense
    (e.g. 1 2 3 are too small to reach 24, or no word can start with “tzxc”). While the former
    might promote “good” states, the latter could help eliminate “bad” states. Such valuations
    do not need to be perfect, and only need to be approximately helpful for decision making
    """
    values = []
    for expr in exprs:
        prompt = value_prompt.format(expr)
        value = llm(message=prompt)
        # TODO: regex capture value
        values.append(value)
    return zip(values, exprs)

def get_proposals():
    pass

def get_samples():
    pass

def argmax():
    pass

def solve_naive(): # cot solver
    # TODO
    pass