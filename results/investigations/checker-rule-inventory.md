# Checker Rule Inventory

Four bounded matrices now provide 13 exact, executable rule boundaries.

| Checker | Accept | Reject | Total |
| --- | ---: | ---: | ---: |
| Nanoda baseline | 0 | 13 | 13 |
| Official Lean | 4 | 9 | 13 |
| Kiota | 11 | 2 | 13 |
| Lean4Lean | 4 | 9 | 13 |

Official Lean and Lean4Lean agree on all 13 boundaries. Nanoda differs from
them on the four serialized quotient primitive signatures. Kiota agrees on
those four but differs on the seven Eq-prerequisite, restored-declaration, and
declaration-environment boundaries.

These counts are descriptive, not votes. Each rule remains linked to its exact
artifact, control, expected-outcome evidence, and checker outcomes in
`checker-rule-inventory.json`.

## Coverage Gaps

The current matrices do not yet directly model:

- universe inequality and broader definitional equality;
- application reduction, recursors, and projections;
- ordinary inductive positivity and parameter uniformity;
- literal extension and parser/configuration behavior;
- axiom policy and unsafe declarations.

The next family is universe definitional equality. The distinct-`IMax`
boundary already has four-checker consensus rejection evidence and can anchor
adjacent source-derived rules.
