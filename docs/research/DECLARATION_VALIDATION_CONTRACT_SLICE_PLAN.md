# Declaration Validation Contract Slice

## Revised Execution Mandate

- Plan revision: 2
- Recorded: 2026-08-30
- Status: active execution mandate; Milestones 0 through 7 recorded
- Planning authority: F-DECLARATION-VALIDATION-CONTRACT-SLICE in
  docs/RESEARCH_STATUS.md
- Milestone 0 record:
  results/research/declaration-validation-milestone-0.json
- Milestone 1 target lock: config/declaration-validation-target.json
- Milestone 1 validation command:
  `scripts/validate-declaration-validation-target`
- Milestone 1 record:
  results/research/declaration-validation-milestone-1.json
- Milestones 2–3 characterization model:
  config/declaration-validation-characterization-model.json
- Milestones 2–3 entry schema:
  schemas/declaration-validation-characterization-entry.schema.json
- Milestones 2–3 validation command:
  `scripts/validate-declaration-validation-characterization-model`
- Milestone 2 record:
  results/research/declaration-validation-milestone-2.json
- Milestone 3 record:
  results/research/declaration-validation-milestone-3.json
- Milestone 4 discovery closure:
  config/declaration-validation-discovery-closure.json
- Milestone 4 validation command:
  `scripts/validate-declaration-validation-discovery-closure`
- Milestone 4 record:
  results/research/declaration-validation-milestone-4.json
- Milestone 5 stable identity registry:
  config/declaration-validation-identity-registry.json
- Milestone 5 generated decision log:
  results/research/declaration-validation-milestone-5-decisions.json
- Milestone 5 validation command:
  `scripts/validate-declaration-validation-milestone-5`
- Milestone 5 record:
  results/research/declaration-validation-milestone-5.json
- Milestone 6 source lock:
  config/declaration-validation-source-lock.json
- Milestone 6 offline validation command:
  `scripts/validate-declaration-validation-source-lock`
- Milestone 6 online verification command:
  `scripts/validate-declaration-validation-source-lock --online`
- Milestone 6 record:
  results/research/declaration-validation-milestone-6.json
- Milestone 7 canonical catalog:
  config/declaration-validation-catalog.json
- Milestone 7 authority rules:
  config/declaration-validation-authority-rules.json
- Milestone 7 generated report:
  docs/research/DECLARATION_VALIDATION_OBLIGATIONS.md
- Milestone 7 validation command:
  `scripts/validate-declaration-validation-catalog`
- Milestone 7 freeze manifest:
  results/research/declaration-validation-milestone-7-freeze.json
- Milestone 7 record:
  results/research/declaration-validation-milestone-7.json

The adversarial review of the initial plan is accepted.

This revision supersedes the previous execution plan where they conflict.

## Objective

Build the first mechanically reproducible characterization of ordinary Lean
declaration validation, suitable eventually for measuring Arena negative-test
coverage and deriving isolated negative witnesses.

The first slice must not manufacture a universal semantic contract where the
available evidence supports only empirical characterization.

The project must preserve the distinction between:

1. normative candidate obligations; and
2. empirical contract scenarios.

No implementation behavior, checker consensus, mutation result, or LLM
judgment may silently cross that boundary.

## Milestone 0 — Resolve Project Authority Before Implementation

Before introducing the new catalog or schema:

1. inspect the current working tree;
2. inspect all uncommitted changes to canonical status and assurance artifacts;
3. determine whether those changes belong to the current research frontier;
4. preserve them exactly;
5. do not overwrite or race them with overlapping edits.

The current research gate permits a research-only characterization view and
excludes treating that view as a production semantic schema or denominator.

Resolve this explicitly in the first milestone.

Either:

- complete the prerequisite characterization work required by the existing
  gate; or
- record a deliberate frontier change stating that this declaration-validation
  slice supersedes that restriction.

There must never be two simultaneously authoritative descriptions of what
research is authorized.

Update the canonical status artifact as part of this milestone, not at the end.

Record:

- repository HEAD;
- dirty-tree state;
- the disposition of every preexisting change as incorporated, committed
  separately, or deliberately left untouched;
- resulting authoritative research frontier.

Do not begin catalog implementation until this is resolved.

## Milestone 1 — Pin the Semantic Target

Create an explicit target profile for this study.

It must identify at minimum:

