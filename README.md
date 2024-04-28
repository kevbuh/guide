# Guide

<div align="center">
    <img src="./assets/guided llm v5.svg" alt="System Overview" width="600"/>
</div>

Logical equivalence symbolic engine guided by tree-of-thoughts 

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add these lines into a .env file
# ANTHROPIC_API_KEY=<your-api-key-here>
# OPENAI_API_KEY=<your-api-key-here>
```

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
- [x] Solve CK's hard expressions
- [ ] Write testcases
    - [x] simplify() (Simplification engine)
    - [x] is_reduced()
    - [ ] proof_engine()
- [ ] Set up experiment suite to track model performance
- [ ] Start experimenting with how to improve ToT
    - [x] remove already chosen options
    - [x] save state into file so you can resume process later
    - [ ] look at entire tree
    - [ ] test with other prompts
    - [ ] choose law with respect to the probabilities
    - [ ] prune based off of >75 score

## Usage

Looks like the system works for simple expressions!

Command: uses GPT-3.5-Turbo and prints out process information. 

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
                       [--verbose] [--cot] [--claude] [--T T] [--B B] [--K K]
                       [--early_stop] [--pure_llm] [--del_choice] [--ckpt]

options:
  -h, --help            show this help message and exit
  --expr EXPR           The expression to evaluate
  --num_steps NUM_STEPS
                        Number of proof steps
  --debug               Print debug statements
  --verbose             Print out states at each step
  --cot                 Use Chain of Thought
  --claude              Use Claude-3-Haiku
  --T T                 ToT tree depth
  --B B                 ToT branching factor
  --K K                 ToT max number of nodes per level
  --early_stop          Return on first proof found
  --pure_llm            Evaluate all expressions through llm instead of
                        symbolic engine
  --del_choice          Delete law option after LLM choice
  --ckpt                Resume from last q in guide/ckpt.txt
```

## Symbolic Logic

### *Notation*

<!-- $T: \text{TRUE}$ -->

<!-- $F: \text{FALSE}$ -->

$\land: \text{AND}$

$\lor: \text{OR}$

$\lnot : \text{NOT}$

$\equiv: \text{Equivalence}$

$\Rightarrow: \text{Implication}$

$\Leftrightarrow: \text{Bi-Conditional}$

<!-- $$ \\{a\dots z\\}: \text{Expression} $$ -->

<!-- $$ A \uparrow B: \text{NAND} $$ -->

<!-- $$ A \downarrow B: \text{NOR} $$ -->

<!-- $$ A \odot B: \text{XNOR} $$ -->
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

10. **Implication Transformation**:
    - $A \Rightarrow B = \lnot A \lor B$

11. **Consensus Theorem**:
    - $(A \land B) \lor (\lnot A \land C) \lor (B \land C) = (A \land B) \lor (\lnot A \land C)$

12. **Consensus Law**:
    - $(A \land B) \lor (\lnot B \land C) \lor (A \land C) = (A \land B) \lor (\lnot B \land C)$

13. **Adjacency Law**:
    - $(A \land B) \lor (A \land \lnot B) = A$

14. **Simplification Law**:
    - $(A \lor B) \land (A \lor \lnot B) = A$

15. **Implication Laws**:
    - $A \Rightarrow B = \lnot A \lor B$
    - $\lnot (A \Rightarrow B) = A \land \lnot B$

16. **Biconditional (iff) Laws**:
    - $A \Leftrightarrow B = (A \land B) \lor (\lnot A \land \lnot B)$
    <!-- - $\lnot (A \Leftrightarrow B) = A \oplus B$ -->

<!-- 11. **Exclusive OR (XOR) Properties**:
    - $A \oplus B = (A \land \lnot B) \lor (\lnot A \land B)$
    - $A \oplus B = (A \lor B) \land \lnot (A \land B)$
    - $A \oplus 0 = A$
    - $A \oplus A = 0$ -->

<!-- 13. **NAND and NOR Laws**:
    - $A \uparrow B = \lnot(A \land B)$
    - $A \downarrow B = \lnot(A \lor B)$ -->

<!-- 14. **Exclusive NOR (XNOR) Properties**:
    - $A \oplus B = \lnot(A \oplus B)$
    - $A \odot B = (A \land B) \lor (\lnot A \land \lnot B)$ -->

<!-- ## Bug tracker -->

<!-- - Symbolic Engine -->
<!-- - Absorption Law doesn't trigger for "(a and (a or b))" -->
<!-- - Absorption Law doesn't trigger for "(a or (a and b)) -> a" -->
<!-- - Absorption Law doesn't trigger for "not((a or (a and b)) -> a)" -->
<!-- - Absorption Law doesn't trigger for "(((y and x) or x) and y)" -->
<!-- - Absorption Law doesn't trigger for "((x or (x and y)) and y)" -->
<!-- - Idempotent Law doesn't work for "((x and y) or (x and y))" -->
