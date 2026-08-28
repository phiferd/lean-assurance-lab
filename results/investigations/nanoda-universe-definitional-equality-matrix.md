# Universe Definitional-Equality Matrix

| Boundary | Nanoda | Official | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| `imax_left_one_reduces_to_right` | ACCEPT | ACCEPT | ACCEPT | ACCEPT |
| `imax_right_zero_reduces_to_zero` | ACCEPT | ACCEPT | ACCEPT | ACCEPT |
| `imax_right_one_compares_as_max` | ACCEPT | REJECT | ACCEPT | REJECT |
| `imax_right_successor_compares_as_max` | ACCEPT | REJECT | ACCEPT | REJECT |
| `distinct_imax_left_parameters_are_not_equal` | REJECT | REJECT | REJECT | REJECT |

All matched controls are accepted by all four checkers. Official Lean and Lean4Lean
agree on all five cases. Nanoda and Kiota accept the two right-successor comparisons
that both Lean implementations reject. This is a bounded observed profile, not a
complete universe-level specification or a majority-vote decision.
