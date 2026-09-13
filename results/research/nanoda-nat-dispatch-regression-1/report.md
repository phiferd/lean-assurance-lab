# Nat dispatcher regression result

Two new Nanoda tests now check all six selected native arithmetic operations and verify that disabling native arithmetic stops reduction. Both new tests passed. The complete Nanoda library suite also passed: 40 tests, zero failures. Eight existing documentation examples remain ignored.

This is preventive test coverage, not a newly discovered arithmetic bug. The tests use Nanoda's internal reduction API and require real natural-number operands and results; they do not establish a public export/import guarantee. The known Nat.land case is reused explicitly.

The [test-only patch](patches/nat-dispatch.patch) and [PR draft](../../action-recommendations/drafts/nanoda-nat-dispatch-regression-pr.md) are prepared locally. Nothing was submitted to Nanoda. Keep the draft with the existing cache draft until maintainer capacity is reassessed, then refresh source/duplicates, rebase and retest before obtaining approval for submission.

The work used three source/setup requests and two supervised build/test reservations (11.015 seconds and 0.208 seconds). Both cleaned up successfully; there were no failed scientific launches, mutations, proofs or new exports. Setup failures and their repairs remain in setup-notes.json. Exact source, patch, dependencies, runner and commands were committed before the first test.

Next selected: NANODA-DEFEQ-CACHE-1, a bounded source-only assessment of mode-sensitive negative-cache behavior. It is READY and has not started. The [canonical result](result.json), [accounting](execution/accounting.json) and raw test logs preserve the evidence. Lab closure validation is recorded separately in validation.json.

All 1,074 Lab checks passed on the final run: 992 current tests, 73 frozen publication tests and nine frozen portfolio tests. The initial run exposed an administrative test that assumed exactly six contribution-ledger entries. It now requires all seven known contribution identities while allowing valid additions; the failed run and repair remain recorded. The Nanoda patch did not change.
