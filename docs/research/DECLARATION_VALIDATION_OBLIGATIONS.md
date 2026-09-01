# Declaration Validation Obligations and Scenarios

> Generated file. Edit `config/declaration-validation-catalog.json`, not this report.

- Catalog ID: `ordinary-declaration-validation.catalog.v1`
- Catalog status: `MILESTONE_9_REVIEWED_FREEZE`
- Catalog SHA-256: `ee46af8fbc760026351960baa000649a31fbaf6ed925b07cff1350b4b89320c3`
- Catalog entries: 27
- Existing evidence/identity dispositions: 41

This report is a deterministic view of the canonical machine-readable catalog. Its catalog hash is checked mechanically. This is the frozen post-adversarial-review inventory.
The bound evidence-lock successor is `ordinary-declaration-validation.evidence-lock.milestone-9-reviewed.v1` at sequence 6.
The separately frozen approved-authority-source registry contains 0 normative documents and 0 mechanized sources. Content addressing alone is not treated as authentication of external origin.
Stable IDs bind the complete canonical semantic projection; observer outcomes and editorial prose remain non-identity research metadata.

## Bound Inputs

| Input | Path | SHA-256 |
| --- | --- | --- |
| approved_authority_sources | config/declaration-validation-approved-authority-sources.json | `1c151df258514fd46f868593e09b18fe0b02e8dfe1c27fa4b92bcc682a830708` |
| approved_authority_sources_schema | schemas/declaration-validation-approved-authority-sources.schema.json | `d4e9c78ab35302d7a56b193d87226a7943b8e85db6fdf89dd19d891ae367b325` |
| authority_rules | config/declaration-validation-authority-rules.json | `de56148f267eca9f1fd91c6f9a8d42f7786e1b946eb7565f704ccaa193838ea0` |
| characterization_model | config/declaration-validation-characterization-model.json | `6633f1408a174e23136f79ba47d191fd09b4ccfa9e51dceb35b78490692c0ff7` |
| discovery_closure | config/declaration-validation-discovery-closure.json | `d45e19670561cbceee89c93cc9cbd3d5c98e04fc35e3b82f66ff681afdbf0731` |
| entry_schema | schemas/declaration-validation-characterization-entry.schema.json | `33f39e95a6d7c55088f10d4eb9dffea82eff83d77397a4ec5bb688e7a2a57ce6` |
| evidence_lock | config/declaration-validation-evidence-locks/milestone-9-reviewed.json | `3b48a3c68900011dc3431382f3fe1bbb87b730f188428d4579dbc32631e3f6bf` |
| evidence_lock_schema | schemas/declaration-validation-evidence-lock.schema.json | `45e0c7a69be059a371f4d33445cb7cdbdad21c542a82b07a7f1dfb65a6416adf` |
| identity_registry | config/declaration-validation-identity-registry.json | `68e8770c808518170a9a22766f8e2ea79d3d2bdf0b643101026d6ec55a69f230` |
| semantic_target | config/declaration-validation-target.json | `4fb46d5b3e078e54cf2731540329f6b14e5b9fa62d25284f78a93db1a27aa5fa` |
| source_lock | config/declaration-validation-source-lock.json | `2ac3836b854392bc8302d78ed38d6a0f85b046fff8d16657a3a20af09d2fc88b` |

## Summary

### Counts by Kind

| Kind | Count |
| --- | --- |
| NORMATIVE_CANDIDATE_OBLIGATION | 19 |
| EMPIRICAL_CONTRACT_SCENARIO | 8 |

### Counts by Layer

| Layer | Count |
| --- | --- |
| KERNEL_DECLARATION_VALIDITY | 19 |
| EXPORT_FORMAT | 3 |
| RECONSTRUCTION | 7 |
| TRUST_POLICY | 3 |
| IMPLEMENTATION_POLICY | 5 |

### Counts by Authority Status

| Authority status | Count |
| --- | --- |
| ESTABLISHED | 0 |
| PROVISIONAL | 27 |
| UNRESOLVED | 0 |

### Counts by Lifecycle Status

| Lifecycle status | Count |
| --- | --- |
| ACTIVE | 27 |
| SUPERSEDED | 0 |
| REDUNDANT | 0 |
| OUT_OF_SCOPE | 0 |

### Counts by Identity Disposition

| Disposition | Count |
| --- | --- |
| CATALOG_ENTRY | 27 |
| DEFERRED_UNRESOLVED_KIND | 1 |
| OUT_OF_SCOPE | 2 |

## Checker Observation Summary

| Observer | ACCEPT | REJECT | ERROR | TIMEOUT | NOT_INSPECTED | NOT_APPLICABLE | UNRESOLVED |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /observer_profiles/official_importer | 1 | 7 | 0 | 0 | 19 | 0 | 0 |
| /observer_profiles/nanoda | 0 | 0 | 0 | 0 | 27 | 0 | 0 |
| /observer_profiles/lean4lean | 1 | 7 | 0 | 0 | 19 | 0 | 0 |
| /observer_profiles/kiota | 6 | 2 | 0 | 0 | 19 | 0 | 0 |

## Catalog Summary Table

