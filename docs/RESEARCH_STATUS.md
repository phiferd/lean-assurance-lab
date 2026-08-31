# Research Status

Last updated: 2026-08-31

## How Status Is Tracked

This document is the canonical human-readable research tracker:

- `Attempted` is the append-only record of completed experiments and durable
  engineering work.
- `Research Frontier` is the ranked queue. Only its `Active` subsection defines
  what should be investigated next.
- `Waiting` records work blocked on upstream adjudication without allowing it to
  displace executable local work.
- `Future Directions` preserves promising ideas that have not yet outranked the
  active queue.
- `Unresolved Problems` records limitations and open claims, not task priority.

`docs/PUBLIC_STATUS.md` remains a generated assurance snapshot rather than a
planning document. GitHub Issues coordinate bounded, claimable work beneath the
Active frontier and track upstream conversations; an Issue does not activate a
research direction or establish project truth. This file retains the project's
own priorities and completion conditions.

Research activity is not progress merely because it produces another document,
taxonomy, or abstraction. Every Active frontier item must have a falsifiable
completion condition and terminate in at least one of:

- executable evidence;
- a characterized boundary;
- a regression or corpus contribution;
- an upstream action recommendation;
- a demonstrated negative result; or
- an explicitly bounded unresolved result.

Keep the number of top-level Active research themes small. The normal target is
one or two coherent frontier themes, with parallel work occurring through
bounded GitHub Issues beneath them rather than by activating many unrelated
research directions.

## Attempted

- Added a disk-backed `scripts/run-campaign` supervisor for already-generated
  bounded mutation batches. It binds the selected mutants and source inputs,
  records phase-level interruptions and logs, adopts pre-existing completed
  build/execution evidence, and resumes without conversational state. Build
  validation now persists each mutant result, matching the existing
  per-mutant execution checkpoint. The unattended loop is deliberately limited
  to build validation, coverage-guided execution, and assurance refresh;
  witness design, semantic classification, and external publication remain
  human or model-review work.
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
  files and built schema-2 forward/reverse indexes for 3,451 canonical covered
  source locations. The lower count is not a coverage regression: schema 2
  uses canonical executable regions from `llvm-cov export`, while schema 1
  counted rendered source lines from `llvm-cov show`.
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
- Replaced the witness-planning stub with direct baseline/mutant execution,
  deterministic subsystem templates, structure-aware NDJSON transformations,
  per-attempt JSONL records, content-bound inputs, and cost accounting.
- Mechanically rediscovered the confirmed `nanoda-0003` universe-ownership
  witness on attempt 1 and automatically minimized it from 522 to 512 bytes
  over 63 additional predicate checks. All 9 records and exact export metadata
  are preserved; both artifacts retain baseline `REJECT` versus mutant `ACCEPT`.
- Executed 60 of 143 deterministic universe-focused candidates against active
  survivor `nanoda-gen-ca8565ff512e`. No candidate distinguished baseline from
  mutant, so the bounded result is durably classified `UNRESOLVED` with reason
  `ATTEMPT_BUDGET_EXHAUSTED`; equivalence is not claimed.
- Added explicit states for witness found, minimized witness found, no witness,
  ambiguous semantics, and reference-checker disagreement.
- Produced `results/assurance/milestone-4.json`; all 11 Milestone 4 checks pass.
- Built unmodified Kiota at Arena-pinned revision
  `58e8636cfb51cf9c3bf3de7455a0e3c6ab68e87a` and content-bound its clean source,
  binary, Arena definition, and implementation family alongside official Lean
  4.33.
- Added validator-neutral direct execution, exact export compatibility rules,
  positive-control checks, raw process evidence, parse behavior, and explicit
  normalized states for accept, reject, decline, crash, timeout, parse error,
  and unknown behavior.
- Established exact expected `REJECT` outcomes for the original and minimized
  `nanoda-0003` witnesses using official Lean plus the accepted declared-universe
  control. Evidence is bound to each artifact SHA-256 without majority voting.
- Cross-validation found durable semantic disagreements for both artifacts:
  official Lean rejects and Kiota accepts. Both remain regression candidates
  with mechanically established expected outcomes and exceptional unresolved
  cross-validator status.
- A malformed-object probe found a separate parse-behavior disagreement:
  official Lean exits successfully after accepting zero declarations, while
  Kiota reports `PARSE_ERROR`.
- Produced `results/assurance/milestone-5.json`; all 15 Milestone 5 checks pass.
- Declared the first held-out transfer experiment before mutation execution:
  source model `nanoda-0001`, held-out validator Kiota, and an independent
  `SKIP_VALIDATION` mutation at Kiota `src/tc.rs:1172-1174`.
- Generated a renamed 438-byte non-`Prop` theorem candidate and a definition-form
  positive control from Arena's `tutorial/012_nonPropThm` seed. Nanoda baseline
  rejects while `nanoda-0001` accepts; both accept the control.
- Official Lean established exact expected rejection for the generated
  candidate and accepted the control before the held-out mutation was applied.
- Froze the corpus and generation boundary at manifest SHA-256
  `5f4776240cd8db4265d27e1f5bc21dbe474368c099a7de2d027727f59236a555`.
  The manifest excludes Kiota mutant outcomes and logs from generation inputs.
- Evaluated the exact frozen SHA against baseline and independently mutated
  Kiota. The candidate changed from `REJECT` to `ACCEPT`; the control remained
  `ACCEPT` in both states. Kiota source was restored to its exact baseline hash.
- Classified the first generalization experiment `POSITIVE_TRANSFER`.
- Produced `results/assurance/milestone-6.json`; all 16 Milestone 6 checks pass.
- Added pinned Lean4Lean at revision
  `ecb3b6661c14f8147be1069b126c629114baf4a8` as a third implementation
  family and defined an analogous Kiota/Lean4Lean fault model for let-bound
  value/type compatibility.
- Froze the fresh Lean4Lean fold before applying or executing its held-out
  mutant. Kiota baseline rejected the 476-byte malformed-let candidate while
  its source mutant accepted it; both accepted the 599-byte control. Official
  Lean independently established candidate `REJECT` and control `ACCEPT`.
- Exhaustively evaluated baseline and mutated Lean4Lean over all 197 original
  corpus tests. The original corpus killed 0 of 1 modeled mutants; the frozen
  candidate changed Lean4Lean from `REJECT` to `ACCEPT`, increasing the
  augmented score to 1 of 1. The control remained `ACCEPT` in both states and
  the held-out source was restored to its exact baseline hash.
- Recast the Milestone 6 Kiota experiment as a separate rotating fold. Its
  original corpus already killed the modeled mutant at
  `tutorial/012_nonPropThm`, so its score remained 1 of 1 after augmentation and
  the fold is `NEUTRAL`.
