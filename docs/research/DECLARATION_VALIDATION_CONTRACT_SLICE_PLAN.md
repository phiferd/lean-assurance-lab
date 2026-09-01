# Declaration Validation Contract Slice

## Revised Execution Mandate

- Plan revision: 3
- Recorded: 2026-08-30
- Amended: 2026-09-01 (pre-Milestone-10 specification clarification)
- Status: Milestones 0 through 10 recorded; Milestone 10 stop condition reached;
  no successor experiment is authorized by this mandate
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
- Milestone 8 canonical inventory:
  config/declaration-validation-catalog.json
- Milestone 8 evidence-lock successor:
  config/declaration-validation-evidence-locks/milestone-8-inventory.json
- Milestone 8 validation command:
  `scripts/validate-declaration-validation-catalog`
- Milestone 8 record:
  results/research/declaration-validation-milestone-8.json
- Milestone 9 adversarial-review record:
  results/research/declaration-validation-milestone-9-adversarial-review.json
- Milestone 9 validation command:
  `scripts/validate-declaration-validation-milestone-9`
- Milestone 9 record:
  results/research/declaration-validation-milestone-9.json
- Milestone 10 study design:
  config/declaration-validation-milestone-10-study.json
- Milestone 10 derived populations:
  results/research/declaration-validation-milestone-10-populations.json
- Milestone 10 generated report:
  docs/research/DECLARATION_VALIDATION_MILESTONE_10_STUDY.md
- Milestone 10 validation command:
  `scripts/validate-declaration-validation-milestone-10`
- Milestone 10 Phase-A record:
  results/research/declaration-validation-milestone-10.json
- Milestone 10 historical attestation:
  results/research/declaration-validation-milestone-10-historical.json

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

### Execution Boundary and Completion Gate

Begin with a separately reviewable five-entry candidate pilot. Do not mark the
canonical catalog `MILESTONE_8_CHARACTERIZATION_INVENTORY`, claim Milestone 8
complete, or proceed to Milestone 9 on the basis of that pilot. After review,
full M8 completion requires the exact disposition vector for all 30 frozen
identities accepted by `scripts/validate-declaration-validation-catalog`.

The M7→M8 transition follows the repository-wide frozen-history invariant.
M8 may advance the canonical catalog only when the immutable M7 attestation and
the immutable reviewed-pilot attestation at
`results/research/declaration-validation-milestone-8-pilot-reviewed-historical.json`
both validate unchanged under the historical-transition regression; later
catalog or schema bytes must not be used to reinterpret either predecessor.

The frozen stable semantic identities and their denotations must not drift.
Checker observations must be derived from the structured, content-bound result
evidence required by the catalog validator. While the current gate is in
force, every admitted entry retains `soundness_relevance = NOT_ASSESSED`.

Catalog adjudication may not extend the frozen approved-authority-source
registry. Lack of qualified normative support must remain `PROVISIONAL` or
`UNRESOLVED` with the required unmet requirement or blocker; it must not be
converted into invented authority. The M7 evidence-lock root is immutable: M8
begins with a content-bound sequence-2 successor, and the repaired pilot binds
its explicit sequence-3 repair successor rather than rewriting either earlier
lock. These requirements are enforced by the canonical schemas, validators,
tests, and freeze/report generation paths; this plan does not substitute prose
for those gates.

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

### Milestone 8 Completion — 2026-08-31

The canonical catalog now has status
`MILESTONE_8_CHARACTERIZATION_INVENTORY` and gives an exact disposition to all
30 frozen identities: 27 active catalog entries, one deferred unresolved-kind
identity, and two reserved out-of-scope identities. The active inventory
contains 19 normative candidate obligations and 8 empirical contract
scenarios. All 27 authority assignments remain `PROVISIONAL`; the frozen
approved-authority-source registry is unchanged and empty, so no
implementation behavior, checker agreement, or discovery evidence is promoted
to normative authority. Every entry retains
`soundness_relevance = NOT_ASSESSED`.

