# Project Plan

## Planning Frame

This plan is governed by `CONSTITUTION.md`.

The constitutional goal is:

```text
Continuously improve and explain the measured assurance state of the Lean
validation ecosystem.
```

The plan below describes the current strategy for advancing that goal. It is
allowed to change. A strategy change is acceptable when it improves trust,
quality, visibility, reproducibility, or community usefulness while preserving
the constitutional tenets.

## Strategic Outcomes

The project is working toward these durable outcomes:

1. A reproducible assurance snapshot for Lean validators and conformance
   corpora.
2. A mechanical artifact graph that records inputs, revisions, assumptions,
   results, and unresolved states.
3. A process for searching for validation gaps, classifying the result, and
   turning confirmed gaps into shared regression tests when they exist.
4. Evidence about whether generated tests improve the ecosystem generally,
   have no measurable effect, regress, or remain unresolved.
5. Reports that make strengths, weaknesses, costs, disagreements, and unknowns
   visible to the Lean community.

## Operating Principles

Each milestone should produce inspectable artifacts. A milestone is not
complete because the system was run once; it is complete when a fresh process
can inspect the repository and understand what was measured, why it matters,
and what remains unresolved.

Claims must remain scoped. The project should never say "Lean is correct" or
"the corpus is sufficient." It may say that, for exact versions and documented
models, a measured assurance condition currently holds or fails.

The near-term strategy uses semantic mutation testing, coverage-guided
execution, witness generation, minimization, and cross-validator confirmation.
Those methods are implementation strategy, not constitutional identity.

Milestones succeed by producing scoped measurements, classifications, and
reports. They must not depend on finding a flaw, proving a theorem, producing a
positive transfer result, or improving a metric. "None found," "no measurable
change," "inconclusive," "incompatible," and "unresolved" are valid outputs
when they are mechanically grounded and clearly reported.

## Current Baseline

Current measured state, distinguishing tracked artifacts from local evidence:

- The project has a constitution and initial design documents.
- The project has a private GitHub repository and an initial committed
  scaffold.
- Lean Kernel Arena is used as the current source of validators and tests.
- `nanoda` is the first controlled validator target.
- Four `nanoda` mutants are registered.
- `nanoda-0001` and `nanoda-0002` are killed by the current Arena corpus.
- `nanoda-0003` survived the current 197-test materialized corpus.
- A generated witness distinguishes baseline `nanoda` from `nanoda-0003`.
- `nanoda-0004` is registered but not yet evaluated.
- Per-test coverage collection completed for all 197 materialized `nanoda`
  tests, with exact instrumented-versus-baseline outcome agreement.
- The local coverage indexes contain 3,884 covered source locations across 20
  Rust source files. They are excluded from Git under the current artifact
  storage policy, so they are reproducible local evidence but not yet durable
  repository artifacts.
- Coverage-guided execution reproduced the `nanoda-0001` kill after 7 of 67
  covering tests and exhausted all 120 covering tests for `nanoda-0003`
  without a difference.
- Coverage schedules have been produced for all four registered mutants.
- Mutation application, coverage scheduling, execution, normalized comparison,
  status recording, and source restoration are mechanical once a mutation spec
  exists. Mutation-site generation is still manual and is the next automation
  boundary.

## Milestone 0: Reproducible Project Foundation

Goal: make the project state durable, versioned, and inspectable.

Status: mostly complete, with remaining artifact-identity work.

Tasks:

1. Keep `CONSTITUTION.md` as the governing project document.
2. Keep setup, design, mutation model, and research status documents current.
3. Track source, scripts, mutation specs, compact result summaries, survivor
   records, and witness metadata in Git.
4. Exclude heavyweight local artifacts such as external checkouts, virtualenvs,
   raw build products, and raw large outcome streams from Git.
5. Add explicit artifact manifests that record exact Arena revision, validator
   revision, corpus inventory digest, mutation spec digest, tool versions,
   build flags, and runtime configuration.
6. Add a lightweight command that reports whether tracked artifacts are
   internally consistent.

Exit criteria:

- A fresh checkout can identify the current project purpose, current status,
  and next task without conversation context.
- The project can distinguish tracked durable artifacts from local scratch
  artifacts.
