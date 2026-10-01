# How the tower result fits the parked completeness goal

Local AI-authored source analysis and checked blueprint, not an upstream proposal.
Pinned con-leche: 10fe085e21773ff0b62a6aacf6db29fccf849bae. No external action.

## What upstream actually says

`ConLeche/Complete.lean` calls this library parked completeness work against the
official kernel. It imports OfficialNested, PosDerivComplete and ProgActive;
no soundness/checker/capstone module consumes it, and outside production modules
are forbidden to import it by the layering rule. The inspected source does not
state a completed top-level OfficialPosAccepts-to-native theorem.

OfficialNested.lean:320 has the REAL `Official.OfficialPosAccepts c decl w base`:
there exist elimination fuel/state with `elimNested c decl fuelE = .ok st`, and
each constructor of every eliminated type passes `checkCtorPos` at some field/
telescope fuels. Its oracle is a parameter; the model omits constructor typing,
parameter defeq, universe checks and uniform-occurrence checking. The comments
describe intended oracle/side-condition hypotheses, not an already implemented
acceptance-to-derivation theorem. These comments must not be mistaken for one.

PosDerivComplete.lean:435 proves `posDR_run`: strengthened `PosDR` implies a
successful native walk with sufficient fuel and root/state invariants. At:618,
`nestedBlockPositivity_complete` assembles root success from holes, uniformity,
and fuel-bounded PosDR derivations. PosDR includes active-key freshness and the
actual `nestWalkStack` reset that the weaker PosD forgot. There is no inspected
theorem converting official positivity acceptance into these derivations.

## Exact checked blueprint and limits

[Tree2CompletenessBlueprint.lean](sources/final/Tree2CompletenessBlueprint.lean)
contains no sorry, new axiom or untrusted decision mechanism.
`DerivationBridge` DEFINES the missing input: official model acceptance implies
a fuel-bounded root PosDR derivation for each member constructor list.
`conditional_assembly` takes that converter as an EXPLICIT theorem parameter,
plus `NestRootOk`, exact hole extraction and constructor uniformity. It calls
existing `nestedBlockPositivity_complete`, which calls `posDR_run`.
This proves the assembly type checks; it DOES NOT prove DerivationBridge.
The explicit converter is a missing lemma, not a permissible hidden semantic
assumption for a completed scientific result. No sorry-bearing design artifact
is mixed with checked artifacts.

For canonical List towers, `restricted_derivation N F (N+5 ≤ F)` already follows
from our earlier constructive `native_family`; its PosDR index is N+1.
`restricted_conditional` consequently checks the literal target:

```lean
Official.OfficialPosAccepts (context N) (declaration N) w base →
  ∃ r, nestedBlockPositivity (checker F) (En N) (Cn N) [roots N] = .ok r
```

with sufficient F≥N+5. Its official antecedent is UNUSED, for any w/base. That
is transparent: the known-valid family has an unconditional native proof.
The corollary is not acceptance-driven reconstruction, not new coverage beyond
the previous theorem, and not the missing general completeness half(A). We do
not declare arbitrary w faithful to production or identify its environment with
`En N`, which lacks the lowered auxiliary declarations.

## A budget detail that affects the exact target

The existing root wrapper demands one derivation index n be bounded by every
constructor crest's automatic fuel. Naively choosing n=N+1 for the whole member
list cannot work at all depths: leaf crest fuel is fixed1026, while this proposed
index exceeds it for N>1025. This is a failure of that proposed sufficient
instantiation, NOT a counterexample to walk completeness. The walker budgets
constructors separately. `restricted_singleton_budgets` checks leaf PosDR index1
and node indexN+1 against their own automatic fuels. Existing leaf_run/node_run
use posDR_run separately, and constructors_run composes the real loops by append.
An all-depth acceptance bridge should preserve this per-constructor budgeting or
prove a appropriately refined root wrapper; do not assume one uniform bound.

## Missing lemma map and acceptable hypotheses