| ID | Rule/scenario | Kind | Layers | Authority | Lifecycle | Arena | Lab |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | Current declaration not visible during validation | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.SELF_REFERENCE.WITNESS |
| DECL.ENV.NAME_FRESHNESS | Declaration name freshness | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.DISCOVERY |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | Declaration expression bound-variable closure | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.DISCOVERY |
| DECL.THEOREM.TYPE_PROP | Theorem proposition-valued type | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | EVID.M8.THEOREM.ARENA | EVID.M8.THEOREM.WITNESS |
| DECL.TYPE.NO_FREE_VARS | Declaration type free-variable closure | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.DISCOVERY |
| DECL.TYPE.NO_METAVARS | Declaration type metavariable closure | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.DISCOVERY |
| DECL.TYPE.SORT_VALUED | Declaration type sort-valued requirement | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.DISCOVERY |
| DECL.TYPE.WELL_FORMED | Declaration type well-formedness | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.DISCOVERY |
| DECL.UNIVERSE.PARAM_OWNERSHIP | Declaration universe-parameter ownership | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.UNIVERSE.WITNESS |
| DECL.UNIVERSE.PARAM_UNIQUENESS | Declaration universe-parameter uniqueness | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.DISCOVERY |
| DECL.VALUE.TYPE_MATCH | Declaration value and declared-type compatibility | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.DISCOVERY |
| DECL.VALUE.WELL_FORMED | Declaration value well-formedness | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.DISCOVERY |
| EXPR.APP.ARGUMENT_TYPE_MATCH | Application argument and domain compatibility | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.DISCOVERY |
| EXPR.APP.FUNCTION_TYPE | Application function-type requirement | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.DISCOVERY |
| EXPR.BINDER.DOMAIN_SORT | Binder domain sort-valued requirement | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.DISCOVERY |
| EXPR.CONST.UNIVERSE_ARITY | Constant universe-argument arity | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.DISCOVERY |
| EXPR.LET.ANNOTATION_SORT | Let annotation sort-valued requirement | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.DISCOVERY |
| EXPR.LET.VALUE_TYPE_MATCH | Let value and annotation compatibility | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.LET_VALUE.WITNESS |
| EXPR.PI.CODOMAIN_SORT | Dependent-function codomain sort-valued requirement | NORMATIVE_CANDIDATE_OBLIGATION | KERNEL_DECLARATION_VALIDITY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.DISCOVERY |
| SCENARIO.AXIOM.ADMISSION_POLICY | Axiom admission policy | EMPIRICAL_CONTRACT_SCENARIO | TRUST_POLICY, IMPLEMENTATION_POLICY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.CONTROL, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.DISCOVERY, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.WITNESS |
| SCENARIO.AXIOM.SAFETY_FLAG | Axiom safety-flag treatment | EMPIRICAL_CONTRACT_SCENARIO | EXPORT_FORMAT, RECONSTRUCTION, TRUST_POLICY, IMPLEMENTATION_POLICY | PROVISIONAL | ACTIVE | — | EVID.M8.AXIOM.WITNESS |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | Ordinary declaration safety reconstruction | EMPIRICAL_CONTRACT_SCENARIO | RECONSTRUCTION, IMPLEMENTATION_POLICY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.CONTROL, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.DISCOVERY, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.WITNESS |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | Export free-variable representability | EMPIRICAL_CONTRACT_SCENARIO | EXPORT_FORMAT, RECONSTRUCTION | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY.DISCOVERY |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | Export metavariable representability | EMPIRICAL_CONTRACT_SCENARIO | EXPORT_FORMAT, RECONSTRUCTION | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.EXPORT.METAVAR_REPRESENTABILITY.DISCOVERY |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | Observer current-declaration visibility | EMPIRICAL_CONTRACT_SCENARIO | RECONSTRUCTION, IMPLEMENTATION_POLICY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.CONTROL, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.DISCOVERY, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.WITNESS |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | Observer replay environment construction | EMPIRICAL_CONTRACT_SCENARIO | RECONSTRUCTION | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.DISCOVERY |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | Unsafe and partial replay filtering | EMPIRICAL_CONTRACT_SCENARIO | RECONSTRUCTION, TRUST_POLICY, IMPLEMENTATION_POLICY | PROVISIONAL | ACTIVE | — | EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.DISCOVERY |

## Frozen Identity Dispositions

| ID | Disposition | Reason | Decisions |
| --- | --- | --- | --- |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.012 |
| DECL.ENV.NAME_FRESHNESS | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.001 |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.004 |
| DECL.SAFETY.SAFE_DEPENDENCY | DEFERRED_UNRESOLVED_KIND | The frozen identity registry defers its kind; M8 preserves that unresolved boundary instead of forcing a normative or empirical classification. | DEC.M5.013 |
| DECL.THEOREM.TYPE_PROP | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.011 |
| DECL.TYPE.NO_FREE_VARS | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.003 |
| DECL.TYPE.NO_METAVARS | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.003 |
| DECL.TYPE.SORT_VALUED | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.008, DEC.M5.018 |
| DECL.TYPE.WELL_FORMED | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.008, DEC.M5.018 |
| DECL.UNIVERSE.PARAM_OWNERSHIP | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.006 |
| DECL.UNIVERSE.PARAM_UNIQUENESS | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.002 |
| DECL.VALUE.TYPE_MATCH | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.010 |
| DECL.VALUE.WELL_FORMED | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.009 |
| EXPR.APP.ARGUMENT_TYPE_MATCH | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.016 |
| EXPR.APP.FUNCTION_TYPE | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.016 |
| EXPR.BINDER.DOMAIN_SORT | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.014 |
| EXPR.CONST.UNIVERSE_ARITY | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.007 |
| EXPR.LET.ANNOTATION_SORT | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.015 |
| EXPR.LET.VALUE_TYPE_MATCH | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.015 |
| EXPR.PI.CODOMAIN_SORT | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.014 |
| EXPR.PROJECTION.TYPING | OUT_OF_SCOPE | The frozen identity registry reserves this item outside the first ordinary-declaration slice, so M8 retains an explicit non-entry disposition. | DEC.M5.017 |
| SCENARIO.AXIOM.ADMISSION_POLICY | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.018 |
| SCENARIO.AXIOM.SAFETY_FLAG | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.018 |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.019 |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.005 |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.005 |
| SCENARIO.LITERAL.AVAILABILITY_POLICY | OUT_OF_SCOPE | The frozen identity registry reserves this item outside the first ordinary-declaration slice, so M8 retains an explicit non-entry disposition. | DEC.M5.021 |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.020 |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.020 |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | CATALOG_ENTRY | The frozen active identity is represented by one exact-denotation M8 catalog entry. | DEC.M5.019 |

## Existing Evidence Dispositions

| Disposition | Count |
| --- | --- |
| LINKED | 24 |
| NOT_APPLICABLE | 0 |
| SUPERSEDED_BY_STRONGER_EVIDENCE | 3 |
| DUPLICATE | 0 |
| OUTSIDE_THIS_ENTRY_LAYER | 6 |
| INSUFFICIENT_FOR_CLAIM | 5 |
| DEFERRED_TO_LATER_STUDY | 3 |

Every frozen existing-evidence record mechanically associated with an active stable identity is listed below; silence is not a disposition.

