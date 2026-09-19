# Kiota constructor-index regression implementation

Item `KIOTA-CTOR-INDEX-TEST-1`, within
`F-EXTERNAL-CONTRIBUTION-PORTFOLIO`. This bounded successor may start only
after `KIOTA-CTOR-INDEX-COVERAGE-1` closes SUCCESS and the canonical queue
selects it READY. Selection does not start it.

## Aim and fixed design

Implement the exact existing-byte two-cell design in
`results/research/kiota-ctor-index-coverage-1/regression-design.json` against a
freshly bound Kiota source revision. The control has `LALNest.node.cidx = 0` and
must accept; the candidate changes only that scalar to `1` and must reject with
the owner-list/index guard's exact message. Preserve `orphan-ctor` as coverage of
the separate missing-owner branch. Do not generate or alter NDJSON bytes.

This is preventive public-import regression coverage, not a current checker
defect, a universal metadata adjudication or proof of soundness. Historical
Kiota `58e8636` results remain historical. The source-audit conclusion is scoped
to retained `9fa2c297`; execution claims require the newly bound source.

## Entry and execution gate

Use at most 90 cumulative active minutes, six read-only source/setup/duplicate
requests, two build reservations of at most 600 seconds each and three test
processes of at most 120 seconds each. A compiling test consumes both a build
reservation and a test process. Run zero checkers, proofs, mutations, new export
generators or external writes. Do not fix production code or expand into other
metadata fields.

Before implementation, commit a work record, exact fresh source archive/revision,
complete executable duplicate inventory, the two fixture hashes and an action
rubric. Before the first process, separately commit the exact patch, expected
cells, dependency/tooling lock, invocations, timeouts, cleanup controls and
accounting. If source or duplicate coverage invalidates the design, close with
that exact result without launching tests.

Add the two byte-identical fixtures and the smallest maintainable test code. The
negative assertion must bind `TcError::Reject` and the exact owner-list/index
message; a generic rejection is insufficient. Run the focused two-cell test and
the complete current Kiota suite. Preserve failures and repair only test or Lab
tooling defects within the same item and remaining budget.

## Completion and successor

Finish with one focused/full-suite-validated test-only patch and local PR draft,
an exact duplicate/no-value result, or a bounded technical incompatibility.
State the beneficiary and limits. An external submission requires a fresh
target/duplicate/capacity preflight and explicit owner approval for the exact
action. At closure run the Lab's affected validators and complete current and
historical suite, refresh derived state, select but do not start one successor,
deliver on `main`, and stop.
