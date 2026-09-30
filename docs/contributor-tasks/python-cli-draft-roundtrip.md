# 1. Python: exercise the E0 draft-to-append CLI in a disposable fixture

Local task draft for owner review; unpublished and unassigned.

**Question:** Does the command-line route preserve researcher control when a draft is edited and submitted, including refusal of incomplete drafts?

**Prerequisites:** Python, the repository's requirements-dev.txt dependencies, comfort with unittest and temporary directories. Repository files only; no Lean toolchain, Arena binaries, large corpus or LLM required. Setup duration is not established.

**Starting evidence:** `scripts/exploration-record`, `lib/exploration_bookkeeping.py`, `schemas/exploration-event.schema.json`, `tests/test_exploration_bookkeeping.py` and the synthetic queue pattern in `tests/test_research_queue_v4.py`. The new library tests already exercise draft nulls and receipt counts; this task fills the command-line integration gap rather than duplicating them.

**Expected artifact:** One focused CLI integration test using a disposable, synthetic campaign/ledger, plus a short reproduction command. Run start draft → refuse unfilled event → fill researcher fields → append → finish draft → refuse unfilled event → fill and append → check. Assert stderr/exit status, append-only ledger bytes and that scientific outcome/interpretation come from the supplied event. Keep all fixture writes out of the real ledger and queue. Use synthetic receipt bytes when counts are included; do not invoke a checker.

**Go:** An isolated temporary repository can exercise the real CLI without relaxing queue or append validation. **Stop:** The harness depends on host binaries or mutating the live campaign; report the minimal setup boundary before changing production behavior. Do not rebuild the evidence system or add another receipt format.

**Completion:** The meaningful CLI path and refusal controls pass under the test suite, or the precise fixture-routing obstacle is retained. Maintainer runs the applicable shared-tooling checks before acceptance. No scientific finding or measured efficiency claim follows.
