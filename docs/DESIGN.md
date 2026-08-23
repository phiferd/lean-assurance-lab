# Design

## Principle

Proof artifacts and checker outcomes are mechanically testable objects. A
distinguishing artifact is an input where two checker implementations produce
different normalized outcomes.

The normalized outcome vocabulary is:

```text
ACCEPT
REJECT
DECLINE
CRASH
TIMEOUT
PARSE_ERROR
UNKNOWN
```

Where a checker cannot expose parser failures separately, the executor records
the coarser result and notes that limitation in the run metadata.

## Components

### Arena Checkout

`external/lean-kernel-arena` contains the upstream Arena repository. It is kept
separate from this research repository so generated mutation results, witness
searches, and reports can evolve independently.

### Corpus Executor

`scripts/run-arena` is the first executor. It delegates to Arena's `lka.py`
commands and records logs under `results/baseline/runs/`.

`scripts/normalize-arena-results` converts Arena `_results/*.json` files into
normalized JSONL. It rejects malformed statuses and duplicate test identities.
For full runs, the orchestrator also requires exact identity-set equality with
the materialized `*.stats.json` corpus, preventing filename collisions or
missing raw results from silently changing a mutation comparison. Later
versions should add a lower-level executor that can run a selected checker
binary directly against a selected NDJSON artifact and emit normalized JSONL
without going through the whole Arena runner.

### Mutant Generator

`scripts/mutate` is a placeholder interface for creating, listing, and building
mutants. The initial implementation should support manually registered mutants
before adding bulk source-to-source mutation.

`scripts/run-mutant` is the current one-mutant orchestrator. It reads a
registered mutant and its exact replacement spec from `mutations/<id>.json`,
restores the checker source to baseline, optionally reruns baseline outcomes,
applies the mutant, builds and runs the mutant, normalizes both sides, compares
outcomes, appends registry status, and restores the checker source and binary to
baseline. It clears stale Arena `_results/<checker>_*.json` files before each
checker run so scoped runs cannot inherit records from earlier full runs. Full
runs enable the normalizer's exact built-corpus inventory check.

Each mutant record should include:

```yaml
id:
checker:
source_file:
source_span:
mutation_operator:
subsystem:
build_artifact:
status:
notes:
```

### Comparator

`scripts/compare` compares normalized checker outcomes. A mutant is killed when
at least one Arena test has a different baseline and mutant outcome.

The comparator intentionally works on normalized JSONL rather than checker logs.
Each executor is responsible for turning its raw output into records of this
form:

```json
{"test":"suite/example.ndjson","outcome":"REJECT","checker":"nanoda","detail":"optional"}
```

This keeps mutation scoring independent of any one checker's command-line
format. Missing records are treated as `UNKNOWN` and reported as differences
only when the opposite side has a concrete different outcome.

### Witness Generator

`scripts/generate` is the replaceable search component. Initial strategies should
prefer structure-aware mutations of existing exported artifacts over byte-level
corruption.

### Minimizer

`scripts/minimize` preserves the predicate:

```text
baseline(input) != mutant(input)
```

The first version can use delta debugging over declaration sequences. Later
versions should reduce expression trees and declaration metadata structurally.

The current minimizer is line-oriented and treats each non-empty exported line
as a removable unit. It requires a predicate command that exits with status 0
when the distinction still holds.

## Data Flow

```text
Arena corpus
  -> baseline checker outcomes
  -> mutant checker outcomes
  -> comparison report
  -> survivor inventory
  -> witness search
  -> minimized witness
  -> candidate Arena regression
  -> rerun mutation analysis
```

## Durable Result Files

The first implementation should produce these files when data exists:

```text
results/baseline/runs/<stamp>/metadata.json
results/baseline/runs/<stamp>/raw.log
results/baseline/outcomes/<checker>.jsonl
results/mutants/registry.jsonl
results/mutants/<mutant-id>/build.json
results/mutants/<mutant-id>/outcomes.jsonl
results/mutants/<mutant-id>/comparison.json
results/mutants/<mutant-id>/runs/<stamp>/*.log
results/survivors/inventory.jsonl
results/witnesses/<witness-id>/metadata.json
corpus/generated/<witness-id>.ndjson
corpus/minimized/<witness-id>-min.ndjson
```

The exact upstream Arena output format may change; raw logs and metadata are
therefore retained even after normalized records are produced.

## Mechanical Controls

Mutation reports must distinguish:

```text
KILLED
SURVIVED
BUILD_FAILED
TEST_FAILED
UNKNOWN
```

Survivor classification must distinguish:

```text
EQUIVALENT
UNREACHABLE
PERFORMANCE_ONLY
MEANINGFUL_SEMANTIC
UNKNOWN_EQUIVALENCE
```

Mutation score is computed only over meaningful tested mutants:

```text
meaningful killed / meaningful tested
```

Equivalent mutants are excluded from the denominator.
