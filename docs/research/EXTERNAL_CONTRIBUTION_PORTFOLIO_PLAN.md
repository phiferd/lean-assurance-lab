# External contribution portfolio

Adopted 2026-09-09 under the owner's explicit project-wide reassessment.
Frontier: `F-EXTERNAL-CONTRIBUTION-PORTFOLIO`. Constitution first; Active status
and `config/research-queue.json` control selection. This is a successor strategy
to the completed cache-predicate transfer. The unstarted one-thread assessment
is deferred with its original evidence and budget retained.

## Aim and evidence

Prefer useful, maintainable external contributions over clearing the remaining
survivor list. Keep three paths available: standard Arena corpus quality,
individual checker hardening, and independent Lean semantic clarification.
The [review package](../../results/research/contribution-portfolio-review-2026-09-09/)
binds the source observations, current upstream disposition, methods review,
correction to the zero-thread recommendation, and comparative decision.

Arena #181 and #182 are verified merged; #181 includes positive maintainer
feedback and a request to remove an unnecessary control. Nanoda #32 is open
with two preventive dispatcher tests. These are evidence of concrete utility
and submission, respectively; neither establishes semantic authority. Candidate
absence from a commit diff or a text search is insufficient to assert absence
from the complete executable suite.

## Ranked horizon

The table lists contribution ranks among the new portfolio items. The queue
retains historical items and is authoritative for global ranks and states.

| Rank | Item | Path | Entry state | Useful deliverable |
| --- | --- | --- | --- | --- |
| 1 | `NANODA-TEST-NONVACUITY-1` | Checker | READY, selected | Reproduce and repair ineffective literal hash tests; small tested patch and PR draft |
| 2 | `ARENA-LET-REGRESSION-1` | Corpus | READY | Audit current duplicates and package one useful existing let mismatch regression, or record exact covered/policy boundary |
| 3 | `NANODA-CACHE-REGRESSION-1` | Checker | READY | Port the existing staged inference-cache witness into a maintainable current checker unit test |
| 4 | `SEMANTIC-LET-CONTRACT-1` | Semantics | READY | Focused reference/export-contract clarification of let annotation checking before reduction |
| 5 | `HSBM-PILOT-1` | All, initially checker | READY | Six fresh commit assessments with explainable selection and at most two actionable regression candidates |
| 6 | `NANODA-DEFEQ-CACHE-1` | Checker | READY reserve | Isolate eager-mode negative-cache behavior introduced by PR #31; execution is a later gated follow-up |
| 7 | `ARENA-INDUCTIVE-ISOLATION-1` | Corpus | READY reserve | One independently useful tutorial/inductive rejection-isolation improvement |
| 8 | `SEMANTIC-IMPORT-CONTRACT-1` | Semantics | READY reserve | One clarification packet for reconstruct/validate/retain treatment of serialized metadata |
| 9 | `NANODA-NESTED-REGRESSION-1` | Checker | READY reserve | Exact design for a reserved-namespace enforcement regression, with positive control |
| 10 | `ARENA-THEOREM-CONTROL-1` | Corpus | PLANNED reserve | A theorem accept companion only if current suite review establishes distinct practical value |

The first item has a concrete source diagnosis and a small likely repair, so
its expected contribution per unit effort exceeds a speculative operational
survivor. The Arena let pair already has reusable evidence and potential shared
value, but duplicate and semantic-policy questions increase uncertainty. The
internal cache regression has direct value without requiring another exported
reachability search. The semantic item makes that unresolved contract question
explicit. HSBM follows these cheap concrete opportunities; the pilot is useful
only if it supplies new actionable work. These are ordinal judgments, not
estimated success probabilities. Category membership alone confers no priority.

## Common entry, execution and closure rules

