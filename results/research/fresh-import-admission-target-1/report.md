# Fresh imported-expression admission target — 2026-11-09

**What did we find?** Current source paths check the result of a dependent
function (Pi) is a type before an ordinary definition's final type comparison.
The inspected local and public cases include valid Pi expressions and other
malformed imports, but no paired raw-import rejection for a well-typed term
used as a Pi result in both the declared-type and value positions. No checker
case ran in this intake, so actual behavior on that pair remains unknown.

**Is it interesting?** Yes, as a small prospective screen. The proposed bad
result is itself well typed, but its type is a function type rather than a
universe sort. Reducing or comparing surrounding expressions cannot establish
the missing Pi-formation premise. One unexpected checked-definition acceptance
would be a candidate defect; expected rejections would only characterize this
sample, not prove either checker correct.

**Does it require more work?** Select the separate four-input E0 screen under
[`E0_PI_CODOMAIN_ADMISSION_SCREEN_1_PLAN.md`](../../../docs/research/E0_PI_CODOMAIN_ADMISSION_SCREEN_1_PLAN.md).
Before launching it, bind exact executable and importer revisions, generate and
independently audit the raw trees, and register its trial. This source-only item
is complete; the screen is the next separate queue item and remains unstarted.

## Source and corpus map

Source tips were read through the GitHub connector on 2026-11-09:
official Lean `bb1f614e408dc4503653bebcbbafaa2240c4b61e`, Nanoda
`0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`, and Lean Kernel Arena
`d81f404fea341e1863dee80a92f752950943b1e3`. These are source identities,
not executable bindings. The earlier E0 runtime remains Lean 4.34.1 and Nanoda
`3a240721`; no observation from those binaries is silently attributed to the
current tips.

| Path | Checked-import behavior relevant to selection |
| --- | --- |
| [Lean `environment.cpp`, ordinary definition admission](https://github.com/leanprover/lean4/blob/bb1f614e408dc4503653bebcbbafaa2240c4b61e/src/kernel/environment.cpp#L121-L184) | `check_constant_val` checks the declared type and ensures a sort; `add_definition` checks the value and compares its inferred type with the declared type afterward. |
| [Lean `type_checker.cpp`, `infer_pi`](https://github.com/leanprover/lean4/blob/bb1f614e408dc4503653bebcbbafaa2240c4b61e/src/kernel/type_checker.cpp#L144-L165) | Infers each domain and the final codomain, requiring both to infer sorts before returning the Pi's sort. |
| [Nanoda `tc.rs`, ordinary `check_declar` and header check](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L82-L101) | Checks the declared type, then infers a definition's value with `Check`, then asserts definitional equality. [`check_declar_info`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L199-L214) requires the declared type to infer a sort. |
| [Nanoda `tc.rs`, `infer_pi`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L655-L674) | Calls `infer_sort_of` on domains and instantiated codomain before constructing the Pi sort. |

The [earlier expression screen](../../../explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1/summary.md)
tested an ill-typed, ignored *application argument* in three positions and
closed NO_SIGNAL in 12 cells. The [symbolic-universe rejection cases](../../../explorations/runs/EXPLORE-SYMBOLIC-UNIVERSE-REJECTION-1/cases.json)
include a valid Pi value and a changed declared universe level, not a non-type
Pi codomain. The [M10 study](../../../docs/research/DECLARATION_VALIDATION_MILESTONE_10_STUDY.md)
describes the codomain premise analytically but does not supply this new raw
two-checker observation or normative authority for it. Arena's
[`pi-closure-context` case](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tests/bugs/pi-closure-context.yaml)
targets a value/type comparison bug with *well-formed* function types; its
[`constlevels` case](https://github.com/leanprover/lean-kernel-arena/blob/d81f404fea341e1863dee80a92f752950943b1e3/tests/bugs/constlevels.yaml)
already exercises malformed constant-level arity. Search of the retained local
E0 summaries and the named Arena tests found no equivalent codomain-sort pair;
this is a bounded corpus review, not an exhaustive negative claim.

## Candidate comparison

| Boundary | Reachability and independent expectation | Coverage and cost | Decision |
| --- | --- | --- | --- |
| Pi codomain must infer a sort | Raw `forallE` and `lam` are supported by the existing 3.1.0 input encoder. A closed lambda `F = fun (_ : Sort 1) => Sort 0` has a Pi type, not a sort; `forall (_ : Sort 1), F` is therefore ill formed. The two ordinary-definition placements each reach checked inference before final comparison. | Valid Pi and related malformed cases exist, but no matching raw negative/control pair was located. Four sort-only inputs, no axioms, constants, recursors or imported prelude. | **Select** for separate E0. |
| Constant universe-argument arity | A polymorphic constant referenced with a missing level argument has a clear independent rejection condition. [Lean `infer_constant`](https://github.com/leanprover/lean4/blob/bb1f614e408dc4503653bebcbbafaa2240c4b61e/src/kernel/type_checker.cpp#L101-L122) checks arity; [Nanoda `infer_const`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L221-L235) substitutes declaration levels. | Arena already has a directly relevant `constlevels` regression. It also requires a preceding polymorphic declaration and disambiguation from parameter ownership. | Do not repeat as the fresh target. |
| Let annotation/value agreement | Both [`infer_let` paths](https://github.com/leanprover/lean4/blob/bb1f614e408dc4503653bebcbbafaa2240c4b61e/src/kernel/type_checker.cpp#L208-L228) check annotation sort and value compatibility in checked mode. | Extensive [prior let contract](../semantic-let-contract-1/clarification-packet.md), [cache regression](../survivor-cache-1/report.md) and Arena let work already cover this neighborhood. | Do not duplicate. |

The proposed Pi screen changes one codomain node in each pair. It will test
acceptance or rejection at ordinary checked admission, not infer general
soundness from checker agreement. No generated input, checker process,
mutant, external action, frozen artifact edit or milestone advance occurred
under this intake. Machine usage for this source-only review is not a
meaningful checker cost; model/token usage is unavailable.
