# A bounded acceptance-driven completeness bridge

Local AI-authored research for human review, not an upstream submission.
Pinned con-leche10fe085e21773ff0b62a6aacf6db29fccf849bae; new proof commit
bae799dfc7c96348e973baf27d7ca153edc7c219. Previous proofs/checkouts preserved.

## Question and result

The canonical positive tower already had native success independent of official
acceptance. An unused acceptance premise added no completeness evidence. This
trial instead admits two explicitly encoded depth-two node fields:

```text
leaf : alpha → Tree
node : (D → List (List Tree)) → Tree
D = alpha     (bad=false)
D = Tree      (bad=true)
```

List retains its exact one-universe/one-parameter/no-index nil/cons schema;
all Pi metadata uses pw=never. The function is outside the two canonical List
keys; no wrapper or function is introduced inside a key. No dependent fields,
indices, Prop or arbitrary grammar extension is included.

The ordinary Lean theorem `Tree2ArrowSchema.acceptance_iff` proves the actual
OfficialPosAccepts proposition holds exactly when bad=false. Positive acceptance
is witnessed by actual elimination and all six lowered constructor checks;
negative acceptance is impossible. The final `Tree2ArrowBridge.acceptance_bridge`
then genuinely consumes that official evidence before building the native proof:

```lean
(bad : Bool)
(ha : Official.OfficialPosAccepts (context bad) (declaration bad) officialWhnf 2) :
 bad = false ∧
 PosDR (checker 16) (env bad) (ctx bad) 4
  (.ctors [] [] 2 [] [A] [Tn] [X] (roots bad)) ∧
 (∃ r, nestedBlockPositivity (checker 16) (env bad) (ctx bad) [roots bad] = .ok r)
```

`bounded_completeness` packages positive official acceptance, negative official
rejection and this implication. No native acceptance, PosDR, desired output or
unproved converter appears as a premise. This completes the bounded trial, not
just an intermediate lemma. No source/model mismatch was found: E0 NO_SIGNAL.

## Why acceptance matters

OfficialPosAccepts allows arbitrary elimination/checking fuel witnesses. The
proof first establishes every successful elimination fuel yields the exact
specified lowered state; no chosen fuel/output is assumed. Its node constructor
check has a function field. For the admitted negative schema, checkPositivity
rejects the recursive domain at every field fuel, and hence at every possible
telescope budget. Extracting this actual check from ha proves bad=false.

Only after that inference does the proof construct the positive native Pi rule,
whose domain occurrence test is false. Its body walks List2 at kb=1, producing
the nested-true kind rather than treating it as a top-level field. It constructs
the inner/outer frames with active-key freshness, the real stack reset and
frame-relative holes. Raw hole2 is never globally equated across frames.

This is finite classification followed by constructive derivation. It is a
real, discriminating instance of acceptance-to-native completeness, but not a
general reconstruction induction over arbitrary official derivations.

## Discharged obligations

- Exact source encoders, List/root lookups, fresh auxiliary names and never
  binders are defined/proved. The native environment stores the ACTUAL changed
  arrow-node declaration; the old node declaration is not silently reused.
- The official pure WHNF environment separately contains opaque root/auxiliary
  inductive types without constructors, plus ordinary List. It is not identified
  with the native environment, and no arbitrary reduction oracle is assumed.
- Pure verified Core16 WHNF is proved on the paired fields and all inspected
  official parameter/member/auxiliary terms. All six positive constructor checks
  pass this actual oracle; the implication's antecedent is therefore nonvacuous.
- Exact native crest, frame-relative node readback and official replacement
  yield the corresponding lowered node expression with allocation unchanged.
  These readback lemmas do not assert a new exact full emitted-record table.
- Finite Core typing/ensure-sort certificates, List instantiations, scopes,
  result/index guards, U4 and root uniformity are discharged. Actual inferred
  imax sorts are retained. Reused Core/List proof text is RECHECKED against the
  changed environment, not transported through an assumed environment oracle.
- Leaf derivation index1 and node index4 are proved. This bounded family can use
  common index4 because each actual whnfWalkFuel crest exceeds it via the proved
  fuelSlack bound. The checker still uses automatic per-crest budgets; this does
  not assert an all-depth common-index bound. Core16 and derivation4 are distinct.
- Existing nestedBlockPositivity_complete/posDR_run is applied only at the end.

## Fit with parked upstream work

Complete.lean:8–21 describes a parked completeness library; no soundness/checker
module consumes it. OfficialNested.lean:317–325 defines positivity acceptance,
not complete official-validator acceptance. Its omissions at:62–66 include
constructor typing, parameter defeq, universes and uniformity. PosDerivComplete
at:69–184 adds active-key and real-stack requirements;:435 and:618–631 prove
PosDR-to-run and root assembly. The earlier generic DerivationBridge blueprint
still has an unproved converter for a broader input class. This trial supplies
a genuine bounded instance without claiming to solve that general gap.

Source duplicate check finds OfficialPosAccepts only in its definition/module
description among pinned ConLeche/tests Lean files. Existing arrow/nesting tests
remain acknowledged; another accepted example would not be this contribution.
This search is not a literature/novelty claim or evidence no one else is working.

## Verification and limits

A fresh three-module dependency-chain replay verified the pinned compiler and
108 historical compiled-import hashes, then compiled Schema, Native and Bridge
in7.332s total, sampled peak RSS1.799GB. All dependency checks and compiles exited0
with complete cleanup; all24 printed axiom reports list only propext,
Classical.choice, Quot.sound. Final source scan finds no sorry/admit/new axiom,
native_decide or run_tac. Independent AI statement/evidence review passes.

All15 development revisions and receipts are retained (55.058s aggregate,
zero resource interruptions, all cleanup complete). Failed elaborations and
positive-control kernel-recursion/selfdependency/sorryAx reports are rejected
attempts, not theorem evidence. Modular field/telescope proofs repaired them;
two unused-simp warnings in the accepted helper are non-material.

The earlier exact six-record Tree2 theorem is preserved. This new arrow-family
result proves existential native success, not its exact full returned-record
observation. Arbitrary-depth acceptance reconstruction/output, value inverses,
fold preservation, whole-validator acceptance, production C++ fidelity, compiled
checker parity and generated/installed recursors remain unproved. No novelty or
human-expert endorsement is claimed. No push, issue, comment or publication ran.
The one Tree2 campaign remains ACTIVE; this bounded trial is COMPLETE.
Existing Library overview version1 is historical and unchanged by this trial.

## Reproduce the accepted chain

Use a NEW nonexistent destination:

```sh
python3 explorations/runs/EXPLORE-TREE2-ACCEPTANCE-BRIDGE-1/replay-chain.py \
  --compiler /Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean \
  --cache /Users/danphifer/Documents/Codex/2026-09-30/task-4/confirmation-fresh \
  --source explorations/runs/EXPLORE-TREE2-ACCEPTANCE-BRIDGE-1/sources/final \
  --destination explorations/runs/EXPLORE-TREE2-ACCEPTANCE-BRIDGE-1/fresh-replay-2
```

The executed destination is fresh-replay. This reuses hash-verified historical
imports, not a clean upstream build or new full-lab E2 assurance closure.