~~~yaml
logical_target:
  implementation_or_specification:
  repository:
  revision:
  modeled_judgment:
export_contract:
  format_version:
  exporter_repository:
  exporter_revision:
artifact_producer:
  lean_version:
  lean_revision_if_known:
observer_profiles:
  official_importer:
    revision:
    configuration:
  nanoda:
    revision:
    configuration:
  lean4lean:
    revision:
    configuration:
    lineage_group:
  kiota:
    revision:
    configuration:
    lineage_group:
~~~

Adapt this shape to repository conventions.

Do not treat the following as interchangeable semantic identities:

- the official Lean kernel;
- the official exported-proof importer or checker;
- the exporter;
- the producer Lean version.

If current evidence mixes Lean 4.29.1-produced artifacts, Lean 4.33 observer
behavior, and lean4export 3.1.0, preserve that fact explicitly.

Do not normalize versions by assumption.

The target profile must distinguish the modeled declaration judgment from the
implementation used to observe or approximate it. Targeting an implementation
revision does not by itself make that implementation normative authority.

## Milestone 2 — Preserve the Two-Kind Model

Do not create one universal obligation type.

The canonical characterization object must distinguish at least:

~~~yaml
kind:
  NORMATIVE_CANDIDATE_OBLIGATION
  EMPIRICAL_CONTRACT_SCENARIO
~~~

These are semantically different research objects.

### Normative Candidate Obligation

A candidate requirement on the modeled declaration-validity judgment for which
normative authority may eventually be established.

Example:

> A theorem declaration's type must satisfy the modeled proposition-valued
> requirement.

The kind identifies the object family. Its epistemic standing is carried by
authority.status. An entry may therefore remain in the normative-candidate
family while its authority becomes ESTABLISHED for the pinned modeled
judgment.

### Empirical Contract Scenario

A precisely characterized observable boundary whose normative interpretation
may depend on:

- serialization;
- reconstruction;
- checker policy;
- implementation completeness;
- version;
- trust configuration;
- unresolved specification choices.

Example:

> imax u (v + 1) versus max u (v + 1)

An empirical scenario must not automatically become a normative obligation.
This example is a calibration case for the ontology and does not expand the
ordinary-declaration discovery surface.

## Orthogonal Classification Axes

Use orthogonal fields.

At minimum:

~~~yaml
kind:
  NORMATIVE_CANDIDATE_OBLIGATION | EMPIRICAL_CONTRACT_SCENARIO
layers:
  - KERNEL_DECLARATION_VALIDITY
  - EXPORT_FORMAT
  - RECONSTRUCTION
  - TRUST_POLICY
  - IMPLEMENTATION_POLICY
authority:
  status:
    ESTABLISHED | PROVISIONAL | UNRESOLVED
  basis:
    ...
lifecycle:
  ACTIVE | SUPERSEDED | REDUNDANT | OUT_OF_SCOPE
~~~

A scenario may span multiple layers.

Do not force layers to be singular.

POLICY and RECONSTRUCTION are not lifecycle or authority-status values.

Do not use a free-form numerical or verbal confidence field.

Authority must instead be justified through auditable evidence and explicit
sufficiency rules.

Include soundness_relevance when evidence supports distinguishing declaration
conformance from logical soundness impact. Do not assume all rejection
obligations are equally security- or soundness-critical. Unknown relevance must
remain explicit rather than being inferred from rejection behavior.

## Milestone 3 — Evidence Qualification, Not Evidence Ranking

Do not use a single one-dimensional evidence hierarchy.

Every evidence item must state what role it plays.

Use roles such as:

- NORMATIVE_SUPPORT;
- IMPLEMENTATION_OBSERVATION;
- DISCOVERY;
- ISOLATION;
- CONTRADICTION;
- CONTROL.

An evidence record should identify:

~~~yaml
role:
source_type:
source_lock:
exact_locator:
claim_supported:
assumptions:
~~~

claim_supported should identify a structured catalog claim, predicate, or JSON
Pointer rather than rely only on free prose.

Different evidence establishes different propositions.

Examples:

- a formal theorem may establish a modeled judgment under explicit
  assumptions;
- official documentation may establish intended behavior;
- an implementation site establishes implementation behavior;
- a witness establishes an observable boundary;
- a mutant may establish reach, infection, or isolation;
- checker results characterize implementations;
- checker agreement does not establish normativity.

