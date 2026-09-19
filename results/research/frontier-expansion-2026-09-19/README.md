# Ten candidates for a broader research frontier

Date: 2026-09-19 UTC. Entry repository commit:
`37137169f12eb8f1807e9e3b2b285a5270afca18`.

This is the owner's requested expansion of the candidate pool, following the
[strategy review](../project-strategy-review-2026-09-19/report.md). It is a
proposal memo, not an execution plan, a completed research item, or a second
authoritative queue. No experiment starts here. The canonical queue and Active
status remain unchanged. Bounds below are suggested pilot sizes, not allocated
budgets or authorization to launch.

## Judgment

The immediately executable frontier is too narrow to support a strong
project-wide comparison: it contains two READY source-only assessments, both
derived from retained evidence. The preceding review improved their ordering
but did not adequately expand the alternatives. The broader methods map already
contains promising techniques; those need concrete experimental candidates,
not another comparison restricted to currently unblocked housekeeping.

A small execution frontier remains sensible. A small pool of alternatives does
not. Keep one or two coherent active themes, but compare them against concrete
proposals spanning different failure surfaces, sources of expectations, and
beneficiaries. These ten are new candidate pilots for this review, not claims
to have invented ten research methods. Several operationalize techniques already
discussed in the [methods map](../../../docs/research/ASSURANCE_METHODS_MAP.md).

The constitution values shared assurance, not a particular technique or a
single vulnerability. That supports retaining useful preventive tests while
allocating more effort to discovering previously unobserved behavior. Finding
no defect in a well-designed experiment can still produce a useful tool,
conformance suite, measured boundary, or decision to stop.

## What the bug record actually supports

- A demonstrated Nanoda test defect: `hash_test0` compared absent optional
  values instead of exercising native literal construction. An assertion-only
  change reproduced the failure; the repair passed the bound suite. This is a
  [test-effectiveness defect](../nanoda-test-nonvacuity-1/report.md), not a
  demonstrated checker soundness defect.
- The [Collatz retrospective](../../collatz-retrospective/REPORT.md)
  rediscovered known official-Lean nested-inductive and Nanoda projection fault
  components against affected/fixed versions. This is substantive capability
  evidence. Its repaired, retrospective, operator-informed execution does not
  establish a novel prospective discovery or general bug-finding rate.
- The record reviewed here does not establish a newly discovered official-Lean
  soundness bug. Fifteen semantic disagreement artifacts are not fifteen bugs;
  implementation policy, stale versions, and unresolved expectations matter.
  Recent preventive tests do not establish defects merely because they pass.

## Candidate experiments

### 1. Verify that the intended theorem was actually checked

**Question.** Can a producer/exporter/checker pipeline report success after
omitting the requested theorem, changing its statement, or failing to account
for a required dependency?

**Pilot.** Start with one small module containing twelve named declarations and
imported dependencies. Trace exact theorem identity and statement through two
supported adapters. Introduce three controlled omission, substitution, or
truncation faults and require the pipeline to detect them. Cap the pilot at
twelve checker launches after its source preflight. If an adapter cannot expose
checked-object evidence, record that specific observability gap.

