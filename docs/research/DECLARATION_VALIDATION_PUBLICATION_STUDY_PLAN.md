# Declaration-Validation Obligation-Sensitive Coverage Study

## Proposed Successor Research Plan

- Plan status: `PROPOSED_NOT_AUTHORIZED`
- Recorded: 2026-09-01
- Proposed frontier ID:
  `F-DECLARATION-VALIDATION-OBLIGATION-COVERAGE-STUDY`
- Predecessor mandate:
  `F-DECLARATION-VALIDATION-CONTRACT-SLICE`
- Immutable M10 predecessor:
  `results/research/declaration-validation-milestone-10-historical.json`
- Immutable M10 predecessor SHA-256:
  `976d450f9f1afd6f1a41c388c5bb623ce524d28aa1d1ac6c6634316eb3a31120`
- Immutable M10 protocol erratum:
  `results/research/declaration-validation-milestone-10-protocol-erratum-1-historical.json`
- Immutable M10 protocol erratum SHA-256:
  `1480e214881bc45c10f23bdac27663c8f31bc2dee6b0e50558c002cae4cdc786`
- Current planning authority: `docs/RESEARCH_STATUS.md`

This document is a proposed successor plan. It does not change the current
research frontier, approve an authority source, promote a catalog entry,
authorize an external action, or begin the study. Activation requires a
deliberate update to `docs/RESEARCH_STATUS.md` after human review.

## Decision Summary

The project has completed and historically frozen the M10 design for a future
obligation-sensitive negative-coverage study. The strict M10 denominator is
empty because every active normative candidate remains `PROVISIONAL`. The next
research question is therefore not how to generate more measurements. It is
whether a bounded set of candidate obligations can be qualified honestly and,
if so, whether premise-sensitive isolated-negative coverage adds assurance
beyond existing Lean Kernel Arena tests and coarse mutation or source-coverage
indications.

The study will:

1. preregister the complete mechanically eligible 15-candidate M10 cohort
   before authority research;
2. discover and freeze candidate authority sources without approving them;
3. approve any admissible authority sources through a separate governed
   decision before catalog adjudication;
4. adjudicate all 15 candidates without substituting easier candidates;
5. freeze whatever strict denominator survives, including an empty one;
6. measure existing Arena isolated-negative coverage against that denominator;
7. compare the isolated result with mutation and source-coverage indications;
8. synthesize missing `Reach(x) AND NOT P(x)` cases under the frozen M10
   contract and its theorem-control erratum;
9. cross-check exact artifacts against pinned validators without voting; and
10. make a preregistered publish, bounded-report, or stop decision.

The paper-level objective is:

> Prove or disprove that obligation-sensitive negative coverage adds
> measurable assurance over existing Lean kernel testing on one bounded,
> normatively grounded trust-boundary slice.

An empty or very small denominator, absent normative documentation, complete
existing Arena coverage, failed synthesis, or no improvement over current
techniques are valid results. The plan must not be weakened to avoid them.

## Constitutional Alignment

This plan advances the constitutional goal only if it preserves all of the
following:

- authority comes from qualified external normative or mechanized evidence,
  never from an LLM, implementation source, checker majority, or the desire for
  a nonempty denominator;
- every claim remains scoped to exact Lean, exporter, corpus, observer,
  configuration, source, and protocol identities;
- unresolved authority, competing violations, parser/reconstruction effects,
  checker disagreements, and negative results remain visible;
- every mature gap ends in a concrete recommendation for a shared corpus test,
  implementation action, further adjudication, or explicit no-action result;
- external actions remain target-specific and human-authorized; and
- M7, reviewed M8, M9, M10, and the M10 erratum remain immutable historical
  predecessors.

The study does not seek to prove Lean correct or create a semantic scoreboard
for validators. It evaluates one bounded method against one frozen slice.

## Pre-Study Work That Must Remain Small

### A. Repository Reproducibility Repair

Before activating this plan, restore the current repository-wide artifact gate.
The current declaration-validation validators pass, but the artifact graph
still binds an older community-workflow digest from before the constitution's
frozen-history addition. The top-level README also still describes Milestones
1 through 9 rather than the completed M10 stop condition.

