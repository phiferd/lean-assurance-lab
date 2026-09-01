# Declaration Validation Milestone 10 Study Design

Study design SHA-256: `f53ac6a72355e24e20e2cdd74dfb4c2d1aff87b5079bfd6dfa9748f89423b496`
Immutable M9 attestation SHA-256: `6a26aff21d26284b5e6298a33bc0977c9c20b0c063d42aafcf0e33210d821a89`
Immutable M9 Phase-A commit: `69dad9d13e4802e5ef29c958c60d2ee387293847`

This is a frozen protocol and readiness analysis, not an executed Arena study. It does not approve authority sources, promote provisional entries, generate semantic evidence, or report a normative coverage percentage.

## Mechanically Derived Populations

- Primary normative negative-coverage denominator: **0**
- Coverage percentage: **NOT_REPORTED_EMPTY_DENOMINATOR**
- Provisional exploratory candidates: **19**
- Empirical characterization-context entries: **8**
- Deferred or reserved identities: **3**

The primary denominator is empty because every active normative candidate has frozen `PROVISIONAL` authority. That result is preserved rather than repaired.

## Complete Readiness Analysis

| Identity | Kind | Authority | Kernel | Scope | Semantic negative | Arena | Isolation | Lifecycle | Primary | Exclusions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| DECL.ENV.NAME_FRESHNESS | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.UNIVERSE.PARAM_UNIQUENESS | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.TYPE.NO_FREE_VARS | YES | NO | YES | YES | YES | UNRESOLVED | UNRESOLVED | YES | NO | AUTHORITY_NOT_ESTABLISHED, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_UNRESOLVED |
| DECL.TYPE.NO_METAVARS | YES | NO | YES | YES | YES | UNRESOLVED | UNRESOLVED | YES | NO | AUTHORITY_NOT_ESTABLISHED, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_UNRESOLVED |
| DECL.EXPR.NO_LOOSE_BOUND_VARS | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY | NO | NO | NO | NO | NO | UNRESOLVED | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_NO |
| SCENARIO.EXPORT.METAVAR_REPRESENTABILITY | NO | NO | NO | NO | NO | UNRESOLVED | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_NO |
| DECL.UNIVERSE.PARAM_OWNERSHIP | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.CONST.UNIVERSE_ARITY | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.TYPE.WELL_FORMED | YES | NO | YES | YES | YES | YES | UNRESOLVED | YES | NO | AUTHORITY_NOT_ESTABLISHED, ISOLATION_FEASIBILITY_UNRESOLVED |
| DECL.TYPE.SORT_VALUED | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.VALUE.WELL_FORMED | YES | NO | YES | YES | YES | YES | UNRESOLVED | YES | NO | AUTHORITY_NOT_ESTABLISHED, ISOLATION_FEASIBILITY_UNRESOLVED |
| DECL.VALUE.TYPE_MATCH | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.THEOREM.TYPE_PROP | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.ENV.CURRENT_DECL_NOT_VISIBLE | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| DECL.SAFETY.SAFE_DEPENDENCY | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | NO | NO_FROZEN_CATALOG_ENTRY, KIND_UNRESOLVED, AUTHORITY_UNRESOLVED, KERNEL_LAYER_UNRESOLVED, STUDY_SCOPE_UNRESOLVED, SEMANTIC_NEGATIVE_TESTABILITY_UNRESOLVED, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_UNRESOLVED, LIFECYCLE_UNRESOLVED |
| EXPR.BINDER.DOMAIN_SORT | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.PI.CODOMAIN_SORT | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.LET.ANNOTATION_SORT | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.LET.VALUE_TYPE_MATCH | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.APP.FUNCTION_TYPE | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.APP.ARGUMENT_TYPE_MATCH | YES | NO | YES | YES | YES | YES | YES | YES | NO | AUTHORITY_NOT_ESTABLISHED |
| EXPR.PROJECTION.TYPING | UNRESOLVED | UNRESOLVED | UNRESOLVED | NO | UNRESOLVED | UNRESOLVED | UNRESOLVED | NO | NO | NO_FROZEN_CATALOG_ENTRY, KIND_UNRESOLVED, AUTHORITY_UNRESOLVED, KERNEL_LAYER_UNRESOLVED, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_UNRESOLVED, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_UNRESOLVED, LIFECYCLE_NOT_ACTIVE |
| SCENARIO.AXIOM.ADMISSION_POLICY | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.AXIOM.SAFETY_FLAG | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.DECL.SAFETY_FLAG_RECONSTRUCTION | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.REPLAY.UNSAFE_PARTIAL_FILTER | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY | NO | NO | NO | NO | NO | YES | NO | YES | NO | KIND_NOT_NORMATIVE, AUTHORITY_NOT_ESTABLISHED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ISOLATION_FEASIBILITY_NO |
| SCENARIO.LITERAL.AVAILABILITY_POLICY | NO | UNRESOLVED | NO | NO | NO | UNRESOLVED | NO | NO | NO | NO_FROZEN_CATALOG_ENTRY, KIND_NOT_NORMATIVE, AUTHORITY_UNRESOLVED, KERNEL_LAYER_ABSENT, STUDY_SCOPE_NO, SEMANTIC_NEGATIVE_TESTABILITY_NO, ARENA_REPRESENTABILITY_UNRESOLVED, ISOLATION_FEASIBILITY_NO, LIFECYCLE_NOT_ACTIVE |

