# Nanoda Quot Eq.refl Prerequisite Witness

Mutant: `nanoda-gen-cd41c71bc814`

The mutation skips Nanoda's exact built-in `Eq.refl` type assertion at
`src/quot.rs:105`, evaluated while checking `Quot.lift`.

The source-derived candidate keeps canonical proposition-valued `Eq` with two
parameters and one index, but gives its sole constructor one unused field:

```lean
inductive LALAltEq (alpha : Sort u) (a : alpha) : alpha -> Prop where
  | refl : (extra : alpha) -> LALAltEq alpha a a
```

The generated inductive, constructor, and recursor are internally valid. The
remapper renames the family to `Eq`, preserves canonical quotient universe
names under fresh IDs, and appends the canonical quotient suffix. A debug
backtrace confirms baseline rejection occurs exactly at line 105.

Nanoda results:

- canonical control: `ACCEPT` in baseline and mutant;
- extra-field `Eq.refl` candidate: baseline `REJECT`, mutant `ACCEPT`.

In test terms, the prerequisite test passes without the mutation and fails
with it. Official Lean establishes expected outcome `REJECT`, and Lean4Lean
also rejects. Kiota accepts the exact candidate; all three accept the control.
The mutant is `MEANINGFUL_SEMANTIC`, with the same unresolved quotient/Eq
contract disagreement exposed by the adjacent Eq-type witness.

Together, the line-89 and line-105 witnesses complete Nanoda's explicit Eq
prerequisite boundary. Any upstream discussion should present them as one
family rather than separate reports.
