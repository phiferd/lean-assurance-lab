# Declaration-Validation Publication Study: Authority-Source Approval Review

Status: **FROZEN BEFORE AUTHORITY-SOURCE APPROVAL**

This packet is a human-readable view of the canonical frozen discovery result at
`results/research/declaration-validation-publication-study-source-discovery.json`.
The JSON record, exact retrieved bytes under
`results/research/evidence/declaration-validation-publication-study/`, and its
validator are controlling. This packet makes recommendations; it does not record
an authority approval decision.

## Decision requested

Review all 18 retained source candidates and record a separate human
`APPROVE` / `REJECT` / `DEFER` decision for each proposed claim-to-obligation
mapping. In particular, decide whether to:

1. **APPROVE only**
   `CLAIM.SOURCE.MANUAL.DEFS.THEOREM_PROP` from
   `SOURCE.CANDIDATE.OFFICIAL.MANUAL.DEFINITIONS` for
   `DECL.THEOREM.TYPE_PROP`;
2. **DEFER** the exact-version manual's more general type-system and function
   claims until their mapping to raw serialized declarations/expressions is
   accepted or rejected explicitly;
3. **DEFER** Lean4Lean positive theorems until their exact axiom/sorry lineage,
   modeled-judgment correspondence, and v4.33.0 compatibility are closed; and
4. **REJECT as normative authority** every implementation-only,
   version-mismatched, insufficiently precise, or active-assumption record while
   retaining it as favorable, limiting, contradictory, or provenance evidence.

No approval should be inferred from the recommendation column. If the human
decision differs, preserve the recommendation and bind the reviewed predecessor
in a separately signed successor decision artifact.

## Search closure and fixed process sentinels

- Closure: `CLOSED`; 30/30 frozen queries executed; 0 access failures.
- External searches: 25/45; primary retrievals: 18/80; citation chases: 2/20.
- Retained sources: 18/40; retrieved bytes: 1,471,263/209,715,200.
- Research time recorded: 5.8/12 hours; no budget exhausted.
- No query, source family, candidate, or outcome route was added after results
  were observed.
- Fixed post-approval authority-process sentinels:
  `DECL.THEOREM.TYPE_PROP` and `EXPR.LET.VALUE_TYPE_MATCH`.

## Recommended APPROVE

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.DEFINITIONS`

- Identity: Lean Language Reference `Manual/Defs.lean`, repository
  `https://github.com/leanprover/reference-manual`, commit
  `02d0d61af6d344da5215eb2eb1efba0ca30ede68`, Git blob
  `d6b99f48428f6fbb55d496c4bd203f92f3457f8e`.
- Content: SHA-256
  `46c08588bd4b9c62fc53dba65dcd39cd9a09a0ad2a37d9731f1aaeb24cb0e024`,
  24,304 bytes. The same commit's `lean-toolchain` binds the manual to
  `leanprover/lean4:v4.33.0`.
- Proposed approval: only `CLAIM.SOURCE.MANUAL.DEFS.THEOREM_PROP`, lines
  575–588 (especially 582), for `DECL.THEOREM.TYPE_PROP`: the theorem
  statement must be a proposition, while definition types may inhabit any
  universe.
- Limiting claim: lines 584–586 say the theorem header is elaborated before its
  body. That is not sufficient to establish
  `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`; do not approve that mapping from this
  source.
- Assumptions/lineage: official, exact-version, Lean-project-governed prose;
  same project lineage as the target and not a mechanized metatheory proof.
- Recommendation: **APPROVE the theorem-Prop claim only** because the wording,
  version, and frozen denotation align directly. Reject or defer the visibility
  inference.

## Recommended DEFER

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.VERSION_BINDING`

- Identity/content: `lean-toolchain` at reference-manual commit
  `02d0d61af6d344da5215eb2eb1efba0ca30ede68`, Git blob
  `025e59548e48cf71f2744154e2890beefe30a258`, SHA-256
  `302cd63c54178885b89e669f33b38f12f4dd7ae7e5cac537b3203e3768d8fb2b`,
  25 bytes.
- Claim: the companion manual snapshot targets Lean v4.33.0.
- Limitation: version provenance only; supports no obligation itself.
- Recommendation: **DEFER as authority**, but require it as the exact version
  binding for any approved manual claim.

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.TYPE_SYSTEM`

- Identity/content: `Manual/Types.lean` at the same commit, Git blob
  `6939b5f99e040a0207afd00759f51c962101e253`, SHA-256
  `29c61358d2dac0a663bd3749267e52cae66c91466816425f513f9ac90830a01b`,
  20,909 bytes.
- Claims: conversion at line 93; dependent-function sort rule at lines
  225–251; universe-variable binding and unbound-use rejection at lines
  420–514.
