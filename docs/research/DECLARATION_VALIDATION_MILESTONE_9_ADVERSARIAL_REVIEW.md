# Declaration-Validation Milestone 9 Adversarial Review

This report is rendered from canonical, explicitly authored review decisions. The renderer supplies no semantic disposition or rationale.

- Review status: `PASS_WITH_NO_CATALOG_CORRECTIONS`
- Baseline commit: `5f7aaa6644db214ce9ca9c81806192231bf585ab`
- Baseline declaration-validation tests: 153
- Challenges completed: 12 of 12
- Catalog corrections: 0
- Remaining provisional entries: 27
- Remaining soundness states `NOT_ASSESSED`: 27

## Review Method

- Predecessor boundary: `IMMUTABLE_CORRECTED_M8_GIT_BLOB_ATTESTATION`
- Semantic decision origin: `EXPLICIT_PRIMARY_REVIEWER_JUDGMENT`
- Renderer role: `PRESENTATION_ONLY`
- Semantic authority claimed by review: `false`

## 1. Which normative entries merely restate implementation checks?

- Decision ID: `CHALLENGE.M9.01.IMPLEMENTATION_RESTATEMENT`
- Attack performed: For each of the nineteen candidates, the reviewer hypothetically removed every mapped implementation check and asked whether the frozen checked-addition judgment still supplied a distinct rule premise, reach condition, formation rule, or environment invariant that was useful independently of implementation agreement.
- Disposition: `RETAINED_PROVISIONAL_IMPLEMENTATION_ONLY`
- Rationale: Every candidate retained a distinct modeled premise after that counterfactual. The reasons are structural to closed declaration formation, expression typing, universe instantiation, safe pre-environment checking, or declaration-kind formation rather than checker consensus. They remain candidates only: the empty approved-source registry still prevents normative establishment.
- Catalog targets: 19
- Surface targets: 0
- Statement hash before: `66013f3373892e6053bc97825f0178c5f4211d2f67aaaf4bb101a7448ade6e2b`
- Statement hash after: `66013f3373892e6053bc97825f0178c5f4211d2f67aaaf4bb101a7448ade6e2b`
- Correction required: `false`

- Evidence `pre_review_catalog`: All 19 normative candidates are explicitly provisional; implementation-source evidence targets discovery or layer metadata and supplies no normative support.
- Evidence `approved_authority_sources`: The frozen approved-source registry is empty.
- Challenge limitation: Implementation sites motivate candidate retention but do not establish the modeled requirement.

### Item-level adjudications

- `DECL.ENV.NAME_FRESHNESS` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Assume the duplicate-name check disappears and permit insertion over an existing environment binding.
  - Rationale: A single checked environment extension needs a fresh binding to preserve the pre-environment lookup meaning and avoid silent replacement; this is distinct from the implementation location of the check.
  - Limitation: No approved source establishes that modeled invariant normatively.
- `DECL.UNIVERSE.PARAM_UNIQUENESS` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Remove duplicate-parameter rejection and treat the declaration parameter list as a substitution domain with repeated names.
  - Rationale: Repeated universe binders make name-indexed ownership and instantiation ambiguous even before any particular checker implementation is considered.
  - Limitation: The review does not establish a normative source for the binder-list representation.
- `DECL.TYPE.NO_FREE_VARS` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Remove the explicit free-variable scan and ask whether a top-level declaration type may depend on an unbound local-context identity.
  - Rationale: The modeled pre-declaration environment supplies constants but no top-level local context, so free-variable closure is a distinct reach premise for a declaration type.
  - Limitation: The pinned export format may prevent an independent end-to-end negative artifact.
- `DECL.TYPE.NO_METAVARS` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Remove the explicit metavariable scan and ask whether an unresolved metavariable is a closed kernel declaration type.
  - Rationale: A metavariable denotes an unresolved external obligation rather than a term justified by the checked kernel environment, which is distinct from generic parser behavior.
  - Limitation: The pinned export representation does not expose metavariable nodes to every observer.
- `DECL.EXPR.NO_LOOSE_BOUND_VARS` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Permit a de Bruijn occurrence outside the binder depth at its occurrence and test whether ordinary expression inference remains a coherent judgment.
  - Rationale: Binder scope is a premise of expression formation; an out-of-range occurrence has no local declaration from which a type can be reconstructed.
  - Limitation: Some observers reject through representation or lookup before an independently named check.
- `DECL.UNIVERSE.PARAM_OWNERSHIP` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Allow a sort level or constant universe argument to mention a parameter absent from the declaration's level-parameter context.
  - Rationale: Universe-level closure is the level analogue of variable closure and is needed to interpret the declaration under its explicitly quantified universe context.
  - Limitation: Existing checker disagreement is implementation observation, not normative support.
- `EXPR.CONST.UNIVERSE_ARITY` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Instantiate a referenced constant with fewer or more universe arguments than its declared universe binders.
  - Rationale: Constant-type instantiation requires one substitution argument per universe binder; this premise is distinct from ownership of names occurring inside those arguments.
  - Limitation: General universe equality and normalization remain imported prerequisites.
- `DECL.TYPE.WELL_FORMED` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Remove full type inference while preserving closure scans and sort-result checking.
  - Rationale: A declaration cannot claim a type whose expression has no type in the modeled pre-environment; inference success is distinct from the later requirement that the inferred result be a sort.
  - Limitation: The broad well-formedness premise contains many imported expression rules.
- `DECL.TYPE.SORT_VALUED` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Supply a well-typed term as the declared type whose own inferred type is not definitionally a sort.
  - Rationale: Inference can succeed for an ordinary term that is not itself a type, so sorthood is a separable declaration-formation premise rather than a textual restatement of well-formedness.
  - Limitation: Definitional equality to a sort remains an imported algorithmic judgment.
- `DECL.VALUE.WELL_FORMED` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Remove value checking while retaining the final value-versus-declared-type comparison.
  - Rationale: A value must first have an inferred type in the safe pre-environment; an equality comparison cannot justify an untypeable value.
  - Limitation: Explicit value closure checks are treated as reach components of this broad premise.
- `DECL.VALUE.TYPE_MATCH` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Use a well-typed value whose inferred type differs definitionally from the declaration's claimed type.
  - Rationale: Value well-formedness does not connect the value to the declared interface; the compatibility equality is therefore an independently violable premise.
  - Limitation: The full definitional-equality algorithm is outside this slice.
- `DECL.THEOREM.TYPE_PROP` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Construct a declaration with a well-formed sort-valued type and matching value but label it as a theorem when the type is not proposition-valued.
  - Rationale: The theorem declaration kind has a distinct proposition-formation premise after generic type and value validity; it is not implied by implementation agreement.
  - Limitation: The proposition predicate's normative authority remains unqualified.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Make a safe declaration visible to constant lookup before checking its own value and attempt direct self-reference.
  - Rationale: The frozen safe ordinary judgment is explicitly nonrecursive and checks against the pre-declaration environment; self-visibility would change that judgment rather than merely alter an implementation detail.
  - Limitation: Observer replay order can conflate this kernel premise with reconstruction behavior.