The repair should be a bounded current-state refresh, not a research milestone:

1. update the README's current-milestone account from canonical status;
2. regenerate the artifact graph through `scripts/build-artifact-graph`;
3. refresh any generated current assurance or community-workflow artifacts
   whose defined generation paths require it;
4. run `scripts/artifact-status --require-current`;
5. run the applicable Milestone 8/9 community-workflow gates; and
6. preserve historical artifacts unchanged.

The study may not start while a required current artifact remains stale or
missing.

### B. Harvest the Reducible-Hidden Positivity Result

The prepared full-recursor reducible-hidden strict-positivity proposal is a
separate completed-work output. It is not part of the declaration-validation
denominator and must not become a study input.

Review:

- `results/action-recommendations/drafts/arena-reducible-positivity-full-recursor-issue.md`;
- `results/investigations/nanoda-ordinary-inductive/reducible-positivity-README.md`;
- the exact candidate/control and cross-validator result bindings; and
- the current duplicate and upstream-state prerequisites required by the
  investigation SOP.

If a human is satisfied and explicitly authorizes the Lean Kernel Arena target,
submit the focused proposal, record the external reference, and update the
action register and current assurance artifacts through their canonical paths.
This plan does not itself grant that authorization. Submission or non-submission
does not block the publication study.

## Immutable Scientific Inputs

An activated successor must resolve all semantic eligibility and protocol facts
from immutable Git-blob attestations rather than mutable current paths.

Required predecessors are:

1. corrected M8 historical attestation;
2. repaired M9 historical attestation;
3. M10 historical attestation;
4. M10 protocol-erratum-1 historical attestation;
5. the M10-reviewed catalog and stable identity registry resolved through those
   attestations;
6. the frozen M10 eligibility algorithm and per-entry readiness decisions; and
7. the frozen M10 `Reach(x) AND NOT P(x)`, control, competing-obligation,
   attribution, and synthesis contracts.

The successor must verify the complete historical chain before creating any
new source registry, catalog successor, study input, denominator, or result.
No mutable path may redefine an M10 eligibility or readiness fact.

## Research Questions

### RQ1 — Authority Qualification

For the preregistered M10-ready cohort, which exact obligations, if any, can be
established for the pinned modeled judgment from version-matched, independently
admissible normative documentation or mechanized results?

### RQ2 — Existing Isolated-Negative Coverage

For the frozen established denominator, which obligations have an existing
Arena case that satisfies the complete M10 isolated-negative contract rather
than merely reaching related checker code or being rejected for some reason?

### RQ3 — Relationship to Coarse Indicators

Where do exact source-line coverage and mutation-kill indications agree or
disagree with obligation-sensitive isolated-negative coverage?

These indicators are secondary observations. Neither is a semantic authority
source or a substitute denominator.

### RQ4 — Directed Synthesis

For established obligations lacking existing isolated coverage, how often can
the frozen tiered strategy construct a content-bound negative artifact
satisfying `Reach(x) AND NOT P(x)`, a matched positive control, and complete
competing-obligation analysis within the preregistered budget?

### RQ5 — Cross-Validator and Ecosystem Value

Do the exact generated or newly isolated cases expose attributed implementation
differences, confirm consistent handling, strengthen shared Arena coverage, or
produce an evidence-based recommendation of no external action?

## Preregistered Qualification Candidate Set

### Mechanical Selection Rule

The default cohort contains every M10 readiness entry satisfying all of:

```text
input_disposition = CATALOG_ENTRY
AND frozen_classification.kind = NORMATIVE_CANDIDATE_OBLIGATION
AND frozen_classification.authority_status = PROVISIONAL
AND frozen_classification.lifecycle_status = ACTIVE
AND study_scope.status = YES
AND semantic_negative_testability.status = YES
AND arena_representability.status = YES
AND isolation_feasibility.status = YES
```

This rule uses only immutable pre-authority M10 properties. It does not inspect
documentation quality, Arena coverage, mutation outcomes, synthesis success, or
checker agreement when selecting the cohort.

The exact result is 15 candidates:

1. `DECL.ENV.NAME_FRESHNESS`
2. `DECL.UNIVERSE.PARAM_UNIQUENESS`
3. `DECL.EXPR.NO_LOOSE_BOUND_VARS`
4. `DECL.UNIVERSE.PARAM_OWNERSHIP`
5. `EXPR.CONST.UNIVERSE_ARITY`
6. `DECL.TYPE.SORT_VALUED`
7. `DECL.VALUE.TYPE_MATCH`
8. `DECL.THEOREM.TYPE_PROP`
9. `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`
10. `EXPR.BINDER.DOMAIN_SORT`
11. `EXPR.PI.CODOMAIN_SORT`
12. `EXPR.LET.ANNOTATION_SORT`
13. `EXPR.LET.VALUE_TYPE_MATCH`
14. `EXPR.APP.FUNCTION_TYPE`
15. `EXPR.APP.ARGUMENT_TYPE_MATCH`

The preregistration validator must rederive this list from the exact historical
M10 study blob and reject additions, omissions, reordering-based semantic
changes, or mutable-current substitution.

### Semantic Family Labels

Family labels are descriptive strata for analysis, not authority or eligibility
criteria:

- environment boundaries:
  `DECL.ENV.NAME_FRESHNESS`, `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`;
- universe boundaries:
  `DECL.UNIVERSE.PARAM_UNIQUENESS`,
  `DECL.UNIVERSE.PARAM_OWNERSHIP`, `EXPR.CONST.UNIVERSE_ARITY`;
- declaration expression and typing boundaries:
  `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.TYPE.SORT_VALUED`,
  `DECL.VALUE.TYPE_MATCH`, `DECL.THEOREM.TYPE_PROP`;
- binder and let boundaries:
  `EXPR.BINDER.DOMAIN_SORT`, `EXPR.PI.CODOMAIN_SORT`,
  `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`;
- application boundaries:
  `EXPR.APP.FUNCTION_TYPE`, `EXPR.APP.ARGUMENT_TYPE_MATCH`.

### No Adaptive Replacement

All 15 candidates must receive an authority disposition. If only three become
`ESTABLISHED`, the strict denominator is three. If none become established, the
strict denominator is empty. No candidate may be added, substituted, split,
merged, narrowed, or broadened merely to improve qualification yield or study
power.

If resource estimates made before authority discovery show that all 15 cannot
be attempted responsibly, a smaller cohort is permitted only through a new,
committed plan revision that:

1. is human-approved before any candidate-specific source discovery begins;
2. derives the subset from frozen M10 properties and preregistered semantic
   strata, not perceived documentation availability;
3. records excluded candidates and the resource rationale;
4. forbids later replacement; and
5. receives a new plan identity and content binding.

Once source discovery begins, the cohort is immutable.

## Authority-Source Qualification Protocol

Authority-source discovery, source approval, and obligation adjudication are
three separate epistemic actions. They must not be collapsed into one renderer,
script, model response, or catalog edit.

### Stage 1 — Freeze the Discovery Protocol

Before retrieving or interpreting new authority material, create a
machine-readable preregistration that binds:

- the immutable M10 and erratum attestations;
- the exact 15-candidate cohort;
- source families and repositories to inspect;
- search queries or navigation procedures;
- retrieval and version-matching rules;
- candidate-source mapping fields;
- roles permitted to propose and approve sources;
- resource and search-closure limits;
- disposition vocabularies;
- publication thresholds; and
- the rule that checker behavior and implementation source cannot qualify
  normativity.

The source-discovery surface should include, where exact provenance permits:

- versioned official Lean reference or kernel documentation;
- release-, revision-, or edition-pinned design documentation with a credible
  normative relationship to the modeled judgment;
- independently inspectable mechanized semantics or results;
- Lean4Lean or related mechanized results only with exact theorem, revision,
  assumptions, axioms, lineage, verification command, and target mapping; and
- primary scholarly artifacts when they state and justify the exact modeled
  rule rather than merely describe an implementation.

Implementation source remains implementation evidence even when it is the
selected logical target. Unversioned latest documentation, search snippets,
LLM summaries, checker consensus, Lab-authored prose, and locally manufactured
"specifications" are inadmissible authority sources.

### Stage 2 — Source Discovery Without Approval

