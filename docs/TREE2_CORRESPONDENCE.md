# What a nested tree means to two positivity models

A checked theorem now relates the constructor shapes used by two different
representations of a restricted nested datatype. That is useful because an
agreement about constructor structure can expose an error that another accepted
example would miss. It is not yet an agreement about values or computation.
The current continuation asks whether the native checker returns the same
structure it is subsequently supposed to use for recursors.

This is local AI-authored research for human review. The existing proof archive
is published; the continuation and this overview await separate publication
approval. There is no unsupported claim that this theorem is novel research or
that Lean's production kernel has been verified.

## A small example

Imagine trees with labels at leaves and a list of groups of children at a node:

```text
leaf "a"
node [ [leaf "a", leaf "b"], [], [leaf "c"] ]
```

The empty group is significant; this is a list of lists, not a flattened list.
In Lean-like notation the constructors are `leaf : alpha → Tree2 alpha` and
`node : List (List (Tree2 alpha)) → Tree2 alpha`.

One representation keeps List as a previously declared datatype and recursively
walks its constructor schema at each particular instantiation. The other
replaces the two nested List applications with freshly allocated auxiliary
types. Giving those auxiliary types descriptive names produces three mutually
recursive sorts:

| Sort | Constructors |
| --- | --- |
| Tree | `leaf alpha`, `node Rows` |
| Rows | `nilRows`, `consRows Children Rows` |
| Children | `nilChildren`, `consChildren Tree Children` |

The example's groups become a Rows chain of three Children chains; the middle
Children chain is empty. Merely noticing six constructors is insufficient:
the outer `cons` must refer to Children and Rows, while the inner `cons` must
refer to Tree and Children. Swapping these references changes the datatype.

In the checked symbolic family, N is the number of List layers. Tree2 is N=2.
The independently specified signature is
`T_N = alpha + R_N`, `R_0 = T_N`, and
`R_j = 1 + R_(j-1) × R_j` for positive j. Here `+` separates constructor
alternatives, `1` means an empty constructor and `×` means two fields. This is
a description of constructor rows; these equations are not themselves a proved
isomorphism of datatype carriers.

## What the existing theorem proves

The archived `Tree2TowerCorrespondence.representation_package` quantifies over
every natural depth N and every pure-Core fuel F with F ≥ N+5. It proves:

1. The pinned simplified official-model elimination returns the exact specified
   auxiliary declaration at queue fuel N+2.
2. A strengthened native positivity derivation is constructed at index N+1.
3. The actual native model's positivity walk succeeds.
4. The actual official output constructor expressions and native canonical
   constructor crests independently decode to the signature above.
5. Each actual auxiliary allocation corresponds to its particular native List
   frame, including its key and reused hole index.

The fuel bound is sufficient, not proved minimal. Acceptance and the native
positivity derivation are conclusions, not assumed premises. At N=0 there are
no List frames and the node field is the root member itself.

The native frame hole has raw index 2 in both the outer and inner List walks.
The proof interprets it relative to its actual frame key. Index 2 alone never
identifies Rows with Children. Abstraction takes place before parameter
substitution; otherwise the inner occurrence can be confused with outer self.

The exact source statement and seven file identities are retained in
[the source archive](../results/research/tree2-confirmed-integration-1/sources/)
and [source lock](../results/research/tree2-confirmed-integration-1/source-lock.json).
The [independent claim review](../results/research/tree2-confirmed-integration-1/independent-claim-review.md)
and [report](../results/research/tree2-confirmed-integration-1/report.md) state the
accepted scope. A fresh historical replay compiled 101 upstream modules and
seven proof modules. Its full historical closure remains bound to its original
frozen inputs; later documentation does not silently reattest that closure.

## Which implementation is connected?

The upstream revision is con-leche
`10fe085e21773ff0b62a6aacf6db29fccf849bae`; the seven proof modules are at local
source commit `e94d00b624951ccc0b4dd0a317eb5e952d948696`.
`ConLeche/Complete/OfficialNested.lean` is an Expr-based transcription of the
nested-elimination and positivity slices of Lean's C++ `inductive.cpp`, with
explicit simplifications. It is not the C++ kernel itself. The checked theorem
calls its `Official.elimNested` and calls native con-leche
`nestedBlockPositivity` with verified **pure** Core operations.

The transcription shares canonical parameter variables, supplies deterministic
fresh names, obtains constructor lists through the explicit lookup, counts
syntactic index telescopes and uses explicit fuel. It uses con-leche reduction
as its oracle. Whole constructor checking, universe/parameter validation and
other official validator stages are not included in that model.

The fixed environment contains explicit Tree/List declarations and constructor
records. List has one universe parameter, one type parameter and zero indices;
its monomorphic uses instantiate the universe to zero. Encoded Pi binder
metadata has `pw=never`. All needed finite Core typing/reduction facts are
proved for this environment, rather than assumed for arbitrary lookups.
Inferred sorts can contain `imax`; no unsupported syntactic replacement by
`Sort 1` is made.

## The current continuation: input shape versus returned output

The existing `nativeRows` function interprets **input constructor crests**.
Its success theorem says there exists a returned record, without identifying
all that record's fields. Native `NestCtorNf` records constructor name, levels,
parameters and read-back walked type. Recursor class selection reads those
records by constructor and instantiated class; the two List `cons` records
must therefore stay distinguishable even though they have the same name.