- `EXPR.BINDER.DOMAIN_SORT` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Use a well-typed non-type term as a lambda or dependent-function binder annotation.
  - Rationale: Extending a local typing context requires the binder annotation itself to denote a type; this is a formation premise independent of the enclosing implementation helper.
  - Limitation: The entry groups lambda and Pi domain formation under one stable premise.
- `EXPR.PI.CODOMAIN_SORT` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Use a codomain that is well typed in the extended context but whose inferred type is not a sort.
  - Rationale: Dependent-function formation separately requires the codomain to be a type after the domain binder is introduced.
  - Limitation: Pi universe computation itself remains part of the imported level judgment.
- `EXPR.LET.ANNOTATION_SORT` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Give a local let a well-typed annotation term that is not itself sort-valued.
  - Rationale: The annotation defines a local type and therefore has a formation condition separate from whether the value matches it.
  - Limitation: The negative artifact must also reach the let rule without an earlier failure.
- `EXPR.LET.VALUE_TYPE_MATCH` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Use a well-formed let annotation and a well-typed value of a definitionally different type.
  - Rationale: Annotation sorthood and value compatibility are independently violable premises of the let typing rule.
  - Limitation: Definitional equality remains imported rather than re-specified.
- `EXPR.APP.FUNCTION_TYPE` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Apply an expression whose inferred type is well formed but not definitionally a dependent-function type.
  - Rationale: Application elimination requires a function telescope before any argument-domain comparison can be meaningful.
  - Limitation: Reduction to weak-head function form is an imported prerequisite.
- `EXPR.APP.ARGUMENT_TYPE_MATCH` — `RETAIN_NORMATIVE_CANDIDATE`
  - Attack: Apply a genuine dependent function to a well-typed argument whose type differs from the expected domain.
  - Rationale: Function-shape reach and argument-domain compatibility are separately violable premises and support distinct negative synthesis.
  - Limitation: The equality decision remains scoped to the pinned implementation profile.

## 2. Which entries confuse kernel validity with export behavior?

- Decision ID: `CHALLENGE.M9.02.KERNEL_EXPORT_BOUNDARY`
- Attack performed: The reviewer traced every relevant phenomenon from malformed declaration construction through parser or exporter representability, replay sequencing, environment insertion, and the checked declaration entrypoints, then tried to move each identity into export, reconstruction, trust, or implementation policy instead of kernel declaration validity.
- Disposition: `KERNEL_EXPORT_BOUNDARY_SEPARATED`
- Rationale: The nineteen normative candidates describe closed declaration formation, expression typing, universe instantiation, environment preconditions, or declaration-kind formation at the checked-addition boundary. Representability, replay order, serialized flags, admission, and unsafe filtering remain empirical scenarios with their non-kernel layers. Similar wording across those groups does not collapse the phenomena: the current-declaration rule constrains the checking pre-environment, while its replay scenario describes how an importer happens to realize that pre-environment.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `semantic_target`: The modeled checked-addition judgment explicitly excludes parsing and reconstruction while separately pinning the export contract.
- Evidence `pre_review_catalog`: Normative entries use only KERNEL_DECLARATION_VALIDITY; export-format boundaries remain empirical scenarios.
- Challenge limitation: Layer separation characterizes the pinned profiles; it is not a universal serialization theorem.

### Item-level adjudications

- `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY` — `BOUNDARY_RETAINED`
  - Attack: Attempt to treat free-variable and metavariable closure only as limitations of serialized expression representability.
  - Rationale: The normative identities constrain an accepted declaration type regardless of serialization, whereas the scenarios ask whether a malformed witness can cross a particular exporter and reconstruction path.
  - Limitation: The available exporters can prevent empirical isolation of the normative checks.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION` — `BOUNDARY_RETAINED`
  - Attack: Attempt to recast current-declaration visibility as nothing more than importer insertion order.
  - Rationale: Checking against the pre-environment is a declaration-validity precondition; replay ordering and environment construction are mechanisms that can satisfy or violate it.
  - Limitation: The official observer is a composite and cannot independently establish the normative precondition.
- `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `EXPR.CONST.UNIVERSE_ARITY` — `KERNEL_FORMATION_RETAINED`
  - Attack: Attempt to treat universe ownership and arity as parser bookkeeping because some observers reconstruct parameters before type checking.
  - Rationale: Uniqueness, ownership of referenced parameters, and constant-instantiation arity are distinct formation premises consumed after reconstruction; an observer that cannot encode an offending level only limits observation.
  - Limitation: Kiota's ownership context differs, so cross-profile observation remains incomplete.
- `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `NON_KERNEL_SCENARIOS_RETAINED`
  - Attack: Attempt to promote admission and safety-flag behavior into kernel validity because they influence whether declarations are checked or replayed.
  - Rationale: These scenarios characterize trust, reconstruction, and implementation policy around which declaration path is selected; they do not state an expression-typing or ordinary checked-declaration premise.
  - Limitation: No soundness significance is inferred from the policy boundary.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.THEOREM.TYPE_PROP`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.TYPE.SORT_VALUED`, `DECL.TYPE.WELL_FORMED`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.VALUE.TYPE_MATCH`, `DECL.VALUE.WELL_FORMED`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.CONST.UNIVERSE_ARITY`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.PI.CODOMAIN_SORT`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `KERNEL_LAYER_RETAINED`
  - Attack: For the remaining typing, closure, freshness, and theorem candidates, search for a serialization, replay, or policy mechanism that fully explains the stated obligation.
  - Rationale: Each remaining identity is an ordinary declaration or expression premise enforced after an object is representable and before checked insertion, so no non-kernel layer supplants its provisional kernel classification.
  - Limitation: Classification remains provisional and bounded to the pinned declaration slice.

## 3. Which scenarios cross multiple layers?

- Decision ID: `CHALLENGE.M9.03.MULTI_LAYER_SCENARIOS`
- Attack performed: The reviewer followed each of the eight empirical scenarios phase by phase and tried both to remove layers that described only a neighboring step and to add layers hidden by an earlier representability or reconstruction failure.
- Disposition: `MULTI_LAYER_SCENARIOS_EXPLICIT`
- Rationale: The recorded layer sets distinguish the phenomenon from the sequential machinery that exposes it. Free-variable and metavariable representability need export plus reconstruction; admission is trust and implementation policy; serialized flags cross export, reconstruction, trust, and implementation; declaration safety reconstruction is reconstruction plus implementation; unsafe or partial filtering also carries trust policy; environment construction is reconstruction alone; and current visibility combines reconstruction with implementation ordering.
- Catalog targets: 8
- Surface targets: 0
- Statement hash before: `67f2196f791ae36df2d7754f502838d8fd19e463bd832a27b9cd76f8c7c14e00`
- Statement hash after: `67f2196f791ae36df2d7754f502838d8fd19e463bd832a27b9cd76f8c7c14e00`
- Correction required: `false`