| Identity | Source-lock evidence | Kind | Disposition | Claim relevance | Catalog evidence | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | LOCAL.DECL_ENV_MATRIX | TRACKED_EVIDENCE | INSUFFICIENT_FOR_CLAIM | DISCOVERY | — | The aggregate matrix is relevant discovery context, but exact scenario results and witnesses provide the claim-specific M8 bindings. |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | LOCAL.KIOTA_SELF_REFERENCE | TRACKED_EVIDENCE | DEFERRED_TO_LATER_STUDY | IMPLEMENTATION_OBSERVATION | — | This reproduction targets a later Kiota upstream revision rather than the pinned M8 observer profile, so it cannot establish the M8 observer outcome. |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | LOCAL.SELF_REFERENCE_METADATA | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves witness-generation provenance; the exact witness and structured checker-result bytes carry the catalog-layer links. |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | LOCAL.SELF_REFERENCE_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.SELF_REFERENCE.KIOTA, EVID.M8.SELF_REFERENCE.LEAN4LEAN, EVID.M8.SELF_REFERENCE.OFFICIAL, EVID.M8.SELF_REFERENCE.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | WITNESS.SELF_REFERENCE | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.SELF_REFERENCE.KIOTA, EVID.M8.SELF_REFERENCE.LEAN4LEAN, EVID.M8.SELF_REFERENCE.OFFICIAL, EVID.M8.SELF_REFERENCE.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | WITNESS.SELF_REFERENCE_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.SELF_REFERENCE.KIOTA, EVID.M8.SELF_REFERENCE.LEAN4LEAN, EVID.M8.SELF_REFERENCE.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| DECL.THEOREM.TYPE_PROP | LOCAL.CORE_DECL_MATRIX | TRACKED_EVIDENCE | INSUFFICIENT_FOR_CLAIM | DISCOVERY | — | The aggregate matrix is relevant discovery context, but it is not the prescribed structured result-row surface for a concrete M8 observer attribution. |
| DECL.THEOREM.TYPE_PROP | LOCAL.M8.PILOT.REPAIR.ARENA_NONPROP_CASE | ARENA_EVIDENCE | LINKED | ARENA_LINKAGE | EVID.M8.THEOREM.ARENA | The immutable reviewed pilot already binds this existing Arena case as empirical coverage provenance only. |
| DECL.THEOREM.TYPE_PROP | LOCAL.NONPROP_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.THEOREM.KIOTA, EVID.M8.THEOREM.LEAN4LEAN, EVID.M8.THEOREM.OFFICIAL, EVID.M8.THEOREM.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| DECL.THEOREM.TYPE_PROP | WITNESS.NONPROP_DEFINITION_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.THEOREM.KIOTA, EVID.M8.THEOREM.LEAN4LEAN, EVID.M8.THEOREM.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| DECL.THEOREM.TYPE_PROP | WITNESS.NONPROP_THEOREM | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.THEOREM.KIOTA, EVID.M8.THEOREM.LEAN4LEAN, EVID.M8.THEOREM.OFFICIAL, EVID.M8.THEOREM.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| DECL.UNIVERSE.PARAM_OWNERSHIP | LOCAL.DECL_ENV_MATRIX | TRACKED_EVIDENCE | INSUFFICIENT_FOR_CLAIM | DISCOVERY | — | The aggregate matrix is relevant discovery context, but exact scenario results and witnesses provide the claim-specific M8 bindings. |
| DECL.UNIVERSE.PARAM_OWNERSHIP | LOCAL.KIOTA_UNIVERSE | TRACKED_EVIDENCE | DEFERRED_TO_LATER_STUDY | IMPLEMENTATION_OBSERVATION | — | This reproduction targets a later Kiota upstream revision rather than the pinned M8 observer profile, so it cannot establish the M8 observer outcome. |
| DECL.UNIVERSE.PARAM_OWNERSHIP | LOCAL.UNIVERSE_OWNERSHIP_METADATA | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves witness-generation provenance; the immutable reviewed pilot binds the exact witness and selected observer result bytes. |
| DECL.UNIVERSE.PARAM_OWNERSHIP | WITNESS.UNIVERSE_OWNERSHIP | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.UNIVERSE.KIOTA, EVID.M8.UNIVERSE.LEAN4LEAN, EVID.M8.UNIVERSE.OFFICIAL, EVID.M8.UNIVERSE.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| DECL.UNIVERSE.PARAM_OWNERSHIP | WITNESS.UNIVERSE_OWNERSHIP_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.UNIVERSE.KIOTA, EVID.M8.UNIVERSE.LEAN4LEAN, EVID.M8.UNIVERSE.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| EXPR.LET.VALUE_TYPE_MATCH | LOCAL.CORE_DECL_MATRIX | TRACKED_EVIDENCE | INSUFFICIENT_FOR_CLAIM | DISCOVERY | — | The aggregate matrix is relevant discovery context, but it is not the prescribed structured result-row surface for a concrete M8 observer attribution. |
| EXPR.LET.VALUE_TYPE_MATCH | LOCAL.LET_VALUE_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.LET_VALUE.KIOTA, EVID.M8.LET_VALUE.LEAN4LEAN, EVID.M8.LET_VALUE.OFFICIAL, EVID.M8.LET_VALUE.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| EXPR.LET.VALUE_TYPE_MATCH | WITNESS.LET_VALUE_TYPE | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.LET_VALUE.KIOTA, EVID.M8.LET_VALUE.LEAN4LEAN, EVID.M8.LET_VALUE.OFFICIAL, EVID.M8.LET_VALUE.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| EXPR.LET.VALUE_TYPE_MATCH | WITNESS.LET_VALUE_TYPE_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.LET_VALUE.KIOTA, EVID.M8.LET_VALUE.LEAN4LEAN, EVID.M8.LET_VALUE.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| SCENARIO.AXIOM.ADMISSION_POLICY | LOCAL.AXIOM_MATERIALIZATION | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves the candidate/control materialization transformation; it does not itself establish a checker outcome or normative claim. |
| SCENARIO.AXIOM.ADMISSION_POLICY | LOCAL.AXIOM_ONLY_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.CONTROL, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| SCENARIO.AXIOM.ADMISSION_POLICY | WITNESS.AXIOM_UNSAFE_ONLY | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| SCENARIO.AXIOM.ADMISSION_POLICY | WITNESS.AXIOM_UNSAFE_ONLY_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.CONTROL, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| SCENARIO.AXIOM.SAFETY_FLAG | LOCAL.AXIOM_FLAG_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.AXIOM.KIOTA, EVID.M8.AXIOM.LEAN4LEAN, EVID.M8.AXIOM.OFFICIAL, EVID.M8.AXIOM.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| SCENARIO.AXIOM.SAFETY_FLAG | LOCAL.AXIOM_MATERIALIZATION | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves the candidate/control materialization transformation; it does not itself establish a checker outcome or normative claim. |
| SCENARIO.AXIOM.SAFETY_FLAG | LOCAL.AXIOM_ONLY_RESULTS | TRACKED_EVIDENCE | SUPERSEDED_BY_STRONGER_EVIDENCE | IMPLEMENTATION_OBSERVATION | — | The reviewed pilot binds the claim-specific safety-flag structured results; the axiom-only result remains linked under the separate admission-policy scenario. |
| SCENARIO.AXIOM.SAFETY_FLAG | WITNESS.AXIOM_UNSAFE_FLAG | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.AXIOM.KIOTA, EVID.M8.AXIOM.LEAN4LEAN, EVID.M8.AXIOM.OFFICIAL, EVID.M8.AXIOM.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| SCENARIO.AXIOM.SAFETY_FLAG | WITNESS.AXIOM_UNSAFE_FLAG_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.AXIOM.KIOTA, EVID.M8.AXIOM.LEAN4LEAN, EVID.M8.AXIOM.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| SCENARIO.AXIOM.SAFETY_FLAG | WITNESS.AXIOM_UNSAFE_ONLY | GENERATED_WITNESS | SUPERSEDED_BY_STRONGER_EVIDENCE | DISCOVERY | — | The reviewed pilot selected the more specific safety-flag reconstruction witness; this unsafe-axiom-only candidate is retained under the separate admission-policy scenario. |
| SCENARIO.AXIOM.SAFETY_FLAG | WITNESS.AXIOM_UNSAFE_ONLY_CONTROL | GENERATED_WITNESS | SUPERSEDED_BY_STRONGER_EVIDENCE | CONTROL | — | The reviewed pilot selected the matched control for the more specific safety-flag reconstruction witness; this control remains linked under the admission-policy scenario. |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | LOCAL.AXIOM_FLAG_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.CONTROL, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | LOCAL.AXIOM_MATERIALIZATION | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves the candidate/control materialization transformation; it does not itself establish a checker outcome or normative claim. |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | WITNESS.AXIOM_UNSAFE_FLAG | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | WITNESS.AXIOM_UNSAFE_FLAG_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.CONTROL, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.OFFICIAL | The exact frozen control is linked without promotion to isolation. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | LOCAL.DECL_ENV_MATRIX | TRACKED_EVIDENCE | INSUFFICIENT_FOR_CLAIM | DISCOVERY | — | The aggregate matrix is relevant discovery context, but exact scenario results and witnesses provide the claim-specific M8 bindings. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | LOCAL.KIOTA_SELF_REFERENCE | TRACKED_EVIDENCE | DEFERRED_TO_LATER_STUDY | IMPLEMENTATION_OBSERVATION | — | This reproduction targets a later Kiota upstream revision rather than the pinned M8 observer profile, so it cannot establish the M8 observer outcome. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | LOCAL.SELF_REFERENCE_METADATA | TRACKED_EVIDENCE | OUTSIDE_THIS_ENTRY_LAYER | PROVENANCE_ONLY | — | This record preserves witness-generation provenance; the exact witness and structured checker-result bytes carry the catalog-layer links. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | LOCAL.SELF_REFERENCE_RESULTS | TRACKED_EVIDENCE | LINKED | IMPLEMENTATION_OBSERVATION | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.CONTROL, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.WITNESS | The exact content-bound record is linked to claim-specific catalog evidence without creating normative authority. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | WITNESS.SELF_REFERENCE | GENERATED_WITNESS | LINKED | DISCOVERY | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.OFFICIAL, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.WITNESS | The exact frozen witness is linked as discovery evidence without promotion to isolation. |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | WITNESS.SELF_REFERENCE_CONTROL | GENERATED_WITNESS | LINKED | CONTROL | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.CONTROL, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.KIOTA, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.LEAN4LEAN, EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.OFFICIAL | The exact frozen control is linked without promotion to isolation. |

