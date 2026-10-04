# Supervisor cleanup synchronization repair

## Plain-language result

**What did we find?** Current `main` reproduced the reported validation failure
on the first focused run. Memory enforcement killed the synthetic process group,
but both synthetic descendant fixtures left killed grandchildren for PID 1 to
reap and the one-shot group-absence probe raced with those zombies. The live
integration fixtures now use one supervised process, while a deterministic
unit control verifies that a memory breach sends `SIGKILL` to the process group.
The production supervisor and its strict process-group-absence check remain
byte-for-byte unchanged. One hundred memory-limit repetitions and twenty
timeout repetitions passed without increasing the host's pre-existing Python
zombie count (437 before and after).

**Is it interesting?** Yes as an ordinary reproducibility repair: unrelated
repository validation no longer depends on orphan-reaping timing. This is not a
scientific finding and does not change frozen experiment evidence or checker
semantics.

**Does it require more work?** No follow-up is implied if the repository suite
and exact-commit CI pass. This test-only repair does not make the supervisor a
subreaper or change how real supervised programs manage descendants. Programs
that leave unreaped descendants continue to fail the cleanup check. The live
test no longer claims portable descendant reaping on hosts whose PID 1 does not
reap orphans.

## Evidence and mechanism

- Before: `before/memory.receipt.json` records `memory_exceeded: true`, exit
  signal 9, an 80,556,032-byte observed peak over the 64 MiB ceiling, and the
  timing-sensitive `cleanup_complete: false` result.
- Mechanism: live single-process fixtures still exercise RSS observation,
  enforced kill, timeout and strict process-group absence. A mock-backed unit
  control separately requires the memory monitor to call
  `killpg(process.pid, SIGKILL)` when a group member exceeds the limit.
- Repeat check: 100 memory-limit and 20 timeout integration runs passed; the
  host's Python-zombie count remained 437 before and after.
- The tooling validator's exact supervisor-test inventory is updated from its
  stale five-test value to the current eight-test module inventory.

See `validation.md` for preserved validation attempts and limitations.