- Evidence `pre_review_catalog`: Every scenario spanning more than one layer records the complete layer set instead of being forced into one layer.
- Challenge limitation: Layer membership is a bounded characterization and remains non-normative.

### Item-level adjudications

- `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY` — `LAYERS_COMPLETE`
  - Attack: Try to remove reconstruction or add kernel validity.
  - Rationale: The scenario is about whether a free-variable-bearing expression survives export and can be reconstructed, not whether a kernel accepts it.
  - Limitation: A representability rejection prevents observing the later kernel condition.
- `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY` — `LAYERS_COMPLETE`
  - Attack: Try to remove reconstruction or add kernel validity.
  - Rationale: The scenario is about serialization and reconstruction of metavariables rather than the distinct declaration-closure premise.
  - Limitation: A representability rejection prevents observing the later kernel condition.
- `SCENARIO.AXIOM.ADMISSION_POLICY` — `LAYERS_COMPLETE`
  - Attack: Try to add reconstruction merely because importers create axioms.
  - Rationale: The challenged phenomenon is whether admission is permitted by trust and implementation policy, not the mechanics of decoding a declaration.
  - Limitation: The scenario does not establish a normative trust rule.
- `SCENARIO.AXIOM.SAFETY_FLAG` — `LAYERS_COMPLETE`
  - Attack: Separate the serialized flag from its reconstruction and policy effects.
  - Rationale: The flag is represented, reconstructed, and interpreted through trust and implementation policy, so all four recorded layers are material.
  - Limitation: The exact policy meaning is profile-specific.
- `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION` — `LAYERS_COMPLETE`
  - Attack: Try to add trust policy because safe and unsafe paths differ.
  - Rationale: This narrower scenario records how a declaration flag is reconstructed and dispatched; it does not claim that the dispatch choice is a trust requirement.
  - Limitation: Trust consequences remain explicitly unassessed.
- `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `LAYERS_COMPLETE`
  - Attack: Try to collapse filtering into importer mechanics alone.
  - Rationale: Filtering is realized during reconstruction but selects declarations according to trust and implementation policy, so the three layers are not redundant.
  - Limitation: The review does not generalize beyond the pinned profiles.
- `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION` — `LAYERS_COMPLETE`
  - Attack: Try to add implementation policy or kernel validity to ordinary replay construction.
  - Rationale: The scenario is specifically the reconstruction of the environment sequence; later checking and policy choices are separate identities.
  - Limitation: A malformed stream remains outside the slice.
- `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY` — `LAYERS_COMPLETE`
  - Attack: Try to treat current visibility as reconstruction alone or as kernel validity alone.
  - Rationale: Replay sequencing constructs the pre-environment and implementation order determines when insertion occurs, while the normative precondition remains a separate identity.
  - Limitation: Observer composition limits independent attribution.

## 4. Which authority claims rely on implementation consensus?

- Decision ID: `CHALLENGE.M9.04.CONSENSUS_AUTHORITY`
- Attack performed: The reviewer searched authority rationales, evidence roles, notes, expected outcomes, generated prose, and historical test descriptions for any inference of the form that checker agreement or inherited expected rejection makes an obligation normative.
- Disposition: `NO_CONSENSUS_BASED_AUTHORITY`
- Rationale: No such inference remains. All twenty-seven entries are PROVISIONAL; checker outcomes are implementation observations; the authority registry has zero approved normative or mechanized sources; and each unmet requirement names the missing qualification. Expected outcomes guide a test comparison but do not establish the modeled contract.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `authority_rules`: The qualification rules forbid checker majority and implementation consensus as normativity.
- Evidence `pre_review_catalog`: All 27 authority states remain provisional with named unmet requirements.
- Challenge limitation: The review does not decide whether a future preapproved source could establish a candidate.

### Item-level adjudications

- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.THEOREM.TYPE_PROP`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.TYPE.SORT_VALUED`, `DECL.TYPE.WELL_FORMED`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.VALUE.TYPE_MATCH`, `DECL.VALUE.WELL_FORMED`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.CONST.UNIVERSE_ARITY`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.PI.CODOMAIN_SORT`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `NO_CONSENSUS_AUTHORITY_FOUND`
  - Attack: Search every targeted entry and its bound prose for consensus language that functions as authority.
  - Rationale: Agreement and disagreement are both recorded as observations, while authority stays provisional with explicit unmet source requirements.
  - Limitation: A future qualified source could change authority only through the later governed process.

## 5. Which supposedly independent sources share lineage?

- Decision ID: `CHALLENGE.M9.05.SHARED_LINEAGE`
- Attack performed: The reviewer traced code derivation, toolchain use, export format, fixtures, replay machinery, expected outcomes, and common Arena inputs for each observer rather than equating different repository names with independence.
- Disposition: `SHARED_LINEAGE_EXPLICIT`
- Rationale: Official Lean is the target plus lean4export and Arena and is not independent. Lean4Lean is derived from the official C++ kernel and shares Lean and lean4export upstreams. Nanoda and Kiota are distinct codebases, but both implement a shared Lean contract and consume correlated export or Arena artifacts; semantic independence is therefore not established. Existing lineage annotations already make only scoped code-lineage claims and do not call any profile an independent authority, so no catalog correction is required.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `semantic_target`: Lean4Lean is recorded as derived from the official C++ kernel; official, Nanoda, and Kiota profiles retain their distinct scoped lineage labels.
- Evidence `source_lock`: Each executable observer configuration repeats the pinned lineage group.
- Challenge limitation: Distinct lineage is not statistical or semantic independence.

### Item-level adjudications

- `observer:official` — `TARGET_COMPOSITE_NOT_INDEPENDENT`
  - Attack: Treat the official executable observer as independent from the target kernel because it is exercised through an external Arena command.
  - Rationale: The observation composes the target implementation with official export and replay machinery, so agreement is self-observation across a pipeline.
  - Limitation: It remains useful as a pinned implementation observation.
- `observer:lean4lean` — `DERIVED_SHARED_CONTRACT_LINEAGE`
  - Attack: Treat a separate Lean implementation as semantically independent merely because the executable code differs.
  - Rationale: The profile documents derivation from the official C++ kernel and shares the Lean toolchain and export contract, creating correlated semantic assumptions.
  - Limitation: The separate implementation can still expose translation or coding disagreements.
