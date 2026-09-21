# One-worker child-panic confirmation

Outcome: **SUCCESS** for the preregistered operational distinction.

Both release builds completed under sampled-RSS, timeout and cleanup controls.
Both controls printed the exact success line. The invalid candidate was rejected
in both profiles: the baseline raised the expected assertion on the main thread,
while the one-worker mutant raised it on `thread_0` and then raised the expected
parent-join panic.

This is a useful diagnostic regression, not a semantic or soundness difference.
The mutation changes where the same invalid input fails; it does not make the
checker accept that input. No upstream action is recommended from this result.

One sandboxed preflight was denied access to the local RSS monitor before a
process launched. That environment failure and its unused materialization are
preserved separately; the unchanged committed harness then completed all six
processes with RSS samples and clean teardown.
