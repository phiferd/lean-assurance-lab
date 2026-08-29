# Checker Rule Inventory

Eight bounded matrices now provide 35 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 12 | 23 | 35 |
| Official Lean | 16 | 19 | 35 |
| Kiota | 25 | 10 | 35 |
| Lean4Lean | 14 | 21 | 35 |

Official Lean and Lean4Lean differ only on the two possibly-Prop projection cases.
Nanoda differs from official Lean on those two cases, four serialized quotient
signatures, and two universe right-successor comparisons. Kiota differs from official
Lean on seven declaration/prerequisite boundaries and the two universe comparisons.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- whole-checker isolation witnesses for ordinary inductive positivity and parameter uniformity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is ordinary inductive witness isolation.
