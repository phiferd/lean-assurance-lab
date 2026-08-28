# Nanoda Quot Equality Prerequisite Witness

Mutant: `nanoda-gen-d39c873fbcb7`

The mutation skips Nanoda's exact built-in `Eq` type assertion at
`src/quot.rs:89`, which is evaluated while checking `Quot.lift`.

The final candidate replaces canonical proposition-valued `Eq` with a valid
inductive equality analogue whose result is `Sort (max 1 u)`. Its parameter
domain and constructor telescope remain canonical, and the canonical quotient
suffix is remapped to the new expression graph. A debug backtrace confirms
that baseline rejection occurs at exactly line 89 after `Quot` and `Quot.mk`
have passed their own checks.

Nanoda results:

- canonical control: `ACCEPT` in baseline and mutant;
- non-proposition-valued Eq candidate: baseline `REJECT`, mutant `ACCEPT`.

In test terms, the prerequisite test passes without the mutation and fails
with it. The source is restored and rebuilt after each differential run.

## Reference Validation

Official Lean establishes expected outcome `REJECT`. Lean4Lean also rejects,
while Kiota accepts the exact candidate; all three accept the matched control.
The mutation is therefore `MEANINGFUL_SEMANTIC`, with an attached unresolved
checker disagreement about the serialized quotient/Eq contract.

This does not justify a separate upstream issue yet. The adjacent `Eq.refl`
prerequisite mutant should be investigated first so any eventual discussion
can describe the complete boundary without duplicate reports.

Reproduction is deterministic through `remap_quot_eq.py` and the preserved
`alt-eq-template-max1.ndjson` export.
