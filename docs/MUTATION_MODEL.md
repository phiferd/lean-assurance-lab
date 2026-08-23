# Mutation Model

## Initial Target

The first checker target is `nanoda`, because it is an independent Rust
implementation and small enough for controlled mutation experiments.

This can change if local investigation shows another Arena checker has a simpler
build path or cleaner mutation surface.

## Mutation Operators

Initial source-level operators:

```text
BOOL_NEGATE
REL_LT_TO_LE
REL_LE_TO_LT
REL_EQ_TO_NE
REL_NE_TO_EQ
RETURN_EARLY_ACCEPT
RETURN_EARLY_REJECT
SKIP_VALIDATION
REMOVE_MATCH_ARM
CHANGE_REDUCTION_CONDITION
WEAKEN_UNIVERSE_CHECK
WEAKEN_INDEX_BOUNDS_CHECK
WEAKEN_SUBSTITUTION_OR_LIFTING
WEAKEN_DECLARATION_VALIDATION
```

The first batch should be manually reviewed and intentionally small. Prefer
mutations in code paths tied to kernel semantics rather than parser plumbing or
performance-only paths.

## Manual Mutant Registry

Before introducing a bulk mutation framework, every controlled mutant is
registered in `results/mutants/registry.jsonl`. A record has this shape:

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
