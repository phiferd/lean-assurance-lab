# Checker Rule Inventory

Eight bounded matrices now provide 36 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 12 | 24 | 36 |
| Official Lean | 16 | 20 | 36 |
| Kiota | 26 | 10 | 36 |
| Lean4Lean | 14 | 22 | 36 |

Official Lean and Lean4Lean differ only on the two possibly-Prop projection cases.
Nanoda differs from official Lean on those two cases, four serialized quotient
signatures, and two universe right-successor comparisons. Kiota differs from official
Lean on seven declaration/prerequisite boundaries, two universe comparisons, and the
proof-parameter constructor-result boundary.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- whole-checker isolation witness for ordinary inductive positivity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is ordinary inductive positivity witness isolation.