- `observer:nanoda` — `DISTINCT_CODEBASE_SEMANTIC_INDEPENDENCE_UNESTABLISHED`
  - Attack: Treat a distinct Rust codebase as independent authority.
  - Rationale: Nanoda has a distinct implementation lineage but consumes the same Lean-level contract and correlated exported or Arena artifacts; that supports diversity, not authority.
  - Limitation: No quantitative dependence model is claimed.
- `observer:kiota` — `DISTINCT_CODEBASE_SEMANTIC_INDEPENDENCE_UNESTABLISHED`
  - Attack: Treat a from-scratch checker that is not a Nanoda fork as independent authority.
  - Rationale: From-scratch describes code provenance, while the semantic contract, serialized input family, and Arena expectations remain shared upstream influences.
  - Limitation: No quantitative dependence model is claimed.

## 6. Which entries cannot be observed independently?

- Decision ID: `CHALLENGE.M9.06.INDEPENDENT_OBSERVABILITY`
- Attack performed: For every active identity, the reviewer attempted to construct an isolated malformed object and trace whether each observer could represent it, reach the intended condition without an earlier rejection, and attribute the outcome to a checker independent of the target implementation.
- Disposition: `INDEPENDENT_OBSERVABILITY_INCOMPLETE`
- Rationale: Independent observability is incomplete for substantive reasons, not merely because cells are NOT_INSPECTED. Exporters can block free variables or metavariables; universe representations can erase or alter ownership context; reach prerequisites can reject before type-match or sort premises; replay order can conflate a target condition with reconstruction; and the official observer is the target composite. Existing concrete outcomes remain observations only, and absence of observation yields no favorable semantic inference.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `pre_review_catalog`: Concrete outcomes exist for only a bounded subset; all missing profile/entry observations remain NOT_INSPECTED rather than inferred.
- Evidence `source_lock`: Existing observations and witnesses are content-bound but do not provide complete independent observation of every entry.
- Challenge limitation: Incomplete observability is preserved as a negative result and blocks empirical establishment where applicable.

### Item-level adjudications

- `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY` — `REPRESENTABILITY_LIMITS_OBSERVATION`
  - Attack: Construct exported witnesses containing free variables or metavariables and require the malformed object to reach the declaration checker.
  - Rationale: Some pipelines reject or cannot encode the object before the intended declaration closure condition, so the later obligation is not independently isolated.
  - Limitation: A parser rejection is not evidence about the kernel condition.
- `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `EXPR.CONST.UNIVERSE_ARITY` — `PROFILE_CONTEXT_AND_EARLY_REJECTION_LIMIT_OBSERVATION`
  - Attack: Construct witnesses that violate one universe premise while satisfying representation and the other premises.
  - Rationale: Profile-specific universe representations and earlier arity or ownership failures prevent a uniform independent observation vector.
  - Limitation: No missing outcome is imputed as acceptance or rejection.
- `DECL.TYPE.WELL_FORMED`, `DECL.TYPE.SORT_VALUED`, `DECL.VALUE.WELL_FORMED`, `DECL.VALUE.TYPE_MATCH`, `DECL.THEOREM.TYPE_PROP`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.PI.CODOMAIN_SORT`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `DECL.EXPR.NO_LOOSE_BOUND_VARS` — `REACH_CONFOUNDING_LIMITS_OBSERVATION`
  - Attack: Violate each typing premise while preserving all prerequisites needed to reach it.
  - Rationale: Many candidate witnesses necessarily encounter well-formedness, inference, or function-type checks before the intended sort or equality premise; the frozen catalog correctly avoids claiming complete isolation.
  - Limitation: Future R(x) and not-P(x) witness synthesis is still required.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION` — `RECONSTRUCTION_CONFOUNDING_LIMITS_OBSERVATION`
  - Attack: Isolate pre-environment visibility and freshness from importer insertion order and environment-map behavior.
  - Rationale: Replay sequencing determines the environment presented to the checker, and the official path is not an independent observer of its own precondition.
  - Limitation: A separate harness could improve isolation later.
- `DECL.UNIVERSE.PARAM_UNIQUENESS`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `OBSERVATIONS_REMAIN_PROFILE_SCOPED`
  - Attack: Use existing observed cases to infer a complete or independent rule across all profiles.
  - Rationale: The concrete outcomes bind useful cases but share contract or execution lineage and do not establish independent semantic coverage.
  - Limitation: This grouped assessment overlaps universe uniqueness because its existing concrete observation does not remove the earlier profile limitation.

## 7. Which entries are duplicates?

- Decision ID: `CHALLENGE.M9.07.DUPLICATE_IDENTITIES`
- Attack performed: The reviewer ignored unique hashes and compared denotations, violation implication, reach prerequisites, rule premises, and future isolated-negative witness denominators across plausible pairs and clusters.
- Disposition: `NO_DUPLICATE_CANONICAL_DENOTATIONS`
- Rationale: No merge or split survived the attack. The candidate pairs may be reached sequentially or share syntax, but they state distinct premises: inferability versus sort-valuedness; body inferability versus declared-type equality; function-type formation versus argument equality; annotation sort versus value equality; parameter uniqueness versus ownership versus instantiation arity; and three distinct closure defects. Replay and safety scenarios describe separate mechanisms or policies from their normative counterparts. Keeping these premises separate improves future R(x) and not-P(x) synthesis without counting textual aliases.
- Catalog targets: 30
- Surface targets: 0
- Statement hash before: `63239bd01c55ab1af413302f58e27fd4aa50ef14e27aad34b1d431f39f0c4bca`
- Statement hash after: `63239bd01c55ab1af413302f58e27fd4aa50ef14e27aad34b1d431f39f0c4bca`
- Correction required: `false`

- Evidence `identity_registry`: Frozen merge and split decisions give each of the 30 identities a distinct statement digest.
- Evidence `pre_review_catalog`: All identity and semantic-denotation hashes are unique within their respective surfaces.
- Challenge limitation: Uniqueness of canonical denotations does not prove that no future evidence will justify a merge or split.

### Item-level adjudications

- `DECL.TYPE.WELL_FORMED`, `DECL.TYPE.SORT_VALUED` — `DISTINCT_RULE_PREMISES`
  - Attack: Ask whether inferability necessarily subsumes sort-valuedness and makes two identities double-count one condition.
  - Rationale: A type expression can be inferable while its inferred result is not a sort, so the second premise is not merely restatement.
  - Limitation: A later witness must satisfy the reach prerequisite explicitly.
- `DECL.VALUE.WELL_FORMED`, `DECL.VALUE.TYPE_MATCH` — `DISTINCT_RULE_PREMISES`
  - Attack: Ask whether value inferability and body/type agreement are the same rejection condition.
  - Rationale: The body can infer successfully to the wrong type, separating formation from definitional equality.
  - Limitation: Equality observation can be blocked by earlier inference failure.
- `EXPR.APP.FUNCTION_TYPE`, `EXPR.APP.ARGUMENT_TYPE_MATCH` — `DISTINCT_RULE_PREMISES`
  - Attack: Ask whether a bad argument is merely one way for the function not to have a Pi type.
  - Rationale: A valid Pi-typed function can receive an argument of the wrong type, while a non-function can fail before argument comparison.
  - Limitation: Negative tests must preserve function reach for the argument case.
- `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH` — `DISTINCT_RULE_PREMISES`
  - Attack: Ask whether checking the value against the annotation renders annotation formation redundant.
  - Rationale: The annotation must itself be type-valued, and a valid annotation can still disagree with the inferred value type.
  - Limitation: Sequential rejection order can obscure the second premise.
- `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `EXPR.CONST.UNIVERSE_ARITY` — `DISTINCT_UNIVERSE_PREMISES`
  - Attack: Merge declaration parameter-list integrity, ownership of referenced parameters, and per-constant instantiation arity.
  - Rationale: Duplicate binders, undeclared referenced parameters, and a wrong number of arguments instantiate different malformed objects and different rule premises.
  - Limitation: Some profiles cannot independently represent every ownership defect.
