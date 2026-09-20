# One-thread determinism assessment

`SURVIVOR-THREAD-ONE-DETERMINISM-1` completed SUCCESS as a source-and-evidence
assessment. It ran no network, build, checker, proof, generator or external
action.

The prior reachability analysis was right to preserve a real operational
boundary: `num_threads=1` changes the original serial `check_declar` loop into
one scoped worker with a fixed 16 MiB stack. This assessment found a bounded,
non-ambient way to observe that boundary. The existing 601-byte invalid export
already reaches `assert_def_eq`; the serial path reports that assertion directly,
whereas the one-worker path must join a panicked worker through Nanoda's fixed
`check_all_declars` join diagnostic.

This is a protocol candidate, not an executed observation. It makes no semantic
acceptance, soundness, current-upstream or checker-authority claim. A separate
successor must bind exact `num_threads=1` configuration bytes, both builds,
controls, raw diagnostics, timeout and cleanup before launching the four cells.
Thread-creation failure, stack exhaustion and multi-worker scheduling remain
excluded because they rely on ambient or unbound conditions.
