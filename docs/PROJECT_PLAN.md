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
3. A process for discovering validation gaps and turning confirmed gaps into
   shared regression tests.
4. Evidence about whether generated tests improve the ecosystem generally,
   rather than only one validator implementation.
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

## Current Baseline

Current durable state:

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
- Coverage collection exists in script form, but the current coverage artifact
  set is incomplete and must not yet be treated as an assurance input.

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

Goal: demonstrate one closed mechanical loop for `nanoda`.

This is the first critical project milestone. It should prove that the project
can move from a modeled semantic fault to a confirmed corpus improvement.

Tasks:

1. Complete full per-test coverage for `nanoda` over the materialized Arena
   corpus.
2. Produce durable coverage artifacts:
   - `coverage.jsonl`
   - `manifest.json`
   - `test-to-lines.json`
   - `line-to-tests.json`
3. Validate coverage artifact integrity:
   - exact test inventory matches baseline outcomes;
   - instrumented outcomes match uninstrumented baseline outcomes;
   - source digest matches the validator source used for scheduling;
   - coverage records are complete for every selected test.
4. Use coverage to schedule known mutants and compare coverage-guided results
   against prior full-corpus results.
5. Run `nanoda-0004` through the mutation loop.
6. Promote the `nanoda-0003` witness to a candidate regression only after its
   expected semantics are mechanically confirmed.
7. Add confirmed candidate regressions to a controlled augmented corpus.
8. Rerun the source mutant and verify the augmented corpus kills it.
9. Verify baseline validator behavior remains consistent on the augmented
   corpus.
10. Record all outputs as durable artifacts.

Exit criteria:

- At least one semantic survivor is converted into a confirmed regression
  candidate.
- The augmented corpus kills the source mutant that originally survived.
- The expected outcome of the generated test is mechanically established.
- Coverage-guided execution is shown to preserve mutation conclusions for
  tested mutants, or its limitations are documented.

Primary artifact:

```text
semantic mutant -> existing corpus gap -> generated witness ->
confirmed regression -> augmented corpus -> source mutant killed
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

Goal: build a meaningful semantic fault model beyond a few manual mutants.

Tasks:

1. Convert current manual mutation specs into a more structured mutation
   catalog.
2. Define mutation operator families by semantic subsystem.
3. Generate a modest batch of compiling semantic mutants for `nanoda`.
4. Record deterministic mutant identities and provenance.
5. Classify build failures separately from semantic survivors.
6. Track mutation score by subsystem and operator.
7. Avoid arbitrary source churn that does not model plausible semantic faults.
8. Keep the initial batch small enough that survivor analysis remains feasible.

Exit criteria:

- The project has a documented semantic mutation model with deterministic
  mutant identities.
- At least one subsystem has enough mutants to produce useful subsystem-level
  metrics.
- Survivors are classified into durable states rather than treated as generic
  failures.

## Milestone 4: Automate Witness Search and Minimization

Goal: reduce manual effort in turning meaningful survivors into evidence.

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

- At least one survivor witness is generated and minimized by an automated
  process.
- The generated witness has durable metadata sufficient to reproduce the
  search or audit its result.
- Failures to find witnesses produce useful unresolved-state artifacts.

## Milestone 5: Cross-Validator Confirmation

Goal: ensure generated tests improve shared Lean validation rather than only
one implementation.

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

- At least one generated witness has cross-validator confirmation.
- Any disagreement is preserved as a durable unresolved artifact.
- Regression candidates include expected outcome evidence, not just a source
  mutant distinction.

## Milestone 6: First Generalization Experiment

Goal: show that generated tests can transfer across independent validators.

Tasks:

1. Select a second validator with enough overlap to support a meaningful
   experiment.
2. Introduce an analogous semantic fault independently into that validator.
3. Generate a test without using the held-out validator's mutant results.
4. Freeze the generated corpus.
5. Evaluate whether the generated corpus detects the independently introduced
   fault.
6. Record whether the result supports cross-implementation generalization.

Exit criteria:

- A test generated from one validator detects an independently introduced
  analogous semantic fault in another validator, or the failed attempt is
  documented with enough detail to guide the next strategy change.

## Milestone 7: Rotating Held-Out Evaluation

Goal: measure whether corpus improvements generalize across validator
implementations.

Tasks:

1. Add support for multiple validators and validator-specific mutation models.
2. Implement leave-one-validator-out evaluation.
3. For each fold:
   - hold out one validator;
   - generate or select augmented tests without using that validator's mutants;
   - evaluate original corpus against held-out mutants;
   - evaluate augmented corpus against held-out mutants;
   - compute score improvement.
4. Report per-validator improvement, regressions, unresolved states, and costs.
5. Keep fold data separate so held-out results cannot influence generation.

Exit criteria:

- The project can produce a rotating held-out report.
- The report distinguishes general semantic improvement from
  implementation-specific overfitting.

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

1. Add artifact identity fields to existing result metadata where practical.
2. Finish the interrupted `nanoda` coverage collection and produce complete
   coverage indexes.
3. Validate coverage completeness against the 197-test materialized corpus.
4. Run coverage scheduling for `nanoda-0001`, `nanoda-0002`, and `nanoda-0003`
   and compare conclusions with prior full-corpus results.
5. Run `nanoda-0004`.
6. Mechanically confirm the expected semantics of the `nanoda-0003` witness
   with compatible validators or a reference path.
7. Convert the confirmed witness into a controlled augmented-corpus test.
8. Rerun `nanoda-0003` against the augmented corpus and record the closed-loop
   result.
9. Update `docs/RESEARCH_STATUS.md` and produce the first local assurance
   snapshot draft.
10. Commit and push after each coherent artifact-producing step.

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
