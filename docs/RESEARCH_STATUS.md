# Research Status

Last updated: 2026-08-23

## Attempted

- Created the initial durable project scaffold.
- Identified upstream Lean Kernel Arena as `https://github.com/leanprover/lean-kernel-arena`.
- Cloned Lean Kernel Arena at `external/lean-kernel-arena`.
- Created Arena Python 3.13 virtualenv at `.venv-arena` and installed Arena
  Python dependencies.
- Built `nanoda` through Arena and validated the smoke run:
  `scripts/run-arena --checker nanoda --test constlevels`.
- Defined the normalized outcome vocabulary and manually controlled mutant
  registry format.
- Added a conservative mutation report command that computes current counters
  from repository state.
- Added a first line-oriented minimizer that preserves an external mechanical
  distinction predicate.
- Registered and tested first nanoda mutant `nanoda-0001`.
- Built the complete Arena test corpus with:
  `../../.venv-arena/bin/python ./lka.py build-test --skip-declined-by nanoda`
  from `external/lean-kernel-arena`.
- Ran both mutated and baseline nanoda over the materialized corpus and compared
  normalized outcomes.
- Added `scripts/run-mutant`, a one-mutant orchestrator that applies a mutation
  spec, builds baseline and mutant checker states, runs Arena, normalizes
  outcomes, compares, updates registry status, and restores baseline source.
- Added the first exact replacement mutation spec at
  `mutations/nanoda-0001.json`.
- Validated the automated loop with:
  `scripts/run-mutant nanoda-0001 --test tutorial/012_nonPropThm`.
- Hardened normalization to reject unknown statuses, missing or duplicate test
  names, and full-run inventories that differ from the materialized corpus.
- Registered and ran semantic mutant `nanoda-0002`, which skips the
  definitional-equality check between a definition body's inferred type and its
  declared type.
- Registered narrow candidates `nanoda-0003` and `nanoda-0004`, targeting
  constant universe-argument ownership and lambda binder validation.
- Ran `nanoda-0003` over the full corpus and found the first meaningful
  survivor: zero normalized differences across all 197 materialized tests.
- Generated a nine-line NDJSON witness outside the current corpus that baseline
  nanoda rejects and `nanoda-0003` accepts, proving the survivor is not an
  equivalent mutation.
- Added a native LLVM 22 per-test Rust coverage collector with resumable,
  source-digest-checked collection state and mechanical baseline-outcome
  validation.
- Collected coverage for all 197 materialized nanoda tests across 20 Rust source
  files and built forward/reverse indexes for 3,884 covered source locations.
- Added `scripts/schedule-mutant` and `scripts/run-mutant-scheduled` for
  fastest-first coverage-guided mutation execution with early kill and baseline
  restoration.
- Verified the scheduler reproduces `nanoda-0001`'s kill after executing 7 of
  67 covering tests, and exhausts all 120 covering tests for surviving
  `nanoda-0003`.
- Reproduced `nanoda-0002`'s kill after 8 of 167 covering tests and classified
  `nanoda-0004` as survived without witness after all 112 covering tests.
- Added a tracked coverage identity snapshot binding all local coverage files,
  197 corpus inputs totaling 9,506,646,641 bytes, baseline outcomes, checker
  source, Arena revision, configuration, and producer scripts by SHA-256.
- Added a `syn`-based Rust mutation parser plus deterministic generation,
  registration, isolated build validation, exact occurrence replacement, and
  resumable coverage-guided batch execution.
- Completed active batch `nanoda-syntax-0003`: 12 of 12 mutants built, 1 was
  killed, and 11 survived after executing 611 of 685 scheduled test-mutant
  pairs in 5,356.7 seconds.
- Confirmed the `nanoda-0003` witness with Arena's unmodified official Lean
  4.33 checker: the witness was rejected for an undefined universe parameter,
  while the declared-universe positive control was accepted.
- Promoted that witness into the controlled augmented corpus and verified that
  baseline nanoda rejects it while `nanoda-0003` accepts it.