Lean4Lean must have an explicit lineage classification.

Its relationship to the official C++ kernel must be recorded when using it as
evidence.

If citing a mechanized Lean4Lean result, record:

- exact revision;
- theorem or definition;
- relevant assumptions or axioms;
- relationship between that result and the targeted declaration judgment;
- the command used to check the mechanized result where feasible.

Do not describe all four validator observations as four equally independent
votes.

There is no majority oracle.

## Milestone 4 — Define Discovery Closure

Remove numerical catalog-size targets.

Do not aim for 20, 30, 40, or any other aesthetically convenient number.

Instead define a closed discovery surface.

Specify:

- exact declaration kinds included;
- exact validation phases included;
- exact source modules inspected;
- exact semantic components inspected;
- how shared expression-typing and environment judgments are treated;
- explicit exclusions and their rationale.

The initial slice should state whether it includes safe axioms, safe
definitions, theorem declarations, and safe opaque declarations, and how it
treats unsafe, partial, mutual, inductive, quotient, projection, and native
extension behavior.

For each declared discovery source:

~~~text
every relevant validation site inspected
        ↓
candidate generated or exclusion recorded
        ↓
candidate disposition assigned
        ↓
merge or split decisions recorded
~~~

Completion means the declared discovery surface has been exhausted under the
documented methodology.

It does not mean a desired number of rules was reached.

Traversal into a helper is not automatically a scope expansion. Every
encountered dependency must be:

1. included as an inventoried predicate;
2. referenced as an imported prerequisite judgment; or
3. explicitly excluded with a reason.

This rule prevents ordinary declaration checking from silently expanding the
slice into generalized reduction, projection typing, inductive validation, or
other previously excluded families.

The starting audit should explicitly inspect, without presupposing
classification:

- declaration name freshness;
- duplicate universe parameters;
- free-variable closure;
- metavariable closure;
- universe ownership;
- constant universe-argument arity;
- declaration type well-formedness;
- declaration value well-formedness;
- body/type compatibility;
- theorem proposition requirement;
- declaration self-visibility;
- safe/unsafe dependency restrictions;
- local binder/sort validity where relevant;
- let annotation/value relations;
- other checks encountered in the declared source modules.

Unexpected checks must not be omitted merely because they do not fit the
initial theory.

### Milestone 4 Completion — 2026-08-30

The frozen
`config/declaration-validation-discovery-closure.json` completes this
milestone without creating a characterization catalog. It fixes four primary
declaration kinds, records every inspected ordinary-declaration site across 22
pinned source files, closes the required starting audit with an explicit
four-observer vector, and disposes every reached helper as included, imported,
or excluded. Its `SITE.*` values are provenance identities and its `SEED.*`
values are provisional grouping keys only. Validation and mutation tests are
provided by `scripts/validate-declaration-validation-discovery-closure` and
`tests/test_declaration_validation_discovery_closure.py`.

The traversal preserved two pinned Kiota differences—current-declaration
visibility and universe-parameter ownership—as empirical observations. It did
not promote them, or any checker consensus, into normative obligations. Stable
semantic IDs and durable merge/split decisions remain Milestone 5 work.

## Milestone 5 — Stable Semantic Identities and Durable Decisions

Semantic IDs must be implementation-neutral.

Examples:

- DECL.THEOREM.TYPE_PROP
- DECL.DEF.BODY_TYPE_MATCH
- DECL.ENV.CURRENT_DECL_VISIBILITY
- DECL.UNIVERSE.PARAM_OWNERSHIP

Mutant IDs, source-line numbers, function names, and checker names are
provenance.

They are not semantic identities.

### ID Evolution Rules

- Editorial clarification that preserves the same semantic denotation retains
  the ID and changes the statement hash.
- Widening or narrowing applicability, changing the modeled judgment, changing
  the target predicate, or changing between normative-candidate and empirical
  kinds creates a new ID.
- A replaced entry becomes SUPERSEDED and names its successor.
- Merged entries remain as REDUNDANT tombstones and name the surviving entry.
- IDs are never deleted and never reused for a different semantic object.

Every nontrivial candidate merge or split must produce a durable decision
record containing:

~~~yaml
decision:
inputs:
result:
reason:
evidence:
catalog_hash_before:
catalog_hash_after:
~~~

