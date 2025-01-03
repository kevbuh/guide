# Guide

<div align="center">
    <img src="./assets/guided llm v5.svg" alt="System Overview" width="600"/>
</div>

<br/>

```This was a side project done at CUPLV. With the release of ChatGPT o1, we have decided to halt research on this project.```

Enhanced Reasoning Tautological Proof Engine guided by Tree-of-Thoughts LLM Search

Paper: https://docs.google.com/document/d/1liiAKZFuTx96SoPN0SpGxQ_fUkkf4cPevdCTqcdylPo/edit?usp=sharing

Google Drive: https://drive.google.com/drive/folders/1jO0-AwkdevsX-YyOQKRhMk6_uAEuWx_H?usp=sharing

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add these lines into a .env file
# ANTHROPIC_API_KEY=<your-api-key-here>
# OPENAI_API_KEY=<your-api-key-here>
```

## Proof Engine

Creates a proof using a guided tree-of-thoughts

```bash
python3 guide/proof_engine.py
```

Output
```
SOLVING: '(x and x) or (x and x)'
LLM: gpt-3.5-turbo
PARAMS: T=5, B=3, K=5, early_stop=False, pure_llm=False
ENGINE: symbolic
METHOD: tree of thoughts
----------------------------
TREE DEPTH:1/5
TREE DEPTH:2/5
pruning 4 leaves...
TREE DEPTH:3/5
FULLY REDUCED EXPR, PROOF DONE.
REMOVING NON-UNIQUE PROOF...
pruning 4 leaves...
TREE DEPTH:4/5
FULLY REDUCED EXPR, PROOF DONE.
REMOVING NON-UNIQUE PROOF...
REMOVING NON-UNIQUE PROOF...
FULLY REDUCED EXPR, PROOF DONE.
REMOVING NON-UNIQUE PROOF...
TREE DEPTH:5/5
----------FINAL PROOF----------
Proof:
(x and x) or (x and x)                Idempotent Law
≡ (x and x or x)                      Idempotent Law
≡ x
----------FINAL PROOF #2----------
Proof:
(x and x) or (x and x)                Distributive Law
≡ ((x and x or x) and (x and x or x)) Idempotent Law
≡ (x or x)                            Idempotent Law
≡ x
----------FINAL PROOF #3----------
Proof:
(x and x) or (x and x)                Idempotent Law
≡ (x and x or x)                      Idempotent Law
≡ (x and x)                           Idempotent Law
≡ x
```


CLI Arguments
```bash
usage: proof_engine.py [-h] [--expr EXPR] [--num_steps NUM_STEPS] [--debug]
                       [--verbose] [--cot] [--model MODEL] [--T T] [--B B]
                       [--K K] [--early_stop] [--pure_llm] [--unique] [--ckpt]
                       [--random] [--greedy]

options:
  -h, --help            show this help message and exit
  --expr EXPR           The expression to evaluate
  --num_steps NUM_STEPS
                        Number of proof steps
  --debug               Print debug statements
  --verbose             Print out states at each step
  --cot                 Use Chain of Thought
  --model MODEL         Specify a model to use
  --T T                 ToT tree depth
  --B B                 ToT branching factor
  --K K                 ToT max number of nodes per level
  --early_stop          Return on first proof found
  --pure_llm            Evaluate all expressions through llm instead of symbolic engine
  --unique              Select unique steps at each node
  --ckpt                Resume from last q in guide/ckpt.txt
  --random              Randomly select expression
  --greedy              Greedy select shortest expression
