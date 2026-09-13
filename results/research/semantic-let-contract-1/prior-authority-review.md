# Retained let authority and exact example review

Local review for `SEMANTIC-LET-CONTRACT-1`; no authority adjudication, network
request, build, checker, proof or new export. The declaration-validation
adjudication skill and current portfolio plan govern this read-only review.

The frozen `EXPR.LET.VALUE_TYPE_MATCH` denotation is: “The inferred type of a
local let value is definitionally equal to its annotation.” Applicability is
“Let expressions reached while checking a primary ordinary declaration after
annotation/value well-formedness.” See
`config/declaration-validation-identity-registry.json` and the corresponding
`identity_denotation` in `config/declaration-validation-catalog.json` (statement
SHA-256 `5a9589eb9198876dfe1b7d309b58d6d8a09d7fb93e861c0d0ef39a1a2805c523`,
denotation SHA-256 `588a74c5867dcf1f6f74f2cdf558b07edc2d1da3f7fc08eede208076bb4f27c8`).
Annotation sorthood remains a separate frozen identity.

`config/declaration-validation-target.json#/logical_target/modeled_judgment`
fixes checked ordinary declaration addition at Lean v4.33.0
`d8b18978322de05a8f3dba51ef03cf5461676c17`, with the immediately preceding
checked environment supplied. Parsing, reconstruction, export production,
elaboration and unchecked insertion are excluded. A question about arbitrary
reduction APIs must therefore state how its admissible inputs connect to this
judgment; it cannot silently broaden this identity.

The exact Gate-4 decisions are in
`results/research/declaration-validation-publication-study-authority-source-approval.json`:

- `CLAIM.SOURCE.MANUAL.TYPES.CONVERSION`: **DEFER**, because general conversion
  prose had not been independently mapped to frozen raw-expression premises.
  Retained source:
  `results/research/evidence/declaration-validation-publication-study/reference-manual-02d0d61-Types.lean`,
  lines 41–94. Zeta is described as replacing let-bound variables with values;
  conversion presupposes a term already having a type. This does not itself
  supply raw malformed-input admissibility or a mandatory algorithmic order.
- `CLAIM.SOURCE.MANUAL.TERMS.ASCRIPTION_MATCH`: **REJECT** for this use, because
  elaboration/ascription prose is insufficiently precise for raw `Expr.letE`.
  The retained `reference-manual-02d0d61-Terms.lean`, lines 1950–1970, is in the
  same evidence directory.
- `CLAIM.SOURCE.LEAN4.TC.IMPLEMENTED_EXPR_CHECKS`: **REJECT** as normative
  authority. The retained `lean4-d8b18978-type_checker.cpp`, lines 200–222,
  checks annotation sorthood and value compatibility when `!infer_only`, before
  extending its local context. That is exact implementation interpretation.
- `CLAIM.SOURCE.LEAN4LEAN.PAPER.INITIAL_METATHEORY`: **DEFER** pending exact
  proof dependencies and target-version correspondence.
  `CLAIM.SOURCE.LEAN4LEAN.AXIOMS.BRIDGES`: **REJECT** as positive authority;
  custom substitution/representation bridge axioms require dependency closure.
  These source identities and limitations are in
  `results/research/declaration-validation-publication-study-source-discovery.json`.

The Gate-6 adjudication retains this entry **PROVISIONAL**, with no approved
claim. `config/declaration-validation-approved-authority-sources/publication-study-v2.json`
approves only theorem-Prop documentation and explicitly forbids cross-claim
reuse. This review does not discharge any qualification requirement.

The minimal existing example is a decoding of the two unchanged 601-byte files,
not newly elaborated Lean source:

```text
candidate: def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
control:   def EcosystemCase : Sort 1 := let u : Sort 1 := Sort 0; u
```

Candidate:
`corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson`
(SHA-256 `52e75d78c948d466e90fb203e7a04192dde4273c7319d44fc261fd2b3b6beeac`).
Control:
`corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson`
(SHA-256 `63ef460ca2aac739482c983457cd14309f4d7149ecd2c0d79d53fe2a410c9f16`).
Both encode a safe definition with opaque hints, no universe parameters, a
`nondep:false` let and body `bvar 0`. The candidate's value `Sort 1` has type
`Sort 2`, whereas its annotation is `Sort 1`. Zeta substitution yields `Sort 1`,
matching the candidate's enclosing declaration type `Sort 2`. The control
substitutes `Sort 0`, matching its enclosing type `Sort 1`.

The body uses the binding: do not describe this as an unused-value example.
The pair changes both the let value and enclosing declaration type; do not
claim it differs in only one serialized field. Its metadata identifies an
export format/producer version, not proof that Lean elaboration emitted this
malformed candidate.

`corpus/expected/nanoda-gen-21ef4d1d32a1-witness.json` and
`results/witnesses/nanoda-gen-21ef4d1d32a1-witness/confirmation.json` bind the
pinned official and Nanoda baseline candidate rejection/control acceptance.
`results/research/arena-let-regression-1/arena-audit-erratum.json` preserves
both profiles and attributes the affirmative-support requirement for `either`
to the **Lab portfolio rule**, not Arena's schema. The older catalog M8 let
witness is the distinct e551 artifact (SHA-256
`a2f53d20e33e3a4f69e5061b3b4b2a328de3c4f9bff64dee3b250cc847427d43`);
its official/Lean4Lean/Kiota outcomes must not be attributed to this 21ef pair.

A useful maintainer question should distinguish (1) premises for assigning a
type to a raw let, (2) the input and environment contract under which a reducer
may erase annotations, and (3) what a serialized-declaration validator promises
to validate. Ask whether the exact candidate may be accepted after zeta under
that specified contract, and where that policy should be documented. Avoid
presupposing an implementation defect, unsoundness, a required checking order,
or a universal Arena `reject`/`either` answer. Existing beta-erasure examples
are context, not an automatic decision for this let pair.

Accounting: review completed at 2026-09-13T13:16:53.660993+00:00; conservative elapsed upper bound 228.006 seconds from the parent item start (2026-09-13T13:13:05.637413+00:00, monotonic 83940.16999425) to review completion (monotonic 84168.176388416). The delegate start was not separately sampled; this upper bound includes pre-delegation parent work. It wholly overlaps the parent active interval and adds no separate budget charge.
