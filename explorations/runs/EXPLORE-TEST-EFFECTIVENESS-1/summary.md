# Three-case Nanoda test-effectiveness screen

**What did we find?** Nanoda's unchanged 44-test library suite passed under all
three seeded checker faults. The Lab's fixed 90-file compact corpus detected the
omitted declaration-type check with three cases, but did not detect the omitted
application-argument equality guard. A separately retained targeted pair did
detect that congruence fault. Neither corpus changed the final verdict for the
lambda-binder omission.

**Is it interesting?** Yes. Two consequential guard omissions passed every
upstream test in this sample, while the compact Lab corpus protected one of
them. The targeted congruence case protected the other. The lambda result is not
a third coverage gap: prior source and execution evidence classifies that
single omission as equivalent at Nanoda's public declaration entrypoint because
later mandatory checks reject the same malformed declarations.

**Does it require more work?** Do not turn these observations into three test
PRs. Retain the two detecting case families and use the result to select a small
cross-implementation test-effectiveness screen. That successor should use
known consequential faults and existing corpus assets, and remain unstarted at
this handoff. No confirmation or external contribution follows from the
equivalent lambda case.

## Exact observations

All four repaired executables have distinct SHA-256 identities. Each profile
ran its unchanged 44-test library suite and 92 checker inputs: 90 complete
Git-tracked NDJSON files no larger than 65,536 bytes, plus the two files from
the earlier congruence screen. The four profiles produced 368 checker
observations and eight Cargo build/test observations.

The pristine executable accepted 51 compact inputs, rejected 38 through a
checker panic, and reported one import or command-line error. The congruence
fault changed only the separately retained invalid candidate from rejection to
acceptance. The declaration-type fault changed three compact invalid cases and
that same retained candidate from rejection to acceptance. The lambda-binder
fault changed no final outcome.

The initial completed matrix is retained as three `INCONCLUSIVE` trials. Cargo
had reused a shared target directory, yielding four identical executable hashes
and therefore four pristine observations. A linked runner revision isolated
all target directories and required distinct hashes before completion. One
earlier sandbox attempt was stopped before compilation when `/bin/ps` was
unavailable to the supervisor. Across 753 retained process receipts, that is
the only supervision fault; the 376 repaired observations have complete
accounting and cleanup.

These are E0 screening observations for Nanoda
`3a2407216ee84a75f9e1aead6803d0578be06ae7`. Seeded faults are not production
bugs, the 90-file sample is not the entire Lab corpus, and a passing test suite
does not establish checker correctness. Exact identities and changed cases are
in `result.json`; raw outcomes and receipts are retained beside it.
