# Full-suite repair 1

The first complete suite retained all output and reconciled all 23 inert
fixtures. Its 770 current tests had one failure in
`test_planning_cannot_promote_classification`; all 73 frozen historical tests
passed.

The failing fixture copied the current successor queue and changed only the
assurance count. Because the queue is correctly no longer on the historical
planning frontier, the planning-only no-classification-change gate did not
apply. The adjacent transition test already expects a successor frontier to
validate. The repaired test explicitly sets the copied queue to
`F-SURVIVOR-TRIAGE-PROPOSAL` before testing the historical planning gate.

This changes no proposal validator, scientific input, run result, queue state
or historical artifact. No research process launched. The failed suite's
469.333436 wall seconds and 23 reconciled administrative fixtures remain
charged to their original validation batch. A new exact code-binding batch and
separate finite allocation cover the focused regression and one complete rerun.

The first focused command used `python3 tests/test_survivor_proposal.py`, which
does not place the repository root on this test module's import path and stopped
before discovery with `ModuleNotFoundError: lib`. The corrected focused command
uses unittest discovery, matching the complete-suite environment. No test,
fixture or research process ran in the failed direct invocation.
