# What a nested tree means to two positivity models

The checked results relate restricted constructor representations and prove
model positivity for fixed schemas and a structural function-domain family.
Their downstream usefulness was tested and **not demonstrated**. The actual
preserved upstream completeness branch already proves the general occurrence,
substitution and restoration facts; our specialized equations do not discharge
its remaining simulation, typing, freshness or key-restriction premises.

The Tree2 campaign is stopped and retained as a checked model case study. No
further grammar, output, fold or proof-framework expansion is selected. The
[utility disposition](../results/research/tree2-utility-disposition-1/report.md)
corrects the earlier target-fit rationale while preserving every historical
proof, outcome and review. The descriptions below document achieved results
and earlier unexecuted proposals; they do not authorize additional research.

This is local AI-authored research for human review. The owner authorized lab publication of the continuation on 2026-10-01;
upstream submissions and community messages remain unauthorized. There is no unsupported claim that this theorem is novel research or
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

## Historical continuation: input shape versus returned output

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
node. The staged proof below now certifies that complete observation and its
connection to the actual six lowered constructor types. The earlier supplied-
telescope theorem remains useful and retains its original, smaller claim.

Existing general recorded-constructor and recursor laws are reusable, but their
well-scoped environment, derivation and stage hypotheses must be discharged.
They are not automatically supplied by an existential successful walk.

## Exact execution and lowering: fixed Tree2

The [staged trial](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/plan.md)
now proves the complete fixed-N=2 output with verified pure Core fuel 7.
[Tree2Execution.actual_output](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/sources/final/Tree2Execution.lean)
says exactly:

```lean
nestedBlockPositivity (checker 7) (En 2) (Cn 2) [roots 2]
  = .ok Tree2Execution.expected
```

The independently specified result has child-first keys (inner, outer), root
kinds ordinary/nested, exact leaf/node normal forms, and six constructor records
in order leaf, outer nil, inner nil, inner cons, outer cons, node. Intermediate
lemmas execute the real inner and outer fields, constructors, frames and caller
guards; the root composition uses the actual automatic walk budgets 1026 and
1028. These are separate from pure Core fuel 7 and PosDR index 3.

[Tree2ObservationBridge.actual_lowering](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/sources/final/Tree2ObservationBridge.lean)
first runs that checker, then groups the **returned** constructor types in
Tree/Rows/Children order and runs real `Official.replaceAll`. It returns exactly
all six constructor types of `target 2`, with that completed allocation state
unchanged. Its `fixed_bridge` packages this equation with the exact official
queue-fuel-4 lowering, constructed native PosDR index 3 and exact observation.
No emitted-record, acceptance, PosDR or successful-Core-operation assumption is
used. This closes the fixed-depth input/output seam rather than adding another
acceptance example. No novelty claim follows without broader literature review.

A fresh four-module replay compiled the fuel helper, execution proof, existing
readback and final bridge in 5.761 seconds total, peak sampled RSS 1.472 GB.
The pinned compiler and all 108 historical import hashes were verified before
compilation; dependency logs show the new helper/execution/readback artifacts
resolved from this fresh directory. Every replay process cleaned up. All printed
accepted theorems have only `propext`, `Classical.choice` and `Quot.sound`.
The 52 retained compile revisions cost 910.442 seconds, including 13 RSS safety
interruptions; all cleanup completed. Failed elaborations with automatic
`sorryAx` remain rejected evidence. Counts are cost observations, not limits.

The fuel helper uses an identifier-only macro to name the pinned imported
private `Tree2TowerWalk.depth_eq_height` theorem. It creates no oracle or axiom:
Lean checks the resulting proof term normally. That private declaration name is
an explicit portability dependency on the pinned module identity. No
`native_decide`, `sorry`, `admit` or new axiom appears in accepted final sources.

The [checkpoint](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/checkpoint.json),
[fresh axiom output](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/fresh-final-replay/Tree2ObservationBridge-compile-stdout.log)
and [final independent AI review](../explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/independent-review-final.md)
retain the evidence. This fixed trial is COMPLETE with E0 NO_SIGNAL: no
source-model mismatch was found; the mathematical bridge was proved. At that checkpoint the Tree2 campaign was ACTIVE for an expanded endpoint;
that endpoint is now withdrawn and the campaign stopped. Earlier
inner-only evidence and the original INCONCLUSIVE trial remain historical.
The delivered Library overview still has identity
`libfile_14f671019e4c8191b23aa2e52406a215`, version 0; this update is local only.