- Produced the two-fold rotating report with aggregate original score 0.5,
  augmented score 1.0, change +0.5, one `POSITIVE` fold, one `NEUTRAL` fold,
  no regressions, and no unresolved tests. Total measured cost was 400 checker
  runs and 6,918.1547 checker-seconds.
- Produced `results/assurance/milestone-7.json`; all 22 Milestone 7 checks pass.
  The aggregate classification is `MIXED_WITH_POSITIVE_GAIN`. All faults in
  these folds were deliberately injected mutants, not bugs found in the
  unmodified validators.
- Defined and schema-validated a versioned assurance policy and current
  snapshot. The snapshot covers three validator identities, the exact 197-test
  corpus, 29 modeled semantic mutants, subsystem scores, witness synthesis,
  generated regressions, disagreements, held-out results, coverage, and cost.
- The current assurance gate reports `FAIL` with four of five hard checks
  passing. Its sole failure is `semantic_checker_disagreements`: the two
  official Lean/Kiota semantic disagreements exceed the configured maximum of
  zero. This is preserved as the measured result rather than converted into a
  favorable milestone claim.
- Recorded 859 checker runs and 12,034.0801 checker-seconds across the
  non-overlapping measured components, with active mutation-batch and build
  wall time labeled separately. Mutation and coverage thresholds remain
  configurable contextual trends rather than enabled gates.
- Produced `results/assurance/milestone-8.json`; all 24 Milestone 8
  implementation checks pass.
- Defined seven machine-readable contribution paths with common and
  type-specific metadata, content-bound evidence validation, constitution-
  aligned guidance, a pull request checklist, and five issue forms.
- Generated `docs/PUBLIC_STATUS.md` from the exact current snapshot SHA-256,
  clearly separating injected faults from potential bugs and preserving the
  unresolved hard-gate failure.
- Produced `results/assurance/milestone-9.json`; all 25 Milestone 9 checks pass.
- Froze a 152-test Arena corpus at pre-regression revision `dd345f6`, affected
  official Lean 4.29 and pre-fix nanoda `ddfac2b`, fixed/independent checker
  binaries, two fault operators, seed `20260824`, and bounded generation inputs
  before any historical checker or disclosed holdout feedback was available.
- Generated an 11,217-byte malformed nested-inductive artifact from the frozen
  operator specification. Affected official Lean accepted it; fixed official
  Lean, Kiota, and Lean4Lean rejected it.
- Invalidated and archived the original projection result after diagnosing an
  absolute LLVM source-path mismatch: 26 projection-bearing historical inputs
  had been incorrectly reported as yielding zero target-covering schedules and
  therefore zero search attempts.
- Froze a coverage-repair amendment, parsed LLVM export data by relative source
  suffix, and found 11 target-covering historical inputs. The repaired stage
  fails closed if source mapping or coverage selection is empty.
- Froze a second amendment after the restored schedule exposed eager,
  effectively unbounded payload materialization ahead of the nominal
  64-candidate limit. The replacement applies the same seeded shuffle and
  deduplication order lazily; direct equivalence tests cover full order and
  bounded prefixes.
- Evaluated all 11 covering historical inputs against fixed nanoda and the
  modeled projection mutant, then found a distinction on structured mutation
  attempt 1. After candidate freeze, pre-fix nanoda accepted the candidate while
  fixed nanoda, both official Lean versions, Kiota, and Lean4Lean rejected it.
- Evaluated the disclosed `nested-unused-param` artifact only after the
  candidate freeze. Affected official Lean accepted it; fixed official Lean,
  fixed nanoda, Kiota, and Lean4Lean rejected it, while the pinned pre-fix
  nanoda rejected this reduced artifact.
- Classified the amended experiment `FULL_CLASS_REDISCOVERY` and produced
  `results/collatz-retrospective/assurance.json`; all 36 combined checks and all
  15 repaired-branch checks pass.
- Audited the Nanoda mutation surface: the parser finds 480 syntax candidates,
  127 satisfy the semantic policy, and 121 of those are covered, but the first
  semantic batch selected only 12 candidates in 7 of 37 eligible functions.
- Added `semantic-diversity-v1`, which spreads a bounded batch across subsystem,
  function, and operator family before considering estimated execution cost.
  The resulting 12-mutant `nanoda-semantic-0002` batch spans 12 functions and
  seven reachable subsystems; all mutants built, eight were killed, and four
  exhausted their covering schedules.
- Established three of the four survivors as equivalent at Nanoda's checker
  entrypoint: two remove assertions already guaranteed by `nat_extension`, and
  one changes only proof-irrelevant `Quot.ind` reduction behavior.
- Added inductive-metadata witness generation and found a distinction for the
  fourth survivor on attempt 20 by incrementing an exported inductive
  declaration's `numIndices`. Baseline Nanoda rejects the exact artifact while
  the mutant, official Lean 4.33, and Lean4Lean accept it. This establishes an
  implementation inconsistency; whether the metadata must be authoritative is
  still an open contract question.
- Reproduced that disagreement against current Nanoda master revision
  `05055695879dfebb6628a67da88ceca6cd6b0421`; current Nanoda accepts the
  unchanged positive control and rejects the hash-bound generated artifact.
  The mutant retains the project's designated-reference `REFERENCE_ALIGNED`
  classification and is excluded from both mutation score denominators, while
  the cross-checker contract remains unresolved.
- Rebuilt the current mutation report, three-artifact regression manifest,
  artifact graph, assurance snapshot, and public status. Artifact freshness
  passes; the sole hard-gate failure is now the three unresolved semantic
  checker disagreements.
- Ran a third semantic-diversity batch across 12 additional functions. Eleven
  mutants built, eight were killed, and three survived; the remaining mutation
  failed its isolated build because the original binder-depth operator changed
  an owned integer into a reference.
- Established the surviving constructor-owner assertion as equivalent at the
  checker entry point after a 300-attempt bounded search found no witness and
  source invariants showed that constructor ownership is reconstructed from the
  containing inductive declaration.
- Replaced the malformed binder-depth operator with
  `BINDER_DEPTH_INCREMENT_ZERO` and ran a targeted 12-mutant batch over
  substitution/lifting and bound-variable functions. All 12 built and all 12
  were killed by the existing corpus.
- Expanded the syntax audit to 524 discovered candidates, 185 on the operator
  surface, 131 eligible under the then-current semantic policy, and 125 with
  line-coverage inputs. Every modeled subsystem now has operator surface.
- Investigated all six uncovered candidates. Five belong to Nanoda's explicitly
  dead debug-only `strong_reduce` entry point and are now outside the model. The
  remaining parallel validation mutant was hidden because coverage used one
  thread while execution used four; baseline rejected two exact malformed
  artifacts that the mutant accepted.
- Changed scheduling to retain modeled zero-coverage candidates and run the
  complete baseline corpus as a conservative fallback. The targeted parallel
  batch built and killed its mutant, and the machine-readable resolution is
  `results/investigations/nanoda-uncovered-mutation-sites.json`.
