# Nanoda Quot Primitive Type Contract

Mutant: `nanoda-gen-7b386d7135bb`

The mutation skips Nanoda's exact expected-type assertion for the serialized
base `Quot` primitive at `src/quot.rs:208`.

The final candidate is a 73-record export containing canonical `Eq`, `Quot`,
and `Quot.mk` declarations. It changes only the base `Quot` declaration's type
reference from expression `43`, the canonical relation-indexed telescope, to
expression `17`, the independently well-formed `Sort u`.

Nanoda results:

- canonical control: `ACCEPT` in baseline and mutant;
- type-mismatch candidate: baseline `REJECT`, mutant `ACCEPT`.

The initial 65-record probe was rejected by both builds because Nanoda
unconditionally initializes the `Quot.mk` cached name while checking `Quot`.
That diagnostic is retained as `transfer-reproduction.json`; extending through
the canonical `Quot.mk` declaration removes this export-shape confounder.

## Reference Validation

The designated official Lean checker accepts the exact candidate and control,
establishing expected outcome `ACCEPT`. Kiota and Lean4Lean independently accept
both as well. The cross-validator result is `CONFIRMED`, not a disagreement
among those three implementations.

This means Nanoda's baseline is the outlier: its extra exact-type assertion
over-rejects an export accepted by every independent checker tested. The mutant
is therefore `REFERENCE_ALIGNED`, not a meaningful semantic fault. This is an
implementation-contract finding about serialized quotient primitives; it does
not by itself establish what Arena should require.

No upstream issue should be filed until the related `Quot.mk`, `Quot.lift`, and
`Quot.ind` checks are tested and the family can be reported without duplicate
noise.