```

## Synthetic Mirror

```bash
python3 guide/symbolic_mirror.py
```
```
(1)
(a or 1)                            Identity Law 1
(a or (a or 1))                     Identity Law 1
((a or a) or (a or 1))              Idempotent Law OR
((a or a) or (a or (a or 1)))       Identity Law 1
(((a or a and b) or a) or (a or (a or 1))) Absorption Law OR
(((a or b and a) or a) or (a or (a or 1))) Commutative Law AND
((((a or b and a) or a) or a) or (a or 1)) Associative Law OR
((((a or b and a) or a) or a) or (a or (a or 1))) Identity Law 1
((((a or b and a) or a) or a and 1) or (a or (a or 1))) Identity Law 2
(((((a or b and a) or a) or a and 1) or a) or (a or 1)) Associative Law OR
```

## Symbolic Logic Reference

### *Notation*

$\land: \text{AND}$

$\lor: \text{OR}$

$\lnot : \text{NOT}$

$\equiv: \text{Equivalence}$

$\Rightarrow: \text{Implication}$

$\Leftrightarrow: \text{Bi-Conditional}$

### *Laws*

1. **Commutative Law**:
   - $A \land B = B \land A$
   - $A \lor B = B \lor A$

2. **Associative Law**:
   - $(A \land B) \land C = A \land (B \land C)$
   - $(A \lor B) \lor C = A \lor (B \lor C)$

3. **Distributive Law**:
   - $A \land (B \lor C) = (A \land B) \lor (A \land C)$
   - $A \lor (B \land C) = (A \lor B) \land (A \lor C)$

4. **Identity Law**:
   - $A \land 1 = A$; $A \land 0 = 0$
   - $A \lor 0 = A$; $A \lor 1 = 1$

5. **Negation Law**:
   - $A \land \lnot A = 0$
   - $A \lor \lnot A = 1$

6. **Idempotent Law**:
   - $A \land A = A$
   - $A \lor A = A$

7. **Absorption Law**:
   - $A \land (A \lor B) = A$
   - $A \lor (A \land B) = A$

8. **De Morgan's Theorem**:
   - $\lnot (A \land B) = \lnot A \lor \lnot B$
   - $\lnot (A \lor B) = \lnot A \land \lnot B$

9. **Double Negation (Involution) Law**:
    - $\lnot (\lnot A) = A$

10. **Implication**:
    - $A \Rightarrow B = \lnot A \lor B$
   
## Roadmap

- [x] Proof engine
    - [x] use the engine to collect all the logical prompts
    - [x] and feed it to the LM
    - [x] complete loop from llm choice back to prompt engine
    - [x] track entire history of selections
        - [x] expressions
        - [x] laws it chose
    - [x] prune identical proofs
- [x] Tree of thoughts
    - [x] integrate original repo
    - [x] option for GPT-3.5 Turbo or Claude-3 Haiku
    - [x] use value evaluation and prune
    - [x] stop when found first proof
    - [x] add expr_history for more accurate value ratings
    - [x] Flag to choose all llm or use symbolic engine 
- [x] Symbolic engine
    - [x] expression to AST representation
    - [x] implement common laws on the AST
    - [x] simplification engine
    - [x] complete implication and bi-conditional laws
    - [x] fix expression bugs (below in bug tracker)
- [ ] Write testcases
    - [x] simplify() (Simplification engine)
    - [x] is_reduced()
    - [ ] proof_engine()
- [ ] Experiments
    - [x] remove already chosen options
    - [x] save state into file so you can resume process later
    - [ ] Set up experiment suite to track model performance
    - [ ] look at entire tree
    - [ ] test with other prompts
    - [ ] choose law with respect to the probabilities
    - [ ] prune based off of >75 score
    - [ ] How variable are the results in terms of temp
    - [ ] How LLM performance scales with number of variables or length of expression
    - [ ] Compare LLM performance vs
        - [ ] Random choice
        - [ ] Greedy
        - [ ] simulated annealing ( prob inverse of complexity)
        - [ ] other heuristics
    - [ ] Find patterns of shortest vs longest proofs
    - [ ] Try different prompts with complexity measure like number of variables, depth, etc
    - [ ] Generate new problems by negating known unsatisfiable expressions
    - [ ] top-p 
        - [0.1, 0.25, 0.5]
    - [ ] temperature tests 
        - [0, 0.25, 0.5, 0.75]
    - [ ] Compare shortest vs longest proofs 
    - [ ] How variable are the results in terms of temp
    - [ ] Does LLM give us insights 
	    - Helps with larger and larger formulas?
    - [ ] Incrementally increase size of formula
    - [ ] How often does it succeed
    - [ ] Find short proofs 
    - [ ] Successful solve = repeat experiment X times with depth and time out and see how often its solved 
    - [ ] Shortest proof == bfs or dfs? vs LLM solution 
    - [ ] Give complexity measure like number of variables, depth, simulated annealing -> prob inverse of complexity
    - [ ] Is it just doing any better than random guesses?
- [ ] Complex expressions
    - [x] CK's
    - [ ] "(a > b) > ((b > c) > (a > c))"
    - [ ] [Common Tautologies](https://mathweb.ucsd.edu/~jeggers/math109/tautologies.pdf) 19-25
        - [x] "(P and (P > Q)) > Q"
        - [x] "((P > Q) and not Q) > not P"
        - [ ] "((P > Q) and (Q > R)) > (P > R)"
        - [x] "((P or Q) and not P ) > Q"
        - [ ] "(P > C) > not P"
            - This isn't a tautology?
        - [ ] "((P > Q) and (R > S)) > ((P or R) > (Q or S))"
        - [x] "(P > Q) > ((P or R) > (Q or R))"
    - [ ] [SATLIB - Benchmark Problems](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
    - [ ] Unsatisfiable formulas and negate

<!-- ## Bug tracker -->
<!-- - Symbolic Engine -->
<!-- - Absorption Law doesn't trigger for "(a and (a or b))" -->
<!-- - Absorption Law doesn't trigger for "(a or (a and b)) -> a" -->
<!-- - Absorption Law doesn't trigger for "not((a or (a and b)) -> a)" -->
<!-- - Absorption Law doesn't trigger for "(((y and x) or x) and y)" -->
<!-- - Absorption Law doesn't trigger for "((x or (x and y)) and y)" -->
<!-- - Idempotent Law doesn't work for "((x and y) or (x and y))" -->