The inventory preserves the reviewed five-entry pilot through its immutable
historical attestation and reuses those exact entries. The remaining entries
bind their frozen M5 denotations, role-qualified M4 discovery evidence, and
source-locked implementation mappings. The 149-row M4-to-M5-to-M8 site vector
exhausts every relevant frozen site/identity pair, while the 30-row identity
vector preserves the deferred and out-of-scope boundaries instead of forcing
catalog entries. The sequence-4
`config/declaration-validation-evidence-locks/milestone-8-inventory.json`
successor extends the repaired pilot chain without selecting a new authority
source or rewriting a predecessor.

The generated report, acyclic Milestone 8 freeze manifest, and completion
record are derived from the canonical inventory. Validation requires the
source lock, immutable M7 and reviewed-pilot historical attestations, catalog
validator, M8 completion bindings, and the complete declaration-validation
test suite. This milestone does not perform the independent adversarial review
or construct an Arena negative-coverage denominator. The next authorized
milestone is Milestone 9.

### Milestone 8 Corrective Content Finalization — 2026-08-31

The independent completion review found that the initial inventory closed the
frozen identity and implementation-site surfaces but did not close the frozen
pre-existing-evidence surface. The corrected canonical catalog now derives 41
identity/evidence pairs from exact source-lock witness tags, witness paths and
SHA-256 values in tracked evidence, and the immutable reviewed-pilot Arena
link. Twenty-four pairs are linked to claim-specific catalog evidence; the
remaining 17 have explicit `INSUFFICIENT_FOR_CLAIM`,
`OUTSIDE_THIS_ENTRY_LAYER`, `DEFERRED_TO_LATER_STUDY`, or
`SUPERSEDED_BY_STRONGER_EVIDENCE` dispositions. Silence is mechanically
rejected.

Existing structured result bytes add profile-scoped observations to
`SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`,
`SCENARIO.AXIOM.ADMISSION_POLICY`, and
`SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`. Candidate/control artifacts remain
`DISCOVERY`/`CONTROL`; no existing Lab evidence is promoted to isolation,
normative authority, or soundness evidence. All 27 authority assignments remain
`PROVISIONAL`, the approved-source registry remains empty, and all soundness
relevance remains `NOT_ASSESSED`.

The path-hashed M8 artifact is now labeled a final content manifest rather than
an immutable freeze. Phase A is commit
`714d0466a9f3e0ed1c8a8c6d20508324a48b3a1d`, with canonical catalog SHA-256
`b3e5b9f59de3600d2c42a1549af51e32e0a589be7484ad4dd0b85cab53c0207f`
and a 137-test passing content gate. Do not rewrite that commit.

### Milestone 8 Immutable Historical Attestation — 2026-08-31

The separate Phase-B
`results/research/declaration-validation-milestone-8-historical.json`
attestation has SHA-256
`54facd2b732e612f21d0016b2525cb61a950cf78811b62b9ac8374fa9e15985a`.
It binds 56 core artifacts and 31 selected evidence records to exact Git blobs
at the Phase-A commit. The historical validator loads the Phase-A schema and
content from those blobs, re-derives the critical identity, evidence, site,
mapping, observer, and Arena boundaries, and verifies that the five pilot
entries remain byte-exact. It does not use mutable current paths to define M8.

The M8→M9 transition regression proves that a simulated future current catalog
can differ while the historical M7, reviewed pilot, and corrected M8 continue
to validate unchanged. Wrong catalog blob, catalog SHA-256, historical commit,
and completion/content-manifest bindings are rejected. The final Phase-B gate
passed all required validators and 139 declaration-validation tests with zero
failures or errors. Corrected Milestone 8 is now an immutable historical
predecessor. The next authorized action is a separate Milestone 9 adversarial
review; **Milestone 9 has not started.**

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

### Milestone 9 Completion — 2026-09-01

The corrected Milestone 8 Git-blob attestation is the immutable predecessor.
The sequence-5 pre-review evidence freeze and pre-review catalog preserve its
complete semantic inventory unchanged; the sequence-6 reviewed successor adds
no normative document, mechanized result, checker observation, or witness.

