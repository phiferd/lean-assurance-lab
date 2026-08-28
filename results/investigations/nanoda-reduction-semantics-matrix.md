# Reduction Semantics Matrix

| Boundary | Nanoda | Official | Kiota | Lean4Lean | Mutation sensitivity |
| --- | --- | --- | --- | --- | --- |
| `beta_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | NOT_TESTED |
| `zeta_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | NOT_TESTED |
| `constructor_projection_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | NOT_TESTED |
| `recursor_iota_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | NOT_TESTED |
| `quot_lift_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | KILLED_BY_CANDIDATE |
| `quot_ind_proof_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | OBSERVATIONALLY_EQUIVALENT |
| `native_nat_ble_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | SURVIVED_EXACT_CANDIDATE |
| `native_nat_land_reduction` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | KILLED_BY_CANDIDATE |

All controls are accepted by all four checkers. `Quot.ind` acceptance is not a
mutation kill: proof irrelevance makes suppression of its proof-valued reduction
observationally indistinguishable in this checker. The native dispatch mutant is
exposed by `Nat.land`, not by the exact `Nat.ble` case whose comparison it mutates.

No external issue is recommended from this passing bounded matrix. The next
investigation is ordinary inductive positivity and parameter uniformity.