Discovery produces a candidate-source register. Each record must contain:

```yaml
source_candidate_id:
external_identity:
source_kind:
version_or_revision:
stable_locator:
retrieved_content_sha256:
authorship_or_governance_basis:
claims_extracted:
assumptions_or_axioms:
modeled_judgment_mapping:
applicable_candidate_ids:
lineage_and_independence:
retrieval_method:
discovery_disposition:
limitations:
```

Allowed discovery dispositions are:

```text
CANDIDATE_FOR_APPROVAL
IMPLEMENTATION_ONLY
VERSION_MISMATCH
JUDGMENT_MISMATCH
INSUFFICIENTLY_PRECISE
UNAUTHENTICATED_ORIGIN
CIRCULAR_PROJECT_SOURCE
ACTIVE_ASSUMPTION_OR_AXIOM_GAP
DUPLICATE_SOURCE
OUT_OF_SCOPE
```

A source may support several candidate mappings, but common source identity
does not make every mapping valid. Discovery must record plausible negative
and disqualifying evidence as well as favorable material.

The discovery result is frozen before approval. A later approval decision may
accept or reject discovered sources; it may not silently add an unreviewed
source.

### Stage 3 — Separate Authority-Source Approval

Approval creates a versioned successor to the currently empty approved-source
registry. It must be a separately authored, human-reviewed decision made before
catalog adjudication.

For every proposed source, the approval record must state:

- exact external identity and authenticated content binding;
- allowed source type;
- exact scope of claims it may support;
- modeled-judgment relationship;
- assumptions, axioms, and unresolved interpretation limits;
- whether its provenance is independent of the implementation behavior being
  evaluated;
- approval or rejection rationale; and
- approving human decision and date.

Approval authenticates a source and bounds its permissible use. It does not
automatically establish any catalog entry. Catalog adjudication must still show
that the approved source supports the exact frozen denotation under the
applicable authority rule.

The approved registry is frozen before adjudication. Adjudication cannot extend
it. Any later source requires a new governed registry successor and a new study
input; it cannot be inserted to rescue a candidate or denominator.

### Stage 4 — Two-Entry Process Sentinel

Before adjudicating the remaining cohort, exercise the full discovery,
approval, evidence-lock, and adjudication path on these two fixed entries:

1. `DECL.THEOREM.TYPE_PROP`; and
2. `EXPR.LET.VALUE_TYPE_MATCH`.

They are selected because both were part of the historical five-entry M8 pilot
and have existing content-bound evidence families. The theorem entry also
exercises the binding to M10 protocol erratum 1. They are not selected because
their authority is expected to be easy.

The sentinel succeeds when the process can reproduce the source decision,
apply the authority rules without source fabrication, preserve the frozen
semantic IDs, and validate both outcomes. It does not require either entry to
become `ESTABLISHED`.

If the sentinel exposes an epistemic or architectural flaw, stop before the
remaining 13 adjudications. Repair the plan or qualification architecture
through an explicit successor. Do not weaken validation or reinterpret the
sentinel outcome.

### Stage 5 — Adjudicate All 15 Candidates

For each frozen candidate:

1. preserve the exact stable identity and canonical semantic denotation;
2. evaluate every approved source mapping relevant to that identity;
3. record supporting, limiting, and contradictory evidence;
4. apply the versioned qualification rule;
5. assign `ESTABLISHED`, `PROVISIONAL`, or `UNRESOLVED` as the evidence requires;
6. preserve `NOT_ASSESSED` soundness relevance unless a separate governed
   soundness process is authorized;
7. record exact unmet requirements or blockers for non-established outcomes;
8. retain all implementation observations as implementation evidence only; and
9. record any discovered denotation error as a correction proposal rather than
   mutating the existing semantic ID.

If an approved source supports a narrower, broader, or different obligation
than the frozen ID, the existing candidate does not become established. Record
the mismatch. A new identity or catalog correction requires its own decision
and cannot enter this frozen study denominator retroactively.

## Denominator Freeze

After all 15 authority dispositions validate, freeze a new immutable study
input containing:

- the immutable M10 and erratum bindings;
- the preregistered candidate cohort;
- frozen source-discovery result;
- frozen approved-source registry successor;
- all candidate authority decisions;
- the reviewed catalog successor;
- the re-applied unchanged M10 eligibility algorithm;
- the strict primary denominator;
- the separately labeled provisional/unresolved exploratory set;
- the empirical and deferred/reserved boundaries inherited from M10;
- the corpus and observer inputs proposed for execution; and
- the execution and reporting budgets.

The strict denominator contains exactly the cohort entries that satisfy the
unchanged M10 primary conjunction after adjudication. The denominator is not a
hand-entered list.

Report raw counts for every disposition. If the denominator is empty, report
no normative coverage percentage and do not execute the primary normative
coverage experiment. An optional exploratory execution may occur only if it
was separately preregistered, remains visibly non-normative, and has a distinct
budget and report.

### Scientific-Claim Tiers

These thresholds affect claim scope and publication framing, not denominator
membership:

- `EMPTY_DENOMINATOR`: zero established obligations; report the authority gap
  and do not claim normative coverage;
- `BOUNDED_PILOT`: one to four established obligations or fewer than three
  represented semantic families; execute only the exact bounded study and make
  no broader methodology claim;
- `NONTRIVIAL_BOUNDED_STUDY`: at least five established obligations spanning at
  least three preregistered semantic families; eligible for the full bounded
  paper-level analysis.

These are transparent study-planning thresholds, not claims that five rules are
semantically representative or that one threshold proves adequacy.

## Experimental Protocol

### Phase 1 — Freeze the Existing-Corpus Baseline

Before examining missing coverage systematically, freeze:

- exact Arena repository revision;
- exact materialized corpus identities and content hashes;
- exporter, producer, parser, reconstruction, and normalization identities;
- observer profiles, configurations, binaries, and build recipes;
- test-to-artifact mappings;
- timeout and resource policy;
- prior-known cases and witnesses; and
- all scripts and schemas used to classify isolated coverage.

The study is not blind: the repository already contains some candidate cases,
witnesses, and mutation results. The preregistration must identify this prior
knowledge. Authority qualification and denominator freeze occur before the
systematic baseline coverage mapping so that existing checker outcomes cannot
be used as authority.

### Phase 2 — Classify Existing Isolated-Negative Coverage

For each strict-denominator obligation `P`, inspect existing Arena artifacts
and assign exactly one primary status:

```text
ISOLATED_COVERED
OBSERVED_NEGATIVE_NOT_ISOLATED
REACH_OR_TARGET_VIOLATION_UNRESOLVED
NO_EXISTING_NEGATIVE_CASE
PIPELINE_NOT_REPRESENTABLE_AT_EXECUTION
EXECUTION_UNRESOLVED
```

`ISOLATED_COVERED` requires every M10 element:

1. content-bound negative artifact;
2. evidence-backed applicability and `Reach(x)`;
3. evidence that `NOT P(x)` holds;
4. a matched same-family positive control;
5. complete competing-obligation analysis;
6. authority-scoped expected normative rejection; and
7. exact checker attribution where obtainable.

Rejection alone does not count. A test whose dummy recursor, malformed
metadata, parser failure, or other independent violation explains rejection is
not isolated coverage for `P`.

### Phase 3 — Compute Coarse Comparator Indications

For each denominator entry, separately record:

- whether relevant implementation source locations are covered by at least one
  corpus input under the frozen configuration;
- whether a mapped semantic mutant is killed, survives, is equivalent,
  reference-aligned, or unavailable;
- whether any existing case is linked by prior project evidence; and
- limitations preventing a comparator observation.

Use controlled labels such as:

```text
SOURCE_REACHED
SOURCE_NOT_REACHED
MUTANT_KILLED
MUTANT_NOT_KILLED
NO_FAITHFUL_MUTANT
COMPARATOR_UNRESOLVED
```

Do not render `SOURCE_REACHED` or `MUTANT_KILLED` as semantic coverage. The
primary analysis is the cross-tabulation between these contextual indicators
and isolated-negative status.

### Phase 4 — Preregister Missing-Case Synthesis

Only after the baseline statuses and comparator table are frozen, preregister
the synthesis inputs and budgets for uncovered established obligations.

