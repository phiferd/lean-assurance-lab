# Rule-Level Evidence Factoring Experiment

- Research snapshot: 2026-08-29
- Repository revision inspected: `debb4606597da9bd27ca4cbca7e3742f294a68dc`

## Scope and question

This Phase 1 experiment tests, rather than assumes, the hypothesis that some
existing rule-level findings can become durable assurance objects whose
identity is independent of the validator, mutant, generator, and checker set
that produced their evidence.

The stronger question is:

> Can an existing finding be represented independently of its discovery
> implementation while preserving what gives the statement authority, its
> contract layer, the isolation of the violation, every validator's actual
> behavior, and the remaining unknowns?

“Independent of the discovery implementation” does not mean that an empirical
claim can never name an implementation. A stable claim about Nanoda's importer,
for example, may intrinsically name Nanoda; what must not define its identity is
the particular mutant or witness generator that happened to expose it.

This document is an analytical factoring exercise, not a production schema.
It does not add generators, validators, metrics, mutation infrastructure, or a
matrix implementation. It does not alter
[Research Status](../RESEARCH_STATUS.md), which remains the planning authority.

## Existing evidence and case selection

The experiment starts from the repository's existing
[checker-rule inventory](../../results/investigations/checker-rule-inventory.md),
not from convenient new mutants. At this snapshot the inventory preserves 37
exact boundaries from eight bounded matrices and explicitly treats agreement
counts as descriptive rather than semantic votes.

Five cases were selected to span different evidentiary situations:

1. built-in `Eq` result-universe prerequisite during quotient initialization;
2. theorem result must be proposition-valued;
3. referenced-constant universe ownership;
4. serialized base `Quot` primitive exact-type handling; and
5. paired standalone/dependent serialized `isUnsafe` axiom probes.

| Selected boundary | Evidentiary pressure it contributes |
| --- | --- |
| quotient built-in `Eq` prerequisite | strong originating-checker isolation plus compatible checker disagreement |
| theorem result is proposition-valued | consensus observation and successful local infection evidence |
| referenced-constant universe ownership | declaration-environment rule with an unresolved upstream disagreement |
| serialized base `Quot` type | designated reference accepts while the discovery checker rejects |
| serialized `isUnsafe` axiom handling | active, policy- and reconstruction-sensitive, stateful behavior |

The last two were selected to resist a clean “normative premise violated,
therefore reject” account. `isUnsafe` is also still the repository's active
research frontier, so its incompleteness must remain visible.

## Candidate factoring criteria

The following questions are used to test each case. They are not proposed
field names or a closed taxonomy.

### Identity

A useful identity should survive changes in discovery mutant, source line,
generator, and current checker cohort. It should denote either a semantic
obligation or a precisely scoped empirical question. An implementation,
version, or configuration may be part of the subject when the claim itself is
implementation-specific.

### Layer

The description must distinguish logical/declaration validity from built-in or
kernel-extension initialization, serialized-format authority, reconstruction,
and configurable trust policy. A case that crosses layers should not be forced
into one.

### Authority

Authority and layer are independent. The criteria used in this experiment are:

- a formal-source claim requires an exact mechanized derivation;
- a documented-reference claim requires an authoritative requirement actually
  consulted;
- a designated-reference characterization requires a pinned compatible
  reference result and an accepted positive control;
- a multi-implementation characterization requires the complete compatible
  observation vector and controls, not a vote;
- an implementation-specific characterization requires the exact subject
  revision/configuration or an explicit provenance gap; and
- where those sources do not determine a contract, authority remains
  unresolved.

Existing `status: ESTABLISHED` expected-outcome records establish the exact
designated-reference result under their mechanical predicate. That status does
not automatically establish an implementation-independent semantic rule.

### Applicability and expected effect

Where the evidence supports it, the account should state a judgment or
context, dependent premises, the target premise, and the expected effect of its
violation. The simple form `R(x) ⇒ P(x)` may help some infection analyses but
must not replace dependent judgments or multi-stage importer behavior.

### Isolation and attribution

Isolation has at least three distinct questions:

1. Is the intended target violation mechanically established?
2. Did a given checker reach the target boundary?
3. Is that checker's rejection attributable to the target rather than an
   earlier or competing violation?

