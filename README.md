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

Milestones 1 through 4 are complete. The project has a closed mechanical
mutation loop for `nanoda`, content-addressed invalidation, and a structured
semantic model spanning validation elision, predicate negation, relational
boundaries, and equality discrimination. Witness search and structure-aware
minimization are executable and auditable. Current work begins Milestone 5:
cross-validator confirmation.

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
  artifact-status
  assurance-snapshot
  build-artifact-graph
  audit-coverage-guidance
  collect-coverage
  compare
  check-distinction
  confirm-witness
  generate
  generate-mutations
  minimize
  milestone-2-assurance
  milestone-3-assurance
  milestone-4-assurance
  mutate
  normalize-arena-results
  promote-scheduled-result
  reindex-coverage
  report
  run-arena
  run-mutation-batch
  run-mutant
  run-mutant-input
  run-mutant-scheduled
  schedule-mutant
  setup-arena
  snapshot-coverage
  validate-mutation-batch
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

Create, build-check, and execute a deterministic syntax-aware mutation batch:

```sh
scripts/generate-mutations --limit 12 --batch-id nanoda-semantic-0001 \
  --write --register
scripts/validate-mutation-batch nanoda-semantic-0001
scripts/run-mutation-batch nanoda-semantic-0001
```

The Rust parser under `tools/nanoda-mutator` discovers syntax-aware candidates
from the catalog at `mutation-model/catalog.json`. The wrapper classifies every
candidate as compiling, build-failed, duplicate, unsupported, or rejected
non-semantic; selects a bounded family-balanced population; assigns
content-deterministic identities; and records exact provenance. Batch
validation compiles every mutant in isolation and proves the checker source has
returned to its baseline digest.

Reproduce the selected population without discarding compatible evidence and
run the Milestone 3 gate with:

```sh
scripts/generate-mutations --limit 12 --batch-id nanoda-semantic-0001 \
  --write --refresh
scripts/report --output results/assurance/milestone-3-report.json
scripts/milestone-3-assurance
```

Execute a bounded witness search and its automatic minimizer with:

```sh
scripts/generate --mutant-id nanoda-gen-ca8565ff512e --subsystem universes \
  --seed-artifact external/lean-kernel-arena/_build/tests/tutorial/good/016_levelParams.ndjson \
  --random-seed 4104 --max-attempts 60
scripts/milestone-4-assurance
```

Every candidate is checked by the direct normalized predicate
`baseline(input) != mutant(input)`. Searches preserve an attempt log and input
hashes whether they find a witness or exhaust their budget. Found witnesses are
minimized automatically while retaining both artifacts and final predicate
checks.

Bind ignored local coverage payloads to a compact tracked identity artifact and
verify the Milestone 1 gate with:

```sh
scripts/snapshot-coverage
scripts/snapshot-coverage --verify
scripts/assurance-snapshot
```

Attest and inspect the repository-wide dependency graph with:

```sh
scripts/build-artifact-graph
scripts/artifact-status --require-current
scripts/milestone-2-assurance
```

The status command reports current, stale, missing, historical, and superseded
artifacts. Use `--simulate-change ARTIFACT_ID` or
`--simulate-missing ARTIFACT_ID` to inspect invalidation without modifying an
input. Normal report commands refuse stale dependencies once the graph exists.
