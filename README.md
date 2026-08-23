# Lean Kernel Arena Mutation & Differential Testing

This repository tracks a mechanical testing project for Lean proof checkers.
The initial target is mutation testing against one checker implementation,
then using surviving mutants to drive adversarial exported-artifact generation.

The project is governed by `CONSTITUTION.md`. The current execution plan lives
in `docs/PROJECT_PLAN.md`.

The core success condition is always executable:

```text
checker_a(input) != checker_b(input)
```

LLMs and humans may propose candidates or explain results, but they do not
decide whether a test succeeded.

## Research Question

How effectively does the current Lean Kernel Arena corpus discriminate correct
Lean kernel behavior from plausible incorrect implementations, and can
automated mutation-driven adversarial test generation systematically improve
that discrimination?

A secondary question is whether the same machinery can discover previously
unknown disagreements among independently implemented Lean proof checkers.

## Current Milestone

Milestone 1 is deliberately small:

1. Use Lean Kernel Arena locally.
2. Select `nanoda` as the first mutation target unless investigation shows a
   better small checker.
3. Build one manually introduced semantic mutation.
4. Run the Arena corpus against baseline and mutant.
5. Record distinguishing tests.
6. Automate the workflow.
7. Add a small controlled mutation batch.
8. Produce the first mutation-survival report.

## Repository Layout

```text
docs/
  DESIGN.md
  MUTATION_MODEL.md
  RESEARCH_STATUS.md
results/
  baseline/
  mutants/
  survivors/
  witnesses/
corpus/
  generated/
  minimized/
scripts/
  collect-coverage
  compare
  generate
  minimize
  mutate
  normalize-arena-results
  reindex-coverage
  report
  run-arena
  run-mutant
  run-mutant-scheduled
  schedule-mutant
  setup-arena
```

The upstream Lean Kernel Arena checkout is expected at `external/lean-kernel-arena`
by default. Override with `LKA_ROOT=/path/to/lean-kernel-arena`.

## First Commands

```sh
scripts/setup-arena
scripts/run-arena --checker nanoda
scripts/normalize-arena-results --checker nanoda \
  --output results/baseline/outcomes/nanoda.jsonl
scripts/report
```

The commands are thin wrappers. They preserve raw outputs under `results/` so
that project state is recoverable from files rather than conversation context.

After a baseline and mutant have both emitted normalized JSONL outcomes, compare
them with:

```sh
scripts/compare results/baseline/outcomes/nanoda.jsonl \
  results/mutants/MUTANT_ID/outcomes.jsonl \
  --mutant-id MUTANT_ID \
  --output results/mutants/MUTANT_ID/comparison.json
```

Normalized outcome records use this minimum shape:

```json
{"test":"path/or/test-id","outcome":"ACCEPT","checker":"nanoda"}
```

Allowed outcomes are `ACCEPT`, `REJECT`, `DECLINE`, `CRASH`, `TIMEOUT`,
`PARSE_ERROR`, and `UNKNOWN`.

## Automated Mutant Loop

Registered mutants with a source replacement spec under `mutations/` can be run
end to end with:

```sh
scripts/run-mutant nanoda-0001 --test tutorial/012_nonPropThm
```

Omit `--test` to run the full materialized Arena corpus. The script restores the
checker to baseline, builds and runs baseline outcomes, applies the mutant,
builds and runs mutant outcomes, normalizes both sides, compares them, updates
the mutant registry, and restores the checker source and binary to baseline.

The Arena `_results` directory is cleared for the selected checker before each
side of the run so normalized outcomes cannot accidentally include stale result
JSON from a previous broader run. Full runs also require the normalized test
identities to match the materialized `*.stats.json` corpus exactly; duplicate,
missing, unexpected, or malformed result records fail the run before comparison.

## Coverage-Guided Mutant Loop

Collect exact per-test Rust line coverage for the materialized nanoda corpus:

```sh
scripts/collect-coverage --timeout 7200 --checker-threads 1
```

The collector uses an isolated instrumented binary under `target-coverage`,
checks every instrumented outcome against the cached baseline, checkpoints each
test, and writes forward and reverse indexes under `results/coverage/nanoda/`.
Interrupted runs can continue with `--resume --reuse-build`, provided the saved
source digest and collection configuration still match.

Inspect or persist the fastest-first covering-test schedule for a mutant:

```sh
scripts/schedule-mutant nanoda-0001
scripts/schedule-mutant nanoda-0001 \
  --output results/mutants/nanoda-0001/schedule.json
```

Run the mutation mechanically against that schedule:

```sh
scripts/run-mutant-scheduled nanoda-0001
```

The scheduled runner validates the coverage/source digest, applies and builds
the mutant, runs covering tests in normal baseline wall-time order, stops on the
first normalized difference, and restores the baseline source and binary. A
survivor must exhaust every covering test. A source span with no covering tests
is reported explicitly as `UNCOVERED`.