## Disposition: no demonstrated upstream reuse

Pinned main contains the official-model spec and native-derivation completeness
theorem, but no acceptance-driven converter. That is not a claim that upstream
has no such work: `complete3-parked` preserves an actual acceptance-to-native
success-or-decline theorem with explicit remaining premises. Its general
occurrence/substitution/restoration proofs already exist. Our earlier blueprint
assembled an assumed converter and did not remove any of those premises.

See the [exact target and before/after dependency assessment](../results/research/tree2-utility-disposition-1/report.md).
Independent source review confirmed no concrete application. The historical
branch was inspected, not rebuilt. The restricted proofs remain valid; their
proof quality and broader syntax coverage alone do not establish scientific
novelty or downstream usefulness.

## Bounded acceptance-driven result: function outside List2

The [new bounded trial](../explorations/runs/EXPLORE-TREE2-ACCEPTANCE-BRIDGE-1/report.md)
now closes the proposed discriminating bridge. It admits node fields
`alpha → List (List Tree)` and `Tree → List (List Tree)`, with the exact same
ordinary List schema and two canonical keys. The function stays outside the keys.
Official model acceptance holds exactly for the parameter-domain choice.
The proof uses its actual constructor check to exclude the recursive negative
domain, then constructs native PosDR index4 and actual native success under
verified pure Core16. Positive official acceptance is also proved using all six
actual lowered constructor checks, so the implication is nonvacuous.

This acceptance premise is USED, unlike the earlier canonical-family corollary.
The explicit changed native node lookup, separately opaque official environment,
all-successful-fuel elimination, paired WHNF, frame readback/restoration, typing,
U4, uniformity and real automatic walk budgets are discharged. No native
acceptance/derivation/output or missing converter premise is assumed.

Fresh Schema/Native/Bridge replay and independent AI review pass; all24 axiom
reports contain only the standard three. The source proof is
[Tree2ArrowBridge.lean](../explorations/runs/EXPLORE-TREE2-ACCEPTANCE-BRIDGE-1/sources/final/Tree2ArrowBridge.lean).
This is a finite two-schema classification plus constructive derivation, not
general official-derivation reconstruction. The historical upstream half(A) theorem retains explicit premises; our result does not discharge them.
The arrow-family result does not identify its full returned observation; the
previous exact six-record theorem applies to the original Tree2 and is preserved.
No folds, arbitrary grammar expansion or external action ran. At that checkpoint the campaign was ACTIVE and the bounded trial COMPLETE.
The campaign is now stopped under the utility disposition; Library overview
version1 remains the older delivered checkpoint.

## Earlier unexecuted endpoint proposal (withdrawn)

For this restricted List-tower family, sufficient model correspondence needs:

1. An exact returned-output and returned-record lowering theorem for every
   natural depth, including zero, with explicit sufficient Core fuel and exact
   key/record ordering. Existing all-depth acceptance and input-crest decoding
   do not imply that equation.
2. Independently specified nested and lowered value models tied to those proved
   constructor signatures and allocation/frame meanings, with translations in
   both directions and both inverse laws. Handwritten lookalike datatypes alone
   would leave this connection missing. Group boundaries and empty rows matter.
3. Fold preservation for arbitrary result types and compatible leaf/node/list
   operations. Leaf counting is only an example, not the general theorem.

This endpoint proposal is withdrawn for lack of demonstrated downstream use.
The list above records unproved obligations, not selected next steps. No value/
fold trial started. Production lowering, installed recursor correctness and
compiled-checker parity remain separate claims outside the achieved case study.

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
That equation is a goal, not a present result. A production/generated-recursors claim would additionally require a connection
to actual generated recursors; that is separate from the restricted model endpoint.

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
stronger than counting constructors or showing another accepted example. At that earlier checkpoint, it remained weaker than the original pilot goal.
The subsequent staged trial above has now proved the full walk generates those
records, together with its keys, kinds and normals. The earlier trial closure
is preserved; no mathematical counterexample has been observed.

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
relative path is retained alongside the corrected replay. This is observational cost accounting, not an attempt budget. The later
utility assessment, rather than these attempt counts, stops the campaign.

