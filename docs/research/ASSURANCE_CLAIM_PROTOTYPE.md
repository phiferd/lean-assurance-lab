# Assurance Claim Prototype: Falsification-First Gate

- Research snapshot: 2026-08-29
- Phase: accepted Phase 2, representative-set gate
- Status: `PASS`

## Scope

This research-only prototype is justified by the
[Phase 1 factoring result](RULE_LEVEL_FACTORING_EXPERIMENT.md). It now exercises
the proposed split across the complete representative set:

1. the quotient built-in `Eq` result-universe prerequisite;
2. theorem results must be proposition-valued;
3. referenced-constant universe ownership;
4. serialized base `Quot` exact-type handling; and
5. serialized `isUnsafe` axiom handling, decomposed into ingestion and
   dependent-visibility scenarios.

It is not a production schema, semantic denominator, coverage metric,
conformance claim, or replacement for the existing checker matrices.

## Mechanical artifact

Run:

```console
scripts/build-assurance-claim-prototype
```

The builder reads the existing exact artifacts, controls, differential runs,
cross-validation records, and current-Kiota reproduction. It verifies the
content hashes and expected vectors, then writes the research result to
[`results/research/assurance-claim-prototype.json`](../../results/research/assurance-claim-prototype.json).

The generated artifact contains minimal normalized observation projections and
content-addressed links to the full evidence. It does not copy raw diagnostics
or replace the source records.

## Smallest model tested

Both claim kinds share:

- stable identity;
- kind;
- semantic/contract layers;
- authority and its evidence criterion;
- a kind-specific statement;
- content-addressed evidence references;
- full revision-scoped checker observations;
- per-observer isolation/attribution;
- explicit unknowns; and
- an actionable recommendation.

The kinds differ only where the evidence requires it.

### Normative-candidate obligation

This shape carries a judgment, applicability, premises, target premise, and an
expected effect with an explicit authority scope.

It does not make the obligation normative merely because the designated
reference has an established expected outcome.

### Empirical contract scenario

This shape carries a subject scope, precondition, stimulus, observation points,
and profile-specific effects. It permits intermediate state and does not
require one validator-independent expected outcome.

## Calibration result: quotient built-in `Eq`

Stable identity:
`quotient.eq.result-universe-prerequisite`.

Kind: `NORMATIVE_CANDIDATE_OBLIGATION`.

Authority remains `UNRESOLVED`: the official reference, Nanoda, and Lean4Lean
reject the exact result-universe deviation; compatible Kiota accepts it. The
official expected `REJECT` is scoped to the designated reference and is not
promoted by the three-to-one observation split.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | diagnostic support |
| Nanoda | `REJECT` | `ACCEPT` | isolated by omission differential |
| Lean4Lean | `REJECT` | `ACCEPT` | diagnostic support |
| pinned Kiota | `ACCEPT` | `ACCEPT` | accepted; target reach unknown |

The object retains the missing Nanoda revision, binary, and configuration as
unknown. It does not infer them from the present checkout.

## Remaining-case result

The three cases behind the second gate fit the existing split without adding a
claim kind.

### Theorem result is proposition-valued

Stable identity: `theorem.result-proposition-valued`.

Kind: `NORMATIVE_CANDIDATE_OBLIGATION`.

Every tested checker rejects the non-`Prop` theorem and accepts the matched
definition-form control. The designated-reference expectation is therefore
`ESTABLISHED` for this exact case, while its epistemic basis remains reference
behavior plus implementation characterization rather than a linked formal
derivation. Nanoda's exact guard-omission differential and the existing
Reach/Infect experiment remain discovery and isolation provenance, not the
identity of the obligation.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | diagnostic support |
| Nanoda | `REJECT` | `ACCEPT` | target guard omission differential |
| Lean4Lean | `REJECT` | `ACCEPT` | diagnostic support |
| pinned Kiota | `REJECT` | `ACCEPT` | diagnostic support |

The control changes declaration kind and benign name rather than providing a
separate proposition-valued theorem. That limitation remains explicit.

### Referenced-constant universe ownership

Stable identity: `declaration.constant-reference-universe-ownership`.

Kind: `NORMATIVE_CANDIDATE_OBLIGATION`.

The official designated reference and Lean4Lean reject the exact undeclared
universe reference while Kiota accepts it. Authority therefore remains
`UNRESOLVED`; the observation count is not a semantic vote. The old Nanoda
differential reaches the precise ownership assertion, but its revision,
binary, configuration, and matched-control run are not all durably linked by
the selected machine records. The prototype records that control cell as
`NOT_DURABLY_LINKED` rather than manufacturing provenance.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | diagnostic support |
| Nanoda | `REJECT` | `NOT_DURABLY_LINKED` | target assertion omission differential; identity unknown |
| Lean4Lean | `REJECT` | `ACCEPT` | compatible rejection, not instrumented |
| pinned Kiota | `ACCEPT` | `ACCEPT` | unresolved disagreement |