## Provisional Exploratory Candidate Strategies

### DECL.ENV.NAME_FRESHNESS

- Tier: 1
- Construction: Duplicate an otherwise valid declaration under an existing environment name.
- Positive control: Rename only the candidate declaration to a fresh name.
- Competing obligations: Keep universe parameters, type, value, and safety metadata byte-equivalent to the valid family.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.UNIVERSE.PARAM_UNIQUENESS

- Tier: 1
- Construction: Duplicate one universe-parameter name in a valid polymorphic declaration.
- Positive control: Use two distinct parameter names and preserve corresponding references.
- Competing obligations: Prove ownership and expression typing remain satisfied in both members of the family.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.TYPE.NO_FREE_VARS

- Tier: 1
- Construction: Place one raw free-variable expression node in an otherwise valid declaration type.
- Positive control: Replace the free variable with a closed constant of the same intended type.
- Competing obligations: Distinguish target closure failure from parser rejection and downstream aggregate type failure.
- Blocking prerequisites: Resolve free-variable Arena/export representability.; Resolve aggregate well-formedness attribution.; Primary counting requires separately established normative authority.

### DECL.TYPE.NO_METAVARS

- Tier: 1
- Construction: Place one raw metavariable expression node in an otherwise valid declaration type.
- Positive control: Replace the metavariable with a closed constant of the same intended type.
- Competing obligations: Distinguish target closure failure from parser rejection and downstream aggregate type failure.
- Blocking prerequisites: Resolve metavariable Arena/export representability.; Resolve aggregate well-formedness attribution.; Primary counting requires separately established normative authority.

### DECL.EXPR.NO_LOOSE_BOUND_VARS

- Tier: 2
- Construction: Increment one bound-variable index in a known-valid binder body beyond the available depth.
- Positive control: Restore the original in-scope index in the same artifact family.
- Competing obligations: Show that any enclosing well-formedness failure is a consequence of the targeted loose occurrence.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.UNIVERSE.PARAM_OWNERSHIP

- Tier: 1
- Construction: Reuse the frozen undeclared-universe family as an exploratory template without treating its outcomes as authority.
- Positive control: Add the referenced universe parameter to the declaration-owned list.
- Competing obligations: Verify arity, sort formation, and all non-ownership prerequisites separately.
- Blocking prerequisites: Primary counting requires separately established normative authority.; A successor must rebind exact artifacts under the M10 evidence contract.

### EXPR.CONST.UNIVERSE_ARITY

- Tier: 2
- Construction: Delete or add one universe argument on a known-valid polymorphic constant reference.
- Positive control: Restore exactly one argument per declared universe parameter.
- Competing obligations: Keep universe ownership and the referenced constant name valid in both artifacts.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.TYPE.WELL_FORMED

