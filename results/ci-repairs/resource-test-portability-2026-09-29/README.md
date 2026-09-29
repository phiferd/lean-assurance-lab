# Resource unit-test portability repair — 2026-09-29

**What did we find?** Three resource unit tests fail on GitHub Ubuntu: one reads
an absolute macOS toolchain path, and two timing tests assume child-accounting
RSS stays below their 100 MB ceiling. The same failures occur in runs
36520040028, 36557980100 and 36558743267, including before exploration adoption.
This is test portability evidence, not a new scientific result.
**Is it interesting?** Operationally yes: a local pass did not establish CI
portability. The production limit classification correctly rejected the
above-ceiling observations; it is not weakened by this repair.
**Does it require more work?** Verify GitHub's Ubuntu run on the pushed repair.
The separate closure-reliability item remains READY and unstarted.

The current unit runner adapts only these three exact test IDs. It supplies
eight exact Lean source files, checked against their original frozen manifest,
to the source-chain test. The two timing tests retain real child execution and
reaping but receive deterministic below-ceiling RSS accounting. All other
tests, including resource-limit and accounting-failure tests, are unchanged.
Every resource execution input still matches its frozen hash; no historical
test, production supervisor, experiment receipt, or manifest was edited.

Validation: five focused regressions pass; the full local runner passes 1,633
current tests, 73 frozen publication tests and nine portfolio-history tests.
Queue and exploration-ledger validation pass. Compressed logs preserve the
GitHub failure and successful local full-suite output. GitHub Actions remains
the authority for the pushed commit's remote result; it is checked before
reporting this repair complete, without creating a follow-up evidence commit.