- `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS` — `DISTINCT_CLOSURE_CONSTRUCTORS`
  - Attack: Merge all declaration closure failures into one generic well-scopedness identity.
  - Rationale: Free variables, metavariables, and loose de Bruijn indices have different constructors, representations, and reach conditions, so one identity would hide distinct synthesis limitations.
  - Limitation: A future aggregate metric must avoid treating correlated parser failures as independent evidence.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY` — `NORMATIVE_AND_EMPIRICAL_IDENTITIES_DISTINCT`
  - Attack: Merge the modeled pre-environment condition with the importer ordering scenario.
  - Rationale: One states what checked declaration validity provisionally requires; the other records how reconstruction realizes or frustrates observation of that condition.
  - Limitation: The normative identity remains provisional.
- `DECL.SAFETY.SAFE_DEPENDENCY`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `SAFETY_AND_REPLAY_IDENTITIES_DISTINCT`
  - Attack: Merge safety dependency, admission, serialized flags, flag reconstruction, and replay filtering into one policy identity.
  - Rationale: The deferred normative dependency question and four empirical policy or reconstruction phenomena have different targets, lifecycle states, and possible counterexamples.
  - Limitation: The deferred dependency identity is not admitted into the active catalog denominator.
- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.SAFETY.SAFE_DEPENDENCY`, `DECL.THEOREM.TYPE_PROP`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.TYPE.SORT_VALUED`, `DECL.TYPE.WELL_FORMED`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.VALUE.TYPE_MATCH`, `DECL.VALUE.WELL_FORMED`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.CONST.UNIVERSE_ARITY`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.PI.CODOMAIN_SORT`, `EXPR.PROJECTION.TYPING`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY`, `SCENARIO.LITERAL.AVAILABILITY_POLICY`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `NO_ADDITIONAL_MERGE_OR_SPLIT`
  - Attack: Scan the remaining identities for paraphrases or coarse entries that hide two independently violable premises.
  - Rationale: The frozen identity decisions provide a single operational denotation for each remaining active or deferred identity, and source tracing revealed no unrecorded conjunct requiring evolution.
  - Limitation: Semantic uniqueness is a reviewer judgment, not a consequence of hash uniqueness.

## 8. Which established entries lack sufficient normative support?

- Decision ID: `CHALLENGE.M9.08.ESTABLISHED_SUPPORT`
- Attack performed: The reviewer enumerated authority states and then searched reports, summaries, expected-outcome prose, and challenge language for any effective treatment of a provisional entry as established.
- Disposition: `NO_ESTABLISHED_ENTRY_TO_DOWNGRADE`
- Rationale: The direct downgrade question is vacuous because zero entries are ESTABLISHED. That vacuity does not support the candidates: all twenty-seven remain PROVISIONAL with unmet requirements, and no derived prose substitutes implementation agreement for qualified normative evidence.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `pre_review_catalog`: The inventory contains zero ESTABLISHED entries of either kind.
- Evidence `approved_authority_sources`: No source is approved to support an established normative claim.
- Challenge limitation: This is a bounded absence finding, not evidence that the provisional candidates are true.

### Item-level adjudications

- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.THEOREM.TYPE_PROP`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.TYPE.SORT_VALUED`, `DECL.TYPE.WELL_FORMED`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.VALUE.TYPE_MATCH`, `DECL.VALUE.WELL_FORMED`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.CONST.UNIVERSE_ARITY`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.PI.CODOMAIN_SORT`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `VACUOUS_NO_ESTABLISHED_ENTRIES`
  - Attack: Look for an ESTABLISHED state or prose that silently grants equivalent authority.
  - Rationale: No established entry exists to downgrade, and provisional language plus unmet requirements is preserved throughout the bound artifacts.
  - Limitation: This is not evidence that any provisional classification is semantically correct.

## 9. Which checks in the declared discovery surface were missed?

- Decision ID: `CHALLENGE.M9.09.DISCOVERY_SURFACE_OMISSIONS`
- Attack performed: The reviewer independently fetched the exact pinned official source blobs, verified their hashes, inspected the twenty-two declared source modules across all four profiles, traced ordinary declaration entrypoints into shared helpers, and examined neighboring type-specific and excluded branches for checks absent from the 149 site or identity dispositions.
- Disposition: `NO_OMISSION_WITHIN_FROZEN_DISCOVERY_SURFACE`
- Rationale: The bounded attack found no missed ordinary declaration-validation check in the declared boundary. Apparent edge findings were already represented: value-expression closure is a reach component of value well-formedness; safe-dependency checking has a durable deferred identity; projection typing and literal or native policy have explicit out-of-scope identities; and excluded declaration families, trust configuration, replay order, and malformed streams are durably disposed. The conclusion is about survival of this source-boundary attack, not completeness of the whole kernel or literature.
- Catalog targets: 30
- Surface targets: 116
- Statement hash before: `7e93be4a069a3f12312a501b83ba2f6418310a83afac828e1b9e29e699702226`
- Statement hash after: `7e93be4a069a3f12312a501b83ba2f6418310a83afac828e1b9e29e699702226`
- Correction required: `false`

- Evidence `discovery_closure`: The frozen boundary contains 22 exhausted sources, 59 disposed sites, closed topics, and disposed helper dependencies.
- Evidence `pre_review_catalog`: The catalog exactly dispositions all 30 identities and all 149 relevant identity/site pairs.
- Challenge limitation: No-omission applies only to the declared frozen surface, not all Lean declaration validation.

### Item-level adjudications

