# Checker Rule Inventory

Six bounded matrices now provide 21 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 4 | 17 | 21 |
| Official Lean | 8 | 13 | 21 |
| Kiota | 17 | 4 | 21 |
| Lean4Lean | 6 | 15 | 21 |

Official Lean and Lean4Lean differ only on the two possibly-Prop projection cases.
Nanoda differs from official Lean on those two cases, four serialized quotient
signatures, and two universe right-successor comparisons. Kiota differs from official
Lean on seven declaration/prerequisite boundaries and the two universe comparisons.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- application, recursor, quotient, and literal reduction;
- ordinary inductive positivity and parameter uniformity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is reduction semantics.