These answers can differ by checker. An omission mutant plus a matched control
can strongly isolate the originating implementation while diagnostics alone
provide weaker attribution for another checker. Unknown and multiple known
violations must remain possible conclusions.

### Observation and provenance

Each case must retain its positive control, negative or deviating artifact,
discovery mechanism, source mutant where relevant, checker identities,
revisions/configurations, minimization or remapping evidence, exact outcomes,
diagnostic stage, and upstream disposition. Aggregate counts cannot replace
the vector.

### Observation cohort and provenance boundary

The case-level cross-validation records bind the common external cohort rather
than relying on a mutable global inventory:

- export format/exporter `3.1.0`, produced by Lean `4.29.1` at githash
  `f72c35b3f637c8c6571d353742168ab66cc22c00`;
- Arena revision `37f7525b732808a49b746dc6999d53c3717db124`;
- official Lean kernel `4.33.0`, binary SHA-256
  `87efe83ae56410a4689b49ff5276dd9663fc85ae3641849d123b5fcef1692585`;
- Kiota revision `58e8636cfb51cf9c3bf3de7455a0e3c6ab68e87a`, binary SHA-256
  `d4a1d35a47d1d1246a1e9418e51a49347887845f713673721357b19e3b49c99f`;
  and
- Lean4Lean revision `ecb3b6661c14f8147be1069b126c629114baf4a8`, binary SHA-256
  `a48d684928795bf318782abc5c5ab07b1eed68ad39f63947554e04f94d8ff6bc`.

The exact bindings, compatibility checks, controls, commands, and diagnostics
remain in each linked cross-validation record. Nanoda provenance is uneven and
must be stated per case: the theorem and `isUnsafe` pair files bind binary
SHA-256 `55a3686145143e1ca4403848659163cb6b67c07f6b6a7807916cbbc4be96bc41`
and configuration SHA-256
`a71e26cccc305652ceae2037435f6d99984a8299c53c7bdace6e90af8d5556f6`;
the `isUnsafe` pairs additionally bind source revision
`6ae1f0cd962f081f6c423454c5da729d841236a7`. The quotient and universe
differential records do not durably bind a Nanoda revision/configuration, so
those values remain unknown.

## Worked calibration: built-in `Eq` prerequisite

This case is calibrated first so that its classifications are evidence-derived
rather than copied mechanically to the remaining cases.

### Candidate boundary

During quotient initialization, the built-in `Eq` declaration used by the
quotient machinery must have a proposition-valued result for the tested
canonical parameter and constructor shape. The exact candidate replaces
canonical `Eq` with an equality analogue whose result is `Sort (max 1 u)`, then
remaps the canonical quotient suffix to that expression graph.

This is intentionally narrower than “every part of the exact built-in `Eq`
type must match.” The evidence exercises the result-universe prerequisite, not
all possible type deviations.

### Layer

**Built-in/kernel-extension initialization prerequisite.** The failure occurs
while initializing quotient support, after the base `Quot` and `Quot.mk`
checks in Nanoda. It is not merely general theorem typing and is not one of the
four serialized quotient-primitive signature checks.

### Authority and criterion

**Designated-reference behavior plus multi-implementation characterization;
semantic authority unresolved.** The official reference and Lean4Lean reject
the candidate, Kiota accepts it, and all accept the control. The
[cross-validation record](../../results/cross-validation/nanoda-gen-d39c873fbcb7-quot-eq-type/results.json)
therefore preserves `semantic_status: UNRESOLVED`. No formal rule derivation or
authoritative external requirement was established in this experiment, so the
three rejections cannot be promoted by majority.

This is more than “a Nanoda check” because the expected result comes from the
pinned designated reference and an independent checker reproduces it. It is
less than formal-spec authority because one compatible checker disagrees and
the rule was inferred from implementation behavior.

### Applicability, premises, and target

- **Context:** quotient support is being initialized from an export containing
  the built-in equality and quotient graph.
- **Established surrounding premises:** the equality analogue preserves the
  canonical parameter domain and constructor telescope; the quotient suffix is
  mechanically remapped; the canonical control is accepted everywhere.
- **Target premise:** the tested `Eq` result is proposition-valued rather than
  inhabiting `Sort (max 1 u)`.
- **Expected effect:** the designated reference rejects the violation during
  quotient initialization. That expectation is not imposed on Kiota as a
  semantic oracle; Kiota's acceptance remains an observation and disagreement.