Apply the unchanged M10 hierarchy:

1. deterministic premise-specific templates;
2. structure-preserving transformations of known-valid artifacts; and
3. constraint-driven constructors targeting `Reach(x) AND NOT P(x)`.

For each target, freeze:

- target identity and exact predicate;
- existing valid seed or constructor family;
- proposed matched-control transformation;
- known competing obligations;
- synthesis tier order;
- candidate, checker, minimization, and wall-time budgets;
- interruption and resume semantics;
- success and bounded-exhaustion states; and
- which prior evidence is permitted as synthesis input.

No target receives an expanded budget because early results look promising.
Budget changes require a new preregistered run identity and remain separate from
the original result.

For `DECL.THEOREM.TYPE_PROP`, the operative erratum requires a Prop-valued
theorem in the same construction family with a matching valid proof. A
definition-form artifact remains auxiliary representability evidence and may
not serve as the matched positive control.

### Phase 5 — Validate and Cross-Check Generated Cases

A generated case counts as newly isolated coverage only if:

- the exact candidate and control are frozen before cross-validator feedback;
- all M10 isolation evidence fields validate;
- every competing obligation is `SATISFIED` or `NOT_APPLICABLE`;
- the authority-scoped normative expected result is established independently
  of checker votes;
- raw and normalized outcomes bind exact checker profiles and pipeline stages;
- baseline/control validity is preserved; and
- minimization, when used, preserves all counting predicates rather than only a
  baseline/mutant distinction.

Run the exact artifacts against the frozen official importer, Nanoda,
Lean4Lean, and Kiota profiles when compatible. Preserve `ACCEPT`, `REJECT`,
`DECLINE`, `CRASH`, `TIMEOUT`, `PARSE_ERROR`, and `UNKNOWN` independently.
Agreement is a result, not authority. Disagreement is an exceptional state,
not an automatic bug assignment.

### Phase 6 — Measure Incremental Results

Report at least:

```text
qualification_candidates = 15
authority_established = N
authority_provisional = P
authority_unresolved = U
primary_denominator = N
existing_isolated_covered = A
existing_observed_not_isolated = B
existing_uncovered_or_unresolved = C
synthesis_targets = D
synthesis_isolated_successes = E
synthesis_bounded_failures = F
final_isolated_covered = A + E
coarse_positive_but_not_isolated = G
checker_disagreement_cases = H
external_actions_recommended = I
```

Show exact numerators and denominators. Report percentages only for a nonempty
denominator and always adjacent to raw counts. Do not aggregate empirical
scenarios, provisional candidates, incompatible observers, or unresolved
executions into the normative denominator.

## Interpretation and Publish-or-Kill Decision

The final analysis must assign one of these preregistered outcomes.

### Strong Positive

At least one established obligation that appeared favorable under a coarse
indicator lacks existing isolated coverage, and directed synthesis produces a
new valid isolated case, or the new case exposes an attributed checker
disagreement or actionable shared-corpus gap.

### Moderate Positive

The established denominator has strong existing isolated coverage, and the
study provides a reproducible authority-qualified quantification that was not
previously available. No claim of broad Lean adequacy follows.

### Specification Result

Several apparently fundamental candidates cannot be established because exact
normative material is absent, version-mismatched, ambiguous, circular, or
insufficiently connected to the modeled judgment. The authority gap is the
primary result; the project does not manufacture a denominator.

### Negative Method Result

Obligation-sensitive analysis adds no material distinction beyond existing
testing for the exact denominator, synthesis adds no isolated cases within its
budget, and the authority analysis yields no independently useful specification
finding.

### Inconclusive

The denominator or execution is too small, incompatible, irreproducible, or
blocked to answer the bounded question. Preserve the boundary and stop.

The publication decision must state:

- exact outcome class;
- claim tier (`EMPTY_DENOMINATOR`, `BOUNDED_PILOT`, or
  `NONTRIVIAL_BOUNDED_STUDY`);
- whether a full paper, workshop/short paper, technical report, or no
  publication is recommended;
- evidence supporting that recommendation;
- limitations and nonclaims; and
- whether the research frontier should stop, repeat under a new preregistration,
  or broaden to a later semantic slice.