- Produced `results/assurance/milestone-1.json`; all eight Milestone 1 checks
  pass.
- Defined a versioned artifact graph schema and attested 29 nodes spanning
  repositories, validators, toolchains, configuration, scripts, corpora,
  mutation definitions, coverage, runs, comparisons, witnesses,
  classifications, and reports.
- Added recursive current/stale/missing evaluation, historical and superseded
  lifecycle states, dependency-digest explanations, and report gates that
  reject stale inputs.
- Mechanically simulated validator-source, corpus, mutation-model, and
  expected-semantics changes; every required descendant became stale.
- Produced `results/assurance/milestone-2.json`; all nine Milestone 2 checks
  pass.
- Added a schema-validated mutation catalog binding all four manual specs and
  defining validation-elision, predicate-negation, relational-boundary, and
  equality-discrimination operator families across semantic subsystems.
- Extended the `syn` mutator to discover Boolean guard and comparison-boundary
  mutations with function, source-column, semantic rationale, and deterministic
  content identity.
- Classified all 480 discovered candidates in active batch
  `nanoda-semantic-0001`: 12 compiling semantic mutants, 0 build failures, 29
  duplicates, 115 unsupported sites, and 324 rejected non-semantic changes.
- Executed the 12-mutant bounded batch from 23:36:11Z to 00:26:56Z: 6 were
  killed and 6 exhausted their covering schedules and survived without
  witnesses.
- Added mutation score strata by operator, operator family, and subsystem with
  a three-mutant sufficiency threshold. Under-sampled strata retain counts and
  report `INSUFFICIENT_SAMPLE` instead of a score.
- Full-corpus audited generated killed mutant `nanoda-gen-34b1a4c65d39` and
  survivor `nanoda-gen-4238224977cc`; both coverage-guided conclusions matched
  after complete 197-test runs.
- Produced `results/assurance/milestone-3.json`; all 13 Milestone 3 checks pass.

## Command Log

