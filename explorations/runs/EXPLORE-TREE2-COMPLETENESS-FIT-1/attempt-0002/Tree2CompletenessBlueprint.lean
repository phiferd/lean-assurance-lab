import Tree2TowerCorrespondence

/- Local AI-authored completeness fit blueprint. No missing lemma is axiomatized.
   The assembly theorem exposes its missing converter as an explicit parameter. -/
namespace Tree2CompletenessBlueprint
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial
set_option maxRecDepth 2000

/-- The missing half(A), with exactly the derivation and budget consumed by
    nestedBlockPositivity_complete. This definition proves nothing. -/
def DerivationBridge (ops : CheckerOps CheckM) (env : Env) (ctx : NestCtx)
 (c : Official.ElimCtx) (decl : List Official.MemberDecl)
 (w : Nat → Expr → CheckM Expr) (base : Nat) (holes : List Expr)
 (ctorss : List (List (ConstantVal × Nat))) : Prop :=
 Official.OfficialPosAccepts c decl w base →
 ∀ cs ∈ ctorss, ∃ n,
  (∀ x ∈ cs, ∀ crest,
   nestCrest ctx.names (ctx.lps.map .param) ctx.params holes
    (x.1.type.instantiateLevelParams x.1.levelParams (ctx.lps.map .param)) = some crest →
    n ≤ whnfWalkFuel crest) ∧
  PosDR ops env ctx n (.ctors [] [] (ctx.hiAt 0)
    (ctx.lps.map .param) ctx.params ctx.names holes cs)

/-- Checked assembly ONLY: hbridge is the explicitly missing theorem, not an
    inferred consequence of official acceptance. Its proof must precede claiming
    official-to-native completeness for any broader input class. -/
theorem conditional_assembly (ops : CheckerOps CheckM) (env : Env) (ctx : NestCtx)
 (c : Official.ElimCtx) (decl : List Official.MemberDecl)
 (w : Nat → Expr → CheckM Expr) (base : Nat) (holes : List Expr)
 (ctorss : List (List (ConstantVal × Nat)))
 (hroot : NestRootOk ctx) (hh : nestHoles ctx = some holes)
 (hu : ∀ cs ∈ ctorss, ∀ ca ∈ cs, nestUniformOk ctx ca.1 = true)
 (hbridge : DerivationBridge ops env ctx c decl w base holes ctorss)
 (ha : Official.OfficialPosAccepts c decl w base) :
 ∃ r, nestedBlockPositivity ops env ctx ctorss = .ok r := by
 exact nestedBlockPositivity_complete hroot hh hu (hbridge ha)

/-- The canonical tower family already has a stronger, unconditional native
    derivation. Arbitrary official WHNF is deliberately NOT asserted faithful. -/
theorem restricted_derivation (N F : Nat) (hf : N+5 ≤ F) :
 PosDR (checker F) (En N) (Cn N) (N+1)
  (.ctors [] [] 2 [] [A] [Tn] [X] (roots N)) := native_family N F hf

/-- Literal restricted conditional fit; the official antecedent is unused,
    since this independently fixed family has a direct constructive proof.
    Not acceptance-driven reconstruction and not general completeness. -/
theorem restricted_conditional (N F : Nat) (hf : N+5 ≤ F)
 (w : Nat → Expr → CheckM Expr) (base : Nat)
 (_ha : Official.OfficialPosAccepts (context N) (declaration N) w base) :
 ∃ r, nestedBlockPositivity (checker F) (En N) (Cn N) [roots N] = .ok r :=
 Tree2TowerWalk.automatic_run N F hf

/-- Sufficient per-constructor budgets, avoiding a uniform depth bound imposed
    on the shallow leaf. Existing tower execution composes these singleton runs. -/
theorem restricted_singleton_budgets (N F : Nat) (hf : N+5 ≤ F) :
 (PosDR (checker F) (En N) (Cn N) 1
   (.ctors [] [] 2 [] [A] [Tn] [X] [(leafCV,1)]) ∧
  1 ≤ whnfWalkFuel (arr A X)) ∧
 (PosDR (checker F) (En N) (Cn N) (N+1)
   (.ctors [] [] 2 [] [A] [Tn] [X] [(node N,1)]) ∧
  N+1 ≤ whnfWalkFuel (arr (tower N) X)) :=
 ⟨⟨Tree2TowerWalk.leaf_singleton N F hf,Tree2TowerWalk.leaf_walk_budget⟩,
  ⟨Tree2TowerWalk.node_singleton N F hf,Tree2TowerWalk.node_walk_budget N⟩⟩

#print axioms restricted_singleton_budgets

#print axioms conditional_assembly
#print axioms restricted_derivation
#print axioms restricted_conditional
end Tree2CompletenessBlueprint
