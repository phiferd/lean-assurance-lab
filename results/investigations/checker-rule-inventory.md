# Checker Rule Inventory

Seven bounded matrices now provide 29 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 12 | 17 | 29 |
| Official Lean | 16 | 13 | 29 |
| Kiota | 25 | 4 | 29 |
| Lean4Lean | 14 | 15 | 29 |

Official Lean and Lean4Lean differ only on the two possibly-Prop projection cases.
Nanoda differs from official Lean on those two cases, four serialized quotient
signatures, and two universe right-successor comparisons. Kiota differs from official
Lean on seven declaration/prerequisite boundaries and the two universe comparisons.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- ordinary inductive positivity and parameter uniformity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is ordinary inductive well-formedness.