- Possible obligations: `DECL.UNIVERSE.PARAM_OWNERSHIP`,
  `DECL.TYPE.SORT_VALUED`, `DECL.VALUE.TYPE_MATCH`,
  `EXPR.BINDER.DOMAIN_SORT`, `EXPR.PI.CODOMAIN_SORT`,
  `EXPR.LET.VALUE_TYPE_MATCH`, and `EXPR.APP.ARGUMENT_TYPE_MATCH`.
- Limitations/lineage: exact official source, but several mappings cross from
  general type-system or source-language prose to raw serialized kernel
  judgments. It does not state duplicate universe-list rejection.
- Recommendation: **DEFER** unless the reviewer explicitly accepts each layer
  mapping; do not approve the file wholesale.

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.FUNCTIONS`

- Identity/content: `Manual/Language/Functions.lean` at the same commit, Git
  blob `a1cbf166665121ba23474f816b11b3fbf50afdb1`, SHA-256
  `14cdbff4765457205438dc76f452645da85a49a2ffd8c4608dcee3932095082f`,
  11,287 bytes.
- Claims: all core function types are dependent and specify domain/codomain
  (lines 18–53); core functions accept type-correct domain elements (lines 135
  and 185–187).
- Possible obligations: binder/Pi sort boundaries and both application
  boundaries.
- Limitations/lineage: official and exact, but it does not give the formal raw
  `Expr.app`, `Expr.lam`, or `Expr.forallE` inference premises, and argument
  compatibility is not stated specifically as definitional equality.
- Recommendation: **DEFER** pending a precision decision.

### `SOURCE.CANDIDATE.LEAN4LEAN.PAPER`

- Identity/content: Mario Carneiro, *Lean4Lean: Towards a formalized
  metatheory for the Lean theorem prover*, arXiv:2403.14064v1, SHA-256
  `56ba2ac2481c6aac8a89f0d88e64115c3d9d80f7ee7c45c8c4ce14f186b0f6e8`,
  612,729 bytes.
- Claim: the work reports initial steps toward an abstract Lean type theory and
  a relation between kernel functions and that theory.
- Possible obligations: broad declaration typing, binder/let, and application
  families.
- Limitations/lineage: 2024 version mismatch; same author/project lineage as
  the mechanization; the paper itself describes the metatheory as initial and
  does not authenticate the pinned 2026 proof dependencies.
- Recommendation: **DEFER** as context and limitation evidence, not standalone
  normativity.

### `SOURCE.CANDIDATE.LEAN4LEAN.THEORY.BASIC`

- Identity/content: `Lean4Lean/Theory/Typing/Basic.lean` at
  `ecb3b6661c14f8147be1069b126c629114baf4a8`, Git blob
  `c7ae89a909b77f0e53453ca129fb9238f8ec8ee9`, SHA-256
  `97eeaafbae07435d3a3d2cedffe04ca8aa37ac8ab812040aa6557cead97ca6be`,
  2,740 bytes.
- Claims: `constDF` requires well-formed levels and exact level arity;
  `appDF` requires a Pi-typed function and domain-typed argument; `lamDF` and
  `forallEDF` require the expected sort premises (lines 25–43).
- Possible obligations: universe ownership/arity, binder/Pi sorts, and both
  application boundaries.
- Limitations/lineage: these are definitions of Lean4Lean's modeled judgment,
  not an independent theorem that the model is Lean v4.33.0's normative
  judgment. No exact compatibility proof was found.
- Recommendation: **DEFER** the precise rules until their normative standing
  and model/target mapping are approved.

### `SOURCE.CANDIDATE.LEAN4LEAN.THEORY.ENVIRONMENT`

- Identity/content: `Lean4Lean/Theory/Typing/Env.lean` at the same revision,
  Git blob `e0eb8db59294f537876ae8c20be76b992e40e93e`, SHA-256
  `b79aa5e1a5c670d2e0851e3e5ef44b62735043546573ac26fa6749c0ce50526d`,
  1,772 bytes.
- Claim: `VDecl.WF` requires well-formed constant types, definition bodies with
  declared types, and successful `addConst` environment extension.
- Possible obligations: name freshness, sort-valued declaration type, body
  type match, and current-declaration visibility.
- Limitations/lineage: abstract `VEnv`/`VDecl.WF` model; same checker-project
  lineage; no self-authenticating correspondence to the concrete target.
- Recommendation: **DEFER**.

### `SOURCE.CANDIDATE.LEAN4LEAN.VERIFY.CHECKER`

- Identity/content: `Lean4Lean/Verify/Environment/Checker.lean` at the same
  revision, Git blob `60e6cdb79716c09d475b9ca023ae8b904799068e`, SHA-256
  `8f1136c70d4749412db060b0a8241b057e22c8ea56e490df839c470485bc53da`,
  12,906 bytes.
- Claims: `checkName.WF` and `checkConstantValCore.WF` yield freshness and a
  sort-valued modeled type (lines 13–118); `checkBody.WF` yields a body with
  the declared type (lines 119–158); `checkTheorem.WF` yields a theorem type
  inhabiting `sort zero`, matching body, and fresh name (lines 160–183).
- Possible obligations: freshness, loose-variable closure, type sorthood, body
  type match, theorem Prop, and current-declaration visibility.
- Assumptions/limitations/lineage: exact theorem axiom sets were not closed;
  imported verification code includes custom implementation-bridge axioms and
  active `sorry`-backed obligations. The checker and proofs share project
  lineage, and the normative status of the modeled relation is unresolved.
- Recommendation: **DEFER**. This is the strongest mechanized candidate, but
  approval before exact `#print axioms` closure and judgment mapping would
  overstate the evidence.