```sh
ps aux | rg -i 'cargo|rustc|lean-kernel-arena/_build/checkers/nanoda'
cd external/lean-kernel-arena/_build/checkers/nanoda/src
cargo build --release
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier/external/lean-kernel-arena
../../.venv-arena/bin/python ./lka.py run --checker nanoda --test constlevels
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/normalize-arena-results --checker nanoda --output results/mutants/nanoda-0001/outcomes-smoke.jsonl
scripts/compare results/baseline/outcomes/nanoda-smoke.jsonl results/mutants/nanoda-0001/outcomes-smoke.jsonl --mutant-id nanoda-0001 --output results/mutants/nanoda-0001/comparison-smoke.json
cd external/lean-kernel-arena
../../.venv-arena/bin/python ./lka.py build-test --skip-declined-by nanoda
../../.venv-arena/bin/python ./lka.py run --checker nanoda
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/normalize-arena-results --checker nanoda --output results/mutants/nanoda-0001/outcomes-full.jsonl
cd external/lean-kernel-arena/_build/checkers/nanoda/src
cargo build --release
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier/external/lean-kernel-arena
../../.venv-arena/bin/python ./lka.py run --checker nanoda
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/normalize-arena-results --checker nanoda --output results/baseline/outcomes/nanoda-full.jsonl
scripts/compare results/baseline/outcomes/nanoda-full.jsonl results/mutants/nanoda-0001/outcomes-full.jsonl --mutant-id nanoda-0001 --baseline-id nanoda-baseline-full --candidate-id nanoda-0001-full --output results/mutants/nanoda-0001/comparison.json
scripts/mutate status nanoda-0001 KILLED MEANINGFUL_SEMANTIC "Killed by full Arena corpus: tutorial/012_nonPropThm changed REJECT to ACCEPT after theorem Prop validation was skipped"
scripts/report
scripts/run-mutant nanoda-0001 --test tutorial/012_nonPropThm
scripts/mutate register nanoda-0002 nanoda src/tc.rs 92 SKIP_VALIDATION definition-body-typecheck "Disabled definitional equality between inferred definition body type and declared type in check_declar"
scripts/run-mutant nanoda-0002 --reuse-baseline
scripts/report
scripts/mutate register nanoda-0003 nanoda src/tc.rs 191 SKIP_VALIDATION universes "Disabled validation that universe levels supplied to referenced constants are declared by the current declaration"
scripts/mutate register nanoda-0004 nanoda src/tc.rs 597 SKIP_VALIDATION declaration-validation "Disabled sort well-formedness validation for lambda binder types during checked inference"
scripts/run-mutant nanoda-0003 --reuse-baseline
cd external/lean-kernel-arena/_build/checkers/nanoda/src
target/release/nanoda_bin config.json < /Users/danphifer/Documents/ChatGPT/LeanVerifier/corpus/generated/nanoda-0003-undeclared-const-universe.ndjson
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/mutate status nanoda-0003 SURVIVED MEANINGFUL_SEMANTIC "Survived all 197 current Arena tests with zero normalized differences; generated witness is rejected by baseline and accepted by mutant"
scripts/report
scripts/collect-coverage --reuse-build --resume --timeout 7200 --checker-threads 1
scripts/reindex-coverage --append-from /tmp/nanoda-coverage-bogus1/coverage.jsonl
scripts/schedule-mutant nanoda-0001 --output results/mutants/nanoda-0001/schedule.json
scripts/schedule-mutant nanoda-0002 --output results/mutants/nanoda-0002/schedule.json
scripts/schedule-mutant nanoda-0003 --output results/mutants/nanoda-0003/schedule.json
scripts/schedule-mutant nanoda-0004 --output results/mutants/nanoda-0004/schedule.json
scripts/run-mutant-scheduled nanoda-0001
scripts/run-mutant-scheduled nanoda-0003
scripts/run-mutant-scheduled nanoda-0002
scripts/run-mutant-scheduled nanoda-0004
scripts/snapshot-coverage
scripts/snapshot-coverage --verify
scripts/generate-mutations --limit 12 --batch-id nanoda-syntax-0003 --write --register
scripts/validate-mutation-batch nanoda-syntax-0003
scripts/run-mutation-batch nanoda-syntax-0003
cd external/lean-kernel-arena
../../.venv-arena/bin/python ./lka.py build-checker official
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/confirm-witness nanoda-0003-undeclared-const-universe --checker official --control corpus/controls/nanoda-0003-declared-const-universe.ndjson
scripts/run-mutant-input nanoda-0003 corpus/generated/nanoda-0003-undeclared-const-universe.ndjson --output results/mutants/nanoda-0003/augmented-comparison.json
scripts/assurance-snapshot
scripts/report --output results/assurance/milestone-1-report.json
scripts/build-artifact-graph
scripts/artifact-status --require-current --output results/artifacts/status.json
.venv-arena/bin/python -c 'import json, jsonschema; from pathlib import Path; jsonschema.Draft202012Validator(json.loads(Path("schemas/artifact-graph.schema.json").read_text()), format_checker=jsonschema.FormatChecker()).validate(json.loads(Path("results/artifacts/graph.json").read_text()))'
python3 -m unittest discover -s tests -p 'test_*.py' -v
scripts/milestone-2-assurance
scripts/artifact-status --simulate-change validator:nanoda
scripts/artifact-status --simulate-missing corpus:arena-materialized
scripts/generate-mutations --limit 12 --batch-id nanoda-semantic-0001 --write --register
scripts/validate-mutation-batch nanoda-semantic-0001
scripts/run-mutation-batch nanoda-semantic-0001
scripts/report --allow-stale-artifacts --output results/assurance/milestone-3-report.json
scripts/audit-coverage-guidance nanoda-gen-34b1a4c65d39 nanoda-gen-4238224977cc
scripts/generate-mutations --limit 12 --batch-id nanoda-semantic-0001 --write --refresh
.venv-arena/bin/python -c 'import json,jsonschema; from pathlib import Path; jsonschema.Draft202012Validator(json.loads(Path("schemas/mutation-catalog.schema.json").read_text())).validate(json.loads(Path("mutation-model/catalog.json").read_text()))'
scripts/milestone-3-assurance --allow-stale-artifacts
scripts/build-artifact-graph
scripts/artifact-status --require-current --output results/artifacts/status.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
scripts/milestone-3-assurance
```

