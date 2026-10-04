# Validation record

Base: `6fae731d29fb51ed636477586b54a4b46df4b82a`

## Preserved failures

1. Current-main reproduction failed on the first memory-breach run with
   `memory_exceeded: true`, `exit_code: -9`, and `cleanup_complete: false`.
   The exact receipt is retained under `before/`.
2. The first `python3 scripts/run-unit-tests` attempt stopped before discovery
   because the fresh environment lacked the queue-referenced
   `external/lean-kernel-arena/tests/nested-unused-param.lean` input.
3. After the documented Arena checkout was installed, a provisional production
   synchronization change failed three historical binding checks because
   `lib/metamorphic_pilot_runner_v3.py` is frozen evidence. That change was
   discarded; the file is byte-identical to the base commit in the final tree.
4. Provisional `SIGCHLD` and external-reaper fixture designs were rejected
   after stress/review showed that they could still create PID-1-owned zombies.
   Neither design is present in the final tree.

## Final checks

- `python3 -m unittest tests.test_metamorphic_supervisor`: 8 passed.
- `scripts/validate-metamorphic-pilot-tooling`: 8 supervisor and 13
  representation tests passed.
- 100 consecutive runs of
  `test_memory_breach_kills_and_cleans_process`: passed.
- 20 consecutive runs of `test_timeout_kills_process_group`: passed.
- Python zombie count surrounding the repeat checks: 437 before, 437 after.

## Repository-wide suite

`python3 scripts/check-portable-evidence-replay` passed with 20 families, 582
receipt files, 635 receipts and 932 raw streams. The final
`python3 scripts/run-unit-tests` run executed 1,677 current tests plus the
historical partitions. The target's eight tests passed, the 73-test publication
study partition passed, and the 14-test portfolio-history partition passed.

The current partition finished with four failures, one error and four expected
skips, all outside this patch:

- three cross-validation profiles were unavailable/incompatible because the
  Arena observer profiles were not materialized;
- portable coverage could not execute absent `rustc`;
- the existing CVC descendant-cleanup integration encountered the same host
  PID-1 zombie-reaping limitation (`fixture PID ... still exists`).

These failures are retained rather than hidden or attributed to this test-only
change. Exact pushed-commit CI remains the authoritative clean-run gate.
