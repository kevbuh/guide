# Guide

<div align="center">
    <img src="https://raw.githubusercontent.com/kevbuh/guide/main/assets/system_overview.png" alt="System Overview" width="600"/>
</div>


Logical equivalence symbolic engine guided by tree-of-thoughts 



## Roadmap

1. Build symbolic engine
2. Build prompt engine
3. Set up LLM
4. Recreate tree of thoughts // Or use original repo
5. Set up experiment suite to track model performances
6. Start experimenting with how to improve ToT

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

## Common Logic Laws

1. **Commutative Law**:
   - AND: $A \land B = B \land A$
   - OR: $A \lor B = B \lor A$

2. **Associative Law**:
   - AND: $(A \land B) \land C = A \land (B \land C)$
   - OR: $(A \lor B) \lor C = A \lor (B \lor C)$

3. **Distributive Law**:
   - $A \land (B \lor C) = (A \land B) \lor (A \land C)$
   - $A \lor (B \land C) = (A \lor B) \land (A \lor C)$

4. **Identity Law**:
   - AND: $A \land 1 = A$; $A \land 0 = 0$
   - OR: $A \lor 0 = A$; $A \lor 1 = 1$

5. **Negation Law**:
   - $A \land \lnot A = 0$
   - $A \lor \lnot A = 1$

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

10. **Double Negation Law**:
    - $\lnot (\lnot A) = A$

11. **Exclusive OR (XOR) Properties**:
    - $A \oplus B = (A \land \lnot B) \lor (\lnot A \land B)$
    - $A \oplus 0 = A$
    - $A \oplus A = 0$

12. **Implication Transformation**:
    - $A \Rightarrow B$ can be expressed as $\lnot A \lor B$

13. **Involution Law**:
   - The application of negation twice returns to the original value: $\lnot(\lnot A) = A$

14. **NAND and NOR Laws**:
   - **NAND**: The negation of AND, denoted as $A \uparrow B$, is equivalent to $\lnot(A \land B)$
   - **NOR**: The negation of OR, denoted as $A \downarrow B$, is equivalent to $\lnot(A \lor B)$

15. **Exclusive NOR (XNOR) Properties**:
   - The negation of XOR, often represented as $A \odot B$, indicates equivalence: $A \oplus B = \lnot(A \oplus B)$ or $A \odot B = (A \land B) \lor (\lnot A \land \lnot B)$

16. **Contradiction**:
   - A conjunction of a statement and its negation is always false: $A \land \lnot A = 0$

17. **Tautology**:
   - A disjunction of a statement and its negation is always true: $A \lor \lnot A = 1$

18. **Consensus Theorem**:
   - In a three-variable system, certain redundant terms can be eliminated: $(A \land B) \lor (\lnot A \land C) \lor (B \land C) = (A \land B) \lor (\lnot A \land C)$

19. **Complementarity Law**:
   - $A \land \lnot A = 0$ and $A \lor \lnot A = 1$, highlighting the nullifying effect of a statement and its negation.

20. **Redundancy Law**:
   - Eliminates redundant terms: $A \lor (A \land B) = A$
   - Simplifies expressions where a term is repeated: $A \land (A \lor B) = A$

21. **Consensus Law**:
   - Removes a term when covered by a consensus: $(A \land B) \lor (\lnot B \land C) \lor (A \land C) = (A \land B) \lor (\lnot B \land C)$

22. **Adjacency Law**:
   - Simplifies expressions involving adjacent terms in a Karnaugh map or truth table: $(A \land B) \lor (A \land \lnot B) = A$

23. **Simplification Law**:
   - A general approach for reducing the complexity of expressions: $(A \lor B) \land (A \lor \lnot B) = A$

24. **Exclusive OR Simplification**:
   - Provides a simpler expression for XOR operations: $A \oplus B = (A \lor B) \land \lnot (A \land B)$

25. **Implication Laws**:
   - Formalizes the relationship between implication and other operations: $A \Rightarrow B = \lnot A \lor B$
   - Expresses implication through negation and disjunction: $\lnot (A \Rightarrow B) = A \land \lnot B$

26. **Biconditional Laws**:
   - Defines the logical equivalence (if and only if): $A \Leftrightarrow B = (A \land B) \lor (\lnot A \land \lnot B)$
   - Provides the negation form: $\lnot (A \Leftrightarrow B) = A \oplus B$