**Output and value.** A reusable end-to-end sentinel and adapter assertions.
The project has already seen success on a malformed object interpreted as zero
declarations; this tests completeness of ordinary validation workflows, beyond
that known diagnostic case. Reuse
[Comparator](https://github.com/leanprover/comparator) and existing Lab adapters
where applicable: theorem-statement matching and permitted-axiom checking are
existing capabilities, not a reason to build another general framework.

**Entry condition.** Supported producer/import contracts and observable checked
objects. Source lists, file hashes, and exit codes alone are insufficient proof
that the intended theorem was checked. Keep this experiment about object
identity and completeness; candidate 9 concerns its trust assumptions.

### 2. Change the encoding while preserving the mathematical object

**Question.** Can record numbering, legal record order, or expression sharing
change a checker's answer for the same declarations and expressions?

**Pilot.** Freeze twelve small accepted exports and up to four transformations.
Independently decode original and transformed files and require equality of
their canonical expression/environment representations before execution. Use
two implementations and at most 120 launches, including baselines, within a
two-day pilot. Include only transformations permitted by the exact format.

**Output and value.** A reusable transformation library, preservation checks,
and minimized representation-sensitive pairs. This explores fresh public inputs
without relying on arbitrary malformed metadata or checker majority as the
oracle. Existing matched controls are not established metamorphic relations;
the methods map currently records no active or planned metamorphic item.

**Entry condition.** A reviewed preservation argument and independent checks of
the decoder/normalizer. Sharing or ordering restrictions can be legitimate
importer contracts. A divergence first establishes representation sensitivity,
not automatically logical unsoundness.

### 3. Follow one suspicious acceptance through to its consequences

**Question.** Does an unexplained accepted declaration enable an invalid use,
or is it harmless under the implementation's reconstruction policy?

**Pilot.** Select one retained suspicious acceptance, with the supplied recursor
type as the leading candidate. First reproduce candidate and compatible control
at an exact current revision. Only if the premise survives, construct one small
downstream use to test the semantic consequence. Use a two-day cap and a frozen
launch/search budget; do not replace the target after observing failure.

**Output and value.** A minimal impact witness, a scoped explanation that the
supplied information cannot affect the tested use, a stale-result finding, or a
bounded unresolved result. This attempts to bridge the gap between disagreement
and meaningful defect, rather than counting another acceptance difference.

**Entry condition.** The
[import-contract review](../semantic-import-contract-1/report.md) establishes
retention/consumption of the supplied type and limitations of arity comparison,
but no current acceptance or defect. A purported contradiction must use the
actual checked declaration path and have its transitive assumptions audited;
`sorry`, an assumed contradiction, unchecked insertion, or native-evaluation
axioms would not establish the desired kernel soundness claim. No universal
metadata obligation is inferred. This is outside the current constructor-index
audit and needs its own recorded authorization and exact scientific gates.

### 4. Generate valid dependent terms instead of mainly corrupting old fixtures

**Question.** Do kernels agree on valid terms where dependent binders, nested
applications, and beta/let reduction interact?

**Pilot.** Generate a fixed cohort of fifty closed terms with explicit typing
derivations in a small Pi/lambda/application/let fragment. Exclude inductives,
quotients, native literals, and disputed declaration metadata. Freeze a simple
universe discipline using closed numeric levels, excluding the previously
studied imax/ownership cases. Freeze generation rules, seed, cohort, and launch
limits before comparing supported implementations.
Use a two-day cap; keep construction and export failures without replacing cases.

**Output and value.** A derivation-carrying generator and compact positive
conformance suite, with minimized unexpected refusals or disagreements. This
samples interactions beyond the known-premise witnesses used by existing
directed generators.

**Entry condition.** Independent review of the encoded typing rules and reuse
assessment of existing generators. The generator and its derivations are
fallible; neither its output nor checker consensus establishes authority. This
is not an independent held-out transfer claim.

### 5. Test whether prior requests contaminate later validation

**Question.** Can a failed declaration, earlier query, or independent declaration
order change the validation of a later request in the same supported session?

**Pilot.** Freeze six small request sequences and compare each target's outcome
in a fresh environment with its outcome after the prefix. Cover successful
insertion, rejected insertion, and independent-declaration permutations, while
preserving dependencies and fresh names. Use at most two supported public APIs
and a one-day pilot with a fixed request budget.

**Output and value.** Stateful conformance tests for cache isolation, environment
updates, and failure recovery. Candidate 2 changes a single input's encoding;
this candidate changes execution history through a public session boundary.
It extends beyond existing internal same-pointer cache tests without assuming
their unresolved public reachability.

**Entry condition.** Establish promised session and failure semantics first.
If an API deliberately terminates after rejection, continued use is not a valid
test of that contract. Do not manufacture a persistence promise or reopen the
previous cache study under a new name.

### 6. Cross-check substitution against a tiny independent model

**Question.** Do lifting and substitution agree with a separately written
capture-avoiding named-variable model over a finite, explicit fragment?

**Pilot.** Enumerate at most 10,000 small terms/contexts covering nested lambdas,
applications, lets, and valid open terms. Compare operations and compositions
through isolated supported APIs for two implementations. Audit translation to
de Bruijn syntax and alpha-equivalence separately. Cap at two days and assess
reuse of existing formalization before writing a new model.

**Output and value.** Portable operation vectors and an executable independent
model. Killing twelve particular binder-depth mutants does not answer this
question about interactions and independently derived expectations.

**Entry condition.** A tractable fragment, inspectable semantics, and available
API seams. [Lean4Lean](https://arxiv.org/abs/2403.14064) is relevant prior work,
not an assumption that every needed operation already has a ready-made oracle.
Model agreement is bounded evidence, not a full-kernel proof or a reopening of
the completed conditional universe-model experiment.

### 7. Extract compact tests from real proof workloads

**Question.** Can compact, dependency-complete slices of real library proofs
expose compatibility gaps that large smoke tests make difficult to localize?

**Pilot.** Select twelve declarations from three retained library exports using
a syntax-feature rule frozen before observing outcomes. Extract their complete
dependency closures with source/byte provenance and explicit size limits.
Mechanically check closure, then compare available implementations under a
two-day and fixed-launch cap. Preserve oversize and extraction failures.

**Output and value.** A dependency slicer and a compact real-workload suite.
This fills the gap between very large smoke-test exports and tiny bespoke
fixtures; only cases with a demonstrated distinguishing benefit should become
contribution candidates.

**Entry condition.** Retained inputs and trustworthy dependency/environment
accounting. Extraction can change the effective environment; original acceptance
does not automatically transfer to the slice. Previously observed libraries
cannot be relabeled as an unobserved holdout.

### 8. Check whether build settings change validation

**Question.** Does the same public input behave differently under debug,
release, and explicit overflow-check configurations?

**Pilot.** Audit input-influenced arithmetic, narrowing conversions, and
debug-only assertions. Select at most four sites before constructing eight
boundary/control fixtures. Start with one checker and three builds on the same
host, within two days and a fixed execution budget.

**Output and value.** A build-configuration conformance matrix and CI sentinel.
The existing relocation/coverage reproducibility work does not establish that
different compilation modes preserve checker outcomes. Distinguish panic,
timeout, rejection, and acceptance instead of collapsing them into failure.

**Entry condition.** Supported configurations and reproducible build inputs.
Arithmetic or debug assertions are candidate surfaces, not defect evidence.
No second architecture or new machine is presumed available.

### 9. Preserve the theorem's trust assumptions across the pipeline

**Question.** Can a theorem's assumptions disappear from the reported assurance
claim even though the theorem and its statement are checked correctly?

**Pilot.** Build six small fixtures spanning ordinary logical dependencies,
an explicitly allowed extra axiom, `sorry`, and native-evaluation assumptions,
including transitive dependencies. Compare expected assumption sets with Lean's
axiom report, serialized declarations, and the existing validation report on
two supported paths. Deliberately use an insufficient allowed-axiom set as a
negative control. Cap at one day with a fixed launch budget.

**Output and value.** An assumption-preservation matrix and integration
regressions. Reuse Comparator's permitted-axiom checks. The
[Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)
and [axiom documentation](https://lean-lang.org/doc/reference/latest/Axioms/)
make theorem identity and acceptable assumptions explicit parts of validation.

**Entry condition.** Pin the exact toolchain's trust mechanism and distinguish
declared extra assumptions from kernel unsoundness. An allowed axiom is not a
bug merely because the kernel accepts a theorem depending on it. The target is
lost or misleading assurance information, separately from candidate 1's
checked-object completeness.

### 10. Find compact valid inputs with disproportionate checking cost

**Question.** Where do sharing, repeated subterms, or normalization depth cause
large jumps in runtime or memory for otherwise small valid inputs?

**Pilot.** Choose two well-formed term families, six bounded sizes, and two
implementations: at most 24 launches, ten seconds each, with a fixed memory
limit and stop-at-first-limit policy per family/implementation. Bind validity
controls and exact inputs before launching.

**Output and value.** A reproducible resource-regression corpus and measured
operating envelopes. Availability and predictable validation cost matter to
ecosystem trust independently of acceptance correctness. This investigates
public-input scaling rather than the historical one-thread mutation survivor.

**Entry condition.** Comparable supported fragments, verified process cleanup,
and reliable resource measurement. A few finite points do not establish an
asymptotic complexity result; different optimization choices alone are not bugs.

## Recommended selection

First choice for a new discovery pilot: **2, representation-preserving
transformations**. It offers broad new inputs, an explicit preservation check,
and reusable shared tests without depending on unresolved rejection policies.
The main risk is establishing legal transformations and avoiding a faulty
equivalence oracle.

Next: **1, intended-theorem completeness**, for immediate practical assurance
and a concrete existing warning signal; then **4, valid dependent-term
generation**, for wider exploration of core reduction behavior. Candidate **3**
is the high-impact conditional option if its current-acceptance preflight
succeeds. These priorities are judgments, not measured defect-yield estimates.

The existing constructor-index audit remains a cheap, bounded contribution
opportunity, but should not define the project's discovery strategy. The
one-thread historical survivor assessment is a reserve, not the natural next
research theme merely because its entry gates are already satisfied.

When selecting a candidate, record its bounded plan, Active status, and canonical
queue together, perform a focused literature/reuse and duplicate check, then
bind exact scientific and tooling inputs before execution. Do not launch ten
parallel experiments or automatically mark these proposals READY. Reassess
after the first pilot using useful new behavior exposed, reusable/adoptable
outputs, limitations learned, and actual investigation cost—not closed-item
counts or a promised number of bugs.

This memo changes no scientific result, frozen artifact, milestone gate,
catalog, upstream disposition, or external-action authorization.

Review checks: an independent local review found the ten pilots distinct and
the proposed ordering defensible, and prompted narrowing candidate 7's question
to match its actual experiment and candidate 4's universe discipline to avoid
repeating known distinctions. The ten-entry count, local links, and current
queue readiness were checked. No scientific suite was rerun for this
proposal-only addition; the preceding strategy review retains its own complete
validation record.