Notes:

- The first non-escalated full corpus build failed because sandboxed commands
  cannot resolve GitHub hosts. Retrying the same Arena build with approved
  network escalation fixed this and produced `57 succeeded, 0 failed`.
- The built test corpus currently occupies about 24 GB under
  `external/lean-kernel-arena/_build/tests`.
- The nanoda source checkout is restored to baseline after the comparison; the
  mutant is preserved in the registry and result artifacts.
- `scripts/run-mutant` clears stale Arena `_results/<checker>_*.json` before
  each side of a run. The normalized full-run artifacts remain in `results/`,
  but raw Arena JSON in `external/lean-kernel-arena/_results` is intentionally
  treated as scratch space.
- The materialized corpus contains 197 unique `*.stats.json` test identities.
  The `nanoda-0002` full run emitted 197 unique raw and normalized results, and
  the new exact-inventory check confirmed the identity sets match. The earlier
  note that an Arena summary reported 198 was historical and is not a current
  dropped-record condition.
- Per-test coverage is stored under `results/coverage/nanoda/` and occupies
  about 26 MB. Valid instrumented checker time was 5,114 seconds (85.2 minutes):
  mathlib 3,949.5 seconds, cslib 639.7 seconds, cedar 220.2 seconds, and std
  161.3 seconds. Single-thread checking was fastest because multi-threaded
  coverage counters caused severe contention.
- The reverse coverage index selected 67 tests for `nanoda-0001`, 167 for
  `nanoda-0002`, 120 for `nanoda-0003`, and 112 for `nanoda-0004`. It included
  all 20 historical killing relationships across the first two mutants.
- Coverage-guided `nanoda-0001` took about 22 seconds including two builds and
  stopped at `tutorial/012_nonPropThm`; the prior full loop took about nine
  minutes. Coverage-guided `nanoda-0003` took about 489 seconds because its
  central line is covered by every large library export.
- The first generated candidate set was superseded because AST-discovered
  `assert!` statements included configuration guards and internal invariants.
  A second partial batch established one survivor before being narrowed again.
  These attempts remain classified in durable manifests instead of being
  omitted from the record.
- Generated source replacements originally exposed a restoration bug because
  `if false { original }` still contains the original text. All source-state
  transitions now check the full mutant first, repeated statements carry an
  exact occurrence index, and batch validation proves the baseline source
  digest before and after isolated builds.
- The active 12-mutant batch ran from 21:31:34Z to 23:00:51Z. The only kill was
  `nanoda-gen-1c536a57344e`; `proj-of-prop` changed from `REJECT` to `ACCEPT`
  after 73 of 147 covering tests. The other 11 mutants exhausted their full
  schedules and are classified `SURVIVED_WITHOUT_WITNESS`.

## Current Metrics

```yaml
mutation_score: 0.9
mutation_score_scope: explicit MEANINGFUL_SEMANTIC classifications only
modeled_mutation_score: 0.3103448275862069
modeled_mutation_score_denominator: 29
generated_mutants: 42
evaluated_mutants: 29
killed_mutants: 9
surviving_mutants: 20
build_failed_mutants: 0
superseded_mutants: 13
unevaluated_mutants: 0
classified_equivalent: 0
classified_unreachable: 0
classified_performance_only: 0
classified_non_semantic: 10
meaningful_survivors: 1
survived_without_witness: 19
unknown_equivalence: 3
witnesses_found: 1
minimized_witnesses: 0
arena_regression_candidates: 1
artifact_nodes: 35
current_artifacts: 28
historical_artifacts: 3
superseded_artifacts: 4
milestone_2_checks_passing: 9
milestone_3_checks_passing: 13
```

