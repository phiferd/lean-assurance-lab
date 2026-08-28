# Restored Nested Declaration Contract Matrix

The second bounded spec-derivation pilot covers three one-field deviations in
restored nested declarations.

| Boundary deviation | Nanoda | Official Lean | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| Restored auxiliary recursor `k` | Reject | Reject | Accept | Reject |
| Restored auxiliary recursor type | Reject | Reject | Accept | Reject |
| Restored constructor index | Reject | Reject | Accept | Reject |

Every matched valid control is accepted by every checker. Within this tested
family, Nanoda matches official Lean and Lean4Lean, while Kiota does not enforce
the three restored metadata relationships.

This is a bounded rule family, not a complete inductive-declaration
specification. It supports discussing the three Kiota outcomes together rather
than filing one report per field. No upstream issue has been filed.
