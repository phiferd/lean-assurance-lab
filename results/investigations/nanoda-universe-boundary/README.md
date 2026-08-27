# Nanoda Universe Boundary Survivor

Mutant: `nanoda-gen-7447f6511962`

Mutation: in `src/level.rs`, `leq_core` changes the `Zero`/`diff` boundary at
line 182 from `diff >= 0` to `diff > 0` (`REL_GE_TO_GT`). The registered
mutation identity is
`7447f65119629638b2fd96c2bce11fdf65a61c6e5726702318c81ba8b0e81be8`.

## Existing Evidence

- The original coverage-guided run selected all 36 tests covering
  `src/level.rs:182` from a 197-test corpus and recorded
  `ALL_COVERING_TESTS_MATCH` with no witness.
- The existing durable result is
  `results/mutants/nanoda-gen-7447f6511962/scheduled-comparison.json`.
- The source is restored to baseline after the reproduction.

## Invalid 120-Second Rerun

Command:

```text
scripts/run-frontier-survivors nanoda-gen-7447f6511962 --timeout 120
```

The scheduler reported current line coverage and selected 36 tests. The raw
run is persisted at
`results/mutants/nanoda-gen-7447f6511962/scheduled-runs/20260827T154134Z/`.

The first recorded difference was:

- test: `mathlib`
- baseline: `ACCEPT`
- mutant: `TIMEOUT` after approximately 120 seconds

This was not a valid kill because the timeout was shorter than a normal
baseline execution of the same input on the same machine.

## Timeout-Controlled Reproduction

The exact `mathlib` input was rerun against both builds with a 900-second bound.
The baseline passed in 347.2 seconds and the mutant passed in 348.7 seconds.
The result, including the input digest and output hashes, is recorded at:

`results/investigations/nanoda-universe-boundary/mathlib-timeout-900s.json`

The complete refreshed schedule then exhausted all 36 tests covering
`src/level.rs:182` from the 198-test corpus. Every normalized outcome matched.
That comparison is recorded at:

`results/mutants/nanoda-gen-7447f6511962/scheduled-runs/20260827T165419Z/comparison.json`

## Status

The mutant is `SURVIVED_WITHOUT_WITNESS`. Preserve the raw 120-second run as an
audit example of an undersized timeout, but do not classify it as a performance
or semantic kill. The next useful work is a source-derived equality-boundary
witness search with matched controls and independent checker validation.