- Assurance claims include exact input identity or are explicitly marked
  provisional.

## Milestone 1: Complete the Single-Validator Hardening Loop

Goal: demonstrate the machinery for a closed mechanical loop for `nanoda`.

Status: in progress. Coverage collection and integrity validation are complete;
coverage-guided execution has been validated on one killed mutant and one
survivor. Mutation generation, `nanoda-0004`, witness confirmation, and the
augmented-corpus rerun remain.

This is the first critical project milestone. It should demonstrate that the
project can mechanically classify a modeled semantic fault and, when a
confirmed corpus gap exists, move from that gap to a regression candidate.

Completed:

1. Collected full per-test coverage for `nanoda` over all 197 tests in the
   materialized Arena corpus.
2. Produced the local coverage artifact set:
   - `coverage.jsonl`
   - `manifest.json`
   - `test-to-lines.json`
   - `line-to-tests.json`
3. Validated coverage artifact integrity:
   - exact test inventory matches baseline outcomes;
   - instrumented outcomes match uninstrumented baseline outcomes;
   - source digest matches the validator source used for scheduling;
   - coverage records are complete for every selected test.
4. Added mechanical coverage scheduling and execution with source-digest
   validation, fastest-first ordering, early kill, complete survivor execution,
   status recording, and baseline restoration.
5. Reproduced the prior full-corpus conclusions for `nanoda-0001` and
   `nanoda-0003` through coverage-guided execution.

Remaining:

1. Decide and implement a durable storage policy for coverage manifests and
   indexes, or record enough identity to regenerate and verify them exactly.
2. Run `nanoda-0002` through coverage-guided execution to complete the known
   killed-mutant scheduler audit.
3. Run `nanoda-0004` through the mutation loop.
4. Automate deterministic semantic mutation-site generation so the normal
   mutation loop no longer depends on manual or LLM-authored source edits.
5. Promote the `nanoda-0003` witness to a candidate regression only after its
   expected semantics are mechanically confirmed.
6. Add confirmed candidate regressions to a controlled augmented corpus when
   such candidates exist.
7. Rerun the source mutant when an augmented-corpus candidate exists and record
   whether the augmented corpus kills it.
8. Verify baseline validator behavior remains consistent on the augmented
   corpus.
9. Record all outputs as durable artifacts.

Exit criteria:

- The system classifies evaluated mutants as killed, survived with witness,
  survived without witness, equivalent or unreachable with evidence,
  disagreement, or unresolved.
- If a generated witness is promoted to a regression candidate, its expected
  outcome is mechanically established.
- If an augmented corpus is produced, the source mutant is rerun and the result
  is recorded, whether killed or not.
- Coverage-guided execution is shown to preserve mutation conclusions for
  tested mutants, or its limitations are documented.

Primary artifact:

```text
semantic mutant -> existing corpus evaluation -> survivor classification ->
optional generated witness -> optional confirmed regression ->
optional augmented corpus -> measured rerun result
```

## Milestone 2: Improve Artifact Graph and Invalidation

Goal: make assurance state expire correctly when inputs change.

Tasks:

1. Define an artifact schema for validators, corpora, mutation specs, coverage,
   runs, comparisons, witnesses, classifications, and reports.
2. Add content digests for every artifact dependency.
3. Record exact revisions for:
   - this repository;
   - Lean Kernel Arena;
   - validator source checkout;
   - Lean version/toolchain;
   - mutation specs;
   - corpus inventory;
   - scripts and configuration used to produce results.
4. Implement a local status command that reports stale, missing, and current
   artifacts.
5. Implement targeted invalidation rules:
   - validator source change invalidates build, coverage, mutants, and related
     scores;
   - corpus change invalidates affected coverage and mutation outcomes;
   - mutation model change invalidates affected mutant populations;
   - expected-semantics change invalidates regression classifications.
6. Preserve historical results while preventing stale artifacts from being used
   in current assurance claims.

Exit criteria:

- The system can explain which claims are current and which are expired.
- A changed input causes affected derived artifacts to be marked stale.
- No report can silently mix incompatible revisions or configurations.

## Milestone 3: Expand Semantic Mutation Coverage

Goal: build a documented semantic fault model beyond a few manual mutants.

