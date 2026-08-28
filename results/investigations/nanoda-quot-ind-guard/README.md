# Nanoda Inverted Quot.ind Guard

Mutant: `nanoda-gen-701a664f39e5`

The mutation changes the `Quot.ind` branch predicate in `reduce_quot` from
`c_name == quot_ind` to `!(c_name == quot_ind)`. In Rust this is semantically
identical to `c_name != quot_ind`, so it duplicates
`nanoda-gen-cb4949d04bbf` at the same source location.

## Intended Branch

Disabling the intended `Quot.ind` iota rule changes only proof normal forms.
`Quot.ind` has a motive into `Prop`, and Nanoda's definitional equality checks
proofs by proof irrelevance. The explicit Arena `quotIndReduction` artifact is
accepted by both baseline and mutant Nanoda.

## Newly Enabled Branch

The inverted predicate can also enter the `Quot.ind`-shaped reducer for another
declaration represented as `Declar::Quot`. This does not create a checker-level
difference:

- `Quot` and `Quot.mk` have too few well-typed arguments to reach `args[4]`;
- `Quot.lift` is consumed by the preceding dedicated branch;
- `Quot.sound` is proof-valued, so a well-typed replacement remains
  observationally irrelevant under proof irrelevance;
- every serialized declaration type and value is traversed by `infer(...,
  Check)`, and `infer_app` checks each argument against its binder before the
  final declaration equality. An ill-typed overapplication cannot be hidden by
  the reducer.

The prior equivalence classifier was strengthened to check the structural
inference precondition explicitly. The source was restored and rebuilt after
the differential probe.

## Status

The mutant is `EQUIVALENT` and duplicates the already classified equality-
discrimination mutant. No regression candidate is warranted.