The existing Kiota #3 adjudication remains the action target; this factoring
does not create a duplicate external action.

### Serialized base `Quot` type treatment

Stable identity: `serialized-quotient.base-type-treatment`.

Kind: `EMPIRICAL_CONTRACT_SCENARIO`.

This case is the decisive type split. Official Lean, Lean4Lean, and Kiota
accept the independently well-formed serialized type deviation and its
canonical control. Nanoda rejects the deviation at an exact-type assertion,
and omitting that assertion makes it accept. Representing this as a normative
rejection obligation would contradict the designated reference.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `ACCEPT` | `ACCEPT` | field treatment unknown |
| Nanoda | `REJECT` | `ACCEPT` | exact-type assertion omission differential |
| Lean4Lean | `ACCEPT` | `ACCEPT` | field treatment unknown |
| pinned Kiota | `ACCEPT` | `ACCEPT` | field treatment unknown |

The empirical scenario preserves the question of whether accepting checkers
ignore, reconstruct, normalize, or validate the field differently. It does not
answer that question by inference.

## Adversarial result: `isUnsafe`

The hard case does not fit one rule. The prototype passes only after splitting
it into two empirical scenarios.

### Serialized ingestion

Stable identity: `serialized-unsafe-axiom.ingestion`.

Kind: `EMPIRICAL_CONTRACT_SCENARIO`.

The standalone one-field probe establishes process behavior, but acceptance
does not distinguish admission from skipping or non-visibility.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `ACCEPT` | `ACCEPT` | admission unknown |
| Nanoda `6ae1f0c` | `REJECT` | `ACCEPT` | serialized flag rejected at parser assertion |
| Lean4Lean | `ACCEPT` | `ACCEPT` | admission unknown |
| pinned Kiota `58e8636` | `ACCEPT` | `ACCEPT` | admission unknown |

### Dependent visibility

Stable identity: `serialized-unsafe-axiom.dependent-visibility`.

Kind: `EMPIRICAL_CONTRACT_SCENARIO`.

The same field change followed by a safe dependent declaration exposes a
different stateful boundary.

| Profile | Candidate | Control | Attribution |
| --- | --- | --- | --- |
| official Lean | `REJECT` | `ACCEPT` | axiom not visible; mechanism unknown |
| Nanoda `6ae1f0c` | `REJECT` | `ACCEPT` | earlier parser rejection |
| Lean4Lean | `REJECT` | `ACCEPT` | axiom not visible; mechanism unknown |
| pinned Kiota `58e8636` | `ACCEPT` | `ACCEPT` | dependent use accepted |
| current Kiota `686063c` | `REJECT` | `ACCEPT` | direct unsafe-axiom rejection |

This decomposition preserves revision drift, parser stage, environment
visibility, and unknown admission mechanism. A single “unsafe axioms must be
rejected” object would still fail.

## Mechanical gate

The generated result is `PASS`; every check is mechanically true:

- exact primary artifact hashes match;
- both claim kinds are exercised;
- every claim has the common envelope and its kind-specific statement shape;
- complete candidate/control vectors match the evidence;
- every durably recorded matched control is accepted, and the missing Nanoda
  universe-control link remains explicit;
- the designated-reference `Eq` outcome remains distinct from unresolved
  semantic authority;
- the Nanoda `Eq` target is isolated by the omission differential;
- evidence payloads remain linked rather than copied;
- `isUnsafe` is decomposed into stateful scenarios;
- both `isUnsafe` pairs differ only at the serialized flag;
- all representative cases factor without adding a third claim kind;
- established, unresolved, and empirical-reference-aligned authority states
  remain distinct;
- the universe case preserves its Nanoda identity/control provenance gap;
- serialized `Quot` is not assigned a normative rejection effect;
- no aggregate count is used as a semantic oracle;
- every recommendation names an action, target, priority, prerequisites, and
  evidence; and
- every claim retains explicit unknowns.

The gate does **not** establish that two kinds are sufficient for every future
boundary. It establishes that the complete adversarial representative set can
be represented without the original overstatement.

## Decision and frontier

Decision: **the representative-set gate is closed; proceed to a research-only
known-rule characterization view derived from existing artifacts.**

That view is the next bounded frontier, not a production schema. It must expose,
per characterized boundary, positive and negative evidence, isolation,
authority, layer, discovery provenance, the full checker observation vector,
disagreement state, unknowns, and recommended action. It must be generated from
existing claim and matrix evidence and must fail closed when a required link is
missing.

RIPR linkage and semantics-directed reproduction remain behind that next gate.
No aggregate semantic-coverage percentage is authorized, and the characterized
set is not a denominator over Lean semantics.

Planning authority and the parallel axiom-policy investigation remain in
[Research Status](../RESEARCH_STATUS.md).
