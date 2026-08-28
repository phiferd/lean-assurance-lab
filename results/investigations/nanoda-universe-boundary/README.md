# Nanoda Universe Boundary Equivalence

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

## Source-Derived Boundary Analysis

The apparent `>=` versus `>` boundary is unreachable as a behavioral
difference because of match-arm ordering:

```text
(Zero, _) if diff >= 0 => true
...
(Zero, Param { .. }) => diff >= 0  // mutant: diff > 0
```

The first arm consumes every `Zero, Param` input for which `diff >= 0`. The
later mutated arm is therefore reachable only when `diff < 0`. In that region,
both `diff >= 0` and `diff > 0` are false. The original and mutant return the
same value for every possible input to this match expression.

A source-derived candidate was also exported from a deliberately unchecked
universe-polymorphic inductive declaration to force a zero-level constructor
field against a parameterized codomain. Both baseline and mutant Nanoda accept
the artifact. Instrumentation confirmed that the specific later arm was
reached only with `diff = -1`; the `diff = 0` case was consumed by the preceding
arm. The candidate and restored differential are:

- `corpus/generated/nanoda-gen-7447f6511962-zero-le-param.ndjson`
- `results/investigations/nanoda-universe-boundary/zero-le-param-reproduction.json`

The hash-bound proof summary is in `equivalence-analysis.json`.

## Status

The mutant is `EQUIVALENT`; no distinguishing witness exists for this source
mutation. Preserve the raw 120-second run as an audit example of an undersized
timeout, but do not classify it as a performance or semantic kill. The checker
source was restored and rebuilt after instrumentation.