## Unresolved Items

- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` — Which preapproved normative source, if any, qualifies this environment-visibility candidate?; A preapproved normative document or mechanized result supporting this modeled environment requirement is absent from the frozen authority-source registry.
- `DECL.ENV.NAME_FRESHNESS` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.EXPR.NO_LOOSE_BOUND_VARS` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.THEOREM.TYPE_PROP` — Which preapproved normative source, if any, qualifies this candidate as a requirement of the modeled judgment?; A preapproved normative document or mechanized result that supports this modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.TYPE.NO_FREE_VARS` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.TYPE.NO_METAVARS` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.TYPE.SORT_VALUED` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.TYPE.WELL_FORMED` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.UNIVERSE.PARAM_OWNERSHIP` — Which preapproved normative source, if any, qualifies universe-parameter ownership for the modeled judgment?; A preapproved normative document or mechanized result supporting declaration universe-parameter ownership is absent from the frozen authority-source registry.
- `DECL.UNIVERSE.PARAM_UNIQUENESS` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.VALUE.TYPE_MATCH` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `DECL.VALUE.WELL_FORMED` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.APP.ARGUMENT_TYPE_MATCH` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.APP.FUNCTION_TYPE` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.BINDER.DOMAIN_SORT` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.CONST.UNIVERSE_ARITY` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.LET.ANNOTATION_SORT` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `EXPR.LET.VALUE_TYPE_MATCH` — Which preapproved normative source, if any, qualifies local let value/type compatibility for the modeled judgment?; A preapproved normative document or mechanized result supporting local let value/type compatibility is absent from the frozen authority-source registry.
- `EXPR.PI.CODOMAIN_SORT` — Which preapproved normative source, if any, qualifies this exact candidate for the modeled judgment?; A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.
- `SCENARIO.AXIOM.ADMISSION_POLICY` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.AXIOM.SAFETY_FLAG` — What is the content-bound outcome of the pinned Nanoda observer for this exact scenario, and how should parser, reconstruction, and trust-policy effects be separated?; A content-bound result for the pinned Nanoda observer and a reviewed cross-layer reconstruction interpretation are not present in this pilot.
- `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.
- `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — What content-bound result bytes establish the complete pinned-observer vector for this exact scenario?; Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.

## Source Mappings

| ID | Implementation | Role | Source ID | Path | Symbol/range |
| --- | --- | --- | --- | --- | --- |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | NANODA | ENFORCEMENT | SRC.NANODA.ENV | src/env.rs | Env, EnvLimit, get_old_declar lines 204-276 |
| DECL.ENV.NAME_FRESHNESS | KIOTA | ENFORCEMENT | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| DECL.ENV.NAME_FRESHNESS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.ENV.NAME_FRESHNESS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT_BASIC | Lean4Lean/Environment/Basic.lean | checkDuplicatedUnivParams, checkNoMVar, checkNoFVar, checkName lines 14-60 |
| DECL.ENV.NAME_FRESHNESS | NANODA | ENFORCEMENT | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| DECL.ENV.NAME_FRESHNESS | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | KIOTA | ENFORCEMENT | SRC.KIOTA.EXPR | src/expr.rs | ExprData variants, loose-bvar range, level substitution helpers |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| DECL.THEOREM.TYPE_PROP | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.TYPE.NO_FREE_VARS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.TYPE.NO_FREE_VARS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT_BASIC | Lean4Lean/Environment/Basic.lean | checkDuplicatedUnivParams, checkNoMVar, checkNoFVar, checkName lines 14-60 |
| DECL.TYPE.NO_FREE_VARS | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.TYPE.NO_FREE_VARS | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.TYPE.NO_METAVARS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.TYPE.NO_METAVARS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT_BASIC | Lean4Lean/Environment/Basic.lean | checkDuplicatedUnivParams, checkNoMVar, checkNoFVar, checkName lines 14-60 |
| DECL.TYPE.NO_METAVARS | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.TYPE.NO_METAVARS | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.TYPE.SORT_VALUED | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.TYPE.SORT_VALUED | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.TYPE.SORT_VALUED | NANODA | ENFORCEMENT | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| DECL.TYPE.SORT_VALUED | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.TYPE.SORT_VALUED | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.TYPE.WELL_FORMED | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.TYPE.WELL_FORMED | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.TYPE.WELL_FORMED | NANODA | ENFORCEMENT | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| DECL.TYPE.WELL_FORMED | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.TYPE.WELL_FORMED | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.UNIVERSE.PARAM_OWNERSHIP | KIOTA | OTHER | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.UNIVERSE.PARAM_UNIQUENESS | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.UNIVERSE.PARAM_UNIQUENESS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.UNIVERSE.PARAM_UNIQUENESS | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT_BASIC | Lean4Lean/Environment/Basic.lean | checkDuplicatedUnivParams, checkNoMVar, checkNoFVar, checkName lines 14-60 |
| DECL.UNIVERSE.PARAM_UNIQUENESS | NANODA | ENFORCEMENT | SRC.NANODA.LEVEL | src/level.rs | no duplicate/all-param helpers lines 83-147; level equality imported |
| DECL.UNIVERSE.PARAM_UNIQUENESS | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.UNIVERSE.PARAM_UNIQUENESS | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.VALUE.TYPE_MATCH | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.VALUE.TYPE_MATCH | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.VALUE.TYPE_MATCH | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.VALUE.TYPE_MATCH | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.VALUE.WELL_FORMED | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| DECL.VALUE.WELL_FORMED | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| DECL.VALUE.WELL_FORMED | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| DECL.VALUE.WELL_FORMED | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| DECL.VALUE.WELL_FORMED | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| DECL.VALUE.WELL_FORMED | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.APP.ARGUMENT_TYPE_MATCH | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.APP.ARGUMENT_TYPE_MATCH | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.APP.ARGUMENT_TYPE_MATCH | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.APP.ARGUMENT_TYPE_MATCH | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.APP.FUNCTION_TYPE | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.APP.FUNCTION_TYPE | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.APP.FUNCTION_TYPE | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.APP.FUNCTION_TYPE | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.BINDER.DOMAIN_SORT | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.BINDER.DOMAIN_SORT | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.BINDER.DOMAIN_SORT | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.BINDER.DOMAIN_SORT | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.CONST.UNIVERSE_ARITY | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.CONST.UNIVERSE_ARITY | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.CONST.UNIVERSE_ARITY | NANODA | ENFORCEMENT | SRC.NANODA.EXPR | src/expr.rs | universe substitution arity assertion lines 382-399 and expression variants |
| EXPR.CONST.UNIVERSE_ARITY | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.CONST.UNIVERSE_ARITY | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.LET.ANNOTATION_SORT | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.LET.ANNOTATION_SORT | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.LET.ANNOTATION_SORT | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.LET.ANNOTATION_SORT | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| EXPR.LET.VALUE_TYPE_MATCH | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.PI.CODOMAIN_SORT | KIOTA | ENFORCEMENT | SRC.KIOTA.TC | src/tc.rs | check_decl 1096-1221, ensure_sort 1247-1253, infer_type 1265-1361, infer_proj 1376-1448, is_prop 1574-1614; generalized defeq/reduction and inductives imported/excluded |
| EXPR.PI.CODOMAIN_SORT | LEAN4LEAN | ENFORCEMENT | SRC.LEAN4LEAN.TYPECHECKER | Lean4Lean/TypeChecker.lean | ensureSortCore, checkLevel, inferConstant, inferLambda/Forall/App/Let/Proj, inferType', isProp; generalized defeq/reduction imported |
| EXPR.PI.CODOMAIN_SORT | NANODA | ENFORCEMENT | SRC.NANODA.TC | src/tc.rs | check_declar, check_declar_info, infer_const, ensure_sort, infer/check expression arms, infer_app/lambda/pi/let/proj, is_prop; defeq imported |
| EXPR.PI.CODOMAIN_SORT | LOGICAL_TARGET | ENFORCEMENT | SRC.OFFICIAL.TYPECHECKER | src/kernel/type_checker.cpp | ensure_sort, check_level, infer_fvar, infer_constant, infer_lambda, infer_pi, infer_app, infer_let, infer_proj, check, is_prop; generalized reduction/defeq followed only as imported dependencies |
| SCENARIO.AXIOM.ADMISSION_POLICY | LEAN4LEAN | POLICY | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| SCENARIO.AXIOM.ADMISSION_POLICY | NANODA | POLICY | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.AXIOM.ADMISSION_POLICY | LOGICAL_TARGET | POLICY | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| SCENARIO.AXIOM.SAFETY_FLAG | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | KIOTA | POLICY | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | LEAN4LEAN | POLICY | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | LEAN4LEAN | POLICY | SRC.LEAN4LEAN.REPLAY | Lean4Lean/Replay.lean | addDecl, replayConstant, replay, skip unsafe/partial lines 129-281 |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | NANODA | POLICY | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | LOGICAL_TARGET | POLICY | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.EXPR | src/expr.rs | ExprData variants, loose-bvar range, level substitution helpers |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | NANODA | RECONSTRUCTION | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.EXPR | src/expr.rs | ExprData variants, loose-bvar range, level substitution helpers |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | NANODA | RECONSTRUCTION | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.ENV | src/env.rs | ConstantInfo and Environment get/insert |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | LEAN4LEAN | RECONSTRUCTION | SRC.LEAN4LEAN.REPLAY | Lean4Lean/Replay.lean | addDecl, replayConstant, replay, skip unsafe/partial lines 129-281 |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | NANODA | RECONSTRUCTION | SRC.NANODA.ENV | src/env.rs | Env, EnvLimit, get_old_declar lines 204-276 |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | NANODA | RECONSTRUCTION | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | OFFICIAL_IMPORTER | RECONSTRUCTION | SRC.OFFICIAL.ARENA_MAIN | checkers/official-v4.33.0/Main.lean | runKernel and main |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | KIOTA | RECONSTRUCTION | SRC.KIOTA.ENV | src/env.rs | ConstantInfo and Environment get/insert |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | LEAN4LEAN | RECONSTRUCTION | SRC.LEAN4LEAN.REPLAY | Lean4Lean/Replay.lean | addDecl, replayConstant, replay, skip unsafe/partial lines 129-281 |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | NANODA | RECONSTRUCTION | SRC.NANODA.ENV | src/env.rs | Env, EnvLimit, get_old_declar lines 204-276 |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | NANODA | RECONSTRUCTION | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | OFFICIAL_IMPORTER | RECONSTRUCTION | SRC.OFFICIAL.ARENA_MAIN | checkers/official-v4.33.0/Main.lean | runKernel and main |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | KIOTA | RECONSTRUCTION | SRC.KIOTA.PARSER | src/parser.rs | expression arms, reject_if_dup, handle_def_like, handle_line, check_last; inductive/quotient arms excluded |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | LEAN4LEAN | RECONSTRUCTION | SRC.LEAN4LEAN.ENVIRONMENT | Lean4Lean/Environment.lean | checkConstantVal, addAxiom, addDefinition, addTheorem, addOpaque, excluded addMutual/dispatch lines 12-119 |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | LEAN4LEAN | RECONSTRUCTION | SRC.LEAN4LEAN.REPLAY | Lean4Lean/Replay.lean | addDecl, replayConstant, replay, skip unsafe/partial lines 129-281 |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | NANODA | RECONSTRUCTION | SRC.NANODA.PARSER | src/parser.rs | expression representability, universe reconstruction, axiom/def/theorem/opaque arms, excluded quotient/inductive arms lines 469-820 |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | LOGICAL_TARGET | RECONSTRUCTION | SRC.OFFICIAL.ENVIRONMENT | src/kernel/environment.cpp | lines 1-308; ordinary-declaration validation concentrated at 92-294 |

## Normative Candidate Obligations


### `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` — Current declaration not visible during validation

- Statement: The ordinary declaration currently being validated is absent from constant lookup in the modeled pre-declaration environment.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The selected witness and source mapping show a bounded implementation boundary, while normative support remains absent from the frozen approved registry.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this modeled environment requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.012`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact official result row. | EVID.M8.SELF_REFERENCE.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | The selected result file does not contain a pinned Nanoda baseline row. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact Lean4Lean result row. | EVID.M8.SELF_REFERENCE.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact Kiota result row. | EVID.M8.SELF_REFERENCE.KIOTA |

