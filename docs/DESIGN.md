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

### Coverage Index And Scheduler

`scripts/collect-coverage` builds nanoda with Rust source coverage in an
isolated `target-coverage` directory and runs every materialized Arena test
separately. Each profile is accepted only when the instrumented normalized
outcome matches the cached baseline. Collection state includes a source digest,
thread count, and test pattern so incompatible interrupted runs cannot be
silently merged.

The coverage collector produces these local artifacts:

```text
results/coverage/<checker>/coverage.jsonl
results/coverage/<checker>/test-to-lines.json
results/coverage/<checker>/line-to-tests.json
results/coverage/<checker>/manifest.json
```

`scripts/schedule-mutant` maps the registered mutant source span through the
reverse index and orders covering tests by uninstrumented baseline wall time.
`scripts/run-mutant-scheduled` executes that schedule directly against nanoda.
Killed mutants stop at the first normalized difference; surviving mutants must
exhaust every covering test. Mutants on uncovered locations are labeled
`UNCOVERED`, not silently treated as normally tested survivors. Coverage is an
execution optimization only: periodic full-corpus audits remain a control for
source-mapping or instrumentation mistakes.

### Mutant Generator

`tools/nanoda-mutator` parses Rust with `syn` and emits validation-elision,
predicate-negation, relational-boundary, and equality-discrimination
candidates. `scripts/generate-mutations` maps candidates to the structured
operator/subsystem catalog, classifies duplicates, unsupported sites, and
rejected non-semantic changes, filters through exact coverage, and selects a
bounded family-balanced population. Identities bind source file, line, column,
operator, original syntax, and mutated syntax. Repeated source text is
disambiguated by an explicit replacement occurrence.

`scripts/validate-mutation-batch` restores every batch mutation before checking
the baseline source digest, compiles each mutation in isolation, records build
failures separately, and rebuilds baseline source at the end. The resumable
`scripts/run-mutation-batch` drives each compiling mutant through
`scripts/run-mutant-scheduled` without LLM involvement.

`scripts/report` emits mutation counts and score strata by operator, operator
family, and semantic subsystem. Strata below the catalog's minimum sample retain
raw counts but are explicitly `INSUFFICIENT_SAMPLE`. The Milestone 3 assurance
gate also requires one killed and one surviving coverage-guided conclusion to
match full 197-test corpus runs.

`scripts/run-mutant` is the current one-mutant orchestrator. It reads a
registered mutant and its exact replacement spec from `mutations/<id>.json`,
restores the checker source to baseline, optionally reruns baseline outcomes,
applies the mutant, builds and runs the mutant, normalizes both sides, compares
outcomes, appends registry status, and restores the checker source and binary to
baseline. It clears stale Arena `_results/<checker>_*.json` files before each
checker run so scoped runs cannot inherit records from earlier full runs. Full
runs enable the normalizer's exact built-corpus inventory check.

Every source-state transition checks the complete mutated replacement before
the original substring. This matters for generated wrappers such as
`if false { original_statement }`, where the original text remains a substring
of the mutant.

### Coverage Identity And Assurance Gate

`scripts/snapshot-coverage` hashes every local coverage artifact, all 197
materialized NDJSON inputs, baseline outcomes, checker source, Arena revision,
checker definition, collection configuration, and producer scripts into a
compact tracked manifest. Its `--verify` mode fails when any bound input or
output changes.

`scripts/assurance-snapshot` is the Milestone 1 gate. It requires current
coverage identity, identity-bound conclusions for all four controlled mutants,
a complete generated mutation batch, independent expected-outcome confirmation
for the promoted witness, and a measured augmented-corpus kill of the source
mutant.

### Artifact Graph And Invalidation