Select one item, commit its work record, bind the exact current source and
existing evidence, and record cumulative active time before substantive work.
READY permits selection and local preparation. For each scientific/test launch,
freeze the exact source, fixtures, test patch, expected cells, tooling revision,
invocation and process controls before launch. A listed cap is a ceiling, not a
substitute for this gate. Reuse current runner/accounting machinery; use an
isolated local checkout, retain failures and repair within the same item and
remaining budget. Do not reopen old runs or reset counters.

Each budget below includes investigation, implementation and repair. Network
counts include source/duplicate GETs and setup downloads; prefer retained exact
source and dependencies. Unavailable setup within the bound produces a precise
blocked result. No new mutation identity, Lean proof launch or external write
is included. Cargo test processes count as scientific test launches even when
their goal is test maintenance. Separate compile-only commands count as builds;
any compiling test invocation also consumes a build slot. Fixes to a current
implementation defect require a new explicitly scoped gate if the item permits
only test changes.

At closure bind patch and validation evidence, explain the contribution decision
and beneficiary, run affected repository validators and the complete current
and historical full-payload suite, refresh derived state using
`scripts/refresh-current-state`, and validate queue/status and generated review.
Choose the highest-value feasible next item after reading the actual result.
PLANNED dependencies becoming complete does not automatically promote or launch
a follow-up. A result that changes the selected candidate or scientific inputs
must be recorded before execution. This planning review launches none of the
listed research items.

## Bounded items and outcome-dependent follow-ups

### NANODA-TEST-NONVACUITY-1

At current Nanoda `4c544ed4099c8227f07d5de77ad1e69fb0740a27`, `hash_test0`
uses a helper with both native-literal extensions disabled. The literal
constructors return `Option`; the source predicts that the equality/hash checks
compare `None` repeatedly. This is a source-supported test-effectiveness defect,
not an observed checker correctness defect.

Use 90 active minutes, at most 8 read-only/setup requests, 3 build reservations
(600 seconds each), and 4 test processes (120 seconds each). First reproduce
with assertions that actual literals were constructed. Configure the test before
constructing the export/DAG; enabling a flag after construction can leave the
optional Nat storage unavailable. Require constructed expression variants and
expected contents, preserve useful same-value interning checks, and retain a
disabled-extension control. Prefer a test-local configuration change. Run the
focused test and current upstream test suite within the bound. Finish with one
small patch, plain-language PR draft, exact test evidence and recommendation.
If current code or duplicate coverage falsifies the premise, record that result
and move to the Arena or existing cache candidate. Success supplies a calibration
case for HSBM; it does not require a broad mutation campaign.

### ARENA-LET-REGRESSION-1

Use the exact existing 601-byte let-value mismatch/control and the 9face reuse
evidence. Inspect the current complete test inventory, static resources,
generated tutorial cases and executable bindings. Positive tutorial lets alone
do not prove missing negative coverage. Resolve whether proposed outcomes are
normative, documented observer behavior, or a permitted characterization.
`either` requires positive support for permitting both outcomes; missing
authority alone does not justify it. Defer strict semantic claims to
`SEMANTIC-LET-CONTRACT-1` if needed.

Use 90 active minutes, 12 read-only/setup requests, 2 static `build-test`
reservations (300 seconds each), zero checker/proof/mutation launches and zero
new NDJSON scientific variants. Prepare at most one small package reusing the
existing bytes, with a control only when it adds practical isolation value. If
covered, bind the exact test relationship and prepare no duplicate. If policy
is unresolved, prepare the exact example and a focused question, withholding
an unsupported test outcome. Reuse the inventory and packaging evidence in
`ARENA-INDUCTIVE-ISOLATION-1`; that reserve may also perform its own bounded
preflight and does not depend on the let contract being resolved.

### NANODA-CACHE-REGRESSION-1

Reuse `SURVIVOR-CACHE-1`'s internal same-checker sequence and malformed-let
control pair. Historical `4db8bcc` is a 2020 architecture; current checked and
unchecked cache maps require explicit source continuity, not textual patch
reuse. Preserve the existing export-reachability result as bounded unresolved.