No new sprawling frontier may begin before this decision is durable.

## External Action Policy

Every mature study finding must enter the schema-backed action recommendation
workflow with:

- concrete action;
- exact target;
- priority;
- prerequisites;
- supporting content-bound evidence;
- security/disclosure assessment where relevant;
- duplicate search where relevant; and
- human authorization state.

Appropriate outcomes include an Arena test proposal, implementation issue,
clarification request, formalization/documentation recommendation, or explicit
no-action result. The study may prepare drafts. It may not submit an issue,
pull request, comment, or disclosure without explicit target-specific human
authorization.

## Required New Durable Artifacts

Use repository conventions and avoid creating duplicate semantic authorities.
At minimum, an activated study requires machine-readable successors for:

1. study preregistration and exact candidate-set derivation;
2. authority-source discovery protocol and result;
3. approved-authority-source registry;
4. per-source approval decisions;
5. per-candidate authority adjudications;
6. reviewed catalog successor and decision log;
7. immutable study input and derived denominator;
8. existing isolated-coverage classifications;
9. coarse comparator observations;
10. synthesis plan, attempts, artifacts, controls, and minimization records;
11. cross-validator results;
12. final analysis and action recommendations;
13. generated human report; and
14. content manifest plus Git-blob historical attestation.

Suggested paths may be chosen during implementation, but canonical facts must
have exactly one machine-readable authority and all prose must derive from it.

The artifact dependency order must remain acyclic, for example:

```text
immutable M10 + erratum attestations
        ↓
study preregistration
        ↓
source-discovery result
        ↓
approved-source registry and approval decisions
        ↓
catalog adjudication and decisions
        ↓
frozen study input and denominator
        ↓
baseline and comparator results
        ↓
synthesis and cross-validator results
        ↓
analysis and action recommendations
        ↓
generated report
        ↓
content manifest
        ↓
historical Git-blob attestation
```

## Required Validation Gates

Before study execution, validators must mechanically check:

- exact M7-through-M10 and erratum historical predecessor validity;
- exact rederivation of the 15-candidate cohort;
- source-discovery closure and frozen-result binding;
- approved-source external identity, scope, assumptions, and predecessor;
- prohibition on catalog adjudication extending the approved registry;
- exact stable-ID denotation preservation;
- authority-rule sufficiency for every `ESTABLISHED` entry;
- complete dispositions for all 15 candidates;
- unchanged M10 eligibility algorithm;
- derived rather than hand-entered denominator;
- separation of primary, exploratory, empirical, and deferred populations;
- frozen corpus, observers, budgets, and prior-knowledge register; and
- M10 erratum application.

Before final claims, validators must additionally check:

- complete baseline disposition for every denominator entry;
- all isolated-coverage evidence elements;
- comparator labels are not rendered as semantic coverage;
- synthesis attempt and budget closure;
- candidate/control content bindings;
- competing-obligation completeness;
- exact checker attribution and raw-result bindings;
- generated report synchronization;
- action-recommendation completeness;
- claim-tier and publication-decision derivation; and
- historical-transition regressions proving M7 through final study history
  remain unchanged under later mutable successor state.

The implementation should provide one focused validation entrypoint for the
new study while continuing to run the existing declaration-validation source,
catalog, historical, M10, erratum, and focused unit gates. A validator may
enforce procedure and evidence bindings; it may not select favorable authority
or research dispositions.

## Execution Stages and Stop Gates

### Gate 0 — Frontier Authorization

`docs/RESEARCH_STATUS.md` deliberately activates this plan and records the
disposition of the completed M10 frontier. Without this gate, do not implement
or execute the successor study.

### Gate 1 — Current-State Repair

Artifact graph, public status, README, and applicable assurance gates are
current. Historical artifacts remain unchanged.

### Gate 2 — Preregistration Freeze

Immutable M10/erratum inputs, complete cohort, source-discovery protocol,
budgets, claim tiers, and stop rules validate before authority research.

### Gate 3 — Source-Discovery Freeze

The closed discovered-source corpus and all favorable/adverse dispositions are
frozen before approval.

### Gate 4 — Authority Approval Freeze