If one source check encodes multiple externally distinguishable predicates,
split when justified.

If multiple implementation checks implement the same semantic boundary, merge
them.

If it is unclear, preserve separate provisional candidates rather than forcing
a decision.

### Milestone 5 Completion — 2026-08-30

The frozen pre-catalog identity registry assigns 30 implementation-neutral
identities to the complete 21-seed Milestone 4 discovery surface. The generated
decision log preserves one disposition for every seed, including each split,
implementation-site merge, identity reuse, unresolved-kind deferral, and
out-of-scope reservation. Every identity records either one of the two intended
kinds or an explicit unassigned kind, plus its identity state, semantic
statement, applicability, statement hash, source seeds, and decisions. Its
evolution policy forbids deletion and reuse while requiring tombstones for
future supersession and merges.

The decision log is generated by
`scripts/render-declaration-validation-milestone-5-decisions` and qualifies its
Milestone 4 inputs as discovery-only evidence under the Milestone 3 evidence
model. `scripts/validate-declaration-validation-milestone-5` verifies the
schemas, exact seed closure, reciprocal references, identity namespaces,
statement hashes, action cardinality, unresolved and out-of-scope states,
content bindings, and generated-log synchronization. Mutation tests are in
`tests/test_declaration_validation_milestone_5.py`.

This is deliberately not the characterization catalog. The registry assigns no
authority status, semantic layer, soundness relevance, or coverage eligibility.
Milestone 6 must next create the content-addressed source lock needed before
these identities can receive complete source provenance and become catalog
objects in Milestone 8.

## Milestone 6 — Content-Addressed Provenance

Repository HEAD alone is insufficient.

External checker repositories may be ignored or untracked, and local canonical
artifacts may have changed since HEAD.

Create a source lock.

### Source-Code Evidence

Record, where applicable:

~~~yaml
repository_url:
revision:
path:
symbol_or_range:
blob_sha256:
source_role:
~~~

Clarify that blob_sha256 is the SHA-256 digest of file content, not a Git
object-ID algorithm.

### Tracked and Local Evidence

Record:

~~~yaml
path:
file_sha256:
json_pointer_or_case_id:
~~~

### Generated Witnesses

Record:

~~~yaml
artifact_sha256:
generator_or_origin:
relevant_case_id:
~~~

### Normative Documentation

Record:

~~~yaml
document_kind:
version_or_edition:
stable_url_or_doi:
section_anchor_or_page:
retrieved_content_sha256:
claim_supported:
~~~

Do not cite an unversioned latest manual page as durable authority when a
versioned edition, release, commit, or archived representation is available.

### Mechanized Results

Record:

~~~yaml
repository_url:
revision:
module:
theorem_or_definition:
path:
blob_sha256:
assumptions_or_axioms:
verification_command:
target_judgment_mapping:
~~~

Source references must be verifiable from a fresh process.

The system should support two modes.

### Offline Validation

Validate:

- catalog structure;
- tracked evidence hashes;
- local artifact references;
- IDs;
- internal consistency;
- generated-report synchronization.

### Online Source Verification

Additionally:

- fetch or verify pinned external repositories;
- confirm revisions;
- confirm blob hashes;
- confirm referenced paths and symbols where mechanically possible;
- verify versioned documentary or mechanized-source locators where feasible.

Do not silently depend on ignored local checker directories.

Observer configuration should be content-bound where possible. Record the
entrypoint, configuration digest, toolchain or build recipe, and binary digest
when an existing behavioral claim depends on them.

### Milestone 6 Completion — 2026-08-30

The frozen `config/declaration-validation-source-lock.json` content-binds the
full target tuple as nine repository/revision identities. It locks all 22
Milestone 4 discovery sources plus 19 exporter, parser, observer-definition,
toolchain, and build-recipe files; 19 tracked Lab evidence artifacts; 12
existing witnesses; 18 optional local observations; and the exact four
observer configurations. `blob_sha256` is explicitly the SHA-256 digest of raw
file content, not a Git object ID.

`scripts/validate-declaration-validation-source-lock` performs fresh-process
offline validation without requiring the ignored `external/` checkout. It
checks schema conformance, predecessor and tracked-file hashes, JSON locators,
witness origins and stable-identity references, complete discovery-source
coverage, observer configuration digests, and renderer synchronization.
Optional local build artifacts are checked when present and reported missing
without becoming offline prerequisites.