- `DEP.DECLARATION_REPRESENTATION`, `DEP.DEFINITIONAL_EQUALITY`, `DEP.ENVIRONMENT_LOOKUP`, `DEP.EXCLUDED_DECLARATION_CHECKERS`, `DEP.EXPORT_PARSER`, `DEP.EXPRESSION_CHECKING`, `DEP.LITERAL_TYPES`, `DEP.LOCAL_CONTEXT`, `DEP.PROJECTION_METADATA`, `DEP.PROPOSITION_TEST`, `DEP.REPLAY_ORDER`, `DEP.TRUST_CONFIGURATION`, `DEP.UNIVERSE_LEVEL_JUDGMENT`, `SITE.KIOTA.ENV.MAP`, `SITE.KIOTA.EXPR.REPRESENTATION`, `SITE.KIOTA.LEVEL.NO_OWNERSHIP_CONTEXT`, `SITE.KIOTA.MAIN.OPERATIONAL`, `SITE.KIOTA.PARSER.DUPLICATE`, `SITE.KIOTA.PARSER.EXCLUDED`, `SITE.KIOTA.PARSER.INSERT_BEFORE_CHECK`, `SITE.KIOTA.PARSER.REPRESENTATION`, `SITE.KIOTA.TC.APP_LET`, `SITE.KIOTA.TC.BINDERS`, `SITE.KIOTA.TC.CONST`, `SITE.KIOTA.TC.DECL`, `SITE.KIOTA.TC.PROJ`, `SITE.KIOTA.TC.UNIVERSE_ABSENCE`, `SITE.LEAN4LEAN.BASIC.HEADER_HELPERS`, `SITE.LEAN4LEAN.DECL.DELTA`, `SITE.LEAN4LEAN.ENV.AXIOM`, `SITE.LEAN4LEAN.ENV.DEF`, `SITE.LEAN4LEAN.ENV.EXCLUDED`, `SITE.LEAN4LEAN.ENV.HEADER`, `SITE.LEAN4LEAN.ENV.OPAQUE`, `SITE.LEAN4LEAN.ENV.THEOREM`, `SITE.LEAN4LEAN.REPLAY.EXCLUDED`, `SITE.LEAN4LEAN.REPLAY.ORDER`, `SITE.LEAN4LEAN.REPLAY.SKIPS`, `SITE.LEAN4LEAN.TC.APP_LET`, `SITE.LEAN4LEAN.TC.BINDERS`, `SITE.LEAN4LEAN.TC.CONST`, `SITE.LEAN4LEAN.TC.DISPATCH`, `SITE.LEAN4LEAN.TC.PROJ`, `SITE.NANODA.ENV.CUTOFF`, `SITE.NANODA.EXPR.UARG_ARITY`, `SITE.NANODA.LEVEL.PARAMS`, `SITE.NANODA.PARSER.EXCLUDED`, `SITE.NANODA.PARSER.ORDINARY`, `SITE.NANODA.PARSER.POLICY`, `SITE.NANODA.PARSER.REPRESENTATION`, `SITE.NANODA.TC.APP_LET`, `SITE.NANODA.TC.BINDERS`, `SITE.NANODA.TC.CONST`, `SITE.NANODA.TC.DECL`, `SITE.NANODA.TC.DISPATCH`, `SITE.NANODA.TC.HEADER`, `SITE.NANODA.TC.PROJ`, `SITE.NANODA.UTIL.CURRENT_VISIBILITY`, `SITE.OFFICIAL.DECL.SHAPES`, `SITE.OFFICIAL.ENV.AXIOM`, `SITE.OFFICIAL.ENV.DEF`, `SITE.OFFICIAL.ENV.EXCLUDED_DISPATCH`, `SITE.OFFICIAL.ENV.HEADER`, `SITE.OFFICIAL.ENV.OPAQUE`, `SITE.OFFICIAL.ENV.THEOREM`, `SITE.OFFICIAL.IMPORTER.REPLAY`, `SITE.OFFICIAL.TC.APP_LET`, `SITE.OFFICIAL.TC.BINDERS`, `SITE.OFFICIAL.TC.CONST`, `SITE.OFFICIAL.TC.DISPATCH`, `SITE.OFFICIAL.TC.HEADER`, `SITE.OFFICIAL.TC.PROJ`, `SRC.KIOTA.ENV`, `SRC.KIOTA.EXPR`, `SRC.KIOTA.LEVEL`, `SRC.KIOTA.MAIN`, `SRC.KIOTA.PARSER`, `SRC.KIOTA.TC`, `SRC.LEAN4LEAN.DECLARATION`, `SRC.LEAN4LEAN.ENVIRONMENT`, `SRC.LEAN4LEAN.ENVIRONMENT_BASIC`, `SRC.LEAN4LEAN.REPLAY`, `SRC.LEAN4LEAN.TYPECHECKER`, `SRC.NANODA.ENV`, `SRC.NANODA.EXPR`, `SRC.NANODA.LEVEL`, `SRC.NANODA.PARSER`, `SRC.NANODA.TC`, `SRC.NANODA.UTIL`, `SRC.OFFICIAL.ARENA_MAIN`, `SRC.OFFICIAL.DECLARATION_HEADER`, `SRC.OFFICIAL.ENVIRONMENT`, `SRC.OFFICIAL.TYPECHECKER`, `SRC.OFFICIAL.TYPECHECKER_HEADER`, `TOPIC.APPLICATION_TYPING`, `TOPIC.AXIOM_ADMISSION_POLICY`, `TOPIC.BODY_TYPE_MATCH`, `TOPIC.BODY_WELL_FORMED`, `TOPIC.CONSTANT_UNIVERSE_ARITY`, `TOPIC.CURRENT_DECL_VISIBILITY`, `TOPIC.DUPLICATE_UNIVERSE_PARAMS`, `TOPIC.EXCLUDED_DECLARATION_KINDS`, `TOPIC.FVAR_CLOSURE`, `TOPIC.LET_ANNOTATION_VALUE`, `TOPIC.LITERAL_EXTENSIONS`, `TOPIC.LOCAL_BINDER_SORT`, `TOPIC.LOOSE_BOUND_VARIABLE`, `TOPIC.MVAR_CLOSURE`, `TOPIC.NAME_FRESHNESS`, `TOPIC.PROJECTION_EXPRESSION_TYPING`, `TOPIC.REPLAY_AND_CHECK_PHASE`, `TOPIC.SAFE_UNSAFE_DEPENDENCY`, `TOPIC.SERIALIZED_SAFETY`, `TOPIC.THEOREM_TYPE_PROP`, `TOPIC.TYPE_WELL_FORMED_SORT`, `TOPIC.UNIVERSE_OWNERSHIP` — `NO_MISSED_SITE_IN_DECLARED_BOUNDARY`
  - Attack: Trace each declared source module from validation entrypoints through helper calls and compare every encountered check or neighboring branch with the frozen source-site and identity closure.
  - Rationale: All encountered ordinary checks map to an active identity or reach component, while neighboring projection, literal, safety-dependency, excluded-declaration, replay, and policy paths have explicit durable dispositions.
  - Limitation: This was a bounded inspection of the declared source boundary, not a new whole-kernel discovery project.