## Recommended REJECT as normative authority

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.TERMS`

- Binding: `Manual/Terms.lean` at reference-manual commit `02d0d61...`, Git
  blob `48977769b7af57eb1c45cc931ce51f7a9aada1c1`, SHA-256
  `d77336aaa07a0a55d4235c0fd0b0960be10c090955ef239a6056972dd0ff7950`,
  76,686 bytes.
- Claim/limits: source-language type ascription must match context by
  definitional equality (lines 1950–1970), but no precise raw let/application
  rule was found.
- Recommendation: **REJECT** as authority for the frozen raw-expression
  obligations; retain as insufficiently precise exact-version prose.

### `SOURCE.CANDIDATE.OFFICIAL.MANUAL.LATEST_MISMATCH`

- Binding: unversioned latest landing page retrieved 2026-09-02, SHA-256
  `494d1c89630a614ea754ddfc8d9e9c4cbd619cfd13e6bdc9bcf5b3d6ab9f78ef`,
  97,155 bytes.
- Claim/limits: HTML line 2857 says it covers Lean `4.34.0-rc2`; the URL is
  mutable and mismatched to v4.33.0.
- Recommendation: **REJECT** for this study; retain as the reason unversioned
  `latest` pages cannot authenticate target-version claims.

### `SOURCE.CANDIDATE.LEAN4.API.ENVIRONMENT`

- Binding: `src/Lean/Environment.lean` at target revision `d8b189...`, Git blob
  `33928512dadcfa2e42a307499e9228596da0341a`, SHA-256
  `ee364e4788ce0560c87f621eeb3c4c3dfec62e8db4e15e099fd80e6adc533b86`,
  137,725 bytes.
- Possible obligations: name freshness and current visibility; no exact
  normative claim was extracted.
- Recommendation: **REJECT** as normative authority; retain for exact API and
  representation terminology.

### `SOURCE.CANDIDATE.LEAN4.IMPLEMENTATION.ENVIRONMENT`

- Binding: `src/kernel/environment.cpp` at target revision `d8b189...`, Git
  blob `8e302240ad0a6394bad8e1b4125f63aff4b54a53`, SHA-256
  `6748cf9368a16b7e4fd8546accc78f98874fb69323934b21c796e722dad136b2`,
  12,458 bytes.
- Implemented behavior: header checks at lines 92–132; safe body/Prop checks
  before insertion at lines 160–223.
- Possible obligations: seven declaration/environment candidates.
- Recommendation: **REJECT** as normative authority because this is the target
  implementation; retain for locator and mapping evidence.

### `SOURCE.CANDIDATE.LEAN4.IMPLEMENTATION.TYPECHECKER`

- Binding: `src/kernel/type_checker.cpp` at target revision `d8b189...`, Git
  blob `5287d22c5db67ceeb01231295c581382e1e78f3d`, SHA-256
  `e996524515626fea05fdfd998e48fec8955881b94528a7bee2f678e526602b2c`,
  48,970 bytes.
- Implemented behavior: universe checks at lines 93–114; lambda/Pi checks at
  117–158; application/let checks at 165–222.
- Possible obligations: eight expression/universe candidates.
- Recommendation: **REJECT** as normative authority; retain as the exact
  implementation mapping.

### `SOURCE.CANDIDATE.LEAN4.PAPER.SYSTEM_DESCRIPTION`

- Binding: de Moura and Ullrich, 2021 system description, SHA-256
  `2b907e98552f5ff4fe77be717f9423311a4d6bf4ac866b143d99f34e83f39c4d`,
  361,568 bytes.
- Claim: historically, a theorem is a definition whose result type is a
  proposition (PDF page 3 / printed page 3).
- Limitations: early Lean 4 version; no source-authored compatibility proof to
  v4.33.0; no bounded obligation inventory.
- Recommendation: **REJECT** as target-version authority; retain as favorable
  historical corroboration.

### `SOURCE.CANDIDATE.LEAN4LEAN.VERIFY.BOUNDARIES`

- Binding: `Lean4Lean/Verify/Environment/Boundaries.lean` at `ecb3b666...`, Git
  blob `5b800d2a5e9b2a2b1372f63f6a681a4c202c4ac3`, SHA-256
  `31b5718f8dd64eab2fd3f9592175c49cfff2693284e37e638a8f0cab144d6e10`,
  1,635 bytes.
- Adverse claim: explicit `sorry` in `checkPrimitiveDef.WF` at line 35.
- Limitation: it may not be a dependency of every proposed checker theorem;
  exact dependency closure is unresolved.
- Recommendation: **REJECT** as positive authority and require it as limiting
  context for any Lean4Lean approval.

### `SOURCE.CANDIDATE.LEAN4LEAN.VERIFY.AXIOMS`

- Binding: `Lean4Lean/Verify/Axioms.lean` at `ecb3b666...`, Git blob
  `f620c1165715ec58d07ed498a75549713c9dd5e4`, SHA-256
  `52fe205cd54e3b38b53862694e4d673b406eb89c99710248cc17f87ef226b43c`,
  20,498 bytes.
- Adverse claim: custom equality axioms bridge executable Lean operations to
  total modeled functions, including loose-bound-variable and substitution
  operations (representative lines 360, 382, 402, 421–440, 463–485, 505–508).
- Possible obligations: closure, universe ownership, binder/let, and
  application families through proof dependencies.
- Recommendation: **REJECT** as positive authority; retain as explicit
  assumption evidence and require exact per-theorem axiom closure.

### `SOURCE.CANDIDATE.KIOTA.PARSER`

- Binding: `src/parser.rs` at Kiota revision
  `58e8636cfb51cf9c3bf3de7455a0e3c6ab68e87a`, Git blob
  `cf6a5bb2c3467f24ecb3f72d14295d09db0d18ae`, SHA-256
  `c6c53ac6a364b9d318585ad7c51ad8dd9883c027cb9dc356c119373782c77392`,
  23,839 bytes.
- Behavior: rejects duplicate names (193–204), inserts ordinary declarations
  in `handle_def_like` (206–275), then invokes `check_decl` from `check_last`
  (586–611).
- Possible obligations: name freshness and current-declaration visibility.
- Limitation/contradiction: insertion-before-check contradicts the official
  safe path's pre-insertion check. It may be a reconstruction choice or defect;
  behavior alone is not normativity.
- Recommendation: **REJECT** as authority; retain as mandatory contradictory
  implementation evidence.

### `SOURCE.CANDIDATE.KIOTA.ENVIRONMENT`

- Binding: `src/env.rs` at the same Kiota revision, Git blob
  `689020bc5d7877e5339929a86a8976aa3cd41cdb`, SHA-256
  `b8665c8b96f770ffffe6d6ff50e05bd4a468edfb835c665ce98485b1bac0107b`,
  4,057 bytes.
- Behavior: `Environment.get` and `insert` use one mutable constant map (lines
  145–151), supporting the insertion-before-check visibility observation.
- Recommendation: **REJECT** as authority; retain as the mechanism behind the
  contradictory implementation evidence.

## Gaps and threats requiring explicit acceptance

1. The cohort may have a sparse normatively grounded denominator. That is a
   valid result, not a reason to substitute candidates or weaken authority.
2. The manual is exact-version and official, but many candidate predicates are
   below its prose layer. Over-broad approval would manufacture normativity.
3. Lean4Lean contains unusually relevant formal rules and soundness theorems,
   but current evidence does not close their exact axiom/sorry dependencies or
   prove that their modeled judgment is the normative Lean v4.33.0 judgment.
4. The primary papers are version-mismatched and provide no explicit
   compatibility mapping.
5. Current-declaration visibility has an implementation disagreement. It must
   not be resolved by checker voting or official-implementation privilege.
6. No contradictory normative primary source was found; absence of a located
   contradiction is not evidence of normative consensus.
7. The unversioned latest manual changed after the target release, confirming
   that immutable source identities are necessary.

## Stop boundary

After review, the next authorized action is to create a separately governed,
human-approved source-decision successor bound to the frozen discovery JSON.
Only then may the two fixed sentinels exercise the authority-adjudication
process. No remaining 15-entry adjudication, baseline measurement, synthesis,
mutation, or checker campaign is authorized by this packet.