### Exact evidence and provenance

- Negative artifact:
  [`nanoda-gen-d39c873fbcb7-quot-eq-type-candidate.ndjson`](../../corpus/generated/nanoda-gen-d39c873fbcb7-quot-eq-type-candidate.ndjson),
  SHA-256 `777475027a53b84836a95eb4758f49fc0aa90923f72e511a48c88fff4a1e32a2`.
- Positive control:
  [`nanoda-gen-d39c873fbcb7-quot-eq-type-control.ndjson`](../../corpus/generated/nanoda-gen-d39c873fbcb7-quot-eq-type-control.ndjson),
  SHA-256 `fdb1b6085c32d29a27ef9aa531bb10dabe8560f6f58efbe1ccfb817b5e329d21`.
- Discovery mutant:
  [`nanoda-gen-d39c873fbcb7.json`](../../mutations/nanoda-gen-d39c873fbcb7.json),
  which omits the `src/quot.rs:89` definitional-equality assertion.
- Isolation and remapping evidence:
  [investigation README](../../results/investigations/nanoda-quot-eq-type/README.md),
  [max-1 reproduction](../../results/investigations/nanoda-quot-eq-type/max1-reproduction.json),
  and [remap audit](../../results/investigations/nanoda-quot-eq-type/remap-audit-2026-08-28.json).
- Expected/reference evidence:
  [expected outcome](../../results/expected-outcomes/nanoda-gen-d39c873fbcb7-quot-eq-type.json)
  and the cross-validation record linked above.

### Isolation

**Isolated for Nanoda; diagnostic attribution for official Lean and Lean4Lean;
no rejection attribution for accepting Kiota.** Nanoda's baseline reaches the
exact assertion after the preceding quotient checks, rejects the candidate,
and accepts the control; the omission mutant accepts both. The remap audit
removes a known graph-integrity confound. Official Lean and Lean4Lean report
quotient-initialization diagnostics consistent with the target, but were not
instrumented to prove that their internal paths are identical. No competing
violation is presently known; that is bounded isolation, not proof over every
possible importer.

### Checker observations

| Checker | Candidate | Control | Attribution note |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | quotient initialization reports unexpected `Eq` type |
| Nanoda | `REJECT` | `ACCEPT` | exact target reached; omission mutant accepts |
| Lean4Lean | `REJECT` | `ACCEPT` | quotient initialization reports unexpected `Eq` type |
| Kiota | `ACCEPT` | `ACCEPT` | compatible disagreement; no target-reach evidence |

This is not summarized as “3/4 reject.”

### Remaining uncertainty and recommended action

The evidence does not settle the serialized built-in contract for all
checkers, nor exercise adjacent `Eq.refl` prerequisites or all possible `Eq`
type deviations. Preserve the unresolved full vector and discuss the quotient
family before any implementation report, as the existing investigation
recommends. Do not promote the case to formal-spec authority.

### Calibration result

The case factors reasonably well as a **normative-candidate obligation with
explicitly limited authority**. Its identity no longer depends on the Nanoda
mutant, but authority, isolation, and disagreement remain attached evidence.

## Case 2: theorem result must be proposition-valued

### Factored claim

- **Candidate identity:** proposition-valued result requirement for theorem
  declarations.
- **Layer:** core declaration typing / logical validity.
- **Authority:** established designated-reference expectation with
  multi-implementation confirmation for the exact artifact. The
  [cross-validation record](../../results/cross-validation/m6-nonprop-theorem/results.json)
  is `CONFIRMED` with `semantic_status: ESTABLISHED`. This experiment did not
  add a formal derivation, so its provenance is still designated-reference and
  implementation characterization rather than formal-spec derivation.
- **Context and target:** a declaration is checked as a theorem; its inferred
  type is not `Prop`. The expected effect is rejection.
- **Contract status:** strongest normative case in the sample, bounded to the
  tested judgment and evidence.

### Exact evidence and provenance

- Negative artifact:
  [`nonprop-theorem.ndjson`](../../corpus/transfer/milestone-6/nonprop-theorem.ndjson),
  SHA-256 `ab15eeebf6466461a14fd9e22e0a8c1258ec37f1964bf6d4d0f698ddf3bccb7f`.
