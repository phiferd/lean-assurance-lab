# Acceptance Impact Pilot 1

Status: **COMPLETE — CONSTRUCTION_OR_SEMANTIC_BOUNDARY**
Frontier: `F-DISCOVERY-AND-CONFORMANCE`  
Item: `ACCEPTANCE-IMPACT-PILOT-1`

## Question

Does the retained `LALNest.rec_1` type-pointer candidate still produce a
compatible-control acceptance difference at the exact current Kiota source
revision, and, only if that premise reproduces, can one fixed downstream use
distinguish a consequential retained-type policy from a harmless policy within
the tested use?

This is a staged investigation. Reproduction is scientific work inside the
item, not a prerequisite result. A successful target/reference premise is,
however, a hard gate on downstream construction.

## Frozen starting evidence

The exact candidate and control are already retained:

- candidate: `corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson`,
  6,332 bytes, SHA-256
  `13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd`;
- control: `corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson`,
  6,332 bytes, SHA-256
  `3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae`.

They differ at exactly `/104/inductive/recs/0/type`: the control points to
expression 49 and the candidate to existing expression 68. No name or
expression node changes. Historical official Lean 4.33.0 and Lean4Lean
observations rejected the candidate while accepting the control; historical
Kiota `58e8636` accepted both. Those observations are context, not a current
result.

The current target source is the already archived Kiota revision
`9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`, bound by
`results/research/kiota-ctor-index-test-1/source-lock.json` and its source
archive. The source review found that the five-Pi arity guard does not
distinguish the pair and that retained recursor types are used by constant
inference, but explicitly made no current acceptance or soundness claim.

## Stage 1: exact current reproduction

Before any checker launch:

1. verify the exact candidate/control bytes and the single scalar difference;
2. materialize and build the archived Kiota `9fa2c297` source without source
   edits, binding the binary, dependency lock and invocation contract;
3. bind the existing official Lean 4.33.0 reference profile;
4. implement or reuse supervised execution with positive RSS sampling, timeout,
   cleanup and exact stdout/stderr receipts;
5. commit a four-cell manifest: candidate and control through current Kiota and
   official Lean.

The current-premise gate passes only when:

- both observers accept the control under their exact success contracts;
- current Kiota accepts the candidate; and
- official Lean rejects the candidate after parsing it as the intended object.

If any condition fails, close the item with the exact result—such as stale
premise, incompatible control, current rejection, reference acceptance or
unresolved infrastructure—and do not construct a downstream witness.

## Stage 2: one downstream consequence

Stage 2 is forbidden until a committed Stage-1 result passes the premise gate.
Before construction, commit an explicit assumption audit and consequence
contract. The audit must separate observed source behavior from semantic
authority and list every assumption needed to interpret retained
`LALNest.rec_1` type 68.

The sole permitted consequence criterion is:

> Add one dependency-complete closed declaration that applies
> `LALNest.rec_1` at the retained expression-68 type in a way that is
> well-typed only under that substituted type, together with a matched control
> use of the unmodified expression-49 type.

Freeze the exact producer, names, terms, expected declaration identities,
independent structural audit and target/reference matrix before observing a
checker. No search over alternatives after an outcome, adaptive case
replacement, extra semantic candidate or broader recursor field is allowed.
If the criterion cannot be constructed under the audited assumptions, record a
precise tested-use boundary rather than weakening it.

## Outcomes and claim limits

Permitted terminal scientific outcomes are:

- `STALE_PREMISE` or `INCOMPATIBLE_CONTROL` after Stage 1;
- `CONSEQUENTIAL_WITHIN_FIXED_USE`, `HARMLESS_WITHIN_TESTED_USE` or a precise
  construction/semantic boundary after Stage 2;
- an evidence-bound unavailable input, authority or capability after feasible
  repairs.

Checker agreement, disagreement and LLM analysis are not semantic authority.
Preserve every failed engineering attempt and repair it within this item.
Per-process time, memory and cleanup controls are nonterminal. No production
checker edit, assurance-milestone advance, network write or external action is
authorized.

## Closure

Both stages completed. The exact downstream use exposed the fifth-domain
difference, but official Lean reached the appended declaration and reported an
application type mismatch rather than the preregistered earlier invalid-recursor
diagnostic. The immutable outcome is therefore
`CONSTRUCTION_OR_SEMANTIC_BOUNDARY`; see the canonical result and report under
`results/research/acceptance-impact-pilot-1/`. No adaptive relabeling or rerun is
permitted.

## Required closure

Closure must bind the exact source, artifacts, manifests, receipts, premise
decision, any Stage-2 assumption/consequence contract, all observed outcomes
and the required project-wide successor review. A current difference alone
does not authorize an upstream report or submission.