Evidence:

- `EVID.M8.SELF_REFERENCE.DISCOVERY` — `DISCOVERY` / `OTHER`: The candidate is scoped to the frozen modeled judgment. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.SELF_REFERENCE.SOURCE` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned Nanoda environment site is mapped as implementation evidence only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.SELF_REFERENCE.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The existing Lab self-reference artifact discovers a bounded candidate; it has not qualified isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.SELF_REFERENCE.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned official observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.SELF_REFERENCE.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Kiota observer accepted the selected artifact; this is a profile-specific implementation observation, not authority contradiction. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.SELF_REFERENCE.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Lean4Lean observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.

### `DECL.ENV.NAME_FRESHNESS` — Declaration name freshness

- Statement: The name of an ordinary declaration being added is absent from the modeled pre-declaration environment.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.001`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT_BASIC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.ENV.NAME_FRESHNESS.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.EXPR.NO_LOOSE_BOUND_VARS` — Declaration expression bound-variable closure

- Statement: Every bound-variable occurrence in a declaration type or value is in scope at its occurrence.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.004`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.SOURCE.SRC.KIOTA.EXPR` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.EXPR.NO_LOOSE_BOUND_VARS.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.THEOREM.TYPE_PROP` — Theorem proposition-valued type

- Statement: A theorem declaration's type satisfies the modeled proposition-valued predicate.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: Existing source, witness, and observer evidence supports a bounded candidate, but the frozen approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result that supports this modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.011`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact official result row. | EVID.M8.THEOREM.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | The selected result file does not contain a pinned Nanoda baseline row. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact Lean4Lean result row. | EVID.M8.THEOREM.LEAN4LEAN |
| /observer_profiles/kiota | REJECT | Extracted from the exact Kiota result row. | EVID.M8.THEOREM.KIOTA |