Tasks:

1. Convert current manual mutation specs into a more structured mutation
   catalog.
2. Define mutation operator families by semantic subsystem.
3. Attempt to generate a modest batch of semantic mutants for `nanoda`.
4. Record deterministic mutant identities and provenance.
5. Classify build failures separately from semantic survivors.
6. Track mutation score by subsystem and operator.
7. Avoid arbitrary source churn that does not model plausible semantic faults.
8. Keep the initial batch small enough that survivor analysis remains feasible.

Exit criteria:

- The project has a documented semantic mutation model with deterministic
  mutant identities.
- Mutation attempts are classified as compiling semantic mutants, build
  failures, duplicates, unsupported mutation sites, or rejected non-semantic
  changes.
- Subsystem-level metrics are reported where the sample is large enough, and
  explicitly marked insufficient where it is not.
- Survivors are classified into durable states rather than treated as generic
  failures.

## Milestone 4: Automate Witness Search and Minimization

Goal: reduce manual effort in classifying meaningful survivors.

Tasks:

1. Replace witness planning with executable witness-search strategies.
2. Support structure-aware mutation of existing NDJSON/export artifacts.
3. Add subsystem-specific generators where useful.
4. Preserve the distinction predicate:

   ```text
   baseline(input) != mutant(input)
   ```

5. Run minimization automatically after a witness is found.
6. Preserve both original and minimized witnesses.
7. Record witness search inputs, random seeds, strategy, attempts, costs, and
   final predicate checks.
8. Distinguish:
   - no witness found yet;
   - witness found;
   - minimized witness found;
   - ambiguous semantics;
   - checker disagreement.

Exit criteria:

- The witness system can execute a search strategy against a survivor and
  produce a durable classification.
- If a witness is found, it has durable metadata sufficient to reproduce the
  search or audit its result.
- If no witness is found, the failed search produces useful unresolved-state
  artifacts rather than disappearing into logs.

## Milestone 5: Cross-Validator Confirmation

Goal: classify generated tests against independent validators so ecosystem
relevance is visible.

Tasks:

1. Add direct execution support for compatible independent validators.
2. Normalize outcomes across validators without hiding meaningful differences.
3. Define compatibility rules for generated tests.
4. Run generated witnesses against available unmodified validators.
5. Record agreement, disagreement, decline, crash, timeout, and parse behavior.
6. Treat semantic disagreement as an exceptional state requiring investigation.
7. Avoid majority-vote semantics as a substitute for evidence.
8. Produce candidate Arena regression tests only when expected behavior is
   mechanically established.

Exit criteria:

- Generated witnesses are evaluated against compatible validators and
  classified as confirmed, disagreement, declined, incompatible, crashed,
  timed out, or unresolved.
- Any disagreement is preserved as a durable unresolved artifact.
- Regression candidates include expected outcome evidence, not just a source
  mutant distinction.

## Milestone 6: First Generalization Experiment

Goal: run the first explicit transfer experiment across independent validators.

Tasks:

1. Select a second validator with enough overlap to support a meaningful
   experiment.
2. Introduce an analogous semantic fault independently into that validator.
3. Generate a test without using the held-out validator's mutant results.
4. Freeze the generated corpus.
5. Evaluate whether the generated corpus detects the independently introduced
   fault.
6. Record whether the result supports transfer, shows no transfer, regresses,
   is inconclusive, or is blocked by incompatibility.

Exit criteria:

- The experiment is run and produces a durable transfer classification:
  positive, neutral, negative, inconclusive, incompatible, or unresolved.
- The result is documented with enough detail to guide the next strategy
  decision.

## Milestone 7: Rotating Held-Out Evaluation

Goal: measure whether corpus changes generalize across validator
implementations.

Tasks:

1. Add support for multiple validators and validator-specific mutation models.
2. Implement leave-one-validator-out evaluation.
3. For each fold:
   - hold out one validator;
   - generate or select augmented tests without using that validator's mutants;
   - evaluate original corpus against held-out mutants;
   - evaluate augmented corpus against held-out mutants;
   - compute score change.
4. Report per-validator improvement, no-change results, regressions,
   unresolved states, and costs.
5. Keep fold data separate so held-out results cannot influence generation.