`results/artifacts/graph.json` is the content-addressed dependency graph for
current assurance claims. Its schema is `schemas/artifact-graph.schema.json`.
Each node records an artifact type, lifecycle, locator, expected SHA-256, and
the exact digest expected for every dependency. Git revision locators bind this
repository and Arena; file and file-set locators bind validator sources,
toolchains, configurations, mutation definitions, corpora, scripts, outcomes,
comparisons, witnesses, classifications, and reports.

`scripts/build-artifact-graph` attests the current graph.
`scripts/artifact-status` recomputes every locator and recursively reports
`CURRENT`, `STALE`, or `MISSING`; retained nodes are displayed as `HISTORICAL`
or `SUPERSEDED` without becoming current claims. A dependency digest mismatch
propagates staleness through every derived node, which prevents artifacts from
incompatible revisions or configurations from being silently combined.

`scripts/report` and `scripts/assurance-snapshot` require their graph
dependencies to be current whenever an attested graph exists. Their explicit
`--allow-stale-artifacts` option is diagnostic only. The Milestone 2 gate
simulates validator-source, corpus, mutation-model, and expected-semantics
changes and requires each to invalidate the intended descendants.

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

`scripts/generate` executes bounded, deterministic witness searches. It prepares
baseline and mutant binaries once, runs each candidate directly against both,
and records normalized outcomes in `attempts.jsonl`. Candidate generation uses
subsystem templates and structure-aware mutations of existing NDJSON exports;
random seeds only control a recorded deterministic candidate order.

Search success is exactly:

```text
baseline(input) != mutant(input)
```

Found artifacts are classified independently from their semantic meaning. A
distinction may have confirmed expected semantics, ambiguous semantics, or a
reference-checker disagreement. A bounded search without a distinction remains
an explicit unresolved result, never evidence of equivalence.

### Minimizer

`scripts/minimize` and the automatic post-search minimizer preserve the predicate:

```text
baseline(input) != mutant(input)
```

The minimizer first delta-debugs declaration records, then removes list elements
and non-identity object fields structurally. It invokes the prepared baseline
and mutant binaries directly rather than accepting an arbitrary shell predicate.
Both the original and minimized artifacts are retained, and both receive final
differential checks. Export metadata is a structural invariant and cannot be
deleted during minimization.

### Cross-Validator Confirmation

`config/validators.json` defines exact checker commands, implementation
families, roles, source identities, and empirically tested export compatibility.
Compatibility requires matching export, exporter, and Lean producer versions;
a pinned and unmodified checker build; and acceptance of a positive control.
Unsupported metadata or a failed control is recorded instead of being coerced
into a semantic result.

`scripts/establish-expected-outcome` uses one designated reference checker and
an accepted positive control to bind `ACCEPT` or `REJECT` to an exact artifact
SHA-256. This is expected-outcome evidence, not a vote. `scripts/cross-validate`
runs every selected compatible checker and retains exit codes, signals,
timeouts, output hashes and tails, parse behavior, and normalized outcomes.

The normalized vocabulary is:

```text
ACCEPT REJECT DECLINE CRASH TIMEOUT PARSE_ERROR UNKNOWN
```

Cross-validator classifications are:

```text
CONFIRMED CHECKER_DISAGREEMENT DECLINED INCOMPATIBLE CRASHED
TIMED_OUT PARSE_ERROR UNRESOLVED
```

Any compatible `ACCEPT` / `REJECT` difference is exceptional and unresolved,
even if other checkers agree. A regression candidate must carry exact expected
outcome evidence; checker disagreement remains attached to that candidate.

### Held-Out Transfer Experiments

Milestone 6 separates generation from evaluation with a content-addressed
freeze boundary. `scripts/freeze-transfer-experiment` declares the analogous
held-out fault, generates candidate and control artifacts from the source
validator's model, verifies the source-validator distinction, establishes the
reference outcome, and writes a freeze manifest while the held-out mutation is
unapplied. The manifest explicitly excludes held-out mutant outcomes and logs
from generation inputs.

