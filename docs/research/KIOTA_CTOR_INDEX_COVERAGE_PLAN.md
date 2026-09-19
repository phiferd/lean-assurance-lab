# Kiota constructor-index regression coverage

Item `KIOTA-CTOR-INDEX-COVERAGE-1`, within
`F-EXTERNAL-CONTRIBUTION-PORTFOLIO`. Selected READY and unstarted by the
[project-wide review](../../results/research/project-strategy-review-2026-09-19/report.md).
This source-only item is independent of CVC, transfer and theorem gates.

## Question and evidence

Does the executable Kiota suite protect the constructor-index owner-list guard
with a meaningful negative assertion and a compatible positive control? If not,
can one maintainable regression reuse the exact retained pair and attribute its
refusal to that guard?

The completed `SEMANTIC-IMPORT-CONTRACT-1` review binds Kiota `9fa2c297` and
the parser's `owner_ctors.get(cidx as usize) != Some(&name)` check. Its
`current-kiota-review.json` and `historical-observations.json` distinguish this
newer source from Kiota `58e8636c`'s old acceptance. The existing candidate is
`corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-ctor-index.ndjson`; its control is
`corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-control.ndjson`. Only one cidx
scalar differs. The 70-fixture inventory lacks an exact hash match, which does
not prove missing equivalent coverage. No current checker defect is claimed.

## Entry and finite scope

Before substantive analysis, commit a fresh work record, cumulative active-time
origin, exact retained source/archive/pair identities, request log and decision
rubric. Preserve the historical observations against their original bindings.
Use at most 60 cumulative active minutes and eight read-only source, inventory
or duplicate requests. Reuse retained source where possible; record freshness
limits or bind a refreshed exact revision before making a current claim. Bind
the complete executable test inventory and test wiring before a coverage claim.

Audit only the owner-list/index guard, semantically equivalent existing tests,
their assertion strength and execution wiring, control compatibility, competing
refusal paths, and target duplicate/disposition evidence. Do not infer absence
from filenames, exact hashes or a commit diff alone. Existing orphan-constructor
coverage must be compared by the property it asserts. Source-supported expected
outcomes remain predictions; a compatible control is not assumed from history.

Run zero builds, tests, checkers, proofs, new-export or mutation generators, and
external writes. Do not extend into recursor-type investigation or a general
metadata survey. The Kiota issue-submission deferral remains; local audit is
permitted and does not authorize submission. Authority and catalog changes are
outside scope. If later work requires adjudication, use the repository skill and
its frozen gates.

## Completion and successor

Produce one source-bound coverage map and one of:

- an exact existing-byte regression design with the intended assertion,
  positive control, expected cells, attribution and beneficiary;
- an exact equivalent-coverage/no-value finding with test locations; or
- a bounded unresolved result naming the compatibility, source-access or
  attribution gap and its unblocking condition.

Do not prepare an untested submission or claim executed behavior. Any test
implementation requires a separately selected bounded successor with exact
scientific inputs, tooling, process controls and launch budget frozen before
execution. A duplicate result warrants no contribution, not sample expansion.

At closure run affected validators, the complete current/historical full-payload
Lab suite, `scripts/refresh-current-state`, queue readiness and generated-view
checks. Reassess this output against the unchanged one-thread reserve, concrete
maintainer requests, held candidates and blocked alternatives. Select but do not
start a successor. Preserve all failures, budgets and historical evidence.