Online mode verifies pinned revisions through the GitHub commit API and fetches
raw source content by exact revision. The frozen live-verification record
confirms 9 revisions, 41 source files, and 13 mechanically checked locator
tokens. Normative-documentation and mechanized-result representations are
present but explicitly empty: Milestone 6 does not promote any source to
normative authority before per-identity review. No catalog entry, layer,
authority status, soundness assessment, or coverage denominator was created.

## Milestone 7 — Canonical Data First

The canonical machine-readable catalog is authoritative.

Human-readable outputs must be derived from it.

Generate or mechanically synchronize:

- obligation and scenario sections;
- summary tables;
- counts by kind;
- counts by layer;
- authority status;
- lifecycle status;
- checker observation summaries;
- unresolved list;
- source mappings.

Do not maintain hand-edited duplicate representations of catalog facts.

The validator must check more than JSON Schema.

At minimum validate:

- unique stable IDs;
- immutable-ID rules;
- valid supersession targets;
- valid merge targets;
- evidence existence;
- evidence hashes;
- JSON Pointer and case references;
- source-lock references;
- allowed kind, layer, and status combinations;
- authority-establishment sufficiency;
- complete observer vectors or explicit NOT_INSPECTED, NOT_APPLICABLE, or an
  equivalent documented state;
- catalog/report hash synchronization.

The generated human report must include the catalog hash from which it was
derived.

### Acyclic Artifact Attestation

Content references must form an acyclic dependency graph.

A decision or adversarial-review record may contain the before and after
catalog hashes. The catalog must not simultaneously content-bind that record in
a way that makes its own hash depend on itself.

Use an attestation order such as:

~~~text
source and evidence locks
        ↓
catalog
        ↓
generated report
        ↓
decision or review records
        ↓
release or freeze manifest
~~~

The catalog may reference decision IDs. A separate release or freeze manifest
should bind the final catalog, generated report, and decision-record hashes
together.

## Authority Establishment Rules

Define explicit sufficiency rules for:

- ESTABLISHED;
- PROVISIONAL;
- UNRESOLVED.

Do not make them excessively rigid if the evidence model genuinely varies by
rule family.

Each authority determination must name a versioned qualification-rule ID and
the evidence that satisfies or fails that rule.

An ESTABLISHED normative candidate must require evidence that establishes
normativity, not merely implementation behavior.

For example, this is insufficient:

~~~text
official rejects
Nanoda rejects
Lean4Lean rejects
Kiota rejects
~~~

That establishes strong behavioral consensus.

It does not alone establish the modeled kernel judgment.

Conversely, a formal source may establish a modeled rule while one
implementation disagrees.

That disagreement is then implementation evidence, not a reason to downgrade
the formal rule automatically.

Document the actual qualification rule used for each established candidate.

### Milestone 7 Completion — 2026-08-30

The authoritative `config/declaration-validation-catalog.json` is deliberately
empty at this milestone. It content-binds the semantic target,
characterization model, discovery closure, stable identity registry, source
lock, entry schema, and authority-rule set. This establishes the canonical
data and generated-view architecture without performing the Milestone 8
per-identity adjudication.

`config/declaration-validation-authority-rules.json` defines six versioned
qualification rules: one for each normative/empirical kind and each of
ESTABLISHED, PROVISIONAL, and UNRESOLVED. An established normative entry must
carry content-bound `NORMATIVE_SUPPORT` aimed at the modeled statement;
implementation agreement cannot satisfy that requirement. Non-established
entries must name unmet requirements, and unresolved entries must preserve a
blocking question, unresolved assumption, or authority contradiction.

`scripts/validate-declaration-validation-catalog` checks the catalog and entry
schemas plus stable-ID immutability, lifecycle and merge/supersession targets,
decision references, evidence and claim pointers, source-lock resolution,
versioned authority sufficiency, exact four-observer vectors, source mappings,
generated-report synchronization, and the acyclic freeze graph. Its focused
test suite exercises populated in-memory normative and empirical entries while
the canonical Milestone 7 catalog remains empty.

