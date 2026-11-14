# Semantic-boundary source selection — 2026-11-14

**What did we find?** Neither inspected mechanism justifies a new experiment.
Nanoda's current recursor path checks each imported rule value, reconstructs the
recursor from the inductive declaration, aligns universe parameters, and compares
the imported rule and execution metadata with the reconstruction before reduction
uses the imported rule. One narrow premise is not directly checked: universe
parameters occurring only in a rule value are not proven to belong to the
recursor's declared universe vector. No distinct downstream effect was found.
The inspected cache path is a real historical ocaml4lean defect, but its exact
witness is already an Arena regression and the affected optimization was fully
reverted. No checker was built or run, so behavior outside these pinned paths
remains unknown and no previously unknown defect was found.

**Is it interesting?** Yes. The comparison identifies the actual invariants,
rather than treating a representation difference or missing cache-key field as
a defect by itself. It also prevents two low-information executions: replaying
published recursor forgeries on a repaired path, and reproducing a publicly
reported cache failure on code that is no longer current.

**Does it require more work?** No result-driven experiment follows. Reconsider
the recursor path only if the residual rule-universe closure gap produces a
concrete rule whose extra level survives substitution, passes reconstruction
comparison and changes a later typing or reduction judgment. Reconsider caching
only when a current implementation reuses a judgment across a live context
dependency without typed locals, scope separation or invalidation. The next
separate queue item is `ASSURANCE-CLAIM-DISPOSITION-1`; this report does not
start it. The missing historical recursor audit and merged-Lean replay remain
unchanged.

## Bound scope

The exact revisions, Git blobs and public exposure are frozen in the
[source inventory](source-inventory.json). The comparison covers Nanoda
`0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`, ocaml4lean PR #7 at
`bd0f7797052760aa9705bc863aa1072732115b63` and its current revert at
`8ef7ebc0f65fc396486e1b45c269e05038be51b5`, and Arena current
`6de4317e0e4c7c34d4c474fda1628a8dc64b34ee`. Published witnesses were read as
coverage evidence, not executed as fresh cases.

## Dispositions

| Mechanism | Reachable causal path and semantic basis | Control and coverage | Disposition |
| --- | --- | --- | --- |
| Recursor validation versus execution | Nanoda parses imported rule bodies, owners and field counts. It checks every imported rule value, derives recursors from checked inductive/constructor data, and compares imported and reconstructed types/rules after universe alignment. Reduction later retrieves the imported recursor and substitutes application levels into that same rule. The semantic obligation is that the executed computation rule is the rule derived from the admitted inductive declaration. | A same-source export with the honest recursor is the valid accept control. Arena #350 retains forged ordinary rule, nested auxiliary rule, recursor-type and wrong-argument rejects; Nanoda #84 is the repair source. | **Do not select.** The published consequential families have the needed validation-to-execution edges and direct regressions. The rule-only universe-closure omission lacks a distinct consumed consequence, so a run now would be another nearby expected-rejection screen. |
| Context-dependent cache reuse | In ocaml4lean PR #7, identical de Bruijn applications are one hash-consed node. Open-term inference resolves bound variables through the binder-domain vector but caches the inferred type by only `(expression node, binder depth)`. The memo survives sibling lambdas, so `f #0` first under `x : A` can store `A`, then hit at the same depth under `y : B`, skipping the required `B ≡ A` check. | A valid shared-DAG control uses the same binder type on both sibling paths. Arena #345 is the exact changed-binder witness and records the affected PR acceptance. PR #7 was merged and then reverted in full. | **Do not select.** This is a known, exposed defect in reverted code with an exact retained regression. A fresh experiment first needs a different current reachable cache path and a distinct omitted dependency. |

## Recursor trace: checked value to consumed value

