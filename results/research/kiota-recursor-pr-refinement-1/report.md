# Kiota recursor PR refinement

The successor improves the tested repair's import cost, compatibility, regression
coverage and reviewability while preserving every predecessor artifact.

The parser now journals only writes performed by the current inductive block.
It owns prior values and restores them in reverse on any returned error. This
removes full-environment cloning and keeps storage proportional to block writes.
The atomicity regression records the allocation address of a nonempty prior
recursor-group vector; it must remain identical after rejection. This catches
the former clone-and-restore implementation, beyond mere content equality.
Separate late failures exercise both ownership and recursor-group rollback.
This is a structural cost improvement with regression coverage, not a measured
throughput or full-mathlib performance claim.

Supplied `k` remains ignored as documented by Kiota; the installed flag is always
reconstructed. A test covers both false-to-true and true-to-false supplied flags.
Complete recursor signature, metadata, universe, positivity and elimination
checks remain. The comparison tests now cover alpha-renaming with canonical-ID
collision, let-convertible signature acceptance and replacement, positional
universe mismatch, duplicate universes and undeclared universes.

The reconstruction implementation moves into `src/tc/recursor.rs`, with pinned
Lean 4.33.0 source links and a guide to the restored nested representation,
breadth-first member ordering and dependent binder contexts. Its construction
logic is preserved except removal of an unused argument. The malformed legacy
nested fixture is renamed to `.reject.ndjson`; its 2,858 bytes remain identical.

The revised PR text leads with the fifth-domain error and its downstream typing
consequence, explains the repair and compatibility, and gives reproducible
commands. It does not assert a false theorem or complete checker soundness.
The original draft and package remain unchanged, indexed as historical.

## Verification

The package applies cleanly to the pinned pristine archive and reproduces all
93 source files byte-for-byte. The candidate/control and four acceptance
fixtures retain their exact identities. One offline compilation, 15 focused
tests, all six original preservation cells, and all 168 full-suite tests pass
(83 unit, 85 integration; none failed or ignored). All nine processes have
positive RSS samples, no memory/timeout failure, and complete group cleanup.
The successor runner's 33 mocked tests exercise exact source inventories,
authored patch payloads, deletions, malformed receipts and attempt accounting.
Independent delegates reviewed production, tests, runner and execution evidence.

The first archive-materialization command used a system Python without the
safe extraction API and stopped before extraction. Switching to the pinned
Python 3.13 completed safe extraction; no Cargo or checker process was involved.
No runtime engineering failure occurred in the nine-cell successor matrix.
Repository-wide closure validation is recorded separately in
`closure-validation.json` and `repository-validation/full-suite-final.log`.

The first repository suite exposed a supervisor start-gate race: a nonempty
zero-RSS observation could release a short process before positive memory was
observed. Prospective supervisor v3 now waits for positive RSS, with two
deterministic regressions and seven focused tests passing. The legacy helper
and all completed Kiota bindings remain unchanged. Five historical tests also
required a READY handoff successor; their frozen bytes were restored after an
attempted edit, and final validation uses the staged handoff state. The failed
suite, rejected edit and focused process receipts are preserved. The final complete suite passes all 1,452 tests: 1,370 live, 73 frozen
publication and 9 frozen portfolio tests. Every frozen custody check passes.

## Upstream recommendation

Read-only observation on 2026-09-22 found main still at `9fa2c297`. The only open
PR, #10, addresses universe-cache identity and CLI verdicts; its changed files
do not overlap this patch. The two open non-PR issues concern self-reference
and universe ownership. This open-item review found no apparent duplicate;
closed history, discussions and all review threads were not exhaustively searched.
Maintainer capacity and acceptance remain unknown.

Recommend this revised patch as the high-priority Kiota submission candidate,
subject to exact human authorization and a fresh preflight if upstream changes.
No external write or submission occurred. A merge is not promised. The project-wide review selects
`TRUST-ASSUMPTION-PIPELINE-PILOT-1` READY and unstarted for source/reuse and
protocol binding. With the concrete PR obstacles resolved, that broader
reporting question outranks more local packaging work; the stateful alternative
still needs session and rollback contracts.
