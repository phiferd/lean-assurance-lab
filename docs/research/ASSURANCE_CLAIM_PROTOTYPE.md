# Assurance Claim Prototype: Falsification-First Gate

- Research snapshot: 2026-08-29
- Phase: accepted Phase 2, first bounded gate
- Status: `PASS`

## Scope

This is the smallest research-only prototype justified by the
[Phase 1 factoring result](RULE_LEVEL_FACTORING_EXPERIMENT.md). It exercises
the proposed split on only:

1. the quotient built-in `Eq` result-universe prerequisite, used as the
   normative-candidate calibration; and
2. serialized `isUnsafe` axiom handling, used as the adversarial case.

It is not a production schema, semantic denominator, coverage metric,
conformance claim, or replacement for the existing checker matrices. It does
not yet factor the theorem, referenced-universe, or serialized `Quot` cases.

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
- every matched control is accepted;
- the designated-reference `Eq` outcome remains distinct from unresolved
  semantic authority;
- the Nanoda `Eq` target is isolated by the omission differential;
- evidence payloads remain linked rather than copied;
- `isUnsafe` is decomposed into stateful scenarios;
- both `isUnsafe` pairs differ only at the serialized flag;
- no aggregate count is used as a semantic oracle;
- every recommendation names an action, target, priority, prerequisites, and
  evidence; and
- every claim retains explicit unknowns.

The gate does **not** establish that two kinds are sufficient for all existing
boundaries. It establishes only that the easiest calibration and hardest
adversarial case can be represented without the original overstatement.

## Decision and frontier

Decision: **proceed to the remaining three Phase 1 cases using the model
unchanged.**

The next bounded step is to factor:

1. theorem result must be proposition-valued;
2. referenced-constant universe ownership; and
3. serialized base `Quot` exact-type handling.

Success requires all three to retain authority, layer, complete observation
vectors, per-observer attribution, provenance gaps, and unknowns without a new
claim kind. Failure means refine or reject the two-kind model before deriving a
characterization matrix.

The known-rule characterization view, RIPR linkage, and semantics-directed
reproduction remain behind that gate. No aggregate semantic-coverage
percentage is authorized.

Planning authority and the parallel axiom-policy investigation remain in
[Research Status](../RESEARCH_STATUS.md).