The original M9 implementation was repaired because its renderer had
manufactured favorable challenge dispositions and a zero-correction result.
The canonical adversarial-review record is now an explicitly authored research
decision artifact. It records the counterargument attempted, item-level
adjudications, rationale, evidence, limitations, correction flag, and
before/after statement hashes for all twelve challenges. The presentation
renderer cannot write or regenerate those semantic fields; the validator checks
coverage, evidence resolution, correction consistency, and reviewed-catalog
state without selecting a disposition.

The primary reviewer independently inspected all 19 normative candidates, all
8 empirical layer assignments, the four observer lineages, observability and
duplicate clusters, established-state vacuity, the exact 22-module discovery
boundary and helper call chains, exclusions, soundness language, and non-LLM
reconstruction. That review found zero catalog corrections. This is the
authored outcome of the recorded attacks, not a renderer constant. Incomplete
independent observation and shared semantic lineage remain limitations rather
than favorable evidence; all authority remains `PROVISIONAL` and all soundness
relevance remains `NOT_ASSESSED`.

The reviewed catalog advances only its milestone envelope and evidence-lock
successor; its entries, site and evidence dispositions, identity dispositions,
and frozen semantic denotations are byte-identical to the pre-review inventory.
The milestone-start binding now mechanically verifies the exact corrected M8
attestation commit `15c76f27479dafc4213774b0acffb0d1d84fa2ed`.
The Phase-A content includes a separate Phase-B Git-blob attestation renderer,
historical validator, and M9→M10 transition/tampering regressions. No authority
source was approved, no soundness claim was made, and no Arena denominator or
broad coverage study was started. The Phase-A gate passed 158 declaration-
validation tests and the 11-test historical-transition module (two Phase-B
tests intentionally skipped until the attestation exists). Milestone 10 has
not started.

### Milestone 9 Immutable Historical Attestation — 2026-09-01

The repaired Phase-A reviewed content is commit
`69dad9d13e4802e5ef29c958c60d2ee387293847`. The separate Phase-B
`results/research/declaration-validation-milestone-9-historical.json`
attestation has SHA-256
`6a26aff21d26284b5e6298a33bc0977c9c20b0c063d42aafcf0e33210d821a89`
and binds 46 exact Git blobs at that commit. Historical validation reconstructs
the immutable M8 predecessor, pre-review and reviewed catalogs, authored review,
evidence locks, reports, content manifest, completion, schemas, renderers,
validators, tests, and discovery/identity/source inputs from those blobs.

The M9→M10 regression permits a simulated future current catalog to differ
while historical M7, the reviewed pilot, corrected M8, and reviewed M9 all
validate unchanged. Wrong reviewed-catalog blob, reviewed-catalog SHA,
historical commit, adversarial-review blob, and completion/content-manifest
bindings fail. The active transition module passes all 11 tests with no skips,
and the Phase-B declaration-validation suite passes all 158 tests. Milestone 9
is now an immutable historical predecessor. **Milestone 10 has not started.**

## Milestone 10 — Design the Next Phase Against the Immutable Reviewed M9 Inventory

### Milestone Boundary and Frozen Input

Milestone 10 is a study-design milestone. It must not execute the Arena study
that it specifies or create new substantive semantic evidence.

The immutable reviewed M9 inventory is the frozen eligibility input. Milestone
10 derives the future coverage denominator from that inventory according to the
eligibility rules below. The input must be resolved through
`results/research/declaration-validation-milestone-9-historical.json` and its
exact Git-blob bindings at the M9 Phase-A commit, not through whatever bytes
later occupy mutable current catalog, review, schema, report, or evidence-lock
paths. A mutable current catalog is not an M10 eligibility input.

The frozen M9 state contains no `ESTABLISHED` entry: all 27 active entries are
`PROVISIONAL`, and the frozen approved-authority-source registry is empty. The
current primary normative negative-coverage denominator is therefore expected
to be empty. An empty denominator is a valid Milestone 10 result, not a defect
to repair. No normative coverage percentage may be reported when that
denominator is empty.

If no frozen entry satisfies the complete eligibility conjunction, record the
primary normative negative-coverage denominator as empty. Do not weaken a
criterion, infer authority, perform authority-resolution work, or reinterpret
an unresolved determination to make the denominator nonempty.