`scripts/run-transfer-experiment` accepts only the exact frozen corpus and
manifest SHA. It builds baseline and mutant held-out binaries, evaluates the
candidate and control, restores the source and binary, and classifies:

```text
POSITIVE_TRANSFER NEUTRAL_TRANSFER NEGATIVE_TRANSFER
INCONCLUSIVE INCOMPATIBLE UNRESOLVED
```

Positive transfer requires the held-out baseline to match the reference,
the analogous mutant to change the candidate outcome in the modeled direction,
and both checker states to accept the positive control. A held-out result can
never retroactively alter the frozen generation artifact.

Milestone 7 generalizes this protocol into separate rotating folds.
`scripts/freeze-rotating-fold` records the source validator's mechanical
distinction, official expected-outcome evidence, exact candidate and control
hashes, pinned held-out source, mutation model, original corpus identity, and a
declaration that no held-out mutant feedback was used. `scripts/run-rotating-fold`
then evaluates the exact freeze against baseline and mutated Lean4Lean, including
all 197 original corpus tests. The held-out mutation is applied only after the
freeze and its source is restored exactly after evaluation.

`scripts/evaluate-m6-rotating-fold` represents the earlier Kiota experiment in
the same fold schema and measures whether its original corpus already killed the
held-out mutant. `scripts/build-rotating-heldout-report` aggregates fold scores
without merging their generation inputs or evaluation evidence. Each fold
records original and augmented kills, mutation scores, score change, unresolved
tests, checker runs, and checker time. Fold outcomes are:

```text
POSITIVE NEUTRAL NEGATIVE INCONCLUSIVE INCOMPATIBLE UNRESOLVED
```

`POSITIVE` means the augmented corpus kills an additional modeled mutant;
`NEUTRAL` means it does not change the held-out score; and `NEGATIVE` means the
augmented score regresses. The remaining states preserve insufficient evidence,
compatibility failures, and unresolved execution separately. These labels refer
to intentionally injected faults, not bugs in unmodified validators. Aggregate
interpretation remains scoped because two folds with one mutant each cannot
establish a general transfer rate or rule out implementation-specific
overfitting.

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
  -> expected-outcome evidence
  -> compatible independent validators
  -> confirmation or durable disagreement
```

## Durable Result Files

The first implementation should produce these files when data exists:

```text
results/baseline/runs/<stamp>/metadata.json
results/baseline/runs/<stamp>/raw.log
results/baseline/outcomes/<checker>.jsonl
results/coverage/<checker>/coverage.jsonl
results/coverage/<checker>/test-to-lines.json
results/coverage/<checker>/line-to-tests.json
results/coverage/<checker>/manifest.json
results/mutants/registry.jsonl
results/mutants/<mutant-id>/build.json
results/mutants/<mutant-id>/outcomes.jsonl
results/mutants/<mutant-id>/comparison.json
results/mutants/<mutant-id>/runs/<stamp>/*.log
results/mutants/<mutant-id>/scheduled-runs/<stamp>/schedule.json
results/mutants/<mutant-id>/scheduled-runs/<stamp>/comparison.json
results/survivors/inventory.jsonl
results/witnesses/<witness-id>/metadata.json
corpus/generated/<witness-id>.ndjson
corpus/minimized/<witness-id>-min.ndjson
results/expected-outcomes/<case-id>.json
results/cross-validation/<case-id>/results.json
corpus/regression-candidates/milestone-5.json
results/transfer/milestone-6/freeze.json
results/transfer/milestone-6/evaluation.json
corpus/transfer/milestone-6/*.ndjson
experiments/milestone-7/spec.json
results/rotating-heldout/milestone-7/folds/lean4lean-freeze.json
results/rotating-heldout/milestone-7/folds/lean4lean-evaluation.json
results/rotating-heldout/milestone-7/folds/kiota-evaluation.json
results/rotating-heldout/milestone-7/report.json
corpus/transfer/milestone-7/*.ndjson
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
