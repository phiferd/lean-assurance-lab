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

## Current Metrics

```yaml
mutation_score: 0.6666666666666666
generated_mutants: 4
killed_mutants: 2
surviving_mutants: 1
classified_equivalent: 0
classified_unreachable: 0
classified_performance_only: 0
meaningful_survivors: 1
unknown_equivalence: 1
witnesses_found: 1
minimized_witnesses: 0
arena_regression_candidates: 0
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

- `nanoda-0004` is registered but has not been run because `nanoda-0003`
  satisfied the immediate survivor-search objective.
- The current automated loop supports exact text replacement specs, not bulk
  source-to-source mutation generation.
- Large corpus files are expensive: `mathlib.ndjson` is about 5.2 GB,
  `cslib.ndjson` about 2.0 GB, and `cedar.ndjson` about 790 MB.

## Next Concrete Experiment

1. Run `nanoda-0004` through `scripts/run-mutant-scheduled` and continue a
   mechanically generated mutation batch.
2. Add an AST-aware source mutation generator so mutation creation and
   registration no longer require LLM or manual edits.
3. Promote the `nanoda-0003` witness into a proposed Arena regression test and
   verify that an augmented-corpus schedule kills it.
4. Periodically compare scheduled results with full-corpus runs to audit the
   coverage exclusion invariant.