This pre-M10 amendment clarifies the future milestone only. It does not start
Milestone 10.

### Authority Is an Input Gate, Not M10 Work

Milestone 10 may define the authority gate that a future primary normative
study requires, but it may not satisfy that gate. Authority resolution remains
a separate governed process. In particular, M10 must not:

- approve normative documentation;
- approve mechanized results;
- create a new version of the approved-authority-source registry;
- promote `PROVISIONAL` to `ESTABLISHED`;
- use checker agreement, consensus, or majority as authority; or
- conduct literature, documentation, source, or mechanization research for the
  purpose of making the denominator nonempty.

Implementation observations remain implementation observations. Checker
agreement and LLM judgment remain non-authoritative. The plan-wide deliverable
named **Research authority resolution** records the Milestone 0 frontier
decision and any separately governed future authority process; it is not
authorization to resolve catalog authority during M10.

### Complete Per-Entry Future-Study Readiness Analysis

Evaluate every entry in the complete frozen reviewed M9 inventory. Preserve an
explicit disposition for frozen deferred or reserved identities so input
closure remains reproducible. Do not short-circuit an entry's analysis because
its authority is `PROVISIONAL` or because another criterion already excludes
it. Logic equivalent to `authority is provisional -> excluded -> stop
analysis` is forbidden.

For every relevant frozen entry, record independent structured determinations
for the study criteria. Reuse frozen catalog vocabulary for kind, layers,
authority (`ESTABLISHED | PROVISIONAL | UNRESOLVED`), and lifecycle (`ACTIVE |
SUPERSEDED | REDUNDANT | OUT_OF_SCOPE`). New readiness determinations must use
the controlled status vocabulary `YES | NO | UNRESOLVED` and carry at least:

~~~yaml
status: YES | NO | UNRESOLVED
basis:
evidence:
blocking_reason_if_any:
~~~

For `study_scope`, `YES` means in scope for the frozen future study, `NO` means
out of that study scope, and `UNRESOLVED` preserves an undecided boundary. This
derived study-scope determination does not alter the entry's frozen catalog
lifecycle.

Do not collapse distinct questions into one overloaded `negative_testable`
Boolean. At minimum, record these three separate dimensions:

`semantic_negative_testability`
: Can an object exist in the modeled semantics that satisfies the applicability
  and reach prerequisites while violating the target predicate?

`arena_representability`
: Can such an object be encoded, exported, transported, parsed, and
  reconstructed through the pinned Arena/export pipeline sufficiently to reach
  the intended observation point?

`isolation_feasibility`
: Can the target violation be exercised without another violated obligation
  independently accounting for rejection?

The per-entry record must be structurally equivalent to:

~~~yaml
entry_id:
kind_eligible:
authority_eligible:
kernel_layer_eligible:
study_scope:
semantic_negative_testability:
arena_representability:
isolation_feasibility:
lifecycle_eligible:
primary_denominator_eligible:
primary_exclusion_reasons:
~~~

Equivalent repository naming is permitted, but the semantic separation is
mandatory. `primary_denominator_eligible` must be mechanically derived from
the individual determinations and frozen catalog values; it must not be entered
as an unexplained Boolean. Every failed or unresolved conjunct must produce an
explicit controlled exclusion reason.

### Two Separate Study Populations

#### A. Primary Normative Negative-Coverage Denominator

This is the strict epistemic denominator for the future Arena normative
negative/isolated-negative coverage study. Membership is derived as `YES` if
and only if the complete conjunction below holds:

~~~text
kind = NORMATIVE_CANDIDATE_OBLIGATION
AND authority.status = ESTABLISHED
AND KERNEL_DECLARATION_VALIDITY is in layers
AND study_scope.status = YES
AND semantic_negative_testability.status = YES
AND arena_representability.status = YES
AND isolation_feasibility.status = YES
AND lifecycle.status = ACTIVE
~~~

`SUPERSEDED`, `REDUNDANT`, and `OUT_OF_SCOPE` are not lifecycle eligible. A
`NO` or `UNRESOLVED` readiness conjunct excludes the entry from this frozen
denominator while preserving the exact determination and reason. Reconstruction,
export-format, trust-policy, and implementation-policy observations do not
become normative kernel obligations merely because they are testable.