Evidence:

- `EVID.M8.THEOREM.DISCOVERY` — `DISCOVERY` / `OTHER`: The candidate is scoped to the frozen modeled judgment. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.SOURCE` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned official implementation source is mapped as an implementation observation only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The existing Lab artifact discovers a bounded non-proposition theorem candidate; it has not qualified isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned official observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Kiota observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Lean4Lean observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.THEOREM.ARENA` — `DISCOVERY` / `ARENA_TEST`: The existing Arena case records a non-proposition theorem rejection boundary as empirical coverage only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.

### `DECL.TYPE.NO_FREE_VARS` — Declaration type free-variable closure

- Statement: A declaration type contains no free-variable expression nodes.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.003`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT_BASIC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_FREE_VARS.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.TYPE.NO_METAVARS` — Declaration type metavariable closure

- Statement: A declaration type contains no metavariable expression nodes.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.003`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT_BASIC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.NO_METAVARS.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.TYPE.SORT_VALUED` — Declaration type sort-valued requirement

- Statement: The inferred type of a declaration's declared type is definitionally equal to a sort.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.008, DEC.M5.018`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.SORT_VALUED.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.TYPE.WELL_FORMED` — Declaration type well-formedness

- Statement: The declared type is well typed in the modeled pre-declaration environment under the declaration's universe parameters.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.008, DEC.M5.018`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.TYPE.WELL_FORMED.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.UNIVERSE.PARAM_OWNERSHIP` — Declaration universe-parameter ownership

- Statement: Every universe parameter referenced by a declaration type or value is owned by that declaration's universe-parameter list.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The selected witness and implementation mapping identify an observed boundary, but qualified normative support is absent from the frozen authority-source registry.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting declaration universe-parameter ownership is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.006`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact official result row. | EVID.M8.UNIVERSE.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | The selected result file does not contain a pinned Nanoda baseline row. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact Lean4Lean result row. | EVID.M8.UNIVERSE.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact Kiota result row. | EVID.M8.UNIVERSE.KIOTA |

