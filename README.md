# Lean Assurance Lab

**New to Lean, proof kernels, or mutation testing? Start with
[Why Test a Proof Kernel?](docs/INTRODUCTION.md). For a real kernel failure and
an honest assessment of this project's limits, read the
[2026 Collatz incident case study](docs/CASE_STUDY_COLLATZ.md).**

Lean Assurance Lab is a mechanical testing project for Lean proof checkers.
The initial target is mutation testing against one checker implementation,
then using surviving mutants to drive adversarial exported-artifact generation.

The project is governed by `CONSTITUTION.md`. The current execution plan lives
in `docs/PROJECT_PLAN.md`. The public assurance state is in
`docs/PUBLIC_STATUS.md`, and contribution requirements are in `CONTRIBUTING.md`.

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

Milestones 1 through 9 are complete. The project has a closed mechanical
mutation loop for `nanoda`, content-addressed invalidation, and a structured
semantic model spanning validation elision, predicate negation, relational
boundaries, and equality discrimination. Witness search and structure-aware
minimization are executable and auditable. Cross-validator execution preserves
semantic and parse disagreements without majority voting. Rotating held-out
evaluation now covers pinned Kiota and Lean4Lean folds in different semantic
subsystems. The measured aggregate is one positive fold and one neutral fold,
improving the modeled held-out score from 0.5 to 1.0.

The versioned current assurance snapshot reports `FAIL`: four of five hard
checks pass, while three unresolved semantic disagreements fail the configured
disagreement check. Two concern universe ownership between official Lean and
Kiota. The third is a current Nanoda nested-inductive metadata over-rejection:
official Lean and Lean4Lean accept the generated artifact while Nanoda rejects
it. This is the intended honest result, not a failed milestone implementation.
The Milestone 8 implementation gate passes all 24 checks, and the Milestone 9
community-workflow gate passes all 25 checks.

The amended frozen Collatz retrospective is complete and classified
`FULL_CLASS_REDISCOVERY`. The original run recreated the affected-official/
fixed-official nested-parameter distinction. After preserving and invalidating
its zero-input projection branch, two protocol amendments repaired relocated
LLVM source paths and bounded candidate materialization. The repaired search
then recreated the pre-fix/fixed nanoda projection-structure-identity
distinction on attempt 1. The scoped report is
[results/collatz-retrospective/REPORT.md](results/collatz-retrospective/REPORT.md).

## Repository Layout

```text
.github/
config/
  assurance-policy.json
  contribution-types.json
docs/
  CASE_STUDY_COLLATZ.md
  DESIGN.md
  INTRODUCTION.md
  MUTATION_MODEL.md
  PUBLIC_STATUS.md
  RESEARCH_STATUS.md
results/
  baseline/
  collatz-retrospective/
  cross-validation/
  expected-outcomes/
  mutants/
  rotating-heldout/
  survivors/
  witnesses/
corpus/
  generated/
  minimized/
  regression-candidates/
  transfer/
scripts/
  artifact-status
  assurance-snapshot
  build-artifact-graph
  build-rotating-heldout-report
  audit-coverage-guidance
  collect-coverage
  collatz-retrospective
  collatz-retrospective-assurance
  compare
  check-distinction
  confirm-witness
  cross-validate
  current-assurance-snapshot
  establish-expected-outcome
  evaluate-m6-rotating-fold
  freeze-rotating-fold
  freeze-transfer-experiment
  generate
  generate-mutations
  minimize
  milestone-2-assurance
  milestone-3-assurance
  milestone-4-assurance
  milestone-5-assurance
  milestone-6-assurance
  milestone-7-assurance
  milestone-8-assurance
  milestone-9-assurance
  mutate
  normalize-arena-results
  promote-scheduled-result
  reindex-coverage
  report
  render-public-status
  run-arena
  run-mutation-batch
  run-mutant
  run-mutant-input
  run-mutant-scheduled
  run-rotating-fold
  run-rotating-fold-resumable
  run-transfer-experiment
  schedule-mutant
  setup-arena
  snapshot-coverage
  validate-mutation-batch
  validate-contribution
  validator-inventory
```

The upstream Lean Kernel Arena checkout is expected at `external/lean-kernel-arena`
by default. Override with `LKA_ROOT=/path/to/lean-kernel-arena`.

## Prerequisites And Clone-Safe Checks

The repository-local unit suite requires Python 3.10 or newer and the two
packages in `requirements-dev.txt`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

The unit suite works without ignored external checkouts. One integration test
is skipped until Lean Kernel Arena checker profiles have been materialized.

Full experiments additionally require Git, Cargo, Rust, Elan, `uv`, the Arena
system prerequisites, and substantial disk space. `scripts/setup-arena` clones
Arena; `scripts/setup-arena --reproducible` also checks the pinned host and tool
identities in `config/reproducibility.json`. Exact portable binary identity is
currently attested on the pinned `aarch64-apple-darwin` environment. The
materialized corpus is approximately 9.5 GB.

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

For a fresh checkout, pin the Arena revision and verify the required host tools
before materializing its checkers and tests:

```sh
scripts/setup-arena --reproducible
scripts/verify-portable-coverage --check-environment-only
```

