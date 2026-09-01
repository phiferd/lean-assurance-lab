# Declaration Validation Milestone 10 Protocol Erratum 1

Canonical erratum SHA-256: `2e0568ee73896847a0dc9661d62d1ead64f3f51581164b8c0c7834d661204f60`
Immutable M10 attestation SHA-256: `976d450f9f1afd6f1a41c388c5bb623ce524d28aa1d1ac6c6634316eb3a31120`
Immutable M10 Phase-A commit: `2811fdbbe146009775ebdb1bd3b153f59ae503eb`

This successor erratum corrects one future-control rule without rewriting or regenerating any historically attested M10 byte.

## Operative Correction

Entry: `DECL.THEOREM.TYPE_PROP`

Frozen target: `/readiness/13/future_witness_strategy/positive_control`

Frozen wording: Use the matched definition-form control or a Prop-valued theorem repair with minimized differences.

Corrected rule: **Use a Prop-valued theorem in the same construction family, with a matching valid proof.**

Changing the declaration from theorem to definition removes applicability of the theorem-specific proposition-type premise instead of repairing that premise. It therefore cannot be the matched positive control for isolated DECL.THEOREM.TYPE_PROP coverage.

## Definition-Form Artifact

The definition-form artifact is retained as `AUXILIARY_REPRESENTABILITY_AND_WELL_FORMEDNESS_CONTROL`. It is explicitly prohibited from serving as `MATCHED_POSITIVE_CONTROL_FOR_ISOLATED_DECL.THEOREM.TYPE_PROP_COVERAGE`.

The related frozen readiness basis at `/readiness/13/isolation_feasibility/basis` is therefore interpreted as follows: Isolation feasibility remains YES as a future construction judgment, but the existing definition-form artifact is only auxiliary representability and well-formedness evidence; it does not itself supply the matched positive control.

## Successor Requirement

A successor claiming isolated DECL.THEOREM.TYPE_PROP coverage must bind a Prop-valued theorem in the same construction family with a matching valid proof.

Any successor must bind both the immutable M10 historical attestation and this erratum's historical attestation before execution. This erratum authorizes no successor execution.

## Unchanged M10 Results

- `primary_denominator_unchanged`: `true`
- `readiness_statuses_unchanged`: `true`
- `exploratory_set_unchanged`: `true`
- `empirical_context_set_unchanged`: `true`
- `deferred_reserved_set_unchanged`: `true`
- `m10_stop_condition_unchanged`: `true`

## Nonclaims

- This erratum does not rewrite, supersede, or regenerate any frozen M10 artifact.
- This erratum does not add an entry to or remove an entry from any M10 population.
- This erratum does not promote authority, establish soundness, or change any readiness status.
- This erratum does not execute or authorize coverage, synthesis, mutation, checker, or authority-resolution research.
- The definition-form artifact remains useful only in the explicitly auxiliary role recorded here.