Nanoda's parser retains the imported recursor type, universe parameters, rule
value, constructor owner and field count in
[`parser.rs:920-945`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/parser.rs#L920-L945).
`RecursorData::aux_data_ck` binds the recursor's parameter/index/motive/minor
counts, `is_k`, name and inductive ownership in
[`env.rs:137-164`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/env.rs#L137-L164).

The current validation path has three relevant edges:

1. After checking the inductive header, specifications and constructors,
   `check_inductive_declar` calls checked inference on every imported rule value,
   then derives fresh recursors from the admitted specifications. See
   [`inductive.rs:68-146`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/inductive.rs#L68-L146).
2. For an ordinary block, Nanoda checks auxiliary metadata, substitutes the
   imported type and reconstructed rule values to a common universe-parameter
   sequence, compares the types/rules, and requires the same constructor and
   field count. See
   [`inductive.rs:1321-1357`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/inductive.rs#L1321-L1357).
3. For nested inductives, restoration rewrites specialized names and parameter
   locals. Comparison then requires equal universe-vector arity, aligns imported
   type/rules by universe position, and checks constructor ownership and field
   counts before definitional equality. See
   [`inductive.rs:1634-1744`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/inductive.rs#L1634-L1744).

The reconstructed rule is validation evidence; the persistent environment
retains the imported rule as the consumer representation. `reduce_rec` retrieves
that recursor, selects the imported rule by the major constructor, uses its
validated field count to split arguments, substitutes application universe
levels into its rule value, and applies it. See
[`tc.rs:1108-1139`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs#L1108-L1139).

The blocking invariant is not byte identity: the *checked imported rule that
reduction consumes* must be well typed and must match the independently derived
rule after the same universe alignment, with constructor and field-count
metadata equal. Given rule-universe closure, substitution congruence carries
that equality to the application levels used by reduction.

There is a bounded missing invariant. Direct rule checking uses a type checker
with no enclosing `DeclarInfo`; universe-membership checks in `infer_const` and
`infer_sort` run only when that declaration context is present. Thus source does
not directly enforce
`universes(RecRule.val) ⊆ recursor.info.uparams`. Recursor-type closure is
checked, and reconstruction comparison rejects consequential rule differences
unless equality hides the extra level. The review found no distinct rule whose
extra universe both survives the later substitution and changes a consumed
judgment. This is a source premise gap, not yet a discriminating experiment or
a global safety claim.

## Cache trace: judgment, key, context and lifetime

The affected PR's expression representation erases binder names and hash-conses
structurally equal applications. Its open-term path stores an inferred `Expr.t`
type under a key consisting of the shared expression node and current binder
depth. Bound-variable lookup, however, reads the ordered binder-domain vector.
The key therefore omits a dependency that determines the bound variable's type.

In PR #7,
[`tc.ml:225-287`](https://github.com/yoonwoojeong/ocaml4lean/blob/bd0f7797052760aa9705bc863aa1072732115b63/src/tc.ml#L225-L287)
sets up the domain-local memo and performs the `(node, depth)` lookup;
[`tc.ml:289-376`](https://github.com/yoonwoojeong/ocaml4lean/blob/bd0f7797052760aa9705bc863aa1072732115b63/src/tc.ml#L289-L376)
pushes binder domains and can reuse the cached application type; and
[`tc.ml:387-400`](https://github.com/yoonwoojeong/ocaml4lean/blob/bd0f7797052760aa9705bc863aa1072732115b63/src/tc.ml#L387-L400)
clears the memo only at the outer traversal boundary. Per-context pool clearing
prevents cross-declaration staleness, but not the sibling collision inside one
traversal.

Arena #345 deliberately shares `f #0` under `x : A` and `y : B`, exactly the
dependency the key omits. The retained source is
[`open-term-cache-context.lean`](https://github.com/leanprover/lean-kernel-arena/blob/6de4317e0e4c7c34d4c474fda1628a8dc64b34ee/tests/bugs/open-term-cache-context.lean)
and its expected reject contract is
[`open-term-cache-context.yaml`](https://github.com/leanprover/lean-kernel-arena/blob/6de4317e0e4c7c34d4c474fda1628a8dc64b34ee/tests/bugs/open-term-cache-context.yaml).
Current ocaml4lean `main` is the full PR #8 revert; the open-term memo is absent.
Its standard lambda path instantiates bodies with fresh typed locals before
ordinary checked application inference, so differing binder types produce
different typed expressions rather than one context-free cache key.

The missing invariant in the affected revision was: reuse a cached typing
judgment only when every local-context dependency is equal, represented in the
term, included in the key, or made irrelevant by scope. The current inspected
path blocks the defect by removing the optimization and using typed locals. This
does not show that every current cache is context independent.

## Selection and research value

No new semantic experiment is selected. The comparison resolved which exact
edges matter and changed the execution decision from “possibly screen one” to
“run neither inspected candidate.” The inventory and traces are reusable when
reviewing a future recursor consumer or context-sensitive cache optimization;
their identifiable consumer is future experiment selection, not a package or
checker matrix. More work on these exact published paths would add little
material information. A different current source path that lacks one named
invariant would be new evidence and should receive its own plan, independent
expectation, valid control and prospective registration.