- Triaged universe survivor `nanoda-gen-0bb50147dff2`. A plain-parameter
  hypothesis did not distinguish it, but a source-directed `imax u v` versus
  `imax w v` declaration changed baseline Nanoda from `REJECT` to mutant
  `ACCEPT` on attempt 2.
- Official Lean 4.33, Kiota, and Lean4Lean all reject the exact `IMax` witness
  and accept its structure-matched control. The expected outcome is established
  without disagreement, and the artifact is a confirmed regression candidate.
- Triaged declaration-visibility survivor `nanoda-gen-8317efea2c7d`. A first
  inductive forward-reference candidate showed that the mutant could cross the
  environment cutoff but remained malformed because it lacked recursor
  metadata. A six-record definition self-reference then changed baseline
  Nanoda from `REJECT` to mutant `ACCEPT`; both accept the matched control.
- Official Lean 4.33 and Lean4Lean reject the self-reference, establishing the
  expected `REJECT` outcome with baseline Nanoda. Kiota accepts it. Source
  tracing found that Kiota inserts the definition before checking its body, and
  the four-outcome disagreement reproduces on fetched upstream `main`
  `686063c`. The witness is retained as a regression candidate with unresolved
  cross-validator disagreement rather than majority-voting Kiota away.
- Rechecked the environment-cutoff mutant against current Arena's newly added
  `tutorial/014_selfProof`, materialized from Arena revision `162f4e5`. Baseline
  Nanoda passes the test by rejecting the theorem self-reference, while
  `nanoda-gen-8317efea2c7d` fails the test by accepting it. The machine
  classification is therefore `KILLED`. This is a later corpus improvement and
  does not rewrite the frozen 197-test survival result. The exact export,
  provenance, and restored differential run are under
  `results/investigations/nanoda-env-cutoff-self-reference/`.

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
scripts/verify-portable-coverage
scripts/verify-portable-coverage --verify
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
scripts/generate --mutant-id nanoda-0003 --subsystem universes --random-seed 4103 --max-attempts 20 --max-minimization-checks 200 --expected-outcome REJECT --expected-evidence results/witnesses/nanoda-0003-undeclared-const-universe/confirmation.json --witness-id nanoda-0003-auto-universe
scripts/generate --mutant-id nanoda-gen-ca8565ff512e --subsystem universes --seed-artifact external/lean-kernel-arena/_build/tests/tutorial/good/013_levelComp1.ndjson --seed-artifact external/lean-kernel-arena/_build/tests/tutorial/good/016_levelParams.ndjson --seed-artifact external/lean-kernel-arena/_build/tests/tutorial/good/020_imax1.ndjson --seed-artifact external/lean-kernel-arena/_build/tests/level-imax-leq.ndjson --random-seed 4104 --max-attempts 60 --witness-id nanoda-gen-ca8565ff512e-search-0001
scripts/milestone-4-assurance --allow-stale-artifacts
cd external/lean-kernel-arena
../../.venv-arena/bin/python ./lka.py build-checker kiota
cd /Users/danphifer/Documents/ChatGPT/LeanVerifier
scripts/validator-inventory
scripts/establish-expected-outcome nanoda-0003-original corpus/generated/nanoda-0003-auto-universe.ndjson --control corpus/controls/nanoda-0003-declared-const-universe.ndjson --reference official --rationale 'undefined universe parameter references must be rejected'
scripts/establish-expected-outcome nanoda-0003-minimized corpus/minimized/nanoda-0003-auto-universe-min.ndjson --control corpus/controls/nanoda-0003-declared-const-universe.ndjson --reference official --rationale 'structurally minimized distinguishing artifact must be rejected'
scripts/cross-validate nanoda-0003-original corpus/generated/nanoda-0003-auto-universe.ndjson --control corpus/controls/nanoda-0003-declared-const-universe.ndjson --expected-evidence results/expected-outcomes/nanoda-0003-original.json --checker official --checker kiota
scripts/cross-validate nanoda-0003-minimized corpus/minimized/nanoda-0003-auto-universe-min.ndjson --control corpus/controls/nanoda-0003-declared-const-universe.ndjson --expected-evidence results/expected-outcomes/nanoda-0003-minimized.json --checker official --checker kiota
scripts/cross-validate malformed-object-probe corpus/probes/malformed-object.ndjson --probe-mode --checker official --checker kiota
scripts/build-regression-candidates
scripts/report --allow-stale-artifacts --output results/assurance/milestone-5-report.json
scripts/milestone-5-assurance --allow-stale-artifacts
scripts/freeze-transfer-experiment
scripts/run-transfer-experiment
scripts/report --allow-stale-artifacts --output results/assurance/milestone-6-report.json
scripts/milestone-6-assurance --allow-stale-artifacts
scripts/freeze-rotating-fold
scripts/run-rotating-fold
scripts/evaluate-m6-rotating-fold
scripts/build-rotating-heldout-report
scripts/report --allow-stale-artifacts --output results/assurance/milestone-7-report.json
scripts/milestone-7-assurance --allow-stale-artifacts
scripts/build-artifact-graph
scripts/artifact-status --require-current --output results/artifacts/status.json
scripts/milestone-7-assurance
scripts/current-assurance-snapshot
scripts/milestone-8-assurance --allow-stale-artifacts
scripts/render-public-status
scripts/validate-contribution --check-catalog
scripts/milestone-9-assurance --allow-stale-artifacts
scripts/build-artifact-graph
scripts/artifact-status --require-current --output results/artifacts/status.json
scripts/milestone-8-assurance
scripts/milestone-9-assurance
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
mutation_score: 0.9375
mutation_score_scope: explicit MEANINGFUL_SEMANTIC classifications only
modeled_mutation_score: 0.9375
modeled_mutation_score_denominator: 48
generated_mutants: 79
evaluated_mutants: 65
killed_mutants: 49
surviving_mutants: 16
build_failed_mutants: 1
superseded_mutants: 13
unevaluated_mutants: 0
classified_equivalent: 12
classified_reference_aligned: 5
classified_unreachable: 0
classified_performance_only: 0
classified_non_semantic: 10
meaningful_survivors: 3
survived_without_witness: 0
unknown_equivalence: 4
witnesses_found: 4
minimized_witnesses: 3
witness_searches_without_result: 2
confirmed_witness_semantics: 3
ambiguous_witness_semantics: 0
witness_checker_disagreements: 1
generated_regression_candidates: 23
artifact_nodes: 162
current_artifacts: 151
historical_artifacts: 7
superseded_artifacts: 4
milestone_2_checks_passing: 9
milestone_3_checks_passing: 13
milestone_4_checks_passing: 11
cross_validators: 3
configured_validators: 3
cross_validation_cases: 24
cross_validation_checker_disagreements: 13
expected_outcomes_established: 23
regression_candidates_with_unresolved_disagreement: 12
milestone_5_checks_passing: 15
transfer_experiments: 1
positive_transfer: 1
neutral_transfer: 0
negative_transfer: 0
inconclusive_transfer: 0
incompatible_transfer: 0
unresolved_transfer: 0
milestone_6_checks_passing: 16
rotating_held_out_folds: 2
rotating_positive_folds: 1
rotating_neutral_folds: 1
rotating_negative_folds: 0
rotating_unresolved_folds: 0
rotating_original_score: 0.5
rotating_augmented_score: 1.0
rotating_score_change: 0.5
rotating_checker_runs: 400
rotating_checker_seconds: 6918.154678831925
milestone_7_checks_passing: 22
current_assurance_status: FAIL
current_hard_gates_passing: 4
current_hard_gates_failing: 1
current_failure_reason: semantic_checker_disagreements
current_semantic_disagreements: 13
current_parse_behavior_disagreements: 1
current_recorded_checker_runs: 925
current_recorded_checker_seconds: 6921.168137743953
milestone_8_checks_passing: 24
contribution_paths: 7
community_issue_forms: 5
milestone_9_checks_passing: 29
action_recommendation_findings: 2
external_actions_pending_human_review: 5
current_upstream_action_preflight_pairs: 8
prepared_external_action_drafts: 5
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