The staged output trial described above exposes one container/frame
boundary at a time and rewrites its exact Core and field-walk facts.
Broad `cbv` reduction expanded environments before certificate matching and
proved unsuitable here. The fixed output composition now succeeds; expanded value/fold work has not
begun. The canonical
queue at that checkpoint kept Tree2 ACTIVE and alias work deferred. The
current queue closes Tree2 and restores alias preparation READY/unstarted.

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

To replay the execution checkpoint with the same verified compiler/cache, use
`explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/replay.py` with source
`explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/sources/Tree2Execution.lean` and
a fresh nonexistent destination. This exact invocation was verified with
`--destination explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/fresh-replay`;
the other flags are the compiler/cache paths in the command above.

To replay the complete fixed bridge, use the retained `replay-v2.py` (the earlier
one-module runner and replay remain unchanged):

```sh
python3 explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/replay-v2.py \
  --compiler /Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean \
  --cache /Users/danphifer/Documents/Codex/2026-09-30/task-4/confirmation-fresh \
  --source explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/sources/final \
  --destination explorations/runs/EXPLORE-TREE2-STAGED-OUTPUT-1/fresh-final-replay-2
```

Use a new nonexistent destination. The executed replay is `fresh-final-replay`;
no full lab E2 closure or clean upstream rebuild is claimed for this pilot.

## 2026-10-01: reusable deterministic lowering prerequisite

Lean now proves that successful official elimination has a unique output for
any context and declaration, regardless of sufficient fuel. Actual acceptance
can therefore be read at an independently proved exact output. This removes the
finite fuel-case enumeration: checked consumers cover the existing all-depth
List tower and the fixed function-domain exclusion. This is useful modest
progress, not an arbitrary-depth function completeness theorem.

That historical next step led to the retained arrow-tower and domain results.
The subsequent utility assessment found no remaining upstream obligation they
discharge; no further scientific step is selected here.
All seven new axiom reports use only propext, Classical.choice and Quot.sound;
fresh replay and independent review passed at that checkpoint; the campaign is now stopped.

## 2026-10-01: nonvacuous bridge for every List depth

Lean checked the family with `leaf : alpha → Tree alpha` and
`node : (D → List^N (Tree alpha)) → Tree alpha`, where D is exactly alpha or
Tree alpha. The official positivity model accepts exactly D=alpha for every
natural N, including zero. Actual acceptance then yields the exact specified
lowering, a constructed native derivation, and native positivity success. This
extends the earlier fixed function-field stage; it does not change the original
Tree2 proof archives or claim a value isomorphism.

This expands the checked restricted class and uses the acceptance premise.
The later utility assessment found no concrete upstream consumer for it. The proof first excludes
the negative domain and then constructs the native derivation by depth induction.
It does not reconstruct arbitrary official proofs. Positive official witnesses,
exact environments and verified reducer facts are all proved; no conversion or
native-success oracle is assumed. The final package is
`Tree2ArrowTowerBridge.restricted_completeness N`, using native Core budget N+5,
separate constructor derivations leaf1/nodeN+2, and real automatic walk budgets.

Fresh seven-module replay and independent review pass. Final axioms are only
`propext`, `Classical.choice`, and `Quot.sound`. Official auxiliary row allocation
is proved; native returned records remain existential. The [result report](../explorations/runs/EXPLORE-TREE2-ARROW-TOWER-1/report.md)
contains statements, trust accounting, exact source, preserved failures and
reproduction commands. It remains a checked restricted model theorem;
downstream usefulness was not demonstrated. No kernel-correctness, full-validator,
novelty, generated recursor or fold claim follows.

The bounded proof result is complete and preserved. The later utility assessment
stops this expansion; no next grammar or fold trial is selected. Lab publication
remains limited to documented findings under the existing authorization, with
ordinary main delivery and exact remote/CI verification.