Use 90 active minutes, 8 read-only/setup requests, 3 builds (600 seconds each)
and 4 tests (120 seconds each). Bind current `InferFlag`, lookup/write policy,
same-pointer lifetime and failure assertion. Port at most the existing pair,
run the current focused/full suite, and prepare a test-only PR draft. Historical
mutant results are supporting prior evidence; no current mutant result is
claimed without a separate frozen launch. If an equivalent current test exists,
record reuse. If the contract changed, explain it and reassess the new eager-mode
candidate. A useful internal regression does not require public export impact.

### SEMANTIC-LET-CONTRACT-1

The question is whether, and under which input/environment assumptions, a raw
let expression's declared annotation and value must be checked before zeta
reduction can erase the let. Reuse the exact let/control evidence, frozen
declaration-validation denotation and prior authority deferral. Distinguish a
typing judgment from the admissible-input precondition of a reduction API.

Use 120 active minutes and at most 8 primary-source GETs; zero build, checker,
proof, mutation or new export launches. Produce one short clarification packet
with exact formal/source statements, assumptions, a minimal existing example,
open alternatives, and a proposed Lean reference/export-contract documentation
change or precise maintainer question. It may conclude no new question is useful
if an existing qualified source settles it. No catalog status or approved source
is changed. Any authority qualification follows its existing successor gates
and repository adjudication skill. Success can guide Arena outcome language;
an unresolved result must not prevent a separate implementation-contract test.

### HSBM-PILOT-1

Reuse the bounded methods review in `semantic-methods-review.json`. Prior work
on boundary values, change-directed testing, test-budget reuse and tangled
commits supports extending existing practice; it does not establish novelty or
yield for this Lab method. Record a compact selection/analysis tool and JSON
ledger using ordinary git inspection; no new framework is justified initially.

Use 120 active minutes, at most 8 primary-source/setup GETs, and zero builds,
checker, proof, mutant or new export launches. Freeze all reachable non-merge
commits in `713c245191f7afbc4e996f853ca3131b9b11ec27..TIP` (lower endpoint
exclusive), with TIP the bound current Nanoda revision. Include merged-branch
changes rather than restricting discovery to direct first-parent commits.
Exclude known calibration commits `9c3a447`,
`4db8bcc`, `404660c`, `6524aed`, and `0928383` from fresh yield. Rank by explicit
diff signals (defaults/options, parser/representation, caches/modes, dispatch,
new checks, test deletions/wiring). Record each signal and commit-size confound;
test-file churn cannot establish coverage or automatically lower risk.

Before semantic inspection select four high-ranked commits, taking distinct
available signal families with full-SHA tie breaks, and two uniformly seeded
controls from the remaining eligible commits (seed 20260909). Bind the whole
population, exclusions, scores and selected IDs; do not replace negative cases.
If fewer eligible commits exist, retain the shortfall as a feasibility result.
Inspect at most three boundary candidates per commit and ten descendant commits
from `git rev-list --ancestry-path --topo-order --reverse CHILD..TIP`, capped at
the bound tip. Bind this follow-up set before semantic inspection; separately
record current-tip continuity. Keep the known observations as calibration only.

Each row records interface/input class/state abstraction; before/after mapping;
expansion, remapping, refinement, tightening or test-effectiveness change;
source-inferred vs demonstrated reachability; non-normative candidate obligation;
test reach, assertion strength, executable binding and timing as separate fields;
current continuity; confidence; time; and ex-ante useful action. Explicit zero
was accepted before Serde: omitted-to-zero is a changed default route, not proof
of a globally new value. Projection structure-name comparison is an enforcement
fast-path obligation, not a general theorem that different names imply non-defeq.