- Twenty evaluated mutants remain classified `SURVIVED_WITHOUT_WITNESS`,
  and four more retain unknown equivalence. They are not claimed equivalent.
- Coverage payloads remain ignored local files; their complete identities and
  corpus inputs are tracked and mechanically verified, but remote payload
  storage is not yet implemented.
- The current operator families remain a narrow source-level semantic model.
  Substitution/lifting and bound-variable handling are now represented and the
  first targeted batch killed all 12 mutants, but match-arm and richer reduction
  mutations remain future work.
- Large corpus files are expensive: `mathlib.ndjson` is about 5.2 GB,
  `cslib.ndjson` about 2.0 GB, and `cedar.ndjson` about 790 MB.
- The repository revision recorded by an attestation becomes historical after
  the attestation commit. Current claims depend on content digests and the exact
  upstream Arena revision, avoiding a self-referential commit hash while
  preserving the producing repository revision for audit.
- The first automated negative witness search was deliberately bounded at 60
  attempts out of 143 generated candidates. It establishes only that those 60
  candidates did not distinguish the checkers; the survivor remains unresolved.
- Kiota accepts both universe-ownership witnesses that official Lean and
  baseline nanoda reject. The minimized case was reproduced against current
  upstream Kiota revision `686063c13b22ce379c05dfe7fc03656655ac60e5` with a
  passing positive control. The schema-validated record is
  `results/investigations/kiota-universe-ownership/upstream-main.json`, and the
  report is `docs/investigations/KIOTA_UNIVERSE_OWNERSHIP.md`. It was submitted
  as [Kiota issue #3](https://github.com/sankalpsthakur/kiota/issues/3). The
  disagreement remains unresolved until upstream adjudication; no majority or
  implementation count is used to decide semantics.
- The minimized witness preserves export metadata but official Lean rejects it
  at `defnInfo invalid`, earlier than the original undefined-universe error.
  Its expected rejection is established, but its explanatory semantics are not
  claimed identical to the original witness.
- Official Lean's direct checker accepts the malformed-object probe as zero
  declarations while Kiota reports a JSON parse error. The probe is diagnostic,
  not a regression candidate.
- The positive transfer result covers one fault family, one small generated
  candidate, and one held-out validator. It demonstrates the protocol and one
  transfer event; it does not establish a general transfer rate.
- The first candidate is structurally derived from an existing Arena test by a
  deterministic rename and control conversion. Later rotating experiments
  should include less direct generators and different semantic subsystems.
- The rotating report contains only two folds and one independently introduced
  mutant per held-out validator. Its positive aggregate change is real for those
  exact models, but it is not a general transfer-rate estimate and cannot rule
  out implementation-specific overfitting.
- The Lean4Lean fold required 6,917.90 checker-seconds because both checker
  states processed every original test and the large `mathlib` export dominated
  the tail. Future folds use `scripts/run-rotating-fold-resumable`, which
  atomically saves every baseline and mutant result, resumes only against exact
  bound inputs and runner hashes, validates the completed corpus prefix, and
  reports abandoned in-flight attempts. The original Milestone 7 runner remains
  unchanged because its content hash is part of the completed evidence.
- The current assurance hard gate remains `FAIL` until the semantic
  official Lean/Kiota disagreements and the current Nanoda `numIndices`
  inconsistency are adjudicated, or the policy changes with an explicit
  rationale. No implementation count is used to collapse these disagreements.
- The Collatz retrospective is operator-informed and post-disclosure. Its
  amended full-class result is evidence only for the frozen bounded protocol,
  not prospective discovery, prevention of the original incident, or a general
  bug-finding rate. The invalid zero-attempt run is preserved for audit. The
  protocol repairs kept the corpus, strategy, generator semantics, seed,
  limits, and feedback boundary fixed, but cannot recreate the original blind
  execution.

## Research Frontier

### Recently Completed

- `F-ASSURANCE-METHODS-LANDSCAPE`: preserved the broader assurance-methods
  landscape in the
  [assurance methods map](research/ASSURANCE_METHODS_MAP.md) with
  primary/official source provenance, explicit project analogues and
  mismatches, non-prioritizing maturity, and evidence-based reconsideration
  conditions. The map is institutional memory; this file remains the planning
  authority.
- `F-RULE-LEVEL-FACTORING-PHASE1`: adversarially factored five existing
  checker-rule boundaries in the
  [Phase 1 factoring experiment](research/RULE_LEVEL_FACTORING_EXPERIMENT.md).
  The result is decision B: normative or normative-candidate obligations and
  scoped empirical contract scenarios need different claim kinds with a shared
  evidence envelope. Serialized `Quot` fails as a universal rejection
  obligation, and `isUnsafe` fails as one rule.
- `F-ASSURANCE-CLAIM-PROTOTYPE-GATE`: built the accepted falsification-first
  [Phase 2 prototype](research/ASSURANCE_CLAIM_PROTOTYPE.md) from existing
  evidence. The generated research artifact passes all thirteen mechanical
  checks: quotient `Eq` fits a bounded normative-candidate obligation, while
  `isUnsafe` is representable only after splitting ingestion from dependent
  visibility. The gate does not yet justify a matrix, RIPR integration,
  semantics-directed reproduction, production schema, or semantic-coverage
  claim.
- `F-ASSURANCE-CLAIM-PROTOTYPE-REMAINDER`: applied the unchanged two-kind
  prototype to theorem proposition-valued results, referenced-constant universe
  ownership, and serialized base `Quot` exact-type handling. The generated
  [representative-set artifact](../results/research/assurance-claim-prototype.json)
  now passes all seventeen checks over six claims. Theorem and universe
  ownership fit normative-candidate obligations with different authority
  states; serialized `Quot` fits only an empirical contract scenario. The old
  Nanoda universe-control provenance gap remains explicit rather than being
  reconstructed from the present checkout. No third claim kind was added.
- `F-ENV-CUTOFF`: found and independently validated the definition
  self-reference witness for `nanoda-gen-8317efea2c7d`. Current Arena's later
  `tutorial/014_selfProof` also kills the mutant, so no duplicate Arena proposal
  is needed. The separate Kiota disagreement is reported as
  [Kiota #5](https://github.com/sankalpsthakur/kiota/issues/5).
- `F-IMAX-EQUALITY`: found a source-directed `imax` witness for
  `nanoda-gen-0bb50147dff2`; official Lean, Kiota, and Lean4Lean all establish
  the expected `REJECT` outcome.
- `F-NUMINDICES-REPORT`: reproduced the nested `numIndices` disagreement on
  current Nanoda master and reported it as
  [Nanoda #29](https://github.com/ammkrn/nanoda_lib/issues/29). The issue now
  explicitly asks whether the serialized field is authoritative rather than
  assuming Nanoda is incorrect.
- `F-UNIVERSE-BOUNDARY`: proved `nanoda-gen-7447f6511962` equivalent by
  match-arm shadowing. The preceding `(Zero, _) if diff >= 0` arm consumes every
  input on which the original later predicate could be true, so the mutated
  `Zero, Param` arm is reachable only for `diff < 0`, where both `>= 0` and
  `> 0` are false. A source-derived candidate and instrumentation reproduction
  confirmed the reachability analysis; the earlier 120-second `mathlib`
  timeout remains archived as an invalid undersized-bound result.
- `F-RESTORED-RECURSOR`: found a one-field restored auxiliary recursor witness
  for `nanoda-gen-8237cd6d3cb2`. The unchanged 105-record nested-inductive
  control is accepted by every tested checker. Changing only `k: false` to
  `k: true` makes baseline Nanoda reject at `src/inductive.rs:1687` while the
  mutant accepts. Official Lean establishes `REJECT` and Lean4Lean confirms;
  Kiota accepts, so its metadata-contract disagreement remains unresolved.
- `F-RESTORED-RECURSOR-TYPE`: found a one-field type witness for
  `nanoda-gen-7b603be7dc87`. Replacing only the restored auxiliary recursor's
  serialized type with the independently well-formed base recursor type makes
  baseline Nanoda reject while the mutant accepts. Official Lean and Lean4Lean
  reject; Kiota accepts, reinforcing one broader restored-recursor validation
  disagreement rather than a separate issue per field.
- `F-RESTORED-CTOR-METADATA`: found a one-field constructor-index witness for
  `nanoda-gen-a59d7fa2cfb3`. Changing only `LALNest.node`'s serialized `cidx`
  from `0` to `1` makes baseline Nanoda reject while the mutant accepts.
  Official Lean and Lean4Lean reject; Kiota accepts, extending the same restored
  nested declaration-validation disagreement to constructor metadata.
- `F-INDUCTIVE-BINDER-TYPE-0`: proved `nanoda-gen-96211e002bfd` equivalent.
  `local_params` and the first inductive-spec traversal derive their compared
  binder types from the same unchanged inductive type, in the same order and
  under identical prior substitutions. Nested specialization rewrites only
  constructors, so the skipped equality assertion cannot fail.
- `F-CONSTRUCTOR-PARAM-BINDER`: proved `nanoda-gen-da679d93da63` equivalent at
  whole-checker scope. A cumulative-sort mismatch survives the local skipped
  check but is rejected by mandatory standalone constructor-type inference.
  More generally, the exact-parameter result check forces each corresponding
  bound variable into the parent inductive application, where standalone
  inference re-establishes the same binder-domain equality.
- `F-IMAX-DIFF-BOUNDARY`: proved `nanoda-gen-ca8565ff512e` equivalent. Disabling
  the equal-`IMax`, `diff = 0` fast path only routes the comparison through the
  exhaustive parameter or nested-maximum fallbacks. Two exported candidates
  matched, and Nanoda's focused equal-`IMax` unit test passed under the mutant.
- `F-QUOT-IND-GUARD`: proved `nanoda-gen-701a664f39e5` equivalent and duplicate
  to the previously classified `nanoda-gen-cb4949d04bbf`. The audit covers both
  loss of proof-only `Quot.ind` reduction and the inverted guard's newly enabled
  path for other quotient primitives; mandatory structural application checking
  prevents malformed overapplications from being hidden by reduction.
- `F-LET-VALUE-TYPE-TRANSFER`: killed `nanoda-gen-e551a17020ce` with the exact
  malformed-let artifact previously generated for Kiota and evaluated against
  held-out Lean4Lean. Baseline Nanoda rejects, the mutant accepts, and both
  accept the matched control. Official Lean, Kiota, and Lean4Lean all confirm
  `REJECT`, so this is a clean regression candidate without a disagreement.
- `F-QUOT-PRIMITIVE-TYPES`: classified four exact-type mutants as
  `REFERENCE_ALIGNED`: base `Quot`, `Quot.mk`, `Quot.lift`, and `Quot.ind`.
  Each one-field sort replacement makes baseline Nanoda reject and its mutant
  accept, while official Lean, Kiota, and Lean4Lean accept every exact artifact.
  The evidence forms one serialized primitive-contract finding, not four issues.
- `F-QUOT-EQ-TYPE`: killed `nanoda-gen-d39c873fbcb7` with a structurally valid
  equality family returning `Sort (max 1 u)` in place of proposition-valued
  built-in `Eq`. Baseline Nanoda rejects exactly at the skipped prerequisite
  assertion and the mutant accepts; both accept the canonical control. Official
  Lean and Lean4Lean reject the candidate, while Kiota accepts it, leaving an
  explicit checker disagreement attached to the regression candidate.
- `F-QUOT-EQ-REFL`: killed `nanoda-gen-cd41c71bc814` with a valid Eq family
  whose sole constructor has one extra unused field. Baseline rejection is
  isolated to `src/quot.rs:105`, the mutant accepts, and both accept the
  canonical control. Official Lean and Lean4Lean reject while Kiota accepts,
  matching the adjacent Eq-type disagreement and completing one prerequisite
  family.
- `F-SERIAL-DECLARATION-LOOP`: killed `nanoda-gen-1dedcb13793f` under Nanoda's
  supported one-thread configuration. The prior 173-test survival used the
  four-thread differential config, which bypassed the mutated serial branch.
  `scripts/run-mutant-input` now accepts and records `--config`; the existing
  malformed-let case is rejected by baseline and accepted by the mutant, while
  both accept its matched control.
- `F-STRING-EXTENSION-GUARD`: classified `nanoda-gen-4238224977cc` equivalent
  at Nanoda's public file/config entrypoint. The active config makes the
  assertion true; with the extension disabled, both the parser and internal
  constructors prevent a string literal from reaching inference.
- `F-BINDER-SORT-SURVIVORS`: classified `nanoda-0004` and
  `nanoda-gen-9a8edf073073` equivalent at the public declaration entrypoint.
  Let value-type equality and recursive comparison of lambda Pi telescopes
  against independently sort-checked expected types re-establish the skipped
  checks. Source-derived malformed probes are rejected by both builds.
- `F-QUOTIENT-CONTRACT-MATRIX`: synthesized four primitive-signature cases and
  two Eq-prerequisite cases into one executable checker matrix. Nanoda rejects
  all six deviations; official Lean and Lean4Lean accept the four primitive
  deviations but reject both Eq deviations; Kiota accepts all six. This is a
  bounded inferred contract, not a complete specification, and no issue was
  filed automatically.
- `F-SPEC-DERIVATION-PILOT`: generalized the rule-to-test method to three
  restored nested-declaration fields. Nanoda, official Lean, and Lean4Lean
  reject restored recursor `k`, recursor type, and constructor-index
  mismatches; Kiota accepts all three. Both pilot matrices are machine-derived
  from exact differential and cross-validation evidence.
- `F-DECLARATION-ENVIRONMENT-MATRIX`: derived two separate executable rules
  for referenced-constant universe ownership and current-declaration
  self-reference. Nanoda, official Lean, and Lean4Lean reject both exact
  violations; Kiota accepts both. `numIndices` remains in the restored
  inductive-metadata family rather than being conflated with environment scope.
- `F-CORE-DECLARATION-TYPING-MATRIX`: added executable characterization cases
  for let annotation/value agreement and the requirement that theorem types are
  propositions. Nanoda, official Lean, Kiota, and Lean4Lean reject both exact
  violations and accept their matched controls.
- `F-CHECKER-RULE-INVENTORY`: aggregated five bounded matrices into 18 directly
  executable checker boundaries. Official Lean and Lean4Lean agree on all 18;
  Nanoda differs from them on six cases, and Kiota differs on nine. The
  inventory records unmodeled surfaces and ranks reduction/projection typing as
  the next source-derived family.
- `F-UNIVERSE-DEFINITIONAL-EQUALITY-MATRIX`: characterized five exact `IMax`
  boundaries. All four checkers accept left-one and right-zero reductions and
  reject equality with distinct left parameters. Nanoda and Kiota accept both
  tested comparisons of `imax` with a successor right operand against `max`;
  official Lean and Lean4Lean reject the general case and its `imax u 1`
  specialization while accepting matched direct-`max` controls. This remains
  an unresolved checker-contract disagreement; no issue was filed.
- `F-PROJECTION-TYPING-MATRIX`: froze three exact Arena tutorial exports plus a
  structure-matched non-projection control. Official Lean and Kiota accept both
  Arena-good projections from a structure that may instantiate to `Prop`;
  Nanoda and Lean4Lean reject both. All four reject the Arena-bad definite-Prop
  data projection and accept the control. The aggregate inventory now covers
  21 boundaries across six matrices.
- `F-INVESTIGATION-ACTION-SOP`: made concrete follow-through a constitutional
  requirement. Every mature finding must recommend a named action, target,
  priority, prerequisites, and evidence. A schema-backed current register
  records two findings and five recommended external actions; external issues,
  pull requests, comments, and disclosures remain blocked on explicit human
  authorization for each target.
- `F-UPSTREAM-ACTION-PREFLIGHT`: rebuilt current Nanoda master `0505569`, Kiota
  main `686063c`, and Lean4Lean arena `bce3448`. All eight candidate/control
  runs reproduce the two finding families, four exact tracker searches found no
  duplicate issues, and the public-report security assessment found no concrete
  exploit requiring private disclosure. Five focused external drafts are
  prepared and hash-bound. At the preflight boundary none had been submitted;
  the later Arena proposal is recorded separately below.
- `F-REDUCTION-SEMANTICS-MATRIX`: normalized eight exact beta, zeta,
  projection, recursor, quotient, and native-natural reduction boundaries.
  All four checkers accept every candidate and control. The focused
  `Quot.lift` candidate kills its dispatch mutant; `Quot.ind` cannot expose
  proof-valued reduction suppression because proof irrelevance identifies the
  results. The exact `Nat.ble` case survives its dispatch mutant, while
  `Nat.land` kills the same mutant by exposing collateral misclassification.
  No checker issue is recommended from this passing bounded matrix.
- `F-ORDINARY-INDUCTIVE-WELL-FORMEDNESS`: characterized six exact strict-
  positivity, constructor-parameter, result-parameter, result-universe, and
  recursive-index boundaries from canonical Arena cases. All four checkers
  reject every malformed candidate and accept every control. Focused Nanoda
  positivity and result-parameter omission probes survive because independent
  `isRec` or reconstructed-recursor consistency checks reject the canonical
  artifacts. That is defense-in-depth evidence, not an equivalence result; no
  external issue is recommended from the consensus matrix.
- `F-ORDINARY-INDUCTIVE-PARAMETER-WITNESS`: killed `nanoda-0006` with a
  fully exporter-generated inductive whose proof parameters `p` and `q` are
  swapped only in the constructor result. Baseline Nanoda rejects at exact
  parameter matching, the omission mutant accepts, and both accept the control.
  Official Lean and Lean4Lean reject; current Kiota main `686063c` accepts.
  One Arena reject-test proposal and one Kiota issue are recommended but remain
  human-gated; no external action has been taken.
- `F-ORDINARY-INDUCTIVE-POSITIVITY-WITNESS`: killed `nanoda-0005` with a
  full-recursor artifact whose shared constructor/recursor field domain changes
  from `Unit` to definitionally equal `LALConstType Unit I`. Baseline Nanoda
  rejects at strict positivity, the omission mutant accepts, and both accept the
  control. Official Lean, Kiota, and Lean4Lean all confirm rejection. A single
  Arena test proposal is recommended because the existing dummy-recursor case
  does not isolate the rule; no implementation issue is recommended.
- `F-LITERAL-PARSER-CONFIGURATION`: closed the family at Nanoda's pinned public
  entrypoint. Two Nat-extension assertion omissions and one String-extension
  assertion omission are already proved equivalent: active config enables the
  extensions, while disabled config rejects literal records in the parser and
  internal constructors before the mutated downstream checks. No checker issue
  or additional matrix is recommended from this configuration-reachability
  result.
- `F-IMAX-ARENA-PROPOSAL`: filed
  [Arena #175](https://github.com/leanprover/lean-kernel-arena/issues/175) to
  clarify and add reject coverage for the two right-successor comparisons.
  Maintainer guidance invited the corner-case tests, and one small Arena test
  contribution was submitted as
  [Arena PR #176](https://github.com/leanprover/lean-kernel-arena/pull/176).
  The single `Tutorial.lean` change adds the adjacent `imax u 1` and
  `imax u (v + 1)` reject cases. The PR is open and mergeable as of 2026-08-29,
  not yet merged. Nanoda and Kiota implementation reports remain unpublished.

### Frontier Transition — 2026-08-30

- The human-approved
  [Declaration Validation Contract Slice](research/DECLARATION_VALIDATION_CONTRACT_SLICE_PLAN.md)
  takes the deliberate-supersession path defined by its Milestone 0. This is a
  planning-authority change, not a claim that the previous characterization
  gate was completed.
- `F-ASSURANCE-CLAIM-CHARACTERIZATION-VIEW` is superseded before its proposed
  builder was implemented. Its two-kind model, evidence-fidelity requirements,
  and prohibition on treating empirical observations as a semantic denominator
  remain mandatory inputs to the replacement frontier.
- `F-AXIOM-UNSAFE-DECLARATIONS` is absorbed as a bounded sub-question of the
  declaration-validation slice. Its existing evidence and unresolved states
  remain intact. This transition does not authorize a broad axiom campaign or
  permit trust-policy behavior into the primary kernel-validity denominator.

### Active

1. `F-DECLARATION-VALIDATION-CONTRACT-SLICE`: execute the revised
   [declaration-validation mandate](research/DECLARATION_VALIDATION_CONTRACT_SLICE_PLAN.md).
   The deliberate frontier transition and starting dirty-tree dispositions are
   recorded in the
   [Milestone 0 result](../results/research/declaration-validation-milestone-0.json).
   Milestone 1 is complete: the
   [semantic target lock](../config/declaration-validation-target.json) pins the
   Lean 4.33.0 checked declaration-addition judgment separately from the Lean
   4.29.1 artifact producer, the lean4export 3.1.0 producer/importer revisions,
   and all four Arena observer profiles. The lock preserves Lean4Lean's official
   C++ kernel lineage and the distinct parser revisions instead of treating
   checker agreement or version labels as semantic authority. Its schema and
   cross-field/evidence checks run with
   `scripts/validate-declaration-validation-target`; completion details are in
   the
   [Milestone 1 result](../results/research/declaration-validation-milestone-1.json).
   Milestones 2 and 3 are also complete. The canonical
   [characterization model](../config/declaration-validation-characterization-model.json)
   and strict
   [entry schema](../schemas/declaration-validation-characterization-entry.schema.json)
   preserve normative candidates separately from empirical scenarios; make
   layer, authority, lifecycle, and soundness relevance orthogonal; and require
   every evidence item to carry a role, source type, lock, exact locator,
   structured claim, and assumptions. Lean4Lean's derived lineage is enforced,
   and a four-observer implementation consensus is mechanically rejected as
   sufficient normative support. Run
   `scripts/validate-declaration-validation-characterization-model`; the durable
   results are
   [Milestone 2](../results/research/declaration-validation-milestone-2.json)
   and
   [Milestone 3](../results/research/declaration-validation-milestone-3.json).
   Milestone 4 is complete. The frozen
   [discovery closure](../config/declaration-validation-discovery-closure.json)
   exhausts 22 pinned source files into 59 disposed sites, closes 22 required
   topics with exact four-observer vectors, and assigns 13 helper dependencies
   to included, imported-prerequisite, or excluded states. It records 21
   provisional `SEED.*` groups but creates no catalog entry and assigns no
   stable semantic ID. In particular, Kiota's pinned current-declaration
   visibility and universe-ownership differences remain empirical observations,
   not normative or soundness conclusions. Run
   `scripts/validate-declaration-validation-discovery-closure`; completion
   details are in the
   [Milestone 4 result](../results/research/declaration-validation-milestone-4.json).
   Milestone 5 is complete. The frozen
   [stable identity registry](../config/declaration-validation-identity-registry.json)
   resolves all 21 provisional discovery seeds into 30 implementation-neutral
   identities: 19 normative candidates, 9 empirical scenarios, and 2 identities
   whose kind remains unresolved. The generated
   [decision log](../results/research/declaration-validation-milestone-5-decisions.json)
   preserves every keep, merge, split, reuse, deferral, and exclusion with
   discovery-only evidence and content-bound before/after hashes. It assigns no
   authority, layer, soundness relevance, catalog status, or coverage
   eligibility. Run `scripts/validate-declaration-validation-milestone-5`;
   completion details are in the
   [Milestone 5 result](../results/research/declaration-validation-milestone-5.json).
   Milestone 6 is complete. The frozen
   [source lock](../config/declaration-validation-source-lock.json) binds nine
   repository/revision identities, 41 pinned source/configuration/build files,
   19 tracked Lab evidence artifacts, 12 existing witnesses, 18 optional local
   observations, and all four observer configurations. Offline validation is
   independent of the ignored `external/` checkout; online verification has
   confirmed all 9 remote revisions, all 41 raw-content SHA-256 values, and 13
   enabled locator tokens. Normative-documentation and mechanized-result slots
   remain explicitly empty pending per-identity authority review. Run
   `scripts/validate-declaration-validation-source-lock`; completion details are
   in the
   [Milestone 6 result](../results/research/declaration-validation-milestone-6.json).
   Milestone 7 is complete. The authoritative
   [canonical catalog](../config/declaration-validation-catalog.json) is
   intentionally empty until Milestone 8 adjudicates the frozen identities.
   Six versioned
   [authority rules](../config/declaration-validation-authority-rules.json)
   cover both object kinds and all three authority states without admitting
   checker consensus as normative support. The
   [generated report](research/DECLARATION_VALIDATION_OBLIGATIONS.md) derives
   all catalog views and embeds the catalog hash; the
   [freeze manifest](../results/research/declaration-validation-milestone-7-freeze.json)
   binds the source lock, authority rules, catalog, report, and decision logs
   in an acyclic order. Run
   `scripts/validate-declaration-validation-catalog`; completion details are in
   the
   [Milestone 7 result](../results/research/declaration-validation-milestone-7.json).
   A separate adversarial review then exposed and the hardened M7 architecture
   corrected additional epistemic-boundary failures: semantic-target
   configuration and implementation files can no longer be relabeled as
   normative support; evidence type is coupled to locked record kind;
   unresolved or active normative assumptions and statement contradictions
   block `ESTABLISHED`; soundness remains mechanically restricted to
   `NOT_ASSESSED`; stable IDs bind their structured denotations; observer and
   implementation mappings are attribution-bound; and Milestone 8 requires an
   exact disposition of all 30 frozen identities. Decision records now bind a
   tracked before snapshot and the supplied after catalog. A new immutable
   [Milestone 7 evidence-lock root](../config/declaration-validation-evidence-locks/milestone-7.json)
   permits later evidence selection through a versioned successor without
   rewriting the frozen Milestone 6 lock. The generated report is status-aware,
   the completion record is schema/render/test gated, and JSON Pointer handling
   is strict RFC 6901. The predecessor sweep also changed Milestone 4's
   completion verification to content-check its mutable frontier documents and
   original validator as historical Git blobs, matching Milestones 5 and 6
   without rewriting historical bytes. These checks mechanically enforce the
   qualification rules; they do not prove those rules epistemically
   sufficient. The five-entry Milestone 8 candidate batch is now prepared and
   awaits review before any further identity adjudication. Its canonical
   candidate data is
   [bound separately](../config/declaration-validation-milestone-8-pilot.json),
   its selected existing observer-result evidence is bound by the sequence-2
   [successor lock](../config/declaration-validation-evidence-locks/milestone-8-pilot.json),
   and its generated review view is
   [available here](research/DECLARATION_VALIDATION_MILESTONE_8_PILOT.md).
   After review, inspect and disposition every frozen identity into the first
   complete characterization inventory. Do not claim Milestone 8 status for
   the pilot or for any incomplete disposition vector. Continue toward the
   adversarial review and frozen design for the later Arena
   negative-coverage phase. This slice does not execute the broad Arena
   coverage campaign, create a public conformance claim, or infer semantic
   authority from checker agreement.

   A final residual exploit-first pass at
   `0bee1b71fe8d49ebe6a8adb5e4193c507ea2e43a` then demonstrated three remaining
   attacks with zero-error validation before repair: locally manufactured
   normative authority, checker outcomes asserted through free-form secondary
   metadata rather than result bytes, and stable-ID denotation drift through
   additional predicates or a different resolving judgment pointer. Equivalent
   probes also admitted forged authoritative documentation, self-asserted formal
   mechanization, and empirical precondition/observation drift. M7 now binds an
   intentionally empty, separately frozen
   [approved authority-source registry](../config/declaration-validation-approved-authority-sources.json).
   Evidence-lock snapshots cannot establish normative authority unless their
   external source identity was approved before catalog adjudication; M8 cannot
   extend that registry. Concrete checker observations are extracted from exact
   structured result pointers, with secondary locator strings treated only as
   annotations. Stable IDs bind a canonical semantic projection covering the
   modeled judgment, exact applicability/reach structure, target predicate,
   violation semantics, and empirical scenario scope/observation target while
   excluding editorial and research-result metadata. The named residual attack
   tests are frozen in `tests/test_declaration_validation_catalog.py`, and the
   generated Milestone 7 completion record preserves the accepted-at-baseline
   and rejected-after-hardening results. The catalog remains empty, the approved
   registry contains zero sources, soundness remains `NOT_ASSESSED`, and the M8
   five-entry pilot awaits review without asserting M8 completion. The exact
   claim is limited to mechanical rejection of these
   attacks, not epistemic sufficiency of the authority model.

   The repository operating-instruction prerequisite is complete: `AGENTS.md`
   now routes agents through this status artifact and the active plan, and the
   repository-local declaration-validation adjudication skill routes M8/M9
   catalog work to the canonical artifacts and validators. This organizational
   change does not start M8, alter the frontier, or change any research finding.

### Waiting

- `W-NANODA-NUMINDICES`: await maintainer guidance on
  [Nanoda #29](https://github.com/ammkrn/nanoda_lib/issues/29). Do not propose an
  Arena `accept` or `reject` test until the contract is adjudicated or Arena
  explicitly chooses `either`. Then update the investigation terminology,
  machine classification, assurance snapshot, and proposed test outcome
  together.
- `W-KIOTA-UNIVERSES`: await adjudication of
  [Kiota #3](https://github.com/sankalpsthakur/kiota/issues/3) for undeclared
  universe ownership.
- `W-KIOTA-SELF-REFERENCE`: await adjudication of
  [Kiota #5](https://github.com/sankalpsthakur/kiota/issues/5) for declaration
  self-reference.
- `W-KIOTA-RESTORED-DECLARATIONS`: decide whether to report Kiota's acceptance
  of three isolated restored nested declaration mismatches: recursor `k`,
  recursor type, and constructor index. Official Lean and Lean4Lean reject all
  three exact artifacts. Discuss them together before filing to avoid issue
  spam and to determine whether one shared validation boundary explains them.
- `W-KIOTA-PROOF-PARAMETER-UNIFORMITY`: review the prepared single Kiota issue
  and Arena reject-test proposal for the swapped proof-parameter witness. Both
  reproduce on current Kiota main and have no matching issue, but publication
  requires target-specific human approval.
- `W-ARENA-REDUCIBLE-POSITIVITY`: review the prepared Arena proposal for the
  full-recursor reducible-hidden positivity witness. It strengthens an existing
  logical test rather than reporting an implementation defect; submission
  requires explicit human approval.
- `W-IMAX-RIGHT-SUCCESSOR`: await review and expected merge of the open,
  mergeable [Arena PR #176](https://github.com/leanprover/lean-kernel-arena/pull/176),
  which contributes the two adjacent tutorial corner cases authorized in
  [#175](https://github.com/leanprover/lean-kernel-arena/issues/175). Do not
  record the contribution as upstream corpus coverage until the PR actually
  merges. Prepared Nanoda and Kiota implementation issues remain
  `REVIEW_REQUIRED`; do not submit either without target-specific approval.
- `W-POSSIBLY-PROP-PROJECTIONS`: discuss whether Nanoda and Lean4Lean should be
  notified using the two prepared issue drafts. Current upstream reproduction
  and duplicate searches are complete. Arena already contains and explains
  both cases, so no Arena proposal is recommended. Both implementation issues
  remain `REVIEW_REQUIRED`.

### Future Directions

- `D-IMPLEMENTATION-SPECS`: independently reverse engineer the accepted export
  contract from official Lean, Nanoda, Kiota, and Lean4Lean, then compare the
  frozen profiles. Start with inductive and recursor metadata. Record parser,
  reconstruction, validation, and semantic-use behavior separately. Translate
  observations into characterization tests first; promote them to conformance
  tests only after an `accept`, `reject`, or `either` contract is justified.
- `D-UNDIRECTED-CAMPAIGN`: run a broader unattended mutant campaign only after
  the targeted frontier stops producing higher-value source-directed work.
  Keep generation, checker execution, minimization, and result persistence
  local and deterministic; reserve model use for source interpretation and
  semantic triage.
- `D-MUTATION-SURFACE`: extend operators to match arms and richer reduction
  behavior after the current survivor queue, retaining isolated build
  validation and semantic-policy review.
- `D-REMOTE-PAYLOADS`: define content-addressed remote storage for ignored
  coverage and materialized-corpus payloads, then keep assurance and public
  status artifacts synchronized when evidence changes.