The strict denominator is currently expected to be empty because no frozen M9
entry satisfies the authority conjunct. M10 must derive and report that result
without epistemic promotion, denominator substitution, criterion weakening, or
percentage manufacture.

#### B. Provisional Exploratory Candidate Set

Separately identify the provisional normative candidates that may inform a
later, clearly labeled exploratory study. Even though they cannot enter the
primary denominator, analyze them for:

- semantic negative-testability;
- Arena representability;
- isolation feasibility;
- future witness-construction strategy; and
- likely blocking prerequisites.

The exploratory candidate set must never contribute to a normative coverage
percentage, be described as established normative coverage, strengthen
authority, or act as a substitute denominator. Empirical contract scenarios
and profile-specific observations remain separately labeled characterization
context rather than entering either normative population.

Exclusion from the primary denominator does not prohibit later clearly labeled
exploratory testing. Such testing belongs to the successor execution plan and
must preserve its provisional, empirical, and profile-scoped labels.

### Future Isolated-Negative Coverage Contract

For a future negative artifact `x` targeting predicate `P`, the intended
semantic proof obligation is conceptually:

~~~text
Reach(x) AND NOT P(x)
~~~

`Reach(x)` means the evidence-backed applicability and prerequisite conditions
needed to reach the target rule premise. Do not use the word `ESTABLISHED` for
reach or applicability unless referring to the formal authority-status enum.

A future artifact may count as primary normative isolated-negative coverage
only when it has all of the following:

1. a content-bound negative artifact;
2. evidence-backed `Reach(x)` applicability and prerequisite conditions;
3. evidence that `NOT P(x)` holds;
4. a matched positive control;
5. complete competing-obligation analysis;
6. an authority-scoped expected normative rejection; and
7. per-checker rejection attribution where obtainable.

Competing-obligation analysis must identify every other obligation capable of
independently explaining rejection and classify it as:

- satisfied;
- not applicable; or
- unresolved.

If any relevant competing obligation remains unresolved, the artifact may be
recorded as an observed negative case but must not count as isolated negative
coverage. Rejection alone does not establish `Reach(x)`, `NOT P(x)`, or
isolation.

The matched positive control must come from the same construction family where
practicable, repair the target violation, and minimize unrelated semantic
differences. Every unavoidable unrelated difference must be explicit and
justified.

For the authority-scoped expected outcome required by primary normative
isolated-negative coverage:

- an `ESTABLISHED` normative obligation may support an expected normative
  rejection;
- a `PROVISIONAL` normative candidate may not support that expected normative
  rejection; and
- an implementation profile may have evidence-backed profile-specific expected
  behavior, but that behavior is not the normative expected outcome required
  for primary coverage.

Under the immutable M9 state, no provisional candidate has the
authority-scoped expected normative rejection needed to count toward primary
normative isolated-negative coverage. This is not a problem M10 must solve.

Checker attribution rules must bind each observation to the exact artifact,
observer profile, configuration, pipeline stage, and normalized outcome. They
must distinguish export, transport, parse, reconstruction, validation, and
policy behavior where those stages can explain an outcome. Cross-checker
agreement is not a majority oracle and must not be used to infer either
normativity or isolation.

Design the future representation for:

~~~text
obligation
 ↕
positive control
 ↕
negative artifact satisfying Reach(x) AND NOT P(x)
 ↕
competing obligations
 ↕
Arena/export pipeline
 ↕
attributed checker observations
~~~

### Future Witness-Synthesis Design, Not Execution

Specify a future witness-synthesis hierarchy without generating a campaign:

1. **Tier 1 — deterministic premise-specific templates**
2. **Tier 2 — structure-preserving transformations of known-valid artifacts**
3. **Tier 3 — constraint-driven constructors targeting `Reach(x) AND NOT
   P(x)`**

"Fuzz until a checker disagrees" is not a definition of semantic negative-test
generation. It neither establishes the target violation nor isolates its cause.