The collector remaps checkout, Cargo, target, and Rust sysroot paths to stable
virtual roots and suppresses the final Mach-O UUID on macOS. It uses an
isolated instrumented binary under `target-coverage`,
checks every instrumented outcome against the cached baseline, checkpoints each
test, and writes forward and reverse indexes under `results/coverage/nanoda/`.
Interrupted runs can continue with `--resume --reuse-build`, provided the saved
source digest and collection configuration still match.

`scripts/verify-portable-coverage` builds in two different absolute paths,
including one with spaces, and requires identical binary hashes and canonical
repository-relative coverage. Exact binary identity is guaranteed only for the
pinned host and toolchain in `config/reproducibility.json`; other targets may
reproduce semantic coverage without producing the same executable bytes.

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

Establish an exact expected outcome and run compatible unmodified validators:

```sh
scripts/validator-inventory
scripts/establish-expected-outcome nanoda-0003-original \
  corpus/generated/nanoda-0003-auto-universe.ndjson \
  --control corpus/controls/nanoda-0003-declared-const-universe.ndjson
scripts/cross-validate nanoda-0003-original \
  corpus/generated/nanoda-0003-auto-universe.ndjson \
  --control corpus/controls/nanoda-0003-declared-const-universe.ndjson \
  --expected-evidence results/expected-outcomes/nanoda-0003-original.json
```

`cross-validate` exits 2 for a checker disagreement so automation cannot mistake
an unresolved difference for success. Results retain raw exit behavior,
compatibility evidence, parse behavior, exact checker identities, and the
no-majority-vote policy.

The Milestone 6 transfer protocol is deliberately two-phase:

```sh
scripts/freeze-transfer-experiment
scripts/run-transfer-experiment
scripts/milestone-6-assurance
```

The freeze command generates the corpus from the nanoda fault model, confirms
it with nanoda and official Lean, and records that no held-out mutant outcome
was used. The evaluation command refuses to overwrite prior results and binds
its Kiota run to the exact frozen-manifest SHA.

Milestone 7 rotates both the held-out implementation and fault subsystem, then
aggregates separately stored folds:

```sh
scripts/freeze-rotating-fold
scripts/run-rotating-fold
scripts/evaluate-m6-rotating-fold
scripts/build-rotating-heldout-report
scripts/report --output results/assurance/milestone-7-report.json
scripts/milestone-7-assurance
```

The fresh Lean4Lean fold evaluates all 197 original corpus tests before adding
the frozen let-value/type mismatch candidate. The retrospective Kiota fold
measures the Milestone 6 candidate against its original corpus baseline. Fold
classification is mechanical and distinguishes `POSITIVE`, `NEUTRAL`,
`NEGATIVE`, `INCONCLUSIVE`, `INCOMPATIBLE`, and `UNRESOLVED`. These experiments
exercise intentionally injected faults; they are not claims of bugs in the
unmodified validators.

`scripts/run-rotating-fold` is retained verbatim as the content-bound producer
of the completed Milestone 7 result. New full-corpus folds use its versioned
successor:

```sh
scripts/run-rotating-fold-resumable \
  --freeze results/rotating-heldout/NEXT/folds/lean4lean-freeze.json \
  --output results/rotating-heldout/NEXT/folds/lean4lean-evaluation.json

# After an interruption, with the same frozen inputs and runner revision:
scripts/run-rotating-fold-resumable \
  --freeze results/rotating-heldout/NEXT/folds/lean4lean-freeze.json \
  --output results/rotating-heldout/NEXT/folds/lean4lean-evaluation.json \
  --resume
```

The successor atomically checkpoints each baseline and mutant checker result,
binds the checkpoint to every frozen input and producer hash, resumes only the
exact sorted corpus prefix, and records abandoned in-flight attempts instead
of silently dropping them from execution accounting.

The current official Lean/Kiota universe-ownership disagreement has an
[upstream-ready investigation report](docs/investigations/KIOTA_UNIVERSE_OWNERSHIP.md)
and a schema-validated reproduction against Kiota's current upstream `main`.
The current Nanoda nested-inductive metadata disagreement has a separate
[hash-bound investigation report](docs/investigations/NANODA_NUMINDICES_OVERREJECTION.md)
reproduced against Nanoda master revision `05055695879dfebb6628a67da88ceca6cd6b0421`.

Produce the current assurance and public status artifacts with:

```sh
scripts/current-assurance-snapshot
scripts/milestone-8-assurance
scripts/render-public-status
scripts/milestone-9-assurance
```

Snapshot production succeeds when it can faithfully compute the report, even
when the report's own hard gate is `FAIL`. Inspect
`results/assurance/current.json` for the gate result, failure reasons, exact
evidence, contextual trend metrics, and execution costs. Mutation-score and
coverage thresholds are policy-controlled trends rather than hard gates by
default.

Validate the contribution catalog or a proposed content-bound contribution
manifest with:

```sh
scripts/validate-contribution --check-catalog
scripts/validate-contribution path/to/contribution.json
```

The seven supported contribution paths, required metadata, review standards,
and responsible-disclosure boundary are documented in `CONTRIBUTING.md`.

Bind ignored local coverage payloads to a compact tracked identity artifact and
verify the Milestone 1 gate with:

```sh
scripts/snapshot-coverage
scripts/snapshot-coverage --verify
scripts/verify-portable-coverage --verify
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

## License

Lean Assurance Lab is licensed under the
[Apache License, Version 2.0](LICENSE). Third-party provenance and modifications
to derived corpus artifacts are recorded in [NOTICE](NOTICE).