The generated
`docs/research/DECLARATION_VALIDATION_OBLIGATIONS.md` includes the canonical
catalog SHA-256 and derives all required summary, observation, unresolved,
source-mapping, normative, and empirical views. The post-catalog decision log
is an empty append-only scaffold. The generated Milestone 7 freeze manifest
binds source/evidence locks, authority rules, catalog, report, and decision
records in an explicitly validated acyclic order. No rule, layer, authority,
soundness assessment, or coverage-denominator membership was assigned.

### Milestone 7 Adversarial Hardening — 2026-08-30

A second, independently conducted adversarial review found that the initial
Milestone 7 validator enforced several labels separately without coupling the
epistemically important relationships between them. Milestone 8 remains
blocked until the corrections below are present. The correction trail is
preserved in the hardened Milestone 7 completion record rather than replacing
the earlier interpretation silently.

The hardened validator now rejects semantic-target-profile configuration as
normative support and mechanically couples every evidence `source_type` to a
compatible content-addressed record kind. `NORMATIVE_SPECIFICATION` and
`AUTHORITATIVE_DOCUMENTATION` can refer only to appropriately classified
normative-document records; `FORMAL_MECHANIZATION` can refer only to a
mechanized-result record; implementation source, checker result, Lab evidence,
and witness types are similarly restricted. `OTHER` evidence cannot support an
authority assignment. These are mechanically tested qualification rules, not
proof that the chosen rules are epistemically sufficient.

Established normative authority now rejects both unresolved and active
supporting assumptions. Any contradiction aimed at either the structured
statement or authority basis blocks `ESTABLISHED`. Because this slice has no
separate soundness-qualification ontology, every admitted entry must retain
`soundness_relevance = NOT_ASSESSED` through Milestone 8.

Stable-ID validation now compares a catalog wrapper's complete copied
denotation—intended kind, semantic statement, applicability, and digest—with
the frozen identity registry. Normative target premises and applicability are
also coupled directly to that denotation. An entry cannot preserve an ID while
substituting the opposite predicate or an `ACCEPT` expectation. Identities
frozen as deferred-kind or reserved-out-of-scope cannot be admitted as active
entries.

Milestone 8 completion now requires an exact disposition vector for all 30
frozen identities. Every `ACTIVE_PROVISIONAL` identity must have a catalog
entry; the deferred-kind identity must remain explicitly deferred; reserved
identities must remain explicitly out of scope. A one-entry catalog cannot
claim completion merely by changing the milestone status and booleans.

Concrete observer outcomes require checker-result evidence that identifies the
same observer profile and outcome. Implementation mappings require an exact
source-bound evidence item, a repository owned by the named implementation,
and a symbol/range bound by the source lock. Post-catalog decisions now require
a tracked content-addressed before-catalog snapshot, verified before/after
statement hashes, the supplied after-catalog hash, and decision-type-specific
merge, split, exclusion, authority, layer, or lifecycle effects.

The frozen Milestone 6 source lock remains unchanged. Milestone 7 adds an empty
sequence-1 evidence-lock root under
`config/declaration-validation-evidence-locks/`; Milestone 8 must create a new
content-bound sequence-2 successor instead of mutating the Milestone 7 or
Milestone 6 lock. The generated report is milestone-aware and exposes
provisional requirements, assumptions, contradictions, and limitations. The
Milestone 7 completion record is schema-validated and deterministically
rendered from exact artifact bindings, and strict RFC 6901 pointer handling
rejects negative indices and malformed escapes.

The final predecessor sweep also corrected the Milestone 4 completion
validator to verify its mutable plan/status and original validator bytes as
historical Git blobs. This is the same non-rewriting predecessor rule already
used for Milestones 5 and 6; current frontier edits no longer make the frozen
Milestone 4 discovery result appear stale.

Milestone 8 should begin with a separately inspectable five-entry candidate
batch. Do not mark the canonical catalog `MILESTONE_8_CHARACTERIZATION_INVENTORY`
until that pilot has been reviewed and the exact 30-identity disposition vector
can be completed without weakening these gates.

### Milestone 7 Residual Adversarial Hardening — 2026-08-31

