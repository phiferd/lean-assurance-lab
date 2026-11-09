# Checked comparison reachability audit — 2026-11-09

**What did we find?** In the inspected ordinary axiom, definition, theorem and
opaque admission paths, Lean and Nanoda check the declared type before using it
in a semantic comparison. For value-bearing declarations, they recursively
check the value before comparing its inferred type with that declared type.
The two fresh candidate constructions below encounter explicit checks before
that final comparison. No current checker cell ran, so their actual rejection
stage and any defect outside these paths remain unknown.

**Is it interesting?** Unclear for defect discovery. The map locates the
infer-only and reduction shortcuts, but neither inspected candidate exposes a
source-supported route for a malformed imported operand to bypass checked
inference. The lambda-binder neighborhood also has direct retained public-entry
probes. This is a source observation, not a proof of checker correctness.

**Does it require more work?** No new E0 screen follows from this audit. A
future screen needs a concrete route that survives the checks mapped here,
with a distinct oracle and a verified raw-import control. The separate project
queue still has unresolved work; its handoff is recorded in the canonical
queue and Active status.

## Exact sources and entry routes

Read through the GitHub connector on 2026-11-09. These are source identities,
not the executable identities used in earlier E0 runs.

| Source | Commit and Git blob |
| --- | --- |
| [Official Lean `src/Lean/Environment.lean`](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/Lean/Environment.lean#L855-L883) | `e5723d5b311aa9151b38e2baaa59f08f004a19e9`; `297985fbec34c08a4f5536a0a0bddf3c65b026ef` |
| [Official Lean `src/kernel/environment.cpp`](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/environment.cpp#L126-L221) | same commit; `f5dd8c2a6df80cfb587595c1d8f3935e3bb123b9` |
| [Official Lean `src/kernel/type_checker.cpp`](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L101-L377) | same commit; `4112234df96e79e3d131796d2c3afa67c5c71211` |
| [Nanoda `src/parser.rs`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/parser.rs#L384-L452) | `0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`; `7fef4c4c1f82d00f95f168dee8b722a189453294` |
| [Nanoda `src/tc.rs`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L80-L224) | same commit; `d1a9f94274ed22f63ed7e2d63348269c18d2eca3` |
| [Arena `tutorial/Tutorial.lean`](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tutorial/Tutorial.lean#L64-L80) | `d81f404fea341e1863dee80a92f752950943b1e3`; `2d6f3ddd803d7903f3b8d3ee6516a9137044c158` |

Lean's `addDeclCore` takes an already constructed `Declaration`; its default
`doCheck := true` routes through `addDeclCheck` to kernel admission. It is not
an NDJSON parser. The prior [raw Pi E0 input review](../../../explorations/runs/EXPLORE-PI-CODOMAIN-ADMISSION-1/input-review.md)
bound a separate Lean importer and verified parsed constructors for that older
execution, but supplies no current runtime observation for the cases below.
Nanoda's parser reads records into a declaration map; its axiom, safe
definition, theorem and opaque record arms are at
[`parser.rs:825-870`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/parser.rs#L825-L870).
The serial and worker paths both call `check_declar` at
[`tc.rs:141-169`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L141-L169).
Nanoda's parser rejects unsafe definitions and unsafe opaque records before
this map; Lean's unsafe definition branch checks the header in the old
environment, then checks its value in an extended environment. This asymmetry
is outside a matched safe ordinary-import screen.

## Source-to-operand matrix

“Checked” means the implementation's recursive check mode, not independent
semantic authority. Inferred types are not separately rechecked at every
comparison; their well-formedness relies on successful checked inference and
the already admitted environment. Every malformed reachability statement below
is conditional on those source-level invariants.

| Reachable comparison or test | Operand origins | Earlier typing or formation premise; shortcut | Malformed imported reachability in this path |
| --- | --- | --- | --- |
| Lean axiom admission; Nanoda axiom admission | No value/type equality. Imported declared type is the only expression. | Lean `check_constant_val` calls `checker.check(type, lparams)` and requires a sort; Nanoda `check_declar_info` uses `infer(type, Check)` then `ensure_sort`. | A malformed type reaches the checker, not a declaration equality comparison. |
| Lean safe definition, theorem, opaque final `is_def_eq`; Nanoda definition, theorem, opaque final `assert_def_eq` | Left: type returned by checked inference of imported value. Right: imported declared type. | Lean checks header with `check_constant_val`, then value with `checker.check`; Nanoda checks header, then `infer(value, Check)`. Their final equality implementations may use infer-only and reduction internally, after those calls return. | A malformed header or value should fail before final equality; a source-level bypass was not found. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/environment.cpp#L159-L221), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L82-L93). |
| Lean theorem `is_prop`; Nanoda theorem zero-sort test | Imported theorem type and its inferred sort. | Same checked header precedes the test. Lean `is_prop` reinfers with infer-only and normalizes its sort level; Nanoda tests the level returned by checked `infer`/`ensure_sort`. | An ill-formed theorem type should fail in header checking; a well-formed non-Prop type reaches this test and is directly covered publicly. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/environment.cpp#L191-L205), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L200-L223). |
| Lean checked application `is_def_eq(arg_type, domain)`; Nanoda checked application `assert_def_eq(domain, arg_type)` | Inferred type of imported argument; domain of the checked function's Pi type, instantiated with prior checked arguments. | Both check the function/head and current argument first. Lean's infer-only application branch skips argument checks, but the checked branch does not. Nanoda's infer-only branch likewise skips the argument comparison. | A malformed argument reaches inference but should not reach a successful enclosing value check. The ignored-argument E0 already sampled this. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L173-L205), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L593-L630). |
| Lean checked let `is_def_eq(value_type, annotation)`; Nanoda checked let `assert_def_eq(value_type, annotation)` | Checked-inferred type of local value; imported let annotation. | Both first require the annotation to infer a sort and check the value. Infer-only skips the local comparison. | A malformed let reaches this local check, not the final declaration equality. This family has extensive prior work. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L208-L229), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L709-L724). |
| Projection proposition tests inside checked inference | Inferred type of imported projected structure; constructor fields from the admitted environment. | Lean and Nanoda first infer the structure with the caller's Check flag, then reduce its type and inspect constructor shape. Their proposition helpers can use infer-only on already derived types. | An imported malformed structure is checked before the proposition test. Projection-from-Prop has direct existing coverage; no new ordinary comparison bypass identified. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L240-L284), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L491-L544). |
| Equality-internal proof irrelevance, structure eta, unit-like and eta helpers | Subexpressions of the preceding equality operands, or expressions derived by reduction/projection from them. | Lean's `infer_type` is infer-only in proof irrelevance/eta/unit-like helpers; Nanoda uses `InferOnly` in proof irrelevance, eta and unit-like helpers. These are reachable inside final or local equality, but not standalone admission entry points. | This audit found no unguarded imported operand at their entry in the ordinary checked path. It does not prove all reductions preserve typing, or cover recursor faults/Lean eta alias. [Lean](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L829-L913), [Nanoda](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L319-L379). |

The explicit formation calls relevant to the fresh candidates are Lean
`infer_lambda` domain `ensure_sort` and `infer_app` function `ensure_pi`, and
Nanoda `infer_lambda` domain `infer_sort_of` and `infer_app` `ensure_pi`.
[Lean's checked `infer_pi`](https://github.com/leanprover/lean4/blob/e5723d5b311aa9151b38e2baaa59f08f004a19e9/src/kernel/type_checker.cpp#L144-L165)
also checks each domain and codomain sort, matching the completed Pi screen.

## Fresh candidate comparison and public overlap

These are source-derived *paper constructions*. `S0 = Sort 0`, `S1 = Sort 1`,
`S2 = Sort 2`, and `F = fun (_ : S1) => S0`. They are not retained raw exports,
parsed-tree audits, or checker outcomes. Both use only sort, lambda, Pi and
application constructors supported by the prior raw 3.1.0 encoder. A separate
E0 would still need new exact bytes and importer verification.

| Candidate and independent expectation | Valid control and single-fault negative | Coverage and cost | Decision |
| --- | --- | --- | --- |
| **Application head must have function type.** `S0` has type `S1`, not a Pi type; applying `S0` is invalid even with a well-typed argument. | Control `d : S1 := (F S0)`; negative `d : S1 := (S0 S0)`. The negative replaces the function head only. | Two raw declarations per checker, no named dependency. A bounded search of current Arena tutorial and bug text found no exact non-function-head pair, but source has an explicit `ensure_pi` immediately after checked function inference in both implementations. This is a weak defect hypothesis, not a demonstrated uncovered gap. | Do not select E0 on this source evidence alone. |
| **Lambda binder annotation must be a type.** `F` has a Pi type, not a sort, so `fun (_ : F) => S0` is ill formed. | Control `d : (forall (_ : S1), S1) := fun (_ : S1) => S0`; negative keeps the declared type and replaces the lambda domain with `F`. Later type mismatch is derivative; the binder check is first. | Two raw declarations per checker, no named dependency. The [retained binder-sort survivor study](../../../docs/RESEARCH_STATUS.md#L2245) already reports source-derived malformed probes rejected by baseline and guard-skipping Nanoda builds at the public declaration entry point, so this is close overlap, not fresh public evidence. | Do not duplicate. |
| **Theorem type must be a proposition.** A well-typed non-Prop type can reach the kind test only after checked header inference. | Definition-form accept companion for a theorem with `type := S1`, `value := S0`; theorem must reject. | [Arena `nonPropThm`](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tutorial/Tutorial.lean#L64-L80) and the retained [core declaration typing matrix](../../../docs/RESEARCH_STATUS.md#L2258) directly cover this requirement. | Do not duplicate. |

The local and public searches above are bounded, not exhaustive. Existing
[`pi-closure-context`](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tests/bugs/pi-closure-context.yaml)
targets a different closure comparison; [`constlevels`](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tests/bugs/constlevels.yaml)
directly covers constant universe arity. The completed
[ignored-argument](../../../explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1/summary.md)
and [Pi-codomain](../../../explorations/runs/EXPLORE-PI-CODOMAIN-ADMISSION-1/summary.md)
E0 samples reported NO_SIGNAL. The Lean eta alias and historical recursor
questions were not replayed here. No current executable was built or run, no
checker result is inferred from agreement, and no external project was edited.
Model/token usage for this source review is unavailable.