Evidence:

- `EVID.M8.UNIVERSE.DISCOVERY` — `DISCOVERY` / `OTHER`: The candidate is scoped to the frozen modeled judgment. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.UNIVERSE.SOURCE` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned Kiota typechecker site is mapped as an implementation observation only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.UNIVERSE.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The existing Lab undeclared-universe artifact discovers a bounded candidate; it has not qualified isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.UNIVERSE.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned official observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.UNIVERSE.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Kiota observer accepted the selected artifact; this is a profile-specific implementation observation, not authority contradiction. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.UNIVERSE.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Lean4Lean observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.

### `DECL.UNIVERSE.PARAM_UNIQUENESS` — Declaration universe-parameter uniqueness

- Statement: The declaration universe-parameter list contains no repeated parameter name.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.002`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT_BASIC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.NANODA.LEVEL` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.UNIVERSE.PARAM_UNIQUENESS.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.VALUE.TYPE_MATCH` — Declaration value and declared-type compatibility

- Statement: The inferred type of a declaration value is definitionally equal to the declaration's declared type.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.010`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.TYPE_MATCH.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `DECL.VALUE.WELL_FORMED` — Declaration value well-formedness

- Statement: A declaration value is well typed in the modeled pre-declaration environment under the declaration's universe parameters.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.009`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.DECL.VALUE.WELL_FORMED.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.APP.ARGUMENT_TYPE_MATCH` — Application argument and domain compatibility

- Statement: The inferred type of an application argument is definitionally equal to the function domain expected at that application.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.016`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.ARGUMENT_TYPE_MATCH.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.APP.FUNCTION_TYPE` — Application function-type requirement

- Statement: The inferred type of an application function is definitionally equal to a dependent-function type.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.016`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.APP.FUNCTION_TYPE.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.BINDER.DOMAIN_SORT` — Binder domain sort-valued requirement

- Statement: The type annotation of a lambda or dependent-function binder has an inferred type definitionally equal to a sort.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.014`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.BINDER.DOMAIN_SORT.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.CONST.UNIVERSE_ARITY` — Constant universe-argument arity

- Statement: A constant expression supplies exactly one universe argument for each universe parameter of the referenced constant.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.007`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.SOURCE.SRC.NANODA.EXPR` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.CONST.UNIVERSE_ARITY.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.LET.ANNOTATION_SORT` — Let annotation sort-valued requirement

- Statement: A local let annotation has an inferred type definitionally equal to a sort.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.015`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.LET.ANNOTATION_SORT.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `EXPR.LET.VALUE_TYPE_MATCH` — Let value and annotation compatibility

- Statement: The inferred type of a local let value is definitionally equal to its annotation.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The selected witness and source mapping support a bounded candidate, but no qualifying normative source is in the frozen approved registry.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting local let value/type compatibility is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.015`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact official result row. | EVID.M8.LET_VALUE.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | The selected result file does not contain a pinned Nanoda baseline row. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact Lean4Lean result row. | EVID.M8.LET_VALUE.LEAN4LEAN |
| /observer_profiles/kiota | REJECT | Extracted from the exact Kiota result row. | EVID.M8.LET_VALUE.KIOTA |

Evidence:

- `EVID.M8.LET_VALUE.DISCOVERY` — `DISCOVERY` / `OTHER`: The candidate is scoped to the frozen modeled judgment. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.LET_VALUE.SOURCE` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned Lean4Lean typechecker site is mapped as implementation evidence only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.LET_VALUE.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The existing Lab let-value mismatch artifact discovers a bounded candidate; it has not qualified isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.LET_VALUE.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned official observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.LET_VALUE.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Kiota observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.LET_VALUE.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Lean4Lean observer rejected the selected artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.

### `EXPR.PI.CODOMAIN_SORT` — Dependent-function codomain sort-valued requirement

- Statement: The codomain of a dependent-function expression has an inferred type definitionally equal to a sort in the extended local context.
- Layers: `KERNEL_DECLARATION_VALIDITY`
- Authority: `PROVISIONAL` via `AUTH.NORMATIVE.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports retaining this bounded candidate, but the pre-M8 approved-authority-source registry contains no qualifying normative source.
- Unmet authority requirements: `A preapproved normative document or mechanized result supporting this exact modeled declaration-validity requirement is absent from the frozen authority-source registry.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.014`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.SOURCE.SRC.KIOTA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.SOURCE.SRC.LEAN4LEAN.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.SOURCE.SRC.NANODA.TC` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.EXPR.PI.CODOMAIN_SORT.SOURCE.SRC.OFFICIAL.TYPECHECKER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

## Empirical Contract Scenarios


### `SCENARIO.AXIOM.ADMISSION_POLICY` — Axiom admission policy

- Statement: Characterize whether an observer admits, rejects, skips, or conditionally permits a serialized axiom after type conformance.
- Layers: `TRUST_POLICY, IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.018`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | ACCEPT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | ACCEPT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.KIOTA |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact exposes this exact empirical boundary as discovery evidence without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.CONTROL` — `CONTROL` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact supplies the matched control for this scenario without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured official result row records ACCEPT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured kiota result row records ACCEPT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.AXIOM.ADMISSION_POLICY.RESULT.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured lean4lean result row records ACCEPT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.

### `SCENARIO.AXIOM.SAFETY_FLAG` — Axiom safety-flag treatment

- Statement: Characterize how each observer reconstructs and acts on the serialized unsafe flag of an axiom.
- Layers: `EXPORT_FORMAT, RECONSTRUCTION, TRUST_POLICY, IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The pilot records exact outcomes for three observer profiles but leaves the Nanoda profile uninspected and does not collapse the cross-layer behavior into one interpretation.
- Unmet authority requirements: `A content-bound result for the pinned Nanoda observer and a reviewed cross-layer reconstruction interpretation are not present in this pilot.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.018`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact official result row. | EVID.M8.AXIOM.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | No pinned Nanoda result row is selected for this pilot. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact Lean4Lean result row. | EVID.M8.AXIOM.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact Kiota result row. | EVID.M8.AXIOM.KIOTA |

Evidence:

