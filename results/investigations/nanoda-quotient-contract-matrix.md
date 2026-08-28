# Quotient Contract Matrix

Six exact cases now define a bounded, executable comparison of quotient
handling across the four checkers.

| Boundary deviation | Nanoda | Official Lean | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| `Quot` serialized type | Reject | Accept | Accept | Accept |
| `Quot.mk` serialized type | Reject | Accept | Accept | Accept |
| `Quot.lift` serialized type | Reject | Accept | Accept | Accept |
| `Quot.ind` serialized type | Reject | Accept | Accept | Accept |
| Built-in `Eq` result universe | Reject | Reject | Accept | Reject |
| Built-in `Eq.refl` extra field | Reject | Reject | Accept | Reject |

Every matched canonical control is accepted by every checker.

The narrow inferred rules are:

- Nanoda enforces all six tested exact boundaries.
- Official Lean and Lean4Lean do not enforce the four serialized primitive
  signatures, but do enforce both tested built-in Eq prerequisites.
- Kiota accepts every tested deviation in this family.

This is not a complete specification for any checker. It is a six-case pilot
showing how implementation-derived rules can translate directly into tests.
The machine-derived source is `nanoda-quotient-contract-matrix.json`.

No upstream issue has been filed from this synthesis. The matrix should be
discussed first because it combines Nanoda over-rejection evidence with Kiota
under-validation evidence under one ambiguous serialized primitive contract.