- Tier: 3
- Construction: Search by constraints for a type-inference failure outside all separately inventoried expression predicates.
- Positive control: Repair the minimal inference defect while preserving declaration kind and surrounding expression family.
- Competing obligations: Enumerate every leaf expression predicate and distinguish derived aggregate failure from independent failure.
- Blocking prerequisites: Identify an isolatable non-leaf type well-formedness violation.; Primary counting requires separately established normative authority.

### DECL.TYPE.SORT_VALUED

- Tier: 1
- Construction: Use a closed well-typed term rather than a type as the declaration's declared type.
- Positive control: Replace that term with its well-formed type in the same declaration family.
- Competing obligations: Prove the negative term is itself well typed and contains no closure, ownership, or expression defects.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.VALUE.WELL_FORMED

- Tier: 3
- Construction: Search by constraints for a value-inference failure outside all separately inventoried expression predicates.
- Positive control: Repair the minimal inference defect while preserving declaration kind, type, and expression family.
- Competing obligations: Enumerate every leaf expression predicate and distinguish derived aggregate failure from independent failure.
- Blocking prerequisites: Identify an isolatable non-leaf value well-formedness violation.; Primary counting requires separately established normative authority.

### DECL.VALUE.TYPE_MATCH

- Tier: 1
- Construction: Pair a closed valid declaration type with a closed well-typed value of a distinct type.
- Positive control: Change only the declared type or value so their inferred types definitionally agree.
- Competing obligations: Prove both type and value well-formedness, closure, and kind-specific applicability independently.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### DECL.THEOREM.TYPE_PROP

- Tier: 1
- Construction: Reuse the frozen non-Prop theorem construction family as an exploratory template.
- Positive control: Use the matched definition-form control or a Prop-valued theorem repair with minimized differences.
- Competing obligations: Re-establish type/value well-formedness, compatibility, and proposition failure from content-bound bytes.
- Blocking prerequisites: Primary counting requires separately established normative authority.; A successor must rebind exact artifacts under the M10 evidence contract.

### DECL.ENV.CURRENT_DECL_NOT_VISIBLE

- Tier: 1
- Construction: Use a value whose constant reference names the declaration currently being checked.
- Positive control: Reference an equivalent previously admitted declaration instead of the current name.
- Competing obligations: Separate environment visibility from constant arity, type matching, ordering, and reconstruction policy.
- Blocking prerequisites: Primary counting requires separately established normative authority.; A successor must distinguish kernel target behavior from reconstruction scenarios.

### EXPR.BINDER.DOMAIN_SORT

- Tier: 1
- Construction: Use a closed well-typed non-type term as a lambda or Pi binder annotation.
- Positive control: Replace it with its well-formed type while preserving the binder body.
- Competing obligations: Prove annotation inference succeeds and attribute enclosing well-formedness failure to sorthood.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### EXPR.PI.CODOMAIN_SORT

- Tier: 1
- Construction: Use a well-typed non-type term as a Pi codomain in the extended local context.
- Positive control: Replace it with its type while preserving the domain and local references.
- Competing obligations: Prove domain sorthood and codomain inference before attributing Pi formation failure to this target.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### EXPR.LET.ANNOTATION_SORT

- Tier: 1
- Construction: Use a well-typed non-type term as a local-let annotation.
- Positive control: Replace the annotation with its type and preserve value and body structure.
- Competing obligations: Prove annotation inference independently and separate sorthood from value/annotation compatibility.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### EXPR.LET.VALUE_TYPE_MATCH

- Tier: 1
- Construction: Reuse the frozen mismatched local-let family as an exploratory template.
- Positive control: Change only the value or annotation so their types definitionally agree.
- Competing obligations: Re-establish annotation sorthood and value well-formedness from exact bytes.
- Blocking prerequisites: Primary counting requires separately established normative authority.; A successor must rebind exact artifacts under the M10 evidence contract.

### EXPR.APP.FUNCTION_TYPE