A separately governed approved-source registry successor and decisions are
frozen before catalog adjudication.

### Gate 5 — Sentinel Validation

The two fixed sentinel entries complete the full process without epistemic or
architectural failure. Their authority outcomes may be unfavorable.

### Gate 6 — Complete Adjudication

All 15 candidates have validated dispositions. No adaptive candidate change has
occurred.

### Gate 7 — Denominator Freeze

The unchanged M10 algorithm derives and freezes the exact denominator and claim
tier before any primary study run.

### Gate 8 — Baseline and Comparator Freeze

Existing isolated-coverage and coarse comparator results are complete and
frozen before directed synthesis.

### Gate 9 — Synthesis Freeze

Targets, strategies, budgets, controls, and prior inputs are frozen before
candidate generation or new checker feedback.

### Gate 10 — Result and Recommendation Closure

Every target has a completed, bounded-failure, incompatible, or unresolved
result; every mature finding has a concrete recommendation.

### Gate 11 — Publish-or-Kill Decision

The preregistered outcome class, claim tier, publication recommendation, and
frontier recommendation are durable before any later slice begins.

### Gate 12 — Historical Freeze

The final study is bound through a two-phase content commit and Git-blob
historical attestation. Later current artifacts cannot redefine it.

## Stop Conditions

Stop without forcing progress if:

- the current artifact graph cannot be restored without rewriting history;
- immutable M10 or erratum inputs fail historical validation;
- the candidate cohort cannot be reproduced exactly;
- source provenance or external identity cannot be authenticated;
- the approval process cannot distinguish normative support from
  implementation behavior;
- the sentinel exposes an uncorrected epistemic-boundary flaw;
- authority adjudication would require changing a frozen semantic ID;
- no candidate becomes established;
- the denominator cannot be derived without weakening M10 eligibility;
- competing obligations cannot be closed for a purported isolated case;
- checker or pipeline attribution cannot be reproduced;
- execution exceeds its frozen budget; or
- dirty current state cannot be reconciled without overwriting unrelated work.

Some stop conditions still yield valid study results. In particular, zero
established obligations is a specification result, not an implementation
failure. Record the result, recommendation, and nonclaim rather than continuing
until the denominator becomes nonempty.

## Explicit Non-Goals

This study must not:

- establish a desired number of obligations;
- select candidates after inspecting documentation quality;
- replace failed candidates with easier ones;
- infer authority from official implementation source, observer agreement,
  mutation behavior, Arena behavior, or LLM judgment;
- call source reach or mutation killing semantic coverage;
- report a normative percentage for an empty denominator;
- hide known prior evidence or claim the retrospective baseline is blind;
- run a broad mutation, fuzzing, or unrelated checker campaign;
- expand into inductives, recursors, quotient, projection, generalized
  reduction, native extensions, compiler behavior, or a new proof assistant;
- formalize the complete Lean kernel;
- build a generalized dashboard or provenance system beyond what the study
  mechanically requires;
- contact an external project without target-specific human authorization; or
- broaden the frontier before the publish-or-kill decision.

## Completion Condition

The proposed frontier is complete when a fresh process can verify:

1. the exact preregistered cohort and immutable M10/erratum inputs;
2. the complete authority-source discovery and approval trail;
3. the authority disposition of all 15 candidates;
4. the mechanically derived denominator, including an empty denominator;
5. every existing isolated-coverage classification;
6. every comparator observation and its non-authoritative scope;
7. every synthesis target, budget, attempt, control, and result;
8. every checker observation and pipeline attribution;
9. every concrete action recommendation or no-action result;
10. the preregistered outcome and publication decision; and
11. the immutable historical binding of the complete study.

The project must then stop this frontier. A later formal-semantics program,
broader obligation slice, or repeated release study requires a new deliberate
frontier decision.

## Authorization Boundary

Writing or reviewing this proposal does not activate it. The next authorized
action after proposal review is a deliberate human decision to:

1. accept the plan unchanged and update `docs/RESEARCH_STATUS.md`;
2. revise the plan before any authority-source discovery; or
3. reject or defer the study.

Until that decision is durable, only the bounded reproducibility repair and
already-governed review of prepared external-action drafts may proceed.