- Matched control:
  [`nonprop-definition-control.ndjson`](../../corpus/transfer/milestone-6/nonprop-definition-control.ndjson),
  SHA-256 `5d2f93abb7b784c619471c465a14f5d534f3a01910098d4c94458326b36919ab`.
- Discovery mutant: [`nanoda-0001.json`](../../mutations/nanoda-0001.json),
  which omits Nanoda's theorem-`Prop` guard.
- Nanoda pair with exact binary and configuration hashes:
  [`nonprop-theorem-nanoda.json`](../../results/investigations/nanoda-core-declaration-typing/nonprop-theorem-nanoda.json).
- Transfer and infection evidence:
  [frozen transfer result](../../results/transfer/milestone-6/freeze.json),
  [held-out evaluation](../../results/transfer/milestone-6/evaluation.json), and
  [`nanoda-0001` reach/infect experiment](../../results/research/reach-infect/nanoda-0001.json).
- Expected/reference evidence:
  [expected outcome](../../results/expected-outcomes/m6-nonprop-theorem.json)
  and the cross-validation record above.

### Isolation and checker observations

The candidate and control preserve the non-`Prop` type/value expression graph,
rename the declaration, and change its form from definition to theorem.
Nanoda's omission mutant accepts the candidate while baseline Nanoda rejects
it; both accept the control. Every checker reports the intended theorem/`Prop`
boundary, so the benign name difference is not the attributed cause. This is
strong isolation for the tested judgment, but not a one-field pair. The
control is a non-`Prop` definition rather than a separate proposition-valued
theorem, so it does not exercise every premise of theorem formation.

| Checker | Candidate | Control | Attribution note |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | explicitly reports theorem type is not a proposition |
| Nanoda | `REJECT` | `ACCEPT` | exact guard omitted by discovery mutant |
| Lean4Lean | `REJECT` | `ACCEPT` | explicitly reports theorem type is not a proposition |
| Kiota | `REJECT` | `ACCEPT` | explicitly reports theorem type is not `Prop` |

### Remaining uncertainty and recommended action

The current evidence is enough to preserve this as a stable project-level
normative boundary, while labeling its epistemic source accurately. A later
prototype should link the existing artifacts rather than backfill a new record
from `nanoda-0001`. No new implementation action follows from this experiment.

### Factoring result

**Fits the normative-obligation side of the abstraction.** Mutation is
discovery and infection provenance, not the rule's identity.

## Case 3: referenced-constant universe ownership

### Factored claim

- **Candidate identity:** universe levels used to instantiate a referenced
  constant must be owned by the declaration currently being checked.
- **Layer:** declaration-environment well-formedness.
- **Authority:** exact designated-reference `REJECT`, corroborated by Nanoda
  and Lean4Lean, with a compatible Kiota disagreement. The
  [cross-validation record](../../results/cross-validation/nanoda-0003-original/results.json)
  remains `semantic_status: UNRESOLVED`; no majority promotion is justified.
- **Context and target:** while checking a declaration, a constant reference
  is instantiated with universe `u`, but `u` is absent from the containing
  declaration's universe parameters. The designated-reference effect is
  rejection.
- **Contract status:** bounded inferred declaration-environment rule with an
  unresolved cross-checker contract.

### Exact evidence and provenance

- Negative artifact:
  [`nanoda-0003-auto-universe.ndjson`](../../corpus/generated/nanoda-0003-auto-universe.ndjson),
  SHA-256 `5f49dd739c4e909a0147b7fc5a8bee4e2eb06ca0f4ad7c87ef20ba871ff7fff3`.
- Positive control:
  [`nanoda-0003-declared-const-universe.ndjson`](../../corpus/controls/nanoda-0003-declared-const-universe.ndjson),
  SHA-256 `94530b9892930781b8f91bb8eb5017e444ef564084ed2b6cfd3ce0eb858faab9`.
- Discovery mutant: [`nanoda-0003.json`](../../mutations/nanoda-0003.json),
  omitting Nanoda's `all_uparams_defined` assertion.
- Generated-witness and minimization evidence:
  [witness metadata](../../results/witnesses/nanoda-0003-auto-universe/metadata.json)
  and [minimized artifact](../../corpus/minimized/nanoda-0003-auto-universe-min.ndjson).
- Expected/reference evidence:
  [expected outcome](../../results/expected-outcomes/nanoda-0003-original.json)
  and the cross-validation record above.
