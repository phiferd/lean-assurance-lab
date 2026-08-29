# Ordinary Inductive Contract Matrix

| Boundary | Nanoda | Official | Kiota | Lean4Lean | Mutation sensitivity |
| --- | --- | --- | --- | --- | --- |
| `classic_strict_positivity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `reducible_hidden_strict_positivity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `constructor_parameter_domain` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |
| `constructor_result_parameter_uniformity` | REJECT | REJECT | REJECT | REJECT | SURVIVED_EXACT_CANDIDATE |
| `constructor_result_universe_uniformity` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |
| `recursive_occurrence_excluded_from_indices` | REJECT | REJECT | REJECT | REJECT | NOT_TESTED |

All controls are accepted by all four checkers. The three focused omission
probes survive their exact canonical candidates because independent `isRec` or
reconstructed-recursor checks reject first or later. This is defense in depth,
not evidence that the omitted checks are equivalent.

No external issue is recommended. Continue locally with internally consistent,
source-derived witnesses that isolate positivity and parameter uniformity.