For a genuine acceptance-driven bridge, first define its admitted declaration
class and official opaque environment. The current fixed schema permits one
universe/one type parameter, no indices/dependency/Prop, exact List nil/cons,
uniform root parameter and never binder metadata. All facts in this canonical
family have explicit checked source identities; extending that class is separate.

| Obligation | Precisely what must be proved | Existing landing point |
| --- | --- | --- |
| Source/environment fit | Exact member/List schema and lookup correspondence, fresh auxiliary names, constructor lists and scopes; no arbitrary environment-check oracle | Official ElimCtx, native NestCtx/En, current explicit tower helpers |
| Lowered-field inverse | Restore each auxiliary reference to the correct key/frame and preserve field/result occurrence tests under abstraction-before-substitution | Official replaceAll/elimNested; allocation_frame, input-row proofs; fixed actual-output bridge |
| Oracle relation | For the independently specified field/crest terms actually inspected, official WHNF and native WHNF agree after representation restoration; official oracle's opaque environment stated | PosOracle.whnf; PosDR.const/pi/hole/frameHole/cont hw premises |
| Native side checks | Prove exact required typing/ensure-sort calls, parameter/index shape N2/N3, scope/arity, U4 and uniformity from the admitted schema and restricted typing assumptions | PosDR.frame/ctorsCons/cont; NestRootOk, root holes, uniformity |
| Freshness and progress | Distinct ancestor keys, self as frame hole, no constant-descent into active key, actual nestWalkStack reset and ProgScoped | PosDR.cont hact/hfr and frameHole; ProgActive only removes redundant stack testing |
| Derivation reconstruction | Induct over accepted official constructor/field checks and lowering discovery to CONSTRUCT PosDR, retaining above invariants, not assume it | Missing half(A); conditional_assembly's explicit DerivationBridge parameter |
| Run composition/budgets | Per-constructor derivation fuel bound and state invariant preservation with enough pure Core fuel; mix leaf/node budgets correctly | posDR_run; current singleton and constructor-loop composition |

Typing/WHNF hypotheses may describe exact independently identified Core terms;
none may assert native positivity acceptance, PosDR existence or desired emitted
records. Calling the missing converter an assumption is only blueprint notation,
not a way to discharge the scientific obligation. The all-depth exact returned-
record equation is valuable consumer correspondence, but existential positivity
completeness itself does not require its full six-record result. Folds are a
later semantic goal and are deferred until this source fit is resolved.

## Scientific interpretation and contribution boundary

We now have a useful checked standalone exact-depth output/lowering theorem and
a source-grounded blueprint for the parked goal. The inspected restricted family
has already proved native completeness by construction; pretending its unused
acceptance premise solved general half(A) would overstate the result. A next
acceptance-driven theorem needs a meaningful admitted-input generality and the
inverse/WHNF/side-condition map above, not another positive example.

This is a specification-level model of production positivity slices. C++ kernel
verification, whole-validator acceptance, compiled checker parity and installed/
generated recursor correctness are distinct. No upstream ownership, novelty or
maintainer interest is inferred. The pinned README's Contributions section says
code contributions are not sought and detailed precise issues are welcome. User
has authorized no issue/comment or publication; AI-writing compatibility remains
unresolved. This artifact is not optimized as an upstream PR or posting text.

## Reproduction

A fresh affected-module replay reverified the compiler and108 prior module
hashes, compiled this blueprint in1.215s with peak sampled RSS1.309GB and complete
cleanup. All four public theorem reports have only propext, Classical.choice,
Quot.sound. The two retained supervised development compiles also passed.

```sh
python3 explorations/runs/EXPLORE-TREE2-COMPLETENESS-FIT-1/replay.py \
  --compiler /Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean \
  --cache /Users/danphifer/Documents/Codex/2026-09-30/task-4/confirmation-fresh \
  --source explorations/runs/EXPLORE-TREE2-COMPLETENESS-FIT-1/sources/final/Tree2CompletenessBlueprint.lean \
  --destination explorations/runs/EXPLORE-TREE2-COMPLETENESS-FIT-1/fresh-replay-2
```

Use a new nonexistent destination. This depends on the recorded historical
imports and is not a clean upstream build or full lab E2 closure.
