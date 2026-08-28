# Declaration Environment Contract Matrix

This bounded family covers two distinct declaration-environment rules.

| Boundary violation | Nanoda | Official Lean | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| Referenced constant uses an undeclared universe | Reject | Reject | Accept | Reject |
| Declaration value references its own declaration | Reject | Reject | Accept | Reject |

Every matched valid control is accepted by every checker.

The cases support two separate inferred rules:

1. Universes used to instantiate a referenced constant must belong to the
   declaration currently being checked.
2. The declaration currently being checked is not visible through ordinary
   constant lookup in its own value.

Nanoda, official Lean, and Lean4Lean enforce both tested rules. Kiota accepts
both exact violations. The common checker split is useful evidence, but it does
not prove that both behaviors arise from one implementation defect.

This matrix excludes `numIndices`: that case concerns restored nested
inductive metadata, not declaration environment visibility. No issue has been
filed from this synthesis.
