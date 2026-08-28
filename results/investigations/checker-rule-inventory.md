# Checker Rule Inventory

Five bounded matrices now provide 18 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 4 | 14 | 18 |
| Official Lean | 6 | 12 | 18 |
| Kiota | 15 | 3 | 18 |
| Lean4Lean | 6 | 12 | 18 |

Official Lean and Lean4Lean agree on all 18 boundaries. Nanoda differs
from them on four serialized quotient signatures and two universe right-successor
comparisons. Kiota differs from them on seven declaration/prerequisite boundaries and
the same two universe comparisons.

These counts are descriptive, not votes. Exact artifacts, controls, expected-outcome
evidence, and checker outcomes remain linked in `checker-rule-inventory.json`.

## Coverage Gaps

- application reduction, recursors, and projections;
- ordinary inductive positivity and parameter uniformity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next ranked family is reduction and projection typing.