A final exploit-first pass tested three residual attacks against commit
`0bee1b71fe8d49ebe6a8adb5e4193c507ea2e43a` before changing the validator. All
three primary attacks validated with zero errors: a locally authored snapshot
behind a plausible normative-document URL established `ESTABLISHED` authority;
free-form locator metadata changed a content-bound Kiota `ACCEPT` result into a
catalog `REJECT`; and additional applicability/premise predicates narrowed a
stable normative ID. Redirecting the modeled-judgment pointer to another
resolving target-profile field also validated. The bounded equivalent probes
confirmed the same source-origin problem for `AUTHORITATIVE_DOCUMENTATION` and
a fully schema-conforming self-asserted `FORMAL_MECHANIZATION`, plus empirical
precondition and observation-point drift.

The authority-source repair uses the bounded approved-registry option. The new
`config/declaration-validation-approved-authority-sources.json` is separately
frozen before Milestone 8 and is intentionally empty. A normative-document or
mechanized evidence-lock record must identify an exact preapproved source whose
external identity and authenticated content or repository blob identity match.
Catalog adjudication cannot extend the frozen registry; a future addition needs
a separate explicit authority-source decision, new registry version, and
corresponding architecture update before catalog adjudication. Content
addressing remains only a claim about inspected bytes, never a claim about
external origin.

Concrete checker observations now require an exact JSON pointer to
`/validators/<index>/result/normalized_outcome`. The validator reads the
checker ID, outcome, case ID, and artifact path from the content-bound result
record and maps the checker to the pinned observer profile. Free-form
`exact_locator.secondary` strings remain human annotations and have no factual
authority. A case-ID locator or metadata surrounding an opposite structured
outcome cannot establish a concrete observation.

Stable identity now uses the frozen
`ordinary-declaration-validation.semantic-denotation-projection.v1`. For
normative entries it binds kind, exact modeled judgment, exact frozen
applicability, absence of additional premises, exact target predicate, and
rejection semantics. For empirical scenarios it binds kind, exact frozen
subject scope and precondition, exact stimulus, a single derived pinned-observer
observation point, and the pinned observer population. Profile-specific
outcomes, evidence, authority state, layers, predicate labels, implementation
mappings, and explanatory prose remain non-identity research metadata. Any
change to the canonical semantic projection requires a new stable ID.

The canonical catalog and identity-disposition vector remain empty; the
approved-source registry is empty; soundness remains `NOT_ASSESSED`; and no
Milestone 8 pilot or authority adjudication was started. The limited claim is:
these specific source-authority, checker-attribution, and semantic-identity
forgery attacks are mechanically rejected. This does not prove the authority
model epistemically sufficient.

## Milestone 8 — Build the First Characterization Inventory

Inspect the declared ordinary-declaration discovery surface.

For every discovered item:

1. assign stable ID;
2. classify kind;
3. classify applicable layers;
4. record authority state;
5. record lifecycle state;
6. attach role-qualified evidence;
7. map implementation sites;
8. link existing Lean Assurance Lab evidence;
9. link existing Arena cases where relevant;
10. record unresolved contradictions.

Do not generate substantial new test suites in this phase.

Existing witnesses may be reused.

Minimal probes are permitted only where necessary to disambiguate the
characterization itself, and must become durable evidence.

## Milestone 9 — Adversarial Review as a Reproducible Artifact

Freeze the pre-review catalog.

Record its hash before adversarial review.

Then conduct a separate adversarial review.

Challenge at minimum:

1. Which normative entries merely restate implementation checks?
2. Which entries confuse kernel validity with export behavior?
3. Which scenarios cross multiple layers?
4. Which authority claims rely on implementation consensus?
5. Which supposedly independent sources share lineage?
6. Which entries cannot be observed independently?
7. Which entries are duplicates?
8. Which established entries lack sufficient normative support?
9. Which checks in the declared discovery surface were missed?
10. Which exclusions are poorly justified?
11. Which soundness_relevance claims overreach the evidence?
12. Could another researcher reconstruct the catalog without trusting the LLM?

Each challenge receives:

~~~yaml
challenge:
target:
disposition:
evidence:
statement_hash_before:
statement_hash_after:
~~~

Freeze the reviewed catalog hash afterward.

Do not rewrite history by deleting incorrect earlier interpretations.

Preserve the correction trail.

Bind the pre-review catalog, reviewed catalog, adversarial-review record, and
generated reports through the acyclic freeze manifest defined in Milestone 7.

## Milestone 10 — Design the Next Phase Against the Frozen Inventory

Do not yet execute the broad Arena coverage study.

Design it precisely.

The reviewed inventory hash becomes the frozen denominator input.