- Upstream disposition:
  [Kiota universe-ownership investigation](../investigations/KIOTA_UNIVERSE_OWNERSHIP.md)
  and [`W-KIOTA-UNIVERSES`](../RESEARCH_STATUS.md#waiting).

### Isolation and checker observations

The candidate/control pair changes whether the containing declaration declares
`u` while preserving the reference that uses it; it also uses a different
benign declaration name (`bad`/`good`). Baseline Nanoda rejects and the precise
omission mutant accepts; both accept the control. Official Lean diagnoses an
undefined universe parameter and Lean4Lean rejects; their paths are not
instrumented. Kiota accepts the exact candidate and control.

| Checker | Candidate | Control | Attribution note |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | reports undefined universe parameter `u` |
| Nanoda | `REJECT` | `ACCEPT` | precise ownership assertion omitted by mutant |
| Lean4Lean | `REJECT` | `ACCEPT` | compatible rejection; not instrumented |
| Kiota | `ACCEPT` | `ACCEPT` | unresolved implementation disagreement |

Isolation is strong for Nanoda and supported by artifact structure and
diagnostics for the designated reference. The older Nanoda witness evidence
does not bind an exact Nanoda revision/configuration; that provenance remains
unknown rather than being inferred from today's checkout.

### Remaining uncertainty and recommended action

Authority remains designated-reference behavior, not a retrieved formal
requirement. Await the existing Kiota #3 adjudication and do not convert the
checker split into semantic truth. The stable identity survives the source
mutant, while its epistemic status remains unresolved.

### Factoring result

**Fits as a normative-candidate obligation with unresolved authority across
implementations.** It demonstrates that stable identity and settled semantic
authority are separate properties.

## Case 4: serialized base `Quot` primitive exact-type handling

### Failed normative factoring

A proposed rule such as “the serialized base `Quot` type must exactly match the
canonical relation-indexed telescope, otherwise reject” contradicts the
designated reference: official Lean, Lean4Lean, and Kiota accept the exact
deviation and its control. Nanoda alone rejects the candidate through an extra
exact-type assertion.

The stable question is instead: **how does a checker treat the serialized base
`Quot` type when it is independently well-formed but differs from the canonical
type reconstructed or expected by Nanoda?** That identity is independent of
the discovery mutant, but it is an empirical import/reconstruction contract
boundary rather than a normative semantic obligation.

### Factored empirical boundary

- **Layer:** serialized format, reconstruction, and implementation validation
  behavior.
- **Authority:** designated-reference `ACCEPT` plus a complete
  multi-implementation characterization. It establishes exact observed
  behavior, not a general statement that the field is non-authoritative.
- **Context and deviation:** a canonical quotient export is present; only the
  base `Quot` declaration's serialized type reference changes from the
  relation-indexed telescope to independently well-formed `Sort u`.
- **Expected effect:** no validator-independent effect is justified. Expected
  behavior must remain profile-specific: official/Kiota/Lean4Lean accept;
  Nanoda rejects under the tested build.
- **Contract status:** `REFERENCE_ALIGNED` Nanoda over-rejection finding and
  empirical serialized-primitive boundary.

### Exact evidence and provenance

- Deviating artifact:
  [`nanoda-gen-7b386d7135bb-quot-type-mismatch.ndjson`](../../corpus/generated/nanoda-gen-7b386d7135bb-quot-type-mismatch.ndjson),
  SHA-256 `4726d6f41d674fc80b8b2b915241eb399d88a42e32ad9e6121df99b3c3614ad0`.
- Canonical control:
  [`nanoda-gen-7b386d7135bb-quot-type-control.ndjson`](../../corpus/generated/nanoda-gen-7b386d7135bb-quot-type-control.ndjson),
  SHA-256 `337e3c4aeec2db1a1fd042010f36b3653c6d7fad8084019bbe4d7b4d40baa4ec`.
- Discovery mutant:
  [`nanoda-gen-7b386d7135bb.json`](../../mutations/nanoda-gen-7b386d7135bb.json),
  which omits Nanoda's `src/quot.rs:208` exact-type assertion.
- Isolation and confound removal:
  [investigation README](../../results/investigations/nanoda-quot-type/README.md)
  and [reproduction](../../results/investigations/nanoda-quot-type/reproduction.json).
- Expected/reference and full vector:
  [expected outcome](../../results/expected-outcomes/nanoda-gen-7b386d7135bb-quot-type.json)
  and [cross-validation](../../results/cross-validation/nanoda-gen-7b386d7135bb-quot-type/results.json).

### Isolation and checker observations

The final 73-record pair differs at the one serialized type reference. It
includes canonical `Quot.mk`, removing an earlier export-shape confound.
Nanoda's baseline rejects, its exact omission mutant accepts, and both accept
the control: Nanoda behavior is isolated. Acceptance by the other checkers does
not reveal whether the field is ignored, parsed then reconstructed, normalized,
or validated under a different relation.

| Checker | Candidate | Control | Attribution note |
| --- | --- | --- | --- |
| official Lean | `ACCEPT` | `ACCEPT` | exact behavior established; field treatment unknown |
| Nanoda | `REJECT` | `ACCEPT` | exact serialized-type assertion isolated by mutant |
| Lean4Lean | `ACCEPT` | `ACCEPT` | exact behavior established; field treatment unknown |
| Kiota | `ACCEPT` | `ACCEPT` | exact behavior established; field treatment unknown |

The quotient differential artifacts bind source and artifact digests but do
not durably bind the exact Nanoda revision/configuration. The empirical claim
must therefore retain that provenance gap.

### Remaining uncertainty and recommended action

Do not infer that accepting checkers ignore the field or that Nanoda is
semantically wrong. Preserve this as a scoped implementation-contract finding,
discuss the four serialized quotient primitives together, and follow
[`D-IMPLEMENTATION-SPECS`](../RESEARCH_STATUS.md#future-directions) if planning
later authorizes parser/reconstruction/validation/semantic-use analysis.

### Factoring result

**Fails as a normative obligation but succeeds as an empirical contract
boundary.** A single rule object with “target premise violated ⇒ reject” would
misstate the designated-reference evidence.

## Case 5: serialized `isUnsafe` axiom handling

This is the deliberate adversarial case. The paired probes change only an
axiom declaration's serialized `isUnsafe` field from `false` to `true`:

- the standalone probe ends after the axiom;
- the dependent probe adds a safe definition that references the axiom.

### Full paired observation vectors

All matched `isUnsafe: false` controls are accepted.

| Probe | official Lean | Nanoda `6ae1f0c` | Lean4Lean | Arena-pinned Kiota `58e8636` |
| --- | --- | --- | --- | --- |
| standalone unsafe axiom | `ACCEPT` | `REJECT` | `ACCEPT` | `ACCEPT` |
| unsafe axiom + safe dependent declaration | `REJECT` (`unknown constant`) | `REJECT` (parser assertion) | `REJECT` (`unknown constant`) | `ACCEPT` |

Current Kiota main at revision
`686063c13b22ce379c05dfe7fc03656655ac60e5` rejects the dependent candidate
directly with `REJECT: unsafe axiom`, unlike the Arena-pinned Kiota revision.
That revision-sensitive result is preserved in the
[current-upstream reproduction](../../results/investigations/nanoda-axiom-unsafe/kiota-upstream-main.json).

### Exact evidence and provenance

- Materialization and content hashes:
  [`materialization.json`](../../results/investigations/nanoda-axiom-unsafe/materialization.json).
- Standalone candidate/control:
  [`axiom-unsafe-only-candidate.ndjson`](../../corpus/generated/axiom-unsafe-only-candidate.ndjson)
  and
  [`axiom-unsafe-only-control.ndjson`](../../corpus/generated/axiom-unsafe-only-control.ndjson).
- Dependent candidate/control:
  [`axiom-unsafe-candidate.ndjson`](../../corpus/generated/axiom-unsafe-candidate.ndjson)
  and
  [`axiom-unsafe-control.ndjson`](../../corpus/generated/axiom-unsafe-control.ndjson).
- Nanoda revision/binary/configuration and exact parser rejection:
  [standalone pair](../../results/investigations/nanoda-axiom-unsafe/axiom-only-nanoda-pair.json)
  and [dependent pair](../../results/investigations/nanoda-axiom-unsafe/nanoda-pair.json).
  The tested configuration has `unsafe_permit_all_axioms: true`, but Nanoda
  rejects the serialized flag first at `src/parser.rs:766`.
- Designated-reference expectations and external vectors:
  [standalone expected outcome](../../results/expected-outcomes/axiom-unsafe-only.json),
  [standalone cross-validation](../../results/cross-validation/axiom-unsafe-only/results.json),
  [dependent expected outcome](../../results/expected-outcomes/axiom-unsafe-flag.json),
  and [dependent cross-validation](../../results/cross-validation/axiom-unsafe-flag/results.json).
- Planning authority:
  [`F-AXIOM-UNSAFE-DECLARATIONS`](../RESEARCH_STATUS.md#active).

These are characterization probes, not artifacts backfilled from a convenient
mutation. No mutation provenance is required for their identity.

### Why one common rule fails

No single statement such as “unsafe axioms must be rejected” or “unsafe axioms
are accepted” preserves the evidence:

- standalone process-level `ACCEPT` does not prove that the axiom was admitted
  to the environment;
- the later `unknown constant` diagnostics establish lack of visibility to the
  safe dependent declaration, but not whether the mechanism was skipping,
  non-admission, or another reconstruction policy;
- Nanoda rejects earlier at a parser assertion, before the configured ordinary
  axiom allow/skip policy can answer the same question;
- pinned and current Kiota revisions implement different observed behavior;
  and
- artifact-level `ACCEPT`/`REJECT` cannot encode the necessary intermediate
  dispositions such as admitted, skipped/non-visible, or rejected.

The dependent expected-outcome record also contains a human rationale broader
than its mechanical predicate. The pinned official result establishes the
exact artifact outcome; the rationale alone does not establish a general
normative safety rule. A factored object must preserve that distinction.

The target field change is isolated at the artifact level. The semantic target
is not isolated because parser acceptance, configurable trust policy,
environment insertion/visibility, and dependent-use behavior are entangled.
There is a stable *investigation* identity, but no faithful single rule identity
yet.

### Authority, layer, and status

- **Layer:** multiple layers—serialized-format acceptance, parser behavior,
  configurable trust policy, environment reconstruction, and safe dependent
  use.
- **Authority:** exact designated-reference and implementation observations;
  no implementation-independent normative contract established.
- **Isolation:** exact field deviation isolated; target semantic premise and
  rejection attribution are multiple/unknown across the cohort.
- **Contract status:** active policy/reconstruction characterization with
  revision-sensitive disagreement, not an inventory-complete rule.

An adequate account would have to split at least serialized flag ingestion,
environment admission/visibility, dependent-use policy, and ordinary-axiom
configuration. Those may be empirical transition boundaries rather than
logical premises.

### Remaining uncertainty and recommended action

Continue only the already active `F-AXIOM-UNSAFE-DECLARATIONS` work: exercise
the Nanoda configuration cross-product with paired standalone/dependent probes
that can mechanically distinguish reject, skip/non-visible, and admit/visible;
bind exact revisions; and seek authoritative export/safety requirements before
any normative promotion. Do not add this family to the completed inventory or
derive a rule from the current binary outcomes.

### Factoring result

**The common rule abstraction fails for this case.** It becomes misleading
unless the case is decomposed into multiple empirical, stateful contract
boundaries. This failure is evidence for the decision below, not a defect to be
papered over.

## Cross-case findings

### What survives factoring

- A stable identity can be independent of mutation and generation provenance.
- Authority must remain separate from semantic/contract layer.
- Expected behavior and complete implementation observations are distinct.
- Isolation and rejection attribution are per-checker claims, not one global
  artifact property.
- Mutation can remain discovery, isolation, and infection provenance rather
  than define the boundary.
- Unknown revision/configuration, contract, reach, and competing-violation
  states are essential evidence.

### What does not survive one universal rule type

- Some durable identities intrinsically describe implementation or
  reconstruction behavior rather than implementation-independent semantics.
- `ACCEPT` can hide environment non-visibility; an observation may require a
  state transition rather than one final Boolean.
- A designated-reference expected outcome is not automatically normative
  semantic authority.
- `violate premise ⇒ reject` is false for the serialized `Quot` case and too
  coarse for `isUnsafe`.

### Relationship to Reach → Infect → Propagate → Reveal

The theorem and quotient-`Eq` cases support a useful conceptual alignment:

`rule applicable → target reached → target premise violated → violation propagates → observable rejection`

For the Nanoda mutation, reach and infection can be instrumented directly. For
the negative artifact, target violation and rejection attribution require
separate evidence. The `isUnsafe` pair demonstrates why the correspondence
cannot be forced: a checker can accept the standalone artifact yet make the
declaration unavailable, with rejection revealed only by a later dependent
declaration. Mutation-level RIPR and semantic negative-test reasoning can share
questions, but not an assumed one-to-one stage model.

## Decision gate

### B. Viable only after splitting the concept

The representative cases do not support one common “assurance rule” object.
The smallest useful conceptual split is:

1. **Normative or normative-candidate semantic obligation.** This carries a
   judgment/context, dependent premises, a target premise, an expected effect,
   and explicit epistemic authority. Promotion to normative status requires
   evidence beyond an unexplained designated-reference result.
2. **Scoped empirical contract boundary or scenario.** This describes exact
   parser, serialization, reconstruction, policy, configuration, or
   implementation behavior. Its subject may intrinsically name an
   implementation/revision/configuration, and it may require intermediate
   state transitions rather than one validator-independent expected outcome.

The two concepts can share an evidence envelope: stable identity, exact
artifacts and controls, discovery provenance, revisions/configurations,
per-checker reach and attribution, full observation vectors, uncertainty, and
recommended action. Implementation-local reachability and mutation-equivalence
facts remain provenance or observations rather than semantic rules.

This split is analytical, not a proposed production schema or closed taxonomy.
`isUnsafe` further shows that one empirical scenario may need decomposition
before it has stable boundary identities.

### Why not the other decisions?

- **Not A:** serialized `Quot` and `isUnsafe` lose authority, state, and
  implementation-specific meaning under one rule type.
- **Not C:** existing matrices preserve excellent exact vectors, but lower-level
  links must be followed to recover authority, isolation, provenance gaps, and
  per-checker attribution. A small shared evidence envelope would add value
  without replacing the matrices.
- **Not D:** the theorem, universe-ownership, and quotient-`Eq` cases factor
  usefully as obligations with bounded authority; serialized `Quot` factors as
  an empirical boundary. The idea is useful after the split.

## Proposed Phase 2 objective for human review

No Phase 2 work was performed in this run. Because decision B is supported, the
following refined objective is proposed for later human approval; it is not
made active here:

> Prototype, from existing matrix and investigation artifacts only, a
> research-only two-kind assurance-claim model that separates normative or
> normative-candidate obligations from scoped empirical contract scenarios,
> while sharing linked evidence/provenance and per-checker
> reach/isolation/attribution. Factor the five cases above, derive only a
> known-rule characterization view, and test one narrow RIPR linkage and one
> semantics-directed reproduction of an existing difficult witness. Do not
> backfill from mutants, calculate semantic coverage, or treat the
> characterized set as a denominator over Lean semantics.

- **Evidence for proposing it:** three sampled cases retain stable obligation
  identities, one retains only an empirical contract identity, and one
  mechanically falsifies the unsplit abstraction.
- **Prerequisites:** reuse exact content-addressed controls and candidates;
  preserve the pinned external-checker cohort; carry unknown Nanoda provenance
  where it is absent; keep `isUnsafe` decomposable; and obtain planning approval
  through [Research Status](../RESEARCH_STATUS.md).
- **Expected assurance benefit:** stable claim identity can survive replaceable
  mutants, generators, and checker cohorts without converting empirical
  importer behavior into unjustified semantic truth.
- **Success condition:** every sampled case can be represented without losing
  authority, layer, full observations, per-checker isolation/attribution,
  configuration/revision scope, or unknowns, and `isUnsafe` decomposes without
  inventing a normative rule.
- **Failure condition:** the prototype must be rejected or refined if it
  duplicates evidence, requires majority counts, hides stateful importer
  behavior, collapses expected outcomes with semantic authority, or needs
  stronger isolation than the existing artifacts establish.

The proposed characterization view remains a research artifact unless a
separate justification supports public assurance claims.

## Accepted follow-up

The accepted Phase 2 representative-set gate is recorded in
[Assurance Claim Prototype](ASSURANCE_CLAIM_PROTOTYPE.md). It exercises all
five sampled boundaries as six claims after decomposing `isUnsafe`. The
unchanged two-kind model passes; the next bounded frontier is a mechanically
derived research-only known-rule characterization view. RIPR linkage and
semantics-directed reproduction remain behind that gate.
