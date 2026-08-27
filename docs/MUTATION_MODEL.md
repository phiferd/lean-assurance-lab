# Mutation Model

## Initial Target

The first checker target is `nanoda`, because it is an independent Rust
implementation and small enough for controlled mutation experiments.

This can change if local investigation shows another Arena checker has a simpler
build path or cleaner mutation surface.

## Mutation Catalog

`mutation-model/catalog.json` is the machine-readable catalog. Its schema is
`schemas/mutation-catalog.schema.json`. It binds the four manual mutation specs
by content digest and defines the minimum sample size used for stratified
metrics.

The active syntax-aware operator families are:

```text
validation-elision
  SKIP_VALIDATION
predicate-negation
  BOOL_NEGATE
relational-boundary
  REL_LT_TO_LE, REL_LE_TO_LT, REL_GT_TO_GE, REL_GE_TO_GT
equality-discrimination
  REL_EQ_TO_NE, REL_NE_TO_EQ
binder-depth-adjustment
  BINDER_DEPTH_INCREMENT_ELIDE, BINDER_DEPTH_INCREMENT_ZERO
```

These operators model omitted checks, inverted guards, endpoint errors,
confusion between equality and inequality, and failure to increase de Bruijn
depth when traversal enters a binder. They are emitted only inside modeled
semantic functions and mapped to an explicit subsystem. Parser, diagnostic,
test, formatting, and infrastructure paths are rejected by policy. The catalog
is intentionally narrower than the list of all source edits one could
mechanically perform.

## Mutant Registry

Every controlled or generated mutant is registered in
`results/mutants/registry.jsonl`. A record has this shape:

```json
{
  "id": "nanoda-0001",
  "checker": "nanoda",
  "source_file": "path/in/checker",
  "source_span": "line-or-range",
  "mutation_operator": "WEAKEN_UNIVERSE_CHECK",
  "subsystem": "universes",
  "status": "REGISTERED",
  "classification": "UNKNOWN_EQUIVALENCE",
  "notes": ""
}
```

The registry is append-only during exploratory work. If a mutant is superseded,
append a later record with the same `id` and a newer `status` rather than
rewriting historical entries.

Automated specs add `replace_occurrence`, generator provenance, and deterministic
IDs derived from source path, line, column, operator, original syntax, and
mutated syntax. The generator parses Rust with `syn`; it does not discover sites
through text or regular-expression matching. `scripts/generate-mutations
--refresh` reproduces an existing bounded population and refuses to reuse build
or execution evidence if the deterministic identities differ.

## Subsystem Labels

```text
universes
definitional-equality
expression-reduction
inductive-declarations
constructors
recursors
quotients
substitution-lifting
bound-variables
proof-irrelevance
declaration-validation
builtin-native-reductions
serialized-input-validation
unknown
```

## Result Categories

Every discovered mutation candidate has one durable attempt status:

```text
COMPILING_SEMANTIC_MUTANT
BUILD_FAILURE
DUPLICATE
UNSUPPORTED_MUTATION_SITE
REJECTED_NON_SEMANTIC
```

The batch manifest retains rejected and unsupported candidates rather than
reporting only successful builds. `BUILD_FAILURE` is separate from checker
outcomes and survivor classification.

### Killed

At least one corpus test produces a different normalized outcome between the
baseline checker and mutant.

### Survived

All corpus tests produce the same normalized outcome.

### Equivalent

The mutation does not change observable checker semantics. This must not count
as a corpus weakness.

### Unknown Equivalence

Equivalence is not proven or strongly justified. These mutants remain outside
the meaningful-survivor count until classified.

### Meaningful Semantic Survivor

The mutation plausibly changes accepted or rejected proof artifacts, but the
current corpus does not expose the difference.

This category drives witness generation.

### Reference Aligned

The mutant differs from baseline on an exact artifact, a designated compatible
reference establishes the expected outcome, and the mutant matches that outcome
while baseline does not. This is evidence of a baseline over-rejection or other
reference disagreement, not evidence that the corpus failed to kill an incorrect
mutant. `REFERENCE_ALIGNED` mutants remain reported but are excluded from both
mutation-score denominators.

### Survived Without Witness

Every selected covering test matched baseline, but no distinguishing witness is
currently attached. This is an unresolved semantic state, not evidence of
equivalence, and it remains eligible for later witness search.

## Soundness and Completeness Direction

For a distinguishing test:

```text
baseline: REJECT
mutant:   ACCEPT
```

is a potential soundness weakening.

```text
baseline: ACCEPT
mutant:   REJECT
```

is a completeness or over-rejection difference.

Both are retained.

## Initial Batch Policy

The first automated batch should be modest and biased toward semantically
meaningful checks:

```text
target_count: 10-25 compiling mutants
excluded_by_default:
  - formatting-only source changes
  - parser-only error paths
  - obvious logging or diagnostic changes
  - performance-only cache changes
  - mutations that do not alter the built artifact
required_metadata:
  - source location
  - operator
  - subsystem
  - build status
  - baseline outcome file
  - mutant outcome file
  - comparison report
```

Selection is deterministic, ordered by estimated covering-test runtime, and
round-robin by operator family. A batch is capped at 25 selected mutants.
When a modeled source location has no line-coverage inputs, generation retains
the candidate with a full-corpus cost estimate and scheduled execution falls
back to every baseline test. Zero selected inputs are never interpreted as a
surviving mutant. Explicitly dead debug/introspection entry points remain
outside the modeled semantic surface.
Mutation scores are reported by operator, operator family, and subsystem. A
stratum with fewer than three evaluated mutants is labeled
`INSUFFICIENT_SAMPLE` and has no score, while its raw killed/survived counts
remain visible.

The report preserves two explicitly scoped aggregate views. `mutation_score`
uses only mutants classified `MEANINGFUL_SEMANTIC`, matching the original
conservative policy. `modeled_mutation_score` includes every evaluated mutant
accepted by the semantic model until later evidence classifies it equivalent,
unreachable, performance-only, or non-semantic. Stratified scores use this
modeled-population scope so unresolved survivors remain visible in the
denominator.