[The prospective pilot](research/TREE2_COMPUTATION_PILOT_1_PLAN.md) fixes N=2,
F=7 and asks for the actual complete returned observation and a connection to
the six lowered rows. Expected key order is inner List then outer List;
expected record order is leaf, outer nil, inner nil, inner cons, outer cons,
node. The full returned observation remains unproved. The smaller checked result below
relates supplied candidate telescopes to exact output expressions; it does not
assert that the full checker produced those telescopes or that record order.

Existing general recorded-constructor and recursor laws are reusable, but their
well-scoped environment, derivation and stage hypotheses must be discharged.
They are not automatically supplied by an existential successful walk.

## Trust and remaining gaps

The historical axiom reports list only Lean's standard `propext`,
`Classical.choice` and `Quot.sound`. There is no new axiom, `sorry`, `admit` or
`native_decide` in the seven final proof sources. Trust includes the Lean 4.33.0
kernel, official standard library and recorded imports; the model's own fidelity
to production code is a separate scientific question.

Nothing here yet proves that values round-trip between actual nested and
three-sorted datatypes, that folds commute with that conversion, that generated
recursors compute correctly, or that the compiled cached checker and C++ kernel
agree. It also does not cover arbitrary List/Option/Prod grammars, dependent
fields, indices or Prop. Existing nested examples and broader reduction tests
are acknowledged; another accepted example alone would add little value.

A later value theorem should preserve group boundaries and connect encoding,
decoding and the node fold equation `fold(node xss) = b(map(map fold) xss)`.
That equation is a goal, not a present result. Even proving it for independently
written datatypes would still require a connection to actual generated recursors.

## Reproduction and pilot outcome

The continuation has checked three finite lemmas in
[Tree2CtorReadback.lean](../explorations/runs/EXPLORE-TREE2-OBSERVATION-1/sources/Tree2CtorReadback.lean):

- `distinct_frame_images`: `nestHoleImg` reads raw variable 2 as `List Tree2`
  under the inner key and `List (List Tree2)` under the outer key; those
  expressions differ.
- `constructor_readbacks`: the real `nestCtorNf`, applied to six explicitly
  supplied telescope/result pairs at their exact frame depths and keys, gives
  the six independently specified records. This proves a readback equation,
  without assuming acceptance or a PosDR derivation.
- `readback_lowering`: reorder those types as leaf, node, outer nil, outer cons,
  inner nil, inner cons, then run real `Official.replaceAll` in the completed
  `target 2` allocation. The result is exactly all six constructor types from
  that target, and the allocation state is unchanged.

This is a useful intermediate result: it connects exact constructor expressions
through the frame-sensitive readback function and existing lowering code. It is
stronger than counting constructors or showing another accepted example. It
remains weaker than the original pilot goal: the full walk must still be shown
to generate those telescopes and append those records, together with its keys,
kinds and normals. No missing premise is disguised as an arbitrary environment
oracle. The immediate gap is composing the finite checker calls into an exact
returned-state equation; no mathematical counterexample has been observed.

A fresh affected-module replay succeeded in 1.309 seconds with sampled peak RSS
1.410 GB and cleanup complete. All 108 existing cached module hashes were
reverified, and dependency resolution selected the historical correspondence
artifact. They were reused read only, not recompiled in this continuation.
[The new axiom output](../explorations/runs/EXPLORE-TREE2-OBSERVATION-1/fresh-replay-2/compile-stdout.log)
contains only `propext`, `Classical.choice`, and `Quot.sound` for all three
lemmas. No `sorry`, `admit`, new axiom or `native_decide` appears in the accepted
new source. [Independent AI source review](../explorations/runs/EXPLORE-TREE2-OBSERVATION-1/independent-review.md)
accepted that restricted scope; it is not human expert endorsement.

The original trial is honestly `INCONCLUSIVE`, with its complete output goal
unresolved. The archive preserves 23 source compile revisions (554.832 seconds
in aggregate), including eight RSS safety interruptions and every rejected
elaboration. Failed attempts' automatic `sorryAx` reports are never counted as
proofs. Safety cleanup succeeded for all attempts. A failed replay with a
relative path is retained alongside the corrected replay. This is observational
cost accounting, not an attempt budget or a reason to end the active campaign.

The next step is a newly recorded staged output trial: expose one container/frame
boundary at a time and immediately rewrite its exact Core and field-walk facts.
Broad `cbv` reduction expanded environments before certificate matching and
proved unsuitable here. Conditional value/fold work has not begun. The canonical
queue keeps this one scientific campaign ACTIVE; alias work remains deferred.

The following invocation was executed successfully from the lab checkout on the
connected Mac, with the pinned compiler and historical cache. Substitute a fresh
nonexistent destination for a repeat. The replay checks compiler/cache hashes,
records `lean --deps`, compiles into that destination under the unchanged
resource supervisor, and prints theorem axioms. It requires the existing 108
recorded artifacts; it is not a clean upstream build recipe.

```sh
python3 explorations/runs/EXPLORE-TREE2-OBSERVATION-1/replay.py \
  --compiler /Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean \
  --cache /Users/danphifer/Documents/Codex/2026-09-30/task-4/confirmation-fresh \
  --source explorations/runs/EXPLORE-TREE2-OBSERVATION-1/sources/Tree2CtorReadback.lean \
  --destination explorations/runs/EXPLORE-TREE2-OBSERVATION-1/fresh-replay-2
```

[The pilot archive](../explorations/runs/EXPLORE-TREE2-OBSERVATION-1/) retains exact
sources, commands, receipts and the [machine-readable checkpoint](../explorations/runs/EXPLORE-TREE2-OBSERVATION-1/checkpoint.json).
All continuation code and notes are local pending separate publication approval.