## First Mutation Result

- Mutant: `nanoda-0001`
- Operator: `SKIP_VALIDATION`
- Subsystem: `declaration-validation`
- Source: `src/tc.rs:175`
- Mutation: theorem `Prop` validation in `check_declar_info` was weakened from
  `if !self.ctx.is_zero(sort)` to `if false && !self.ctx.is_zero(sort)`.
- Smoke comparison: survived `constlevels`
  (`results/mutants/nanoda-0001/comparison-smoke.json`).
- Full corpus comparison: killed by one normalized outcome difference
  (`results/mutants/nanoda-0001/comparison.json`).
- Distinguishing test: `tutorial/012_nonPropThm`.
- Mechanical difference: baseline `REJECT`, mutant `ACCEPT`.
- Full comparison size: 197 normalized result records.
- Automated scoped rerun: killed again by `tutorial/012_nonPropThm`, with
  artifacts at
  `results/mutants/nanoda-0001/comparison-tutorial_012_nonPropThm.json`.

## Second Mutation Result

- Mutant: `nanoda-0002`
- Operator: `SKIP_VALIDATION`
- Subsystem: `definition-body-typecheck`
- Source: `src/tc.rs:92`
- Mutation: skipped `assert_def_eq(inferred_type, d.info().ty)` after inferring
  the value of a definition, theorem, or opaque declaration.
- Full corpus comparison: killed by 19 normalized outcome differences
  (`results/mutants/nanoda-0002/comparison.json`).
- All 19 differences were baseline `REJECT` to mutant `ACCEPT`; the first was
  `bogus1`, and the direct tutorial witness was `tutorial/002_badDef`.
- Both sides contained the same 197 test identities; no comparison difference
  came from a missing result.

## First Meaningful Survivor

- Mutant: `nanoda-0003`
- Operator: `SKIP_VALIDATION`
- Subsystem: `universes`
- Source: `src/tc.rs:191`
- Mutation: skipped the check that every universe level supplied to a referenced
  constant is declared in the current declaration's `levelParams`.
- Full corpus result: survived with zero differences across the exact same 197
  test identities (`results/mutants/nanoda-0003/comparison.json`).
- Semantic witness:
  `corpus/generated/nanoda-0003-undeclared-const-universe.ndjson`.
- Witness behavior: restored baseline rejects with exit 101 at the mutated
  assertion; `nanoda-0003` accepts with exit 0.
- The witness declares `unused.{u} : Prop`, then defines a declaration with no
  universe parameters whose value references `unused.{u}`. The undeclared level
  does not appear in the resulting type, so removing the ownership check admits
  the artifact.
- Durable records:
  `results/survivors/inventory.jsonl` and
  `results/witnesses/nanoda-0003-undeclared-const-universe/metadata.json`.

## Unresolved Problems

- Six mutants in active batch `nanoda-semantic-0001`, eleven mutants in the
  superseded first batch, one earlier generated mutant, and `nanoda-0004`
  survived without witnesses. They are not claimed equivalent.
- Coverage payloads remain ignored local files; their complete identities and
  corpus inputs are tracked and mechanically verified, but remote payload
  storage is not yet implemented.
- The current four operator families remain a narrow source-level semantic
  model; match-arm, substitution/lifting, and richer reduction mutations remain
  future work.
- Large corpus files are expensive: `mathlib.ndjson` is about 5.2 GB,
  `cslib.ndjson` about 2.0 GB, and `cedar.ndjson` about 790 MB.
- The repository revision recorded by an attestation becomes historical after
  the attestation commit. Current claims depend on content digests and the exact
  upstream Arena revision, avoiding a self-referential commit hash while
  preserving the producing repository revision for audit.

## Next Concrete Experiment

1. Begin mechanical witness search for the two active universe-boundary
   survivors and the six superseded quotient-validation survivors.
2. Add structure-aware NDJSON transformations and automatic witness
   minimization.
3. Prepare a second independent validator for direct compatibility and
   confirmation runs.
