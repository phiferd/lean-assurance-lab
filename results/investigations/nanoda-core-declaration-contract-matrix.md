# Core Declaration Typing Contract Matrix

This family covers two distinct core declaration typing rules.

| Boundary violation | Nanoda | Official Lean | Kiota | Lean4Lean |
| --- | --- | --- | --- | --- |
| Let annotation differs from value type | Reject | Reject | Reject | Reject |
| Theorem declaration has a non-Prop type | Reject | Reject | Reject | Reject |

Every matched valid control is accepted by every checker. The exact cases
support two consensus rules: checked let annotations must match the value type,
and theorem declarations must be proposition-valued.

This matrix establishes a useful contrast with the first three families: the
spec-derivation process records consensus rules as well as disagreements. It
does not imply that the four implementations agree on every aspect of ordinary
declaration checking.