M10 may inspect and reference existing frozen evidence. It may create only
synthetic fixtures strictly necessary to test M10 schemas, validators, and
derivation logic. Such fixtures must be unmistakably labeled as synthetic
validation fixtures and must not be represented as research findings,
semantic witnesses, Arena coverage, or checker-characterization evidence.

M10 must not create new substantive semantic evidence by running:

- new Arena test campaigns;
- new checker comparison campaigns;
- mutation campaigns;
- generated Lean witness campaigns;
- broad witness synthesis; or
- new cross-validation intended to characterize checker semantics.

No broad negative-coverage, isolated-negative-coverage, synthesis, mutation,
or checker experiment may begin during M10.

### Durable M10 Output and Execution Gates

The durable scientific output must have this derivation structure:

~~~text
immutable reviewed M9 inventory
        ↓
per-entry future-study readiness analysis
        ↓
derived primary normative denominator
        ↓
provisional exploratory candidate set
        ↓
frozen future experiment protocol
~~~

The frozen future experiment protocol must define at least:

- the denominator eligibility algorithm;
- explicit exclusion reasons;
- the exploratory-candidate policy;
- semantic negative-testability;
- Arena representability;
- isolation feasibility;
- the `Reach(x) AND NOT P(x)` evidence contract;
- the matched positive-control contract;
- competing-obligation analysis;
- authority-scoped expected-outcome rules;
- checker attribution rules;
- the synthesis hierarchy; and
- study execution gates.

M10 is responsible for the frozen next-phase study specification, complete
per-entry eligibility/readiness analysis, mechanical denominator derivation,
future isolated-negative coverage contract, future synthesis and attribution
rules, execution gates, and the minimum schemas, validators, generated reports,
content manifests, and historical-freeze machinery needed to make that design
durable. It must verify and consume the completed M0–M9 artifacts, not recreate
their semantic target lock, source lock, characterization schema, inventory,
decision records, or adversarial review.

The future experiment may execute only under a separately authorized successor
plan or milestone after the M10 protocol is historically frozen. That successor
must bind the M10 attestation as its immutable protocol input and satisfy the
protocol's execution gates before producing substantive evidence.

The empty denominator derived during M10 characterizes the immutable M9 input; it does not permanently define the denominator of every successor study. If a separately governed later process changes authority or other eligibility-relevant state, an execution milestone must create a new immutable study-input snapshot, bind the unchanged M10 protocol, re-apply the frozen M10 eligibility algorithm to that snapshot, freeze the resulting denominator, and only then execute coverage. The M10 protocol may not be rewritten merely because eligibility state later changes.

### M10 Historical Freeze

Completion must follow the same two-phase historical pattern used for corrected
M8 and repaired M9:

**Phase A**

1. finalize the complete M10 study-design state;
2. run its required schemas, validators, derivation checks, and transition
   regressions; and
3. commit the exact required content.

**Phase B**

1. create a separate Git-blob historical attestation;
2. bind the Phase-A commit and every exact artifact required to reconstruct and
   validate M10; and
3. prove that later mutable current files and successor research plans may
   evolve without redefining M10.

The Phase-B attestation must validate from the bound historical blobs rather
than mutable current paths. This milestone specification requires that
machinery; this pre-M10 amendment does not build it.

### M10 Phase-A Design Freeze — 2026-09-01

Phase A consumes the immutable reviewed M9 catalog and identity registry only
through the exact Git blobs bound by the M9 historical attestation at commit
`69dad9d13e4802e5ef29c958c60d2ee387293847`. The authored study design records
all eight independent readiness determinations for all 30 frozen identities;
it does not stop analysis after observing the frozen `PROVISIONAL` authority
state. The derived populations contain an empty strict primary denominator,
19 separately labeled provisional exploratory candidates, eight empirical
characterization-context entries, and the one deferred plus two reserved
identities. Because the strict denominator is empty, no normative percentage
is computed or reported.

The frozen protocol defines `Reach(x) AND NOT P(x)`, matched positive controls,
competing-obligation dispositions, authority-scoped expected outcomes, exact
checker attribution, a three-tier synthesis hierarchy, and ten gates that block
substantive successor execution until a separately authorized plan binds this
protocol and freezes a new input-derived denominator. No authority source was
approved, no catalog entry was promoted, and no Arena, checker, mutation, or
witness-synthesis campaign was executed. At the Phase-A boundary, Phase B still
had to bind the committed artifacts as exact Git blobs and pass the successor-
transition and tampering regressions.