- `DECL.VALUE.WELL_FORMED`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS` — `REACH_COMPONENT_ALREADY_REPRESENTED`
  - Attack: Treat free-variable and metavariable scans in declaration values as omitted standalone source sites.
  - Rationale: Those scans are part of making the value inferable and closed before value/type agreement; the active value well-formedness identity and closure identities already preserve the semantic distinction.
  - Limitation: Future tests must document which prerequisite caused an early rejection.
- `DECL.SAFETY.SAFE_DEPENDENCY`, `EXPR.PROJECTION.TYPING`, `SCENARIO.LITERAL.AVAILABILITY_POLICY` — `DURABLY_DISPOSED_NOT_OMITTED`
  - Attack: Reclassify deferred or excluded neighboring checks as omissions merely because they are outside the active twenty-seven entries.
  - Rationale: Each has a stable identity and explicit lifecycle or scope disposition, so it cannot disappear from closure accounting even though it is absent from the active catalog denominator.
  - Limitation: Scope justification is challenged separately in Challenge 10.

## 10. Which exclusions are poorly justified?

- Decision ID: `CHALLENGE.M9.10.EXCLUSION_JUSTIFICATION`
- Attack performed: The reviewer tested every exclusion, deferred identity, and excluded phase for convenience bias by asking whether ordinary declaration validity actually depends on it and whether removing it would distort a later negative-test denominator.
- Disposition: `EXCLUSIONS_SCOPED_AND_JUSTIFIED`
- Rationale: The retained boundary is coherent. Projections require metadata and a dedicated expression rule; literals and native extensions require availability policy; inductives, recursors, quotients, unsafe or partial declarations, and mutual groups use declaration-specific validation outside the ordinary axiom, definition, opaque, and theorem slice; general reduction is infrastructure rather than a single declaration premise; malformed streams are parser robustness; and trust configuration or normalization is policy or harness infrastructure. Safe dependency remains deferred rather than excluded, preserving its denominator impact for a successor decision.
- Catalog targets: 3
- Surface targets: 22
- Statement hash before: `2c848cd1822b12cf1eb6f43d215a0ba2e4cbdbfca1f48113315e0d570cc5e903`
- Statement hash after: `2c848cd1822b12cf1eb6f43d215a0ba2e4cbdbfca1f48113315e0d570cc5e903`
- Correction required: `false`

- Evidence `discovery_closure`: Every declared exclusion, excluded phase, and excluded dependency has a non-empty bounded rationale and source linkage where applicable.
- Evidence `pre_review_catalog`: The deferred-kind and two out-of-scope identities remain explicit non-entry dispositions rather than disappearing.
- Challenge limitation: A justified exclusion is a scope decision, not a claim that the excluded area lacks assurance value.

### Item-level adjudications

- `DECL.SAFETY.SAFE_DEPENDENCY`, `DEP.TRUST_CONFIGURATION` — `DEFERRED_IDENTITY_RETAINED`
  - Attack: Exclude safe-dependency behavior as mere policy because qualification is difficult.
  - Rationale: The question plausibly affects ordinary safe declarations but needs a separate semantic decision, so durable deferral preserves rather than erases it.
  - Limitation: No trust or soundness classification is made here.
- `EXPR.PROJECTION.TYPING`, `EXCL.PROJECTION_METADATA`, `DEP.PROJECTION_METADATA`, `PROJECTION_METADATA` — `SPECIALIZED_RULE_BOUNDARY_RETAINED`
  - Attack: Pull projection checks into ordinary expression typing because projection nodes appear in shared type-checker dispatch.
  - Rationale: Projection validity depends on inductive and projection metadata deliberately excluded from this ordinary declaration slice and has its own stable identity.
  - Limitation: A successor slice may qualify it separately.
- `SCENARIO.LITERAL.AVAILABILITY_POLICY`, `EXCL.LITERALS_NATIVE`, `DEP.LITERAL_TYPES`, `NATIVE_EXTENSION` — `AVAILABILITY_POLICY_BOUNDARY_RETAINED`
  - Attack: Treat literal and native-extension rejection as an ordinary kernel declaration obligation.
  - Rationale: The checks depend on extension availability and environment policy rather than a universal ordinary declaration premise.
  - Limitation: Profile-specific behavior remains an empirical scenario.
- `EXCL.INDUCTIVE_QUOTIENT`, `DEP.EXCLUDED_DECLARATION_CHECKERS`, `INDUCTIVE_FAMILY`, `QUOTIENT_PRIMITIVES` — `DECLARATION_FAMILY_BOUNDARY_RETAINED`
  - Attack: Include inductive families, generated recursors, and quotient primitives because they enter the same environment.
  - Rationale: They invoke distinct family-wide and primitive validation not modeled by the ordinary declaration contract under review.
  - Limitation: The exclusion does not claim those declarations are unimportant.
- `EXCL.UNSAFE_PARTIAL_MUTUAL`, `UNSAFE_DEFINITION`, `UNSAFE_OPAQUE`, `PARTIAL_DEFINITION`, `MUTUAL_DEFINITION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `SPECIALIZED_POLICY_BOUNDARY_RETAINED`
  - Attack: Include all unsafe, partial, and mutual semantics in the ordinary slice because replay filters them.
  - Rationale: The active replay scenario records the relevant filtering observation, while specialized declaration semantics remain outside ordinary checked additions.
  - Limitation: No soundness consequence is assessed.
- `EXCL.GENERAL_REDUCTION`, `GENERAL_REDUCTION` — `INFRASTRUCTURE_BOUNDARY_RETAINED`
  - Attack: Count the entire reduction engine as a missed declaration-validity obligation.
  - Rationale: Reduction supports typing and definitional equality but is not one independently enumerable declaration premise in this contract slice.
  - Limitation: Specific equality premises remain active catalog identities.
- `EXCL.MALFORMED_STREAM`, `JSON_SYNTAX`, `ARENA_NORMALIZATION`, `ELABORATION` — `HARNESS_AND_FRONTEND_BOUNDARY_RETAINED`
  - Attack: Include malformed input, syntax, normalization, and elaboration failures in the declaration-validity denominator.
  - Rationale: These paths concern transport, frontend, or harness behavior before a modeled declaration reaches checked addition.
  - Limitation: Representability effects are retained separately as empirical scenarios.

## 11. Which soundness_relevance claims overreach the evidence?

