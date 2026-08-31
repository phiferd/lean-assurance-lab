# Declaration Validation Milestone 8 Pilot

> Generated file. Edit `config/declaration-validation-milestone-8-pilot.json`, not this report.

- Pilot ID: `ordinary-declaration-validation.milestone-8-pilot.v1`
- Status: `MILESTONE_8_FIVE_ENTRY_PILOT_REVIEWED`
- Pilot SHA-256: `6fa2622de2d23e520a609a811d38f67097778a89203349993a619f0afc3057ed`
- Candidate entries: 5
- Bound authority registry: `ordinary-declaration-validation.approved-authority-sources.m7.v1`
- M4 site dispositions: 31

This is the reviewed, historical five-entry candidate batch preserved before the complete Milestone 8 inventory. It does not change the canonical catalog status or disposition the remaining frozen identities.

## Selection

Select five frozen identities with already content-bound Lab result bytes, an existing generated witness or control where relevant, and a source-locked implementation site. The batch is chosen to exercise both catalog kinds and multiple declaration-validation boundaries; it is not a ranking or a coverage denominator.

- Four normative candidate obligations and one empirical contract scenario.
- Theorem proposition-valued typing, current-declaration visibility, universe-parameter ownership, local let value/type compatibility, and serialized axiom safety-flag treatment.
- Structured official, Kiota, and Lean4Lean outcome extraction, plus explicit uninspected Nanoda rows.

## Candidate Summary

| Stable ID | Kind | Authority | Observer vector |
| --- | --- | --- | --- |
| `DECL.THEOREM.TYPE_PROP` | `NORMATIVE_CANDIDATE_OBLIGATION` | `PROVISIONAL` | `official_importer=REJECT, nanoda=NOT_INSPECTED, lean4lean=REJECT, kiota=REJECT` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `NORMATIVE_CANDIDATE_OBLIGATION` | `PROVISIONAL` | `official_importer=REJECT, nanoda=NOT_INSPECTED, lean4lean=REJECT, kiota=ACCEPT` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `NORMATIVE_CANDIDATE_OBLIGATION` | `PROVISIONAL` | `official_importer=REJECT, nanoda=NOT_INSPECTED, lean4lean=REJECT, kiota=ACCEPT` |
| `EXPR.LET.VALUE_TYPE_MATCH` | `NORMATIVE_CANDIDATE_OBLIGATION` | `PROVISIONAL` | `official_importer=REJECT, nanoda=NOT_INSPECTED, lean4lean=REJECT, kiota=REJECT` |
| `SCENARIO.AXIOM.SAFETY_FLAG` | `EMPIRICAL_CONTRACT_SCENARIO` | `PROVISIONAL` | `official_importer=REJECT, nanoda=NOT_INSPECTED, lean4lean=REJECT, kiota=ACCEPT` |

## Per-Entry Review Material

### `DECL.THEOREM.TYPE_PROP` — Theorem proposition-valued type

- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` — Existing source, witness, and observer evidence supports a bounded candidate, but the frozen approved-authority-source registry contains no qualifying normative source.
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Source mappings: `LOGICAL_TARGET` at `SRC.OFFICIAL.ENVIRONMENT`
- Arena disposition: `LINKED` — `tutorial/012_nonPropThm` at `external/lean-kernel-arena/_build/tests/tutorial/bad/012_nonPropThm.ndjson`
- Open questions: Which preapproved normative source, if any, qualifies this candidate as a requirement of the modeled judgment?

### `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` — Current declaration not visible during validation

- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` — The selected witness and source mapping show a bounded implementation boundary, while normative support remains absent from the frozen approved registry.
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Source mappings: `NANODA` at `SRC.NANODA.ENV`
- Arena disposition: `NOT_INSPECTED` — No Arena case linkage was inspected during this narrowly scoped repair pass.
- Open questions: Which preapproved normative source, if any, qualifies this environment-visibility candidate?

### `DECL.UNIVERSE.PARAM_OWNERSHIP` — Declaration universe-parameter ownership

- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` — The selected witness and implementation mapping identify an observed boundary, but qualified normative support is absent from the frozen authority-source registry.
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Source mappings: `KIOTA` at `SRC.KIOTA.TC`
- Arena disposition: `NOT_INSPECTED` — No Arena case linkage was inspected during this narrowly scoped repair pass.
- Open questions: Which preapproved normative source, if any, qualifies universe-parameter ownership for the modeled judgment?

### `EXPR.LET.VALUE_TYPE_MATCH` — Let value and annotation compatibility

- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` — The selected witness and source mapping support a bounded candidate, but no qualifying normative source is in the frozen approved registry.
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Source mappings: `LEAN4LEAN` at `SRC.LEAN4LEAN.TYPECHECKER`
- Arena disposition: `NOT_INSPECTED` — No Arena case linkage was inspected during this narrowly scoped repair pass.
- Open questions: Which preapproved normative source, if any, qualifies local let value/type compatibility for the modeled judgment?

### `SCENARIO.AXIOM.SAFETY_FLAG` — Axiom safety-flag treatment

- Layers: `EXPORT_FORMAT`, `RECONSTRUCTION`, `TRUST_POLICY`, `IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` — The pilot records exact outcomes for three observer profiles but leaves the Nanoda profile uninspected and does not collapse the cross-layer behavior into one interpretation.
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Source mappings: `KIOTA` at `SRC.KIOTA.PARSER`
- Arena disposition: `NOT_APPLICABLE` — This serialized safety-flag reconstruction scenario is not represented as an Arena semantic-obligation link in the pilot.
- Open questions: What is the content-bound outcome of the pinned Nanoda observer for this exact scenario, and how should parser, reconstruction, and trust-policy effects be separated?

