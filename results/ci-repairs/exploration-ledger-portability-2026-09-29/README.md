# E0 ledger portability repair — 2026-09-29

**What did we find?** The first closed E0 record referenced ignored local
baseline and coverage files. GitHub run 36576243728 rejected the missing
baseline during ledger validation, before running the tests. This was an
archive-portability defect, not a semantic observation.
**Is it interesting?** Yes operationally: an exploratory record must distinguish
retained input identity from availability of a local reproduction payload.
**Does it require more work?** Validate this repair locally and on the exact
pushed commit. Select the separate LazyLean E0 campaign, keep the memory audit
deferred, and require the separately scoped snapshot/reuse repair before a new
E1/E2 closure relies on that machinery. No experiment is executed by this repair.

New starts automatically record SHA-256 for each available input. OPEN records
require those bytes. Closed records can be checked without those payloads, but
available bytes must match their recorded identity. Raw output and dirty-source
patches remain mandatory. Reproduction still requires reacquiring exact inputs.
The existing start is mapped by its exact event hash to its already retained,
hash-checked identity file; no old ledger event or evidence file is edited.

Regressions cover a fresh Git clone with an ignored input absent, the actual
historical ledger with untracked payloads absent, missing raw evidence, changed
inputs, missing OPEN inputs and tampered historical identities. Existing E0
lifecycle and promotion checks remain. The full current/historical suite and
GitHub's run on the delivery commit determine completion; no extra closure
receipt or scientific result is created for this repair.
