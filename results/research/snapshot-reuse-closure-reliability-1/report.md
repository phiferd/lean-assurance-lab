# Validation snapshot and stage reuse closure reliability — 2026-09-29

**What did we find?** The shared closure controller now runs the expensive full
suite from a detached checkout of the exact bound commit, not from the mutable
publication worktree. It refuses publication if declared current inputs differ
from the validated snapshot. Separate content dependencies for status, suite,
and publication reuse the suite after a publication-only document change but
rerun it after a real test dependency changes. Thirty-one focused controls
pass. Three failed ordered closure attempts are preserved and repaired. No
scientific experiment ran.

**Is it interesting?** Yes. An arbitrary edit followed by restoration could
previously affect validation while escaping the before/after byte comparison.
The snapshot removes that path. Removing global `HEAD` from reusable stage
digests also avoids invalidating expensive work solely because an unrelated
commit changed.

**Does it require more work?** No repair follows from the passing ordered
closure. The next separate queue item is
`RESOURCE-SHORT-PROCESS-MEMORY-AUDIT-1`, a read-only audit of eighteen retained
receipts. It is not part of this result and remains unstarted.

## Technical result and limits

Schema-v3 closure scopes declare three complete dependency sets: status,
suite, and publication. Every declared file must belong to at least one set,
publication must cover all declared files and trees, and the suite binds every
tracked repository directory as a Git tree. Reuse specifications hash the
applicable file/tree/host-payload bindings, predecessor receipt, command, and
executable identity without using the repository commit as an all-stage
invalidator. Final checks retain their tracked-worktree binding.

The controller materializes a detached worktree at the committed input
identity. Tracked validation executes there. The ignored Arena checkout is
copied without its 25 GiB build tree; that tree and the coverage payload are
materialized as isolated copy-on-write clones. Their exact frozen file
bindings and the Arena revision enter suite and publication identities. Source-custody
ancestors therefore remain ordinary directories. Supervisor test receipts are
created inside the snapshot and copied into the versioned control stage after
execution, outside scientific evidence.

Focused regressions demonstrate edit-and-restore isolation, publication
mismatch refusal, reuse after a declared publication-only document commit, and
invalidation after a committed suite dependency change. Existing ownership,
resume, output inventory, tamper refusal, failed-attempt, and historical-byte
controls remain passing.

Attempt 0001 stopped before test discovery because a top-level `external`
symlink violated source custody. Attempt 0002 ran all current and historical
partitions and exposed snapshot-local receipt, retained Arena checkout, and
closure-time successor-state requirements. Attempt 0003 stopped before test
discovery because edits to five frozen historical tests violated their exact
portfolio bytes; those edits were restored. All three attempts remain
immutable. Attempt 0004 is the required final current/historical closure
receipt against the completed item and READY successor state.

This is workflow evidence, not evidence about Lean semantics, checker
correctness, resource performance, or scientific confirmation. The dependency
sets are authoritative only for their declared closure scope; a future item
must enumerate its own complete inputs.