Exit criteria:

- The project can produce a rotating held-out report with positive, neutral,
  negative, inconclusive, and unresolved fold outcomes.
- The report distinguishes general semantic improvement, lack of measurable
  transfer, regressions, and implementation-specific overfitting risk.

## Milestone 8: Assurance Snapshot and Gate

Goal: publish a reproducible current-state report.

Tasks:

1. Define the assurance snapshot format.
2. Report at least:
   - exact revisions and configurations;
   - validators;
   - corpus inventory;
   - total semantic mutants;
   - killed by existing corpus;
   - killed by generated corpus;
   - meaningful survivors;
   - equivalent or unreachable mutants;
   - unresolved mutants;
   - subsystem scores;
   - witness synthesis success rate;
   - generated regressions;
   - cross-validator disagreements;
   - held-out score changes;
   - coverage statistics;
   - execution cost.
3. Define gates separately from trend metrics.
4. Fail hard on:
   - unexplained baseline changes;
   - incomplete result inventories;
   - unresolved semantic checker disagreement;
   - regression candidates without mechanically established expected outcomes;
   - stale artifacts used as current claims.
5. Keep mutation score and coverage thresholds configurable and contextual.

Exit criteria:

- The project can produce a current assurance snapshot from repository
  artifacts.
- The snapshot clearly says whether the current gate passes or fails, why, and
  which evidence supports that conclusion.

## Milestone 9: Community Workflow

Goal: make external participation useful without weakening standards.

Tasks:

1. Write contribution guidance aligned with the constitution.
2. Define how to contribute:
   - validators;
   - corpus tests;
   - mutation operators;
   - witness generators;
   - reports;
   - bug investigations;
   - documentation.
3. Define required metadata for each contribution type.
4. Add review checklists for mechanical evidence and scoped claims.
5. Create issue templates for:
   - validator disagreement;
   - proposed regression;
   - mutation operator proposal;
   - stale artifact or reproduction failure;
   - assurance report issue.
6. Prepare public-facing status language before making the repository public.

Exit criteria:

- A community member can understand the project goal, standards, current state,
  and how to contribute without private context.
- Contributions can be accepted or rejected against the constitution rather
  than personal preference.

## Near-Term Task Queue

These are the next concrete tasks, in order:

1. Resolve coverage artifact storage and add exact identity fields to the
   compact tracked metadata needed to reproduce or validate the current local
   coverage set.
2. Run `nanoda-0002` and `nanoda-0004` through
   `scripts/run-mutant-scheduled`.
3. Add deterministic, syntax-aware semantic mutation generation and automatic
   registration for an initial bounded `nanoda` mutation batch.
4. Run the generated batch mechanically using coverage schedules, with periodic
   full-corpus audits of the coverage exclusion invariant.
5. Mechanically confirm the expected semantics of the `nanoda-0003` witness
   with compatible validators or a reference path.
6. If confirmation succeeds, convert the witness into a controlled
   augmented-corpus test.
7. Rerun `nanoda-0003` against the augmented corpus if one is produced, and
   record the measured result.
8. Update `docs/RESEARCH_STATUS.md` and produce the first local assurance
   snapshot draft.
9. Commit and push after each coherent artifact-producing step.

## Decision Rules

Prefer tasks that improve:

- reproducibility;
- scoped evidence;
- current-state visibility;
- shared corpus quality;
- cross-validator confidence;
- unresolved-state clarity.

Deprioritize tasks that:

- chase a metric without improving assurance;
- add architecture before the current loop works;
- require human judgment in the normal path;
- produce results that cannot be reproduced;
- obscure uncertainty;
- only improve one implementation without explaining ecosystem relevance.

## Open Planning Questions

These questions should remain explicit until answered by evidence:

1. Which validators are mature and compatible enough for early
   cross-validator confirmation?
2. What outcome should be recorded when a baseline validator panics on a test
   that is semantically expected to reject?
3. Which semantic subsystems need the first structured mutation batches?
4. What artifact storage policy should preserve reproducibility without
   committing multi-gigabyte generated files?
5. What is the smallest useful public assurance snapshot?
6. Which parts of Lean Kernel Arena should remain upstream dependencies, and
   which project-specific executors should live here?
