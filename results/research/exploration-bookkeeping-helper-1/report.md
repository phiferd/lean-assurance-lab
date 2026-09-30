# E0 bookkeeping maintenance

What did we find? The existing CLI now prints schema-backed unappended drafts and derives supported counts from retained receipts. The six-trial campaign reproduces 40 final cells, 48 actual launches, three prelaunch failures and eight retained nonfinal construction cells without reading the operations.json totals. Is it interesting? Yes, as a small mechanical repair for observed transcription errors; no measured time or token saving is claimed. Does it require more work? Retain after the full current/historical suite and applicable checks pass. Select separate source/fixture preparation for PR15373's alias seam, leaving it unstarted. No scientific experiment or external write ran.

## Implementation and scope

lib/exploration_bookkeeping.py and scripts/exploration-record add draft/counts commands. Required fields come from the existing schema; scientific outcome, completeness, observations, decision and question remain explicit nulls. The unchanged append path is the only ledger writer and refuses an unfinished draft. Finish mechanics can use explicitly selected final receipts. Repeated cell/result/supervisor exports deduplicate on raw stream paths; stream hashes are verified and conflicting or overlapping identities fail. Each trial requires exactly one explicit final-result path matching its existing completed_runs; retained earlier receipts remain counted. Supported prelaunch exports deduplicate by attempt directory; unknown errors are refused. These are observations, not launch budgets or classification of nonfinal work as waste.

The current lower status table now reports the memory audit as DEFERRED. Live v4 queue validation rejects inconsistent unfinished-item table states; historical Attempted records remain unchanged. No separate state store or receipt format was added. Fresh read-only PR33 metadata records the separate task's upstream update; reported tests are attributed to its PR body, not rerun here, and CI/review endpoints remain UNKNOWN.

## Validation candidate

Eight helper regressions cover actual campaign counts, preserved ledger bytes, unfilled draft refusal, researcher control, conflicts, overlap, missing/tampered raw files, prelaunch deduplication and ambiguous final selection. All 33 exploration tests pass and all four queue-v4 tests pass, including the stale-table regression. Foreign-checkout replay passed eleven replay tests and one closure-receipt test. Full suite and final affected checks must be confirmed in the retained validation logs before reporting completion. The previous E0 CI was a handoff pass that intentionally skipped full unit/replay; it is not validation for this shared helper.

No external publication occurred. Original lab and Nanoda checkouts were not edited. Scientific pilot feasibility is in ../lean-eta-pilot-feasibility-1/assessment.md; no confirmed defect or broad eta novelty follows.

## Final observed validation

The standard `python3 scripts/run-unit-tests` invocation returned 1: its current
partition ran 1,672 tests in 485.081 seconds with five payload skips and four
errors, all from sandbox denial of /bin/ps before synthetic supervisor-child
launch. All other current tests passed. Its historical publication partition
passed 73 tests with one payload skip; portfolio passed nine tests. The unchanged
`test_metamorphic_supervisor.py` module passed all seven tests in 1.382 seconds
on a narrowly approved host-access retry, recovering all four initial errors.
No validation input or production code changed between the full invocation and
retry. All non-skipped constituent tests therefore passed; a single clean full
runner invocation and full-payload integration are not claimed. Logs preserve
the initial failure, skips and successful host retry separately.

Focused exploration: 33 passed. Queue-v4: four passed. Foreign-checkout replay:
eleven tests plus one closure-receipt test passed. Final ledger/queue/generated
planning view/external view/diff checks must be read alongside their validation
log. No remote CI ran for these unpublished local commits. Deterministic source
extraction/hash commands in the source-only triage were permitted; its no-launch
statements refer to checker/build execution, not those bookkeeping commands.
