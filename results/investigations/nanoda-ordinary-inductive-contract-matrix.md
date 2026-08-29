# Ordinary Inductive Contract Matrix

| Boundary | Nanoda | Official | Kiota | Lean4Lean | Mutation sensitivity |
| --- | --- | --- | --- | --- | --- |
| `classic_strict_positivity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `reducible_hidden_strict_positivity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `constructor_parameter_domain` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |
| `constructor_result_parameter_uniformity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `constructor_result_universe_uniformity` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |
| `recursive_occurrence_excluded_from_indices` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |
| `constructor_result_proof_parameter_uniformity` | REJECT | REJECT | ACCEPT | REJECT | KILLED_BY_CANDIDATE |
| `reducible_hidden_strict_positivity_isolated` | REJECT | REJECT | REJECT | REJECT | KILLED_BY_CANDIDATE |

All controls are accepted by all four checkers. The three canonical omission
probes survive their exact canonical candidates because independent `isRec` or
reconstructed-recursor checks reject first or later. This is defense in depth,
not evidence of equivalence. The two source-derived candidates kill the exact
parameter-uniformity and positivity omissions; Kiota alone accepts the former.

A Kiota issue and two Arena reject-test proposals are recommended but require
human approval. No implementation issue is recommended for the positivity case.