Only entries satisfying all of the following may enter the primary
negative-coverage denominator:

~~~text
kind = NORMATIVE_CANDIDATE_OBLIGATION
authority.status = ESTABLISHED
KERNEL_DECLARATION_VALIDITY is in layers
in scope for the frozen study
negative-testable
not superseded, redundant, or out of scope
~~~

Study inclusion and negative-testability must be structured determinations, not
bare Boolean assertions. Record:

~~~yaml
status:
basis:
evidence:
exclusion_reason_if_any:
~~~

Reconstruction, trust-policy, implementation-policy, provisional, unresolved,
and empirical-only scenarios remain visible but are excluded with explicit
machine-readable reasons.

A test may count as isolated negative coverage only when it has:

1. a content-bound negative artifact;
2. a matched positive control;
3. established applicability and reach conditions;
4. evidence that the target predicate is violated;
5. competing-obligation analysis;
6. an authority-scoped expected outcome;
7. per-checker rejection attribution where obtainable.

Merely observing that a checker rejects an artifact does not establish isolated
coverage.

Design the future representation for:

~~~text
obligation
 ↕
positive control
 ↕
negative artifact
 ↕
competing obligations
 ↕
Arena tests
 ↕
checker observations
~~~

Stop before executing a large synthesis or coverage campaign.

## Required Deliverables

The first slice should leave durable artifacts for:

1. **Research authority resolution**

   Canonical frontier and status updated before substantive execution.

2. **Semantic target lock**

   Pinned logical, export, producer, and observer target tuple.

3. **Source lock**

   Content-addressed source provenance for code, local evidence, documentation,
   and mechanized results.

4. **Canonical characterization schema**

   Supporting both normative candidate obligations and empirical contract
   scenarios.

5. **Canonical inventory**

   Covering the declared discovery surface.

6. **Decision records**

   For nontrivial merges, splits, exclusions, authority changes, and
   supersessions.

7. **Generated human report**

   Derived from canonical data.

8. **Validation tooling**

   Offline validation plus optional online provenance verification.

9. **Durable adversarial review**

   With before and after catalog and statement hashes.

10. **Frozen next-phase specification**

    Defining exactly how Arena negative and isolated-negative coverage will
    later be measured.

11. **Freeze manifest**

    Acyclically binding the final catalog, reports, decision records, review,
    and next-phase specification.

## Stop Conditions

Stop and record an unresolved research issue rather than forcing progress if:

- the semantic target cannot be pinned coherently;
- normative and empirical objects cannot be represented without conflation;
- an authority claim cannot be independently supported;
- source provenance cannot be reproduced;
- existing repository conclusions contradict the proposed ontology;
- a discovery-source boundary cannot be exhaustively inspected;
- existing dirty canonical state cannot safely be reconciled;
- content-addressed artifacts cannot be arranged without cycles.

Do not solve ambiguity by silently choosing the interpretation that makes the
project cleaner.

## Explicit Non-Goals

Do not:

- maximize mutation score;
- run another broad autonomous mutation campaign;
- generate dozens of Arena tests;
- open upstream pull requests or issues;
- call checker disagreements soundness bugs without proof;
- formalize the complete Lean kernel;
- begin the independent Rocq project;
- create a new repository;
- use checker voting;
- treat the official importer as identical to the kernel;
- turn 37 empirical boundaries into 37 semantic obligations;
- invent a numerical target for catalog size;
- produce manually maintained reports duplicating canonical data;
- silently expand ordinary declaration validation into inductive-family,
  quotient, projection, generalized reduction, native-extension, compiler, or
  malformed-syntax studies.

## Research Standard

The central question is not:

> How many rules can we extract?

It is:

> Can we produce a closed, reproducible characterization of a bounded Lean
> declaration-validation surface while maintaining a mechanically auditable
> distinction between what is normatively established and what is only
> empirically observed?

The project succeeds if another technically competent researcher can start
from the pinned sources and repository artifacts and independently determine:

- what was inspected;
- what candidates were discovered;
- why candidates were merged or split;
- what authority each candidate has;
- what remains unresolved;
- what evidence supports every claim;
- exactly which normative set would become the denominator for the subsequent
  Arena-coverage experiment.

An LLM may discover, organize, hypothesize, critique, and generate artifacts.

An LLM is never semantic authority.