- `EVID.M8.AXIOM.DISCOVERY` — `DISCOVERY` / `OTHER`: The scenario is retained as a bounded empirical observation, not a modeled-kernel rule. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.AXIOM.SOURCE` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned Kiota parser site is mapped as an implementation observation only. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.AXIOM.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The existing Lab axiom artifact discovers a bounded scenario stimulus; it has not qualified isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.AXIOM.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned official observer rejected the selected axiom-flag artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.AXIOM.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Kiota observer accepted the selected axiom-flag artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.
- `EVID.M8.AXIOM.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The pinned Lean4Lean observer rejected the selected axiom-flag artifact. Assumptions: `—`. Contradiction: `—`. Limitations: `—`.

### `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION` — Ordinary declaration safety reconstruction

- Statement: Characterize how each observer reconstructs and selects validation behavior from serialized safety metadata on ordinary declarations.
- Layers: `RECONSTRUCTION, IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.019`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.KIOTA |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.SOURCE.SRC.LEAN4LEAN.REPLAY` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact exposes this exact empirical boundary as discovery evidence without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.CONTROL` — `CONTROL` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact supplies the matched control for this scenario without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured official result row records REJECT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured kiota result row records ACCEPT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION.RESULT.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured lean4lean result row records REJECT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.

### `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY` — Export free-variable representability

- Statement: Characterize whether an export profile can represent a free-variable expression and how each observer treats such an input.
- Layers: `EXPORT_FORMAT, RECONSTRUCTION`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.005`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY.SOURCE.SRC.KIOTA.EXPR` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY` — Export metavariable representability

- Statement: Characterize whether an export profile can represent a metavariable expression and how each observer treats such an input.
- Layers: `EXPORT_FORMAT, RECONSTRUCTION`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.005`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.EXPORT.METAVAR_REPRESENTABILITY.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.METAVAR_REPRESENTABILITY.SOURCE.SRC.KIOTA.EXPR` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.METAVAR_REPRESENTABILITY.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.EXPORT.METAVAR_REPRESENTABILITY.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY` — Observer current-declaration visibility

- Statement: Characterize whether the declaration currently being checked is visible through constant lookup in each observer's reconstructed environment.
- Layers: `RECONSTRUCTION, IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.020`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | REJECT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.OFFICIAL |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | REJECT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.LEAN4LEAN |
| /observer_profiles/kiota | ACCEPT | Extracted from the exact structured normalized-outcome field in the content-bound compatible checker result row. | EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.KIOTA |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.KIOTA.ENV` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.LEAN4LEAN.REPLAY` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.NANODA.ENV` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.SOURCE.SRC.OFFICIAL.ARENA_MAIN` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.WITNESS` — `DISCOVERY` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact exposes this exact empirical boundary as discovery evidence without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.CONTROL` — `CONTROL` / `WITNESS_ARTIFACT`: The frozen existing Lab artifact supplies the matched control for this scenario without establishing isolation. Assumptions: `—`. Contradiction: `—`. Limitations: `Existing Lab evidence alone does not establish isolation, negative coverage, normativity, or soundness.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.OFFICIAL` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured official result row records REJECT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.KIOTA` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured kiota result row records ACCEPT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY.RESULT.LEAN4LEAN` — `IMPLEMENTATION_OBSERVATION` / `CHECKER_RESULT`: The content-bound structured lean4lean result row records REJECT for this exact scenario and pinned compatible profile. Assumptions: `—`. Contradiction: `—`. Limitations: `This is a profile-specific implementation observation, not normative authority or a soundness conclusion.`.

### `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION` — Observer replay environment construction

- Statement: Characterize the declaration ordering, dependency replay, filtering, and reconstruction steps that build the environment presented to validation.
- Layers: `RECONSTRUCTION`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.020`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.KIOTA.ENV` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.LEAN4LEAN.REPLAY` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.NANODA.ENV` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION.SOURCE.SRC.OFFICIAL.ARENA_MAIN` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

### `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — Unsafe and partial replay filtering

- Statement: Characterize whether an observer replays, skips, rejects, or transforms constants marked unsafe or partial.
- Layers: `RECONSTRUCTION, TRUST_POLICY, IMPLEMENTATION_POLICY`
- Authority: `PROVISIONAL` via `AUTH.EMPIRICAL.PROVISIONAL.V1`
- Authority basis: The frozen discovery surface supports this profile-scoped scenario, but the inventory selects no complete content-bound observer outcome vector.
- Unmet authority requirements: `Content-bound structured result evidence has not established concrete outcomes for all applicable pinned observer profiles.`
- Active evidence assumptions: `—`
- Lifecycle: `ACTIVE`
- Soundness relevance: `NOT_ASSESSED`
- Decision IDs: `DEC.M5.019`

Observer vector:

| Profile | Outcome | Attribution | Evidence |
| --- | --- | --- | --- |
| /observer_profiles/official_importer | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/nanoda | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/lean4lean | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |
| /observer_profiles/kiota | NOT_INSPECTED | No content-bound concrete outcome was selected for this identity in the Milestone 8 inventory. | — |

Evidence:

- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.DISCOVERY` — `DISCOVERY` / `LAB_EXPERIMENT`: The frozen discovery closure supplies the bounded implementation-site surface for this stable identity; it does not establish authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Discovery closure and implementation agreement are not normative authority.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.SOURCE.SRC.KIOTA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.SOURCE.SRC.LEAN4LEAN.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.SOURCE.SRC.LEAN4LEAN.REPLAY` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.SOURCE.SRC.NANODA.PARSER` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.
- `EVID.M8.INVENTORY.SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER.SOURCE.SRC.OFFICIAL.ENVIRONMENT` — `IMPLEMENTATION_OBSERVATION` / `IMPLEMENTATION_SOURCE`: The pinned source file implements, reconstructs, or observes part of this bounded catalog boundary without establishing authority. Assumptions: `—`. Contradiction: `—`. Limitations: `Implementation-source attribution is not a normative or soundness conclusion.`.

## Milestone Boundary

- M9 challenged all twelve mandated review classes and found no semantic catalog correction justified by the frozen evidence.
- The review preserves incomplete independent observability, provisional authority, explicit cross-layer scenarios, exclusions, and unresolved boundaries rather than upgrading them.
- No implementation behavior, checker agreement, adversarial-review result, or LLM judgment establishes normativity.
- All 27 active entries remain PROVISIONAL and all soundness relevance remains NOT_ASSESSED.
- The reviewed inventory is a frozen input for Milestone 10 design; it is not yet a negative-coverage denominator and no broad coverage study has begun.

Next milestone: `MILESTONE_10_DESIGN_FROZEN_INVENTORY_COVERAGE_STUDY`