Promising feasibility means at least two fresh, nonduplicate candidates from
different commits with an exact path to a small maintainable contribution; name
at most two. Fewer is a negative or bounded unresolved pilot, not a reason to
expand the sample. No comparative efficiency/prevalence claim follows from this
sample. Such a claim needs a separately designed equal-budget comparator and
fresh cases. Promote one candidate into an existing or newly bounded regression
item only after its scope/action gate is recorded.

### Conditional and reserve items

- `NANODA-DEFEQ-CACHE-1`: 90 active minutes, 8 read-only requests, initially
  zero builds/tests/exports. Independently bind current source/test inventory;
  reuse prior cache-test infrastructure if available, without making it a
  prerequisite. Examine PR #31 / `092838312149611649d27781e1d242be4cba4a12` and current
  negative-cache `(x,y,eager_mode)` keys. Derive an exact same-context sequence
  where mode-sensitive outcomes must differ, or a scoped exclusion. Output an
  existing-byte regression protocol/PR outline or exact boundary. Execution
  requires a separately recorded test budget and frozen cells; it is not
  automatically enabled by this source-only assessment's success.
- `ARENA-INDUCTIVE-ISOLATION-1`: reuse the Arena let audit's current inventory
  or establish it through this item's own bounded preflight. Use 90 minutes,
  8 GETs and zero checker,
  proof or byte-generation launches to inspect at most four existing tutorial
  cases for independent rejection reasons (including incomplete recursors).
  Select one useful existing complete-artifact reuse package or explain why
  none is warranted. A new witness requires a later exact scientific gate.
- `SEMANTIC-IMPORT-CONTRACT-1`: independently available 120-minute reserve,
  at most 8 primary-source GETs, zero launches. Use existing restored recursor
  `k`/type, constructor-index and `numIndices` evidence to clarify which serialized
  fields are validated, reconstructed or retained and what an independent
  implementation is required to do. Produce one coherent documentation/contract
  question packet; preserve unresolved authority and combine related issues.
- `NANODA-NESTED-REGRESSION-1`: use an independent current-suite audit, reusing
  HSBM calibration evidence if available, to assess existing coverage. With
  90 minutes, 8 GETs, initially zero test/build/export launches, bind a
  reserved `_nested` namespace candidate/control at the intended public input
  or supported internal API. Check all relevant type traversal paths and failure
  attribution. Finish with one exact regression design or scoped exclusion;
  execution needs its own frozen cells and finite test budget. Do not promote
  the commit author's safety intent into a universal Lean obligation.
- `ARENA-THEOREM-CONTROL-1`: after the let audit or an equivalent current
  inventory preflight identifies a distinct asymmetric refusal risk, a
  60-minute reserve with 6
  GETs, 1 static build (300 seconds), zero checker/new export launches, compares
  the existing theorem accept control with current `tutorial/012_nonPropThm`
  and other accepts. Prepare a companion only if it protects a distinct
  asymmetric refusal risk; otherwise record no contribution. Lab denominator
  completion alone is insufficient, consistent with prior maintainer feedback.

## Follow-through and retained alternatives

For every positive result, recommend a concrete patch/documentation target,
priority, validation prerequisites and exact external action for owner approval.
PR #32 is already submitted; do not duplicate it. Arena #181/#182 are merged;
incorporate substantive feedback when preparing future patches. Their merge
removes the old lack-of-Arena-feedback premise for reassessing the owner-deferred
Kiota clarification, but does not itself authorize an issue. Evaluate that
clarification with the import-contract reserve to avoid separate issue spam.

The one-thread survivor remains a low-value operational reserve until a
deterministic trigger or upstream need strengthens its action path. Transfer
intake still lacks independent custody inputs; the original CVC-4/CVC-5 gates
remain historical and unmet. The ownership pair and remote-payload work remain
retained alternatives with their previous evidence, not artificial substitutes
for concrete corpus/checker work. At closure explicitly compare changed
maintenance needs, literature currency and feasible local blocker removal.
