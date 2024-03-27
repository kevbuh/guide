# Guide

<div align="center">
    <img src="./assets/system_overview.png" alt="System Overview" width="600"/>
</div>


Logical equivalence symbolic engine guided by tree-of-thoughts 


## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Example usage

Looks like Claude-3 Haiku is already really good at identifying tautologies without ToT...

```bash
(venv) ➜  guide git:(main) ✗ python3 guide/prompt_engine.py

original input expression: (x and y) or (x and y)
Choose one of the following that you think will best help you solve if this statement is a tautology.
Generate thoughts about which logical law helps you most, then output 1 row, where the row is a selection of what law is best.
#1., 'Commutative Law', '(x and y or x and y)'
#2., 'Commutative Law', '(y and x or x and y)'
#3., 'Commutative Law', '(y and x or y and x)'
#4., 'Distributive Law', '((y and x or y) and (y and x or x))'

---------------------

The logical law that would be most helpful in determining if the given statement is a tautology is the Distributive Law.

The Distributive Law states that for any logical expressions A, B, and C, the following is true:

(A and B) or (A and C) = A and (B or C)

Applying the Distributive Law to the given expression, we get:

(x and y) or (x and y) = x and (y or y)

Since y or y is always true (i.e., 1), the expression simplifies to:

x and 1 = x

Therefore, the given expression is a tautology, as it is always true regardless of the values of x and y.

The correct selection is:

4., 'Distributive Law', '((y and x or y) and (y and x or x))'
```

## Roadmap

- [x] Build symbolic engine
    - [x] expression to AST representation
    - [x] implement common laws on the AST
    - [ ] complete writing the logic for the implication and bi-conditional laws
- [x] Build prompt engine
    - [x] use the engine to collect all the logical prompts
    - [x] and feed it to the LM
- [ ] boolean tree of thoughts
    - [x] integrate original repo
    - [ ] Set up boolean task
    - [ ] Option for GPT-3.5 Turbo or Claude-3 Haiku
- [ ] Set up experiment suite to track model performances
- [ ] Start experimenting with how to improve ToT

## Symbols

$$ T: \text{TRUE}$$

$$ F: \text{FALSE}$$

$$ \\&: \text{AND}$$

$$ |: \text{OR}$$

$$ \sim : \text{NOT}$$

$$ \equiv: \text{Equivalence}$$

$$ \rightarrow: \text{Implication}$$

$$ \leftrightarrow: \text{Bi-Conditional}$$

$$ \\{a\dots z\\}: \text{Expression} $$

$$ A \uparrow B: \text{NAND} $$

$$ A \downarrow B: \text{NOR} $$

$$ A \odot B: \text{XNOR} $$


## Common Logic Laws

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
   - $A \land \lnot A = 0$ (contradiction)
   - $A \lor \lnot A = 1$ (tautology)

6. **Idempotent Law**:
   - $A \land A = A$
   - $A \lor A = A$

7. **Zero and One Law**:
   - $A \land 0 = 0$
   - $A \lor 1 = 1$

8. **Absorption Law**:
   - $A \land (A \lor B) = A$
   - $A \lor (A \land B) = A$

9. **De Morgan's Theorem**:
   - $\lnot (A \land B) = \lnot A \lor \lnot B$
   - $\lnot (A \lor B) = \lnot A \land \lnot B$

10. **Double Negation (Involution) Law**:
    - $\lnot (\lnot A) = A$

11. **Exclusive OR (XOR) Properties**:
    - $A \oplus B = (A \land \lnot B) \lor (\lnot A \land B)$
    - $A \oplus B = (A \lor B) \land \lnot (A \land B)$
    - $A \oplus 0 = A$
    - $A \oplus A = 0$

12. **Implication Transformation**:
    - $A \Rightarrow B = \lnot A \lor B$

13. **NAND and NOR Laws**:
    - $A \uparrow B = \lnot(A \land B)$
    - $A \downarrow B = \lnot(A \lor B)$

14. **Exclusive NOR (XNOR) Properties**:
    - $A \oplus B = \lnot(A \oplus B)$
    - $A \odot B = (A \land B) \lor (\lnot A \land \lnot B)$

16. **Consensus Theorem**:
    - $(A \land B) \lor (\lnot A \land C) \lor (B \land C) = (A \land B) \lor (\lnot A \land C)$

17. **Consensus Law**:
    - Removes a term when covered by a consensus
    - $(A \land B) \lor (\lnot B \land C) \lor (A \land C) = (A \land B) \lor (\lnot B \land C)$

18. **Adjacency Law**:
    - Simplifies expressions involving adjacent terms in a Karnaugh map or truth table
    - $(A \land B) \lor (A \land \lnot B) = A$

19. **Simplification Law**:
    - $(A \lor B) \land (A \lor \lnot B) = A$

20. **Implication Laws**:
    - $A \Rightarrow B = \lnot A \lor B$
    - $\lnot (A \Rightarrow B) = A \land \lnot B$

21. **Biconditional (iff) Laws**:
    - $A \Leftrightarrow B = (A \land B) \lor (\lnot A \land \lnot B)$
    - $\lnot (A \Leftrightarrow B) = A \oplus B$
