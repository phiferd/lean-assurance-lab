# Lean Assurance Lab

**New to Lean, proof kernels, or mutation testing? Start with
[Why Test a Proof Kernel?](docs/INTRODUCTION.md). For a real kernel failure and
an honest assessment of this project's limits, read the
[2026 Collatz incident case study](docs/CASE_STUDY_COLLATZ.md).**

Lean Assurance Lab is a continuous assurance project for Lean's
proof-validation ecosystem. It uses independent validators, generated positive
and negative tests, semantic mutation, contract characterization, coverage,
witness generation, and other reproducible techniques to discover and
characterize validation boundaries.

**Want to contribute?**

- Claimable work: [GitHub Issues](https://github.com/phiferd/lean-assurance-lab/issues)
- Research priority and context: [`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md)
- Contribution and evidence contract: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Agent workflow: [`docs/AGENT_WORKFLOW.md`](docs/AGENT_WORKFLOW.md)
- Project review and proposed next steps: [`docs/PROJECT_REVIEW.md`](docs/PROJECT_REVIEW.md)
- Current measured assurance state: [`docs/PUBLIC_STATUS.md`](docs/PUBLIC_STATUS.md)

The project is governed by `CONSTITUTION.md`.
[`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md) is the research-planning
authority: its Active frontier says what the project should investigate next.
GitHub Issues coordinate bounded, claimable work beneath that frontier;
creating an Issue does not independently activate a research direction or
establish a result. [`docs/PUBLIC_STATUS.md`](docs/PUBLIC_STATUS.md) is a
generated report of measured state, not a priority queue. Methods, project-plan,
and research documents preserve intellectual and implementation history, but
do not independently authorize work.

Contribution requirements are in [`CONTRIBUTING.md`](CONTRIBUTING.md).
Completed findings follow the concrete recommendation and human authorization
rules in [`docs/INVESTIGATION_SOP.md`](docs/INVESTIGATION_SOP.md).
Evaluated proposals for post-milestone work, including the boundary between
near-term improvements and independent exploratory research, are in
[`docs/research/RESEARCH_BACKED_IMPROVEMENTS.md`](docs/research/RESEARCH_BACKED_IMPROVEMENTS.md).

Mechanical completion conditions vary by task. A central differential pattern
is executable:

```text
checker_a(input) != checker_b(input)
```

LLMs and humans may propose candidates or explain results, but they do not
replace the task's stated mechanical completion condition. Witnesses, scoped
equivalence results, characterized boundaries, negative results, and bounded
unresolved results can all be valid outcomes when their evidence is preserved.

## Research Question

How effectively can reproducible evidence characterize the validation
boundaries and measured assurance state of Lean's proof-validation ecosystem?
Current methods include testing how well the Lean Kernel Arena corpus
discriminates plausible incorrect implementations, using semantic mutation and
adversarial generation to improve that discrimination, and investigating
disagreements among independently implemented validators without treating
implementation vote as semantic authority.

## Current Milestone

The Declaration Validation Contract Slice has completed Milestones 0 through
10 and is the immutable predecessor of the completed obligation-sensitive coverage
publication study. M10's empty strict normative denominator, 19 provisional
candidates, eight empirical scenarios, and `Reach(x) AND NOT P(x)` contract are
resolved through its historical attestation and the separately frozen theorem-
control erratum, not mutable current files. The study preregistered
the mechanically derived 15-candidate technically ready cohort, kept four
readiness holdouts outside it, frozen bounded authority-source discovery, and
recorded the separate human approval outcome. Only the exact v4.33 theorem-Prop
manual claim is approved; all other candidate mappings remain deferred or
rejected in their recorded evidentiary roles. Gate 6 has now completed authority
adjudication for the exact 15-candidate cohort: `DECL.THEOREM.TYPE_PROP` is the
sole `ESTABLISHED` obligation, while the other 14 remain `PROVISIONAL`; no
candidate is `UNRESOLVED`. The Gate-5 repair continues to enforce the exact
human-approved source/claim/candidate scope. Gate 7 denominator derivation is
frozen from exact Gate-6 Git inputs under the unchanged M10 algorithm. Its
strict primary denominator contains only `DECL.THEOREM.TYPE_PROP`, representing
one preregistered semantic family, so the mechanically selected claim tier is
`BOUNDED_PILOT`. The other 14 candidates remain separately labeled
`PROVISIONAL`. The required presentation-only manuscript skeleton was committed
before derivation and carries no semantic authority. Gate 8 now freezes the
exact existing corpus, observer, build, configuration, mapping, resource, and
prior-knowledge inputs. Its one baseline row is
`OBSERVED_NEGATIVE_NOT_ISOLATED`: the existing non-Prop theorem negative is
content-bound and attributable, but no M10-erratum-compliant same-family theorem
control exists in the frozen prior inputs. Existing isolated coverage is
therefore 0/1 (0.0%). The separate coarse indicators are `SOURCE_REACHED`,
`MUTANT_KILLED`, and `EXISTING_CASE_LINKED`; none is semantic coverage. The
theorem obligation is the sole Gate-9 synthesis target. Its frozen protocol
allows one negative/control pair, reusing the known negative and constructing
a matched Prop-valued theorem control, with at most eight checker launches and
600 seconds of active run time. [Gate 10 is complete](docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_GATE_10_REPORT.md):
all four frozen observers accepted the matched theorem control and rejected the
unchanged M6 negative, using eight launches and 3.875 active seconds. Final
isolated coverage is 1/1 (100.0%), while the frozen baseline remains 0/1. This
completes missing control evidence for a known negative; it discovers no new
negative or implementation defect. The Arena companion-control recommendation
is deferred pending review, upstream/duplicate checks and human authorization.
[Gates 11–12 are complete](docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_FINAL_REPORT.md).
The literal preregistered decision is `STRONG_POSITIVE / BOUNDED_PILOT /
PUBLISH_BOUNDED`: a bounded technical report, with no broad method or new-defect
claim. The final study is frozen at content commit `4cd21c6` and bound by a
separate Git-blob attestation. This study is stopped; later research needs an
explicit successor plan.

Validate the complete historical study without checker execution using
`scripts/close-declaration-validation-publication-study validate-historical`.
For the local full-payload boundary after closure, use
`scripts/validate-publication-study-snapshot --require-full-payload`. This
successor checks the original validators against the historical frontier and
exact local payloads; it does not reopen the study. Routine current assurance refresh is one logged, fail-fast command:
`scripts/refresh-current-state`.

Verify Gate-10 recorded evidence without launching a checker using
`scripts/validate-declaration-validation-publication-study-gate-10`; add
`--require-full-payload` to verify the complete local predecessor payloads.

The broader project also has a closed mechanical mutation loop for `nanoda`,
content-addressed invalidation, executable witness search and minimization,
cross-validator observations that preserve disagreements without majority
voting, and rotating held-out evaluation over pinned Kiota and Lean4Lean folds.
The measured rotating aggregate remains one positive fold and one neutral
fold, improving the modeled held-out score from 0.5 to 1.0.

The versioned current assurance snapshot reports `FAIL`: four of five hard
checks pass, while 15 unresolved semantic disagreements fail the configured
disagreement check. One additional parse-behavior disagreement remains visible,
and 9 mechanically executed survivors await semantic or witness triage outside
the canonical modeled population. The exact current cases and evidence are
generated in `docs/PUBLIC_STATUS.md`; the failure is the intended honest result,
not a failed milestone implementation.
The Milestone 8 implementation gate passes all 24 checks, and the Milestone 9
community-workflow gate passes all 30 checks.

The amended frozen Collatz retrospective is complete and classified
`FULL_CLASS_REDISCOVERY`. The original run recreated the affected-official/
fixed-official nested-parameter distinction. After preserving and invalidating
its zero-input projection branch, two protocol amendments repaired relocated
LLVM source paths and bounded candidate materialization. The repaired search
then recreated the pre-fix/fixed nanoda projection-structure-identity
distinction on attempt 1. The scoped report is
[results/collatz-retrospective/REPORT.md](results/collatz-retrospective/REPORT.md).

## Shared Ecosystem Contribution

The project has submitted one small Lean Kernel Arena test contribution:
[Arena PR #176](https://github.com/leanprover/lean-kernel-arena/pull/176). Its
single tutorial-file change adds the two adjacent `imax` right-successor reject
cases (`imax u 1` and `imax u (v + 1)`) developed from the project's checker
disagreement evidence. The PR is open and mergeable as of 2026-08-29; expected
merge is not recorded as completed. Current upstream status and the next local
research frontier are tracked in
[`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md).

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
.venv/bin/python scripts/run-unit-tests
```

The clone-safe runner executes the unchanged unit suite and skips only the
frozen Gate-8 input-freeze test when its inventoried observer binaries,
coverage files, or corpus files are absent. The skip is reported as
`full-payload integration unavailable`. Missing tracked inputs fail preflight;
when all payloads are present, the original test runs and hash mismatches fail. CI uses this clone-safe mode. Use `--require-full-payload`
when all frozen inputs are expected locally. This mode does not replace the
full-payload assurance validator. Existing materialization-dependent tests
retain their explicit skips. The publication-study tests also
inspect immutable predecessor commits, so retain complete Git history (use
`fetch-depth: 0` in CI); shallow clones can fail during test setup.

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
