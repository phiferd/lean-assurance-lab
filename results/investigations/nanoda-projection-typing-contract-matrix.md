# Projection Typing Contract Matrix

| Boundary | Nanoda | Official | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| `possibly_prop_direct_field_projection` | REJECT | ACCEPT | ACCEPT | REJECT |
| `possibly_prop_dependent_past_field_projection` | REJECT | ACCEPT | ACCEPT | REJECT |
| `definite_prop_data_projection` | REJECT | REJECT | REJECT | REJECT |

All matched controls are accepted. Official Lean and Kiota accept the two Arena-good
possibly-Prop projections, while Nanoda and Lean4Lean reject them. All four reject
definite data projection from `Prop`. These are exact characterization cases, not votes.