- Tier: 1
- Construction: Apply a closed well-typed non-function term to a closed argument.
- Positive control: Replace the function term with a compatible lambda or named function.
- Competing obligations: Prove function and argument subexpressions are individually well formed before shape checking.
- Blocking prerequisites: Primary counting requires separately established normative authority.

### EXPR.APP.ARGUMENT_TYPE_MATCH

- Tier: 1
- Construction: Apply a valid function to a closed well-typed argument of the wrong type.
- Positive control: Replace only the argument with a term of the expected domain type.
- Competing obligations: Prove function Pi shape and argument well-formedness before checking domain equality.
- Blocking prerequisites: Primary counting requires separately established normative authority.

## Future Isolated-Negative Coverage Contract

Semantic obligation: `Reach(x) AND NOT P(x)`.

A future primary case requires:

- content-bound negative artifact
- evidence-backed Reach(x) applicability and prerequisites
- evidence that NOT P(x) holds
- matched positive control
- complete competing-obligation analysis
- authority-scoped expected normative rejection
- per-checker rejection attribution where obtainable

Competing obligations must each be `SATISFIED` or `NOT_APPLICABLE`; any `UNRESOLVED` item blocks isolated coverage. Rejection alone proves neither the target violation nor isolation.

## Checker Attribution

Each observation binds artifact bytes, observer profile, configuration, pipeline stage, normalized outcome, and raw result. Pipeline stages are kept distinct: EXPORT, TRANSPORT, PARSE, RECONSTRUCTION, VALIDATION, POLICY.

Cross-checker agreement is not authority and is not an isolation oracle.

## Synthesis Hierarchy

1. `DETERMINISTIC_PREMISE_SPECIFIC_TEMPLATES`
2. `STRUCTURE_PRESERVING_TRANSFORMATIONS_OF_KNOWN_VALID_ARTIFACTS`
3. `CONSTRAINT_DRIVEN_REACH_AND_NOT_P_CONSTRUCTORS`

## Successor Execution Gates

- `GATE.M10.01` — A separately authorized successor plan binds the immutable M10 historical attestation.
- `GATE.M10.02` — The successor freezes a new immutable study-input snapshot before running any checker.
- `GATE.M10.03` — The unchanged M10 eligibility algorithm is re-applied to the successor input snapshot.
- `GATE.M10.04` — The resulting primary denominator and exploratory set are frozen before execution.
- `GATE.M10.05` — Every primary member has ESTABLISHED authority from a separately governed process.
- `GATE.M10.06` — Every planned case has a content-binding and matched positive-control construction plan.
- `GATE.M10.07` — Competing-obligation analysis is complete or the case is barred from isolated coverage.
- `GATE.M10.08` — Observer profiles, configurations, pipeline stages, and raw-result bindings are fixed.
- `GATE.M10.09` — Campaign budgets, interruption recording, and resumable evidence paths are durably specified.
- `GATE.M10.10` — Normative and exploratory results have separate reports, labels, and percentage calculations.

A successor must bind the immutable M10 attestation, freeze a new input snapshot, reapply the unchanged algorithm, and freeze the resulting denominator before substantive execution.

## M10 Prohibitions and Nonclaims

- `NEW_ARENA_TEST_CAMPAIGN`
- `NEW_CHECKER_COMPARISON_CAMPAIGN`
- `MUTATION_CAMPAIGN`
- `GENERATED_LEAN_WITNESS_CAMPAIGN`
- `BROAD_WITNESS_SYNTHESIS`
- `NEW_SEMANTIC_CROSS_VALIDATION`
- `AUTHORITY_SOURCE_APPROVAL`
- `AUTHORITY_PROMOTION`
- `DENOMINATOR_CRITERION_WEAKENING`

- M10 does not execute Arena, mutation, synthesis, or checker-comparison campaigns.
- M10 does not establish any normative authority or approve any authority source.
- Readiness feasibility judgments are protocol-design inputs, not semantic evidence or coverage results.
- The provisional exploratory set is not a normative denominator and yields no normative percentage.
- The empty primary denominator is a valid characterization of the immutable M9 input.
- Observer agreement, rejection, or disagreement does not establish normativity or isolation.
- No soundness relevance is inferred or assessed by this study design.
