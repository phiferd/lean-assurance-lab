import Tree2DomainOfficial
import Tree2DomainWalk

/- Local AI-authored grammar conversion; no production-kernel claim. -/
namespace Tree2DomainBridge
open ConLeche Tree2Bridge Tree2TowerSupport Tree2DomainGrammar Tree2DomainNative
set_option maxRecDepth 3000
set_option maxHeartbeats 2000000

/-- Actual acceptance supplies the native occurrence-free condition; the raw,
    canonical and typed native interpretations are separately proved. -/
theorem domain_conversion (D : Domain) (N F : Nat)
 (hf : Tree2DomainSchema.coreBound D N ≤ F)
 (ha : Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (Tree2DomainOfficial.officialWhnf N) 2) :
 (D.raw 0).instantiate1 A = D.official ∧
 ((D.encode P (t P)).replaceApps (nestCanonSub [Tn] [] 1) 0 1).replaceFVars
  (nestKeyMap [A] [X]) = D.native ∧
 D.native.nestOcc [Tn] 1 2 = false ∧
 ∀ d, 2 ≤ d → inferTypeCore .verified (En D N) F d D.native = .ok (.sort D.sortLevel) := by
 have hd := Tree2DomainOfficial.acceptance_domain D N ha
 refine ⟨Domain.raw_instantiate D 0 A,?_,(Domain.native_occ D).trans hd,?_⟩
 · rw [Domain.canonicalize,Domain.key_map]
 · intro d hdep
   apply domain_infer D N d F hdep
   unfold Tree2DomainSchema.coreBound at hf
   omega

theorem positive_derivation (D : Domain) (N F : Nat)
 (hf : Tree2DomainSchema.coreBound D N ≤ F) (hd : D.hasSelf=false) :
 PosDR (checker F) (En D N) (Cn D N) (N+2)
 (.ctors [] [] 2 [] [A] [Tn] [X] (Tree2DomainSchema.roots D N)) := by
 have hfN : N+5 ≤ F := by unfold Tree2DomainSchema.coreBound at hf; omega
 apply PosDR.ctorsCons (crest := arr A X)
  (ty := .sort (.imax (.succ .zero) (.succ .zero)))
  (sv := .imax (.succ .zero) (.succ .zero))
  (m₁ := 1) (m₂ := N+2) (ks := [.ordinary]) (nds := [(A,bm)]) (cur := X)
 · decide
 · exact root_crests.1
 · exact leaf_infer N F (by omega)
 · exact ensure_sort N F 2 _ (by omega)
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact ordinary_field N F (by omega)
   · omega
   · exact PosDR.teleNil
 · rfl
 · rfl
 · rfl
 · omega
 · exact Tree2DomainWalk.node_singleton N F hf hd

theorem acceptance_bridge (D : Domain) (N F : Nat)
 (hf : Tree2DomainSchema.coreBound D N ≤ F)
 (ha : Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (Tree2DomainOfficial.officialWhnf N) 2) :
 D.hasSelf=false ∧
 Official.elimNested (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (N+2) = .ok (Tree2DomainSchema.target D N) ∧
 PosDR (checker F) (Tree2DomainSchema.env D N) (Tree2DomainSchema.ctx D N)
  (N+2) (.ctors [] [] 2 [] [A] [Tn] [X] (Tree2DomainSchema.roots D N)) ∧
 ∃ r, nestedBlockPositivity (checker F) (Tree2DomainSchema.env D N)
  (Tree2DomainSchema.ctx D N) [Tree2DomainSchema.roots D N] = .ok r := by
 have hd := Tree2DomainOfficial.acceptance_domain D N ha
 exact ⟨hd,Tree2DomainOfficial.lowering D N,positive_derivation D N F hf hd,
  Tree2DomainWalk.automatic_run N F hf hd⟩

/-- Nonvacuous acceptance/derivation package for every finite grammar shape and
    every List depth. No accepting or derivation premise is assumed. -/
theorem restricted_completeness (D : Domain) (N : Nat) :
 (Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (Tree2DomainOfficial.officialWhnf N) 2
   ↔ D.hasSelf=false) ∧
 (Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (Tree2DomainOfficial.officialWhnf N) 2 →
  D.hasSelf=false ∧
  Official.elimNested (Tree2DomainSchema.context D N)
   (Tree2DomainSchema.declaration D N) (N+2) = .ok (Tree2DomainSchema.target D N) ∧
  PosDR (checker (Tree2DomainSchema.coreBound D N)) (Tree2DomainSchema.env D N)
   (Tree2DomainSchema.ctx D N) (N+2)
   (.ctors [] [] 2 [] [A] [Tn] [X] (Tree2DomainSchema.roots D N)) ∧
  ∃ r, nestedBlockPositivity (checker (Tree2DomainSchema.coreBound D N))
   (Tree2DomainSchema.env D N) (Tree2DomainSchema.ctx D N)
   [Tree2DomainSchema.roots D N] = .ok r) := by
 exact ⟨Tree2DomainOfficial.acceptance_iff D N,
  fun ha => acceptance_bridge D N _ (Nat.le_refl _) ha⟩

#print axioms domain_conversion
#print axioms positive_derivation
#print axioms acceptance_bridge
#print axioms restricted_completeness
end Tree2DomainBridge
