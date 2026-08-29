# Checker Rule Inventory

Eight bounded matrices now provide 37 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 12 | 25 | 37 |
| Official Lean | 16 | 21 | 37 |
| Kiota | 26 | 11 | 37 |
| Lean4Lean | 14 | 23 | 37 |

Official Lean and Lean4Lean differ only on the two possibly-Prop projection cases.
Nanoda differs from official Lean on those two cases, four serialized quotient
signatures, and two universe right-successor comparisons. Kiota differs from official
Lean on seven declaration/prerequisite boundaries, two universe comparisons, and the
proof-parameter constructor-result boundary.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is literal extensions and parser/configuration behavior.
