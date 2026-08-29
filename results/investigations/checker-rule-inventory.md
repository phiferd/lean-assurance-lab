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

- axiom policy and unsafe declarations.

Literal extension and parser/configuration assertion mutants are classified at the
public entrypoint without a separate cross-checker matrix.

The next ranked family is axiom policy and unsafe declarations.
