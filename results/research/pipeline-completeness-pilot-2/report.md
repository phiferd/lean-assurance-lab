# Pipeline completeness pilot 2 result

Outcome: **SUCCESS**.

The independent sentinel tied the requested object to the exact export bytes,
ordered twelve-theorem inventory, statement set and transitive value-dependency
closure. It passed only the frozen baseline and returned the preregistered
distinct failure for each omission, substitution and truncation artifact.

## Matrix

| Artifact | Sentinel | Official Lean | Lean4Lean |
| --- | --- | --- | --- |
| exact baseline | `PASS` | accept | accept |
| target omission | `FAIL_MISSING_TARGET` | accept | accept |
| compatible artifact substitution | `FAIL_ARTIFACT_OR_DECLARATION_IDENTITY` | accept | accept |
| truncated final record | `FAIL_PARSE_OR_DEPENDENCY_CLOSURE` | reject | reject |

The four accept cells for omission and substitution are the practical result:
both checkers correctly validated the artifacts they were given, but their zero
exit status could not establish that those artifacts were the intended one. The
sentinel closed that orchestration gap. This is not a checker soundness defect;
it is evidence that a checker receipt needs an independently bound object
identity and completeness assertion.

## Engineering record

The pilot preserved and repaired three non-scientific incidents without closing
or changing the scientific matrix:

1. the first preflight invocation could not start because the sandbox blocked
   the supervisor's `/bin/ps` RSS backend;
2. the first producer invocation stopped before launch because the controller
   sent a three-field file binding to a two-field legacy verifier; and
3. the first actual producer build succeeded, but the controller initially
   mislabeled ordinary Lake build stdout as failure.

Regressions now cover the binding contract and successful builds with preserved
Lake output. The repaired controller reran its preflight, rebuilt in a fresh
workspace and completed all eight checker cells. No attempt count was used as a
terminal condition.

## Recommendation and claim boundary

Retain the sentinel, exact export inventory, three fault constructors, execution
manifest and closure regression as a reusable local checked-object receipt
package. Integrations should require both checker acceptance and sentinel `PASS`;
process success alone answers only whether the supplied artifact validates.

This result covers one Lean 4.29.1-produced module, the bound official and
Lean4Lean adapters, and the three exact fault classes. It does not prove either
checker correct, generalize to all exporters or formats, or authorize an
external submission. A later contribution should package the generic receipt
contract only after selecting a concrete beneficiary and refreshing its
integration surface.