## M4 Implementation-Site Closure

Every frozen M4 site relevant to one of these five frozen M5 identities has an explicit M8 characterization disposition. This is provenance and completeness of implementation characterization; it is not normative support.

| Stable ID | M4 site | Implementation | M8 disposition |
| --- | --- | --- | --- |
| `SCENARIO.AXIOM.SAFETY_FLAG` | `SITE.OFFICIAL.ENV.AXIOM` | `LOGICAL_TARGET` | `MAPPED_POLICY` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.OFFICIAL.ENV.DEF` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.OFFICIAL.ENV.THEOREM` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.OFFICIAL.ENV.THEOREM` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.OFFICIAL.ENV.OPAQUE` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.OFFICIAL.TC.CONST` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `EXPR.LET.VALUE_TYPE_MATCH` | `SITE.OFFICIAL.TC.APP_LET` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.OFFICIAL.TC.DISPATCH` | `LOGICAL_TARGET` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.NANODA.TC.HEADER` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.NANODA.TC.CONST` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `EXPR.LET.VALUE_TYPE_MATCH` | `SITE.NANODA.TC.APP_LET` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.NANODA.ENV.CUTOFF` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.NANODA.UTIL.CURRENT_VISIBILITY` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `SCENARIO.AXIOM.SAFETY_FLAG` | `SITE.NANODA.PARSER.POLICY` | `NANODA` | `MAPPED_POLICY` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.NANODA.LEVEL.PARAMS` | `NANODA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `SCENARIO.AXIOM.SAFETY_FLAG` | `SITE.LEAN4LEAN.ENV.AXIOM` | `LEAN4LEAN` | `MAPPED_POLICY` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.LEAN4LEAN.ENV.DEF` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.LEAN4LEAN.ENV.THEOREM` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.LEAN4LEAN.ENV.THEOREM` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.LEAN4LEAN.ENV.OPAQUE` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.LEAN4LEAN.TC.CONST` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `EXPR.LET.VALUE_TYPE_MATCH` | `SITE.LEAN4LEAN.TC.APP_LET` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.LEAN4LEAN.TC.DISPATCH` | `LEAN4LEAN` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.LEAN4LEAN.REPLAY.ORDER` | `LEAN4LEAN` | `MAPPED_RECONSTRUCTION` |
| `DECL.THEOREM.TYPE_PROP` | `SITE.KIOTA.TC.DECL` | `KIOTA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.KIOTA.TC.CONST` | `KIOTA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `EXPR.LET.VALUE_TYPE_MATCH` | `SITE.KIOTA.TC.APP_LET` | `KIOTA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.KIOTA.TC.UNIVERSE_ABSENCE` | `KIOTA` | `OBSERVED_ABSENCE` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.KIOTA.PARSER.INSERT_BEFORE_CHECK` | `KIOTA` | `MAPPED_RECONSTRUCTION` |
| `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` | `SITE.KIOTA.ENV.MAP` | `KIOTA` | `MAPPED_IMPLEMENTATION_BEHAVIOR` |
| `DECL.UNIVERSE.PARAM_OWNERSHIP` | `SITE.KIOTA.LEVEL.NO_OWNERSHIP_CONTEXT` | `KIOTA` | `OBSERVED_ABSENCE` |

The two Kiota universe-ownership sites are retained as `OBSERVED_ABSENCE`: the frozen checking path has no current-declaration ownership context/check. This is neither an enforcement mapping nor an unsoundness claim.

## Authority Provenance

The repaired pilot content-binds the empty historical registry snapshot at `config/declaration-validation-approved-authority-sources/m7-pre-m8.json` (SHA-256 `1c151df258514fd46f868593e09b18fe0b02e8dfe1c27fa4b92bcc682a830708`). It also preserves the pre-hardening pilot provenance record at `results/research/declaration-validation-milestone-8-pilot-pre-hardening-provenance.json`.

A future registry successor must be separately approved against its predecessor before a later catalog can bind it; this pilot neither approves a source nor selects one.

## Historical Boundary

The pilot predecessor is the immutable M7 historical attestation at `results/research/declaration-validation-milestone-7-historical.json` (SHA-256 `2970a01211e51475a02e4c031725d228a008e568804b34f1df5baf3250f4bef8`), specifically its `catalog` artifact. It does not read the mutable current catalog path.

The pre-hardening provenance record, repaired evidence-lock chain, and every other pilot input are resolved from exact Git blobs at the pilot repair commit. Future M8 catalog evolution therefore cannot re-interpret this pilot through later catalog or schema bytes.

## Required Review

- Review the five selected stable identities, their exact denotations, and whether each stated layer is appropriately scoped.
- Review each provisional authority disposition against the frozen empty approved-authority-source registry; do not promote an entry by implementation agreement.
- Review the complete observer vectors, including all NOT_INSPECTED rows and preserved Kiota disagreements.
- Review whether the demonstrated source-mapping and evidence-lock representation is adequate before adjudicating the remaining 25 identities.

## Stop Boundary

The five-entry pilot review is complete. Preserve this historical pilot; do not modify the canonical catalog status, create a 30-identity disposition vector, claim Milestone 8 completion, or begin Milestone 9 from this artifact.

## Nonclaims

- This is a five-entry candidate pilot, not the canonical Milestone 8 characterization inventory.
- All four normative candidates remain PROVISIONAL because the frozen approved-authority-source registry contains no qualifying normative support.
- The empirical axiom safety-flag scenario is PROVISIONAL; its observed profile differences do not establish a universal semantic rule.
- No checker outcome, agreement, disagreement, or implementation-source mapping establishes normative authority or logical-soundness relevance.
- The remaining 25 frozen identities have not been dispositioned by this pilot.