- Decision ID: `CHALLENGE.M9.11.SOUNDNESS_OVERREACH`
- Attack performed: The reviewer inspected every soundness_relevance field and searched catalog, review, and generated prose for claims such as soundness-critical or merely policy that would assign significance without the later qualification process.
- Disposition: `NO_SOUNDNESS_OVERREACH`
- Rationale: All twenty-seven entries remain NOT_ASSESSED, and the prose treats kernel, reconstruction, export, trust, and implementation layers as classifications rather than soundness conclusions. Some boundaries may later prove important, but neither implementation consensus nor inability to observe justifies assessment now.
- Catalog targets: 27
- Surface targets: 0
- Statement hash before: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Statement hash after: `ce4364d2eaf5142577302a6845eeb9014c32e1193f4a22c20ec0585aa13e81d1`
- Correction required: `false`

- Evidence `pre_review_catalog`: All 27 entries retain soundness_relevance=NOT_ASSESSED with no basis evidence reference.
- Challenge limitation: No soundness conclusion, favorable or unfavorable, is drawn.

### Item-level adjudications

- `DECL.ENV.CURRENT_DECL_NOT_VISIBLE`, `DECL.ENV.NAME_FRESHNESS`, `DECL.EXPR.NO_LOOSE_BOUND_VARS`, `DECL.THEOREM.TYPE_PROP`, `DECL.TYPE.NO_FREE_VARS`, `DECL.TYPE.NO_METAVARS`, `DECL.TYPE.SORT_VALUED`, `DECL.TYPE.WELL_FORMED`, `DECL.UNIVERSE.PARAM_OWNERSHIP`, `DECL.UNIVERSE.PARAM_UNIQUENESS`, `DECL.VALUE.TYPE_MATCH`, `DECL.VALUE.WELL_FORMED`, `EXPR.APP.ARGUMENT_TYPE_MATCH`, `EXPR.APP.FUNCTION_TYPE`, `EXPR.BINDER.DOMAIN_SORT`, `EXPR.CONST.UNIVERSE_ARITY`, `EXPR.LET.ANNOTATION_SORT`, `EXPR.LET.VALUE_TYPE_MATCH`, `EXPR.PI.CODOMAIN_SORT`, `SCENARIO.AXIOM.ADMISSION_POLICY`, `SCENARIO.AXIOM.SAFETY_FLAG`, `SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION`, `SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY`, `SCENARIO.EXPORT.METAVAR_REPRESENTABILITY`, `SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY`, `SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION`, `SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER` — `NOT_ASSESSED_RETAINED`
  - Attack: Find an explicit or implicit soundness classification that outruns the evidence and qualification gates.
  - Rationale: No catalog field or bound prose makes a qualified soundness claim; potentially important cases remain explicitly unresolved.
  - Limitation: NOT_ASSESSED is not a claim of irrelevance.

## 12. Could another researcher reconstruct the catalog without trusting the LLM?

- Decision ID: `CHALLENGE.M9.12.LLM_INDEPENDENT_RECONSTRUCTION`
- Attack performed: The reviewer reconstructed the immutable M8 predecessor from its attested Git blobs, reran deterministic population and validation, and compared stable identities, active entries, identity and site dispositions, evidence dispositions, observer vectors, source mappings, authority states, Arena dispositions, and predecessor identity.
- Disposition: `RECONSTRUCTABLE_WITHOUT_LLM_AUTHORITY`
- Rationale: The research state is mechanically reproducible without trusting an LLM: the attested predecessor yields 27 active entries, 30 identity dispositions, 149 site or identity dispositions, existing-evidence dispositions, observer vectors, source mappings, authority states, Arena dispositions, and the exact M8 identity. That reproducibility does not make the authored adversarial judgments mechanically true; their attacks, evidence, rationales, limitations, and outcomes are durable review inputs that validators preserve rather than synthesize.
- Catalog targets: 30
- Surface targets: 0
- Statement hash before: `63239bd01c55ab1af413302f58e27fd4aa50ef14e27aad34b1d431f39f0c4bca`
- Statement hash after: `63239bd01c55ab1af413302f58e27fd4aa50ef14e27aad34b1d431f39f0c4bca`
- Correction required: `false`

- Evidence `m8_historical_attestation`: Corrected M8 inputs resolve through exact Git blobs rather than mutable paths or conversational state.
- Evidence `m9_inventory_populator`: The M9 pre-review bytes are deterministically reproduced from immutable M8; the reviewed catalog is checked against that input plus explicit corrections through a defined canonical inventory projection.
- Evidence `catalog_validator`: Schema, evidence, authority, identity, observer, site, report, and historical gates are executable without LLM judgment.
- Challenge limitation: Mechanical reconstruction proves reproducibility of the recorded catalog, not semantic truth.

### Item-level adjudications

- `M8_PREDECESSOR`, `27_ACTIVE_ENTRIES`, `30_IDENTITY_DISPOSITIONS`, `149_SITE_IDENTITY_DISPOSITIONS` — `MECHANICALLY_RECONSTRUCTED`
  - Attack: Reconstruct counts and catalog bytes using only frozen Git-bound inputs and scripts.
  - Rationale: The immutable M8 attestation and deterministic population reproduce the catalog state and closure counts without a semantic oracle.
  - Limitation: Mechanical equality proves provenance and consistency, not semantic truth.
- `EXISTING_EVIDENCE`, `OBSERVER_VECTORS`, `SOURCE_MAPPINGS`, `AUTHORITY_STATES`, `ARENA_DISPOSITIONS` — `MECHANICALLY_RECONSTRUCTED`
  - Attack: Rebuild the evidence, observer, source, authority, and Arena projections from their content-bound inputs.
  - Rationale: The evidence locks and canonical inputs determine those projections and preserve NOT_INSPECTED or unqualified states rather than asking an LLM to fill gaps.
  - Limitation: Execution outcomes remain bounded to their pinned artifacts and profiles.
- `AUTHORED_M9_JUDGMENTS` — `EXPLICIT_NON_DERIVED_RESEARCH_DECISIONS`
  - Attack: Attempt to regenerate challenge dispositions and rationales from the reviewed catalog.
  - Rationale: The renderer only presents the canonical record and the validator only checks procedure and consistency; semantic judgments remain authored, evidence-linked decisions and may record either failure or retention.
  - Limitation: Another researcher may disagree semantically while still reproducing the same recorded state.

## Preserved Nonclaims

- A no-correction review result does not prove the catalog complete beyond its frozen discovery surface.
- The review does not establish any normative candidate, empirical scenario, or soundness relevance.
- Incomplete independent observation remains visible and is not treated as a favorable result.
- No Arena coverage denominator or broad negative-test study is created by Milestone 9.
- The adversarial review is reproducible audit evidence, not semantic authority.

Next milestone: `MILESTONE_10_DESIGN_FROZEN_INVENTORY_COVERAGE_STUDY`
