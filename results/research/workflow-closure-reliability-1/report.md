# Closure reliability and intervention accounting — 2026-09-29

**What did we find?** The shared closure path now allows only one owner, keeps
interrupted attempts, resumes exact completed stages, reruns downstream stages
when a declared dependency changes, rejects unexplained cached-output changes,
and keeps its test receipts outside scientific evidence. Twenty closure tests
and four usage-accounting tests pass. No scientific experiment ran, and no token
saving was established.

**Is it interesting?** Yes as a reusable workflow repair. It directly covers
the concurrent state-edit failure and the control/scientific receipt collision
seen during resource closure. It also replaces informal cost impressions with
aggregate response-level counters separated into cached input, uncached input,
cache-write input, output and reasoning output.

**Does it require more work?** No repair follows from these passing controls.
The next separate item is a one-trial E0 inventory screen for fresh,
diversity-balanced Nanoda mutation targets. The historical short-process memory
audit stays deferred; it was not answered by this implementation.

## Technical result and limits

The controller retains the original exact committed-byte inventory and ordered
validation path. Its new repository-keyed advisory lock spans the whole closure.
Each resumable stage writes an immutable receipt binding the committed inventory,
predecessor receipts, normalized command, executable bytes, and complete output
tree. An unchanged receipt is reusable; a declared dependency change creates a
new stage version; damaged or structurally unknown cache evidence stops. Raw
failure logs and interrupted stage directories remain alongside later retries.

The first real ordered closure exposed an additional historical boundary: the
stateful pilot freezes the exact bytes of `lib/closure_controls.py`. Five replay
tests rejected the in-place edit after the current partition ran 1,642 tests.
That failed stage is retained unchanged. The repair restores the old module
byte-for-byte and places the prospective controller in
`lib/closure_controls_v2.py`; the live command and focused tests opt into the
successor while historical consumers continue to resolve their original bytes.
All 23 focused stateful-validation transition/replay tests then passed.

The first delivered candidate exposed one Ubuntu-only test-fixture cleanup race.
After 1,642 current tests, `TemporaryDirectory` could not remove `.git` because
detached Git auto-maintenance was still touching the short-lived synthetic
repository. The frozen publication and portfolio/history partitions still
passed. The repair disables garbage collection and maintenance only for that
synthetic repository; the failed GitHub Actions run and exact traceback are
preserved with the other implementation failures. The ordered closure is rerun
after this dependency change rather than reusing its prior success.

The full-suite fixture receipt directory is materialized inside that suite's
versioned workflow-validation stage, never below `results/research`. The existing
resource scientific replay and its attempt-family projection remain unchanged.

Usage extraction reads only explicit retained local Codex JSONL files, selects
one root turn, and emits an allowlist of identifiers, timestamps, source-file
hashes, model names and numeric usage. It never emits prompts, reasoning, tool
arguments or tool output. The aggregate is not account-wide billing evidence;
deleted/missing sessions and responses after the observation cutoff are unknown,
and no dollar amount or saving is inferred.

At the 2026-09-29 11:37:43 UTC cutoff, 82 unique response records were visible:
9,175,446 input tokens, of which 8,904,064 were cached and 271,382 were derived
uncached input; zero cache-write input tokens; 51,800 output tokens, including
16,829 reasoning-output tokens; and 9,227,246 input-plus-output tokens. The
successful final closure, repository delivery and later responses necessarily
fall after this cutoff. Reasoning output is a component reported separately,
not an amount to add again to total tokens.

The failed implementation attempts and their capture limits are preserved in
`implementation-failures.json`. The successful ordered repository closure is
required at the exact path named by `result.json`; its successful mechanical path
contains no model decision between stages.