### M10 Historical Freeze Completion — 2026-09-01

The Phase-A design content is commit
`2811fdbbe146009775ebdb1bd3b153f59ae503eb`. The separate Phase-B
`results/research/declaration-validation-milestone-10-historical.json`
attestation has SHA-256
`976d450f9f1afd6f1a41c388c5bb623ce524d28aa1d1ac6c6634316eb3a31120`
and binds 24 exact Git blobs at that commit. Historical validation reconstructs
the immutable M9 predecessor, authored M10 design, derived populations,
generated report, content manifest, completion record, schemas, renderers,
validators, tests, and authority documents from those blobs rather than from
mutable successor paths.

The M10-to-successor transition regression permits later mutable study inputs
and research plans to change while the frozen protocol continues to validate.
Wrong study blob, population SHA-256, historical commit, and completion/content-
manifest bindings fail. The complete declaration-validation suite passes all
175 tests with no skips. Milestone 10 has reached its stop condition. No broad
coverage, synthesis, mutation, checker, or authority-resolution work is
authorized by this completed mandate.

### M10 Protocol Erratum 1 — 2026-09-01

The frozen future-witness strategy for `DECL.THEOREM.TYPE_PROP` incorrectly
allowed the matched positive control to be the existing definition-form
artifact. Changing a theorem to a definition removes applicability of the
theorem-specific requirement that the type be a proposition; it does not repair
that premise. The historically attested M10 bytes remain unchanged.

The operative successor rule is: use a Prop-valued theorem in the same
construction family, with a matching valid proof. The definition-form artifact
may remain as auxiliary representability and well-formedness evidence, but it
must not count as the matched positive control for isolated
`DECL.THEOREM.TYPE_PROP` coverage. The related M10 isolation-feasibility result
remains `YES` as a future construction judgment. The denominator, readiness
statuses, exploratory set, empirical context, deferred/reserved set, and M10
stop condition are unchanged.

The canonical correction is
`results/research/declaration-validation-milestone-10-protocol-erratum-1.json`.
It binds the exact M10 historical attestation and exact frozen study-design Git
blob. Phase A must validate the correction, generated report, unchanged M10
bytes, and negative regressions. Phase B must separately bind the Phase-A
erratum content as exact Git blobs. A future execution plan must bind both the
M10 historical attestation and the erratum historical attestation. This erratum
authorizes no coverage, synthesis, mutation, checker, authority-resolution, or
other successor experiment.

### M10 Stop Condition

Milestone 10 ends when:

- the complete immutable M9 inventory has been evaluated for future-study
  readiness without authority short-circuiting;
- the strict primary normative denominator has been mechanically derived, even
  if empty;
- the provisional exploratory set has been identified without epistemic
  promotion;
- the future Arena negative/isolated-negative coverage experiment has been
  specified precisely;
- execution gates are explicit; and
- the specification has been durably validated and historically frozen through
  the two-phase pattern above.

Then stop. The actual broad coverage, synthesis, mutation, or checker experiment
belongs to a successor plan or milestone and must not begin during M10.

## Required Deliverables

This is the cumulative, plan-wide deliverable list for the complete contract
slice. It is not a fresh M10 work list. Items completed during M0–M9 are
immutable predecessor artifacts for M10 to verify and consume. M10 must not
redo the semantic target lock, source lock, canonical characterization schema,
canonical inventory, prior decision records, generated predecessor reports, or
prior adversarial review.

For M10, this list primarily requires the frozen next-phase study
specification, complete per-entry readiness analysis, mechanically derived
denominator and exploratory set, future isolated-negative coverage contract,
synthesis and attribution rules, execution gates, and the minimum new
schemas/validators/reports/content manifest/historical attestation required to
make that design durable. **Research authority resolution** below does not
authorize M10 to approve sources or resolve catalog authority.

The first slice should cumulatively leave durable artifacts for:

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
