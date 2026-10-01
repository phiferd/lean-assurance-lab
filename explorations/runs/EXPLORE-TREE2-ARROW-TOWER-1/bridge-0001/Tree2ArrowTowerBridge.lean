import Tree2ArrowTowerOfficial
import Tree2ArrowTowerWalk

/- Local AI-authored restricted acceptance bridge; no production-kernel claim. -/
namespace Tree2ArrowTowerBridge
open ConLeche Tree2Bridge Tree2TowerSupport Tree2ArrowTowerNative
set_option maxRecDepth 3000
set_option maxHeartbeats 2000000

theorem positive_derivation (N F : Nat) (hf : N+5 ≤ F) :
 PosDR (checker F) (En N) (Cn N) (N+2)
 (.ctors [] [] 2 [] [A] [Tn] [X] (Tree2ArrowTowerSchema.roots false N)) := by
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
 · exact Tree2ArrowTowerWalk.node_singleton N F hf

/-- Actual acceptance is consumed; no conversion/derivation/native-success
    premise, and the actual Core budget is explicit and separately proved. -/
theorem acceptance_bridge (bad : Bool) (N F : Nat) (hf : N+5 ≤ F)
 (ha : Official.OfficialPosAccepts (Tree2ArrowTowerSchema.context bad N)
  (Tree2ArrowTowerSchema.declaration bad N) (Tree2ArrowTowerOfficial.officialWhnf N) 2) :
 bad = false ∧
 Official.elimNested (Tree2ArrowTowerSchema.context bad N)
  (Tree2ArrowTowerSchema.declaration bad N) (N+2) =
  .ok (Tree2ArrowTowerSchema.target bad N) ∧
 PosDR (checker F) (Tree2ArrowTowerSchema.env bad N) (Tree2ArrowTowerSchema.ctx bad N)
  (N+2) (.ctors [] [] 2 [] [A] [Tn] [X] (Tree2ArrowTowerSchema.roots bad N)) ∧
 (∃ r, nestedBlockPositivity (checker F) (Tree2ArrowTowerSchema.env bad N)
  (Tree2ArrowTowerSchema.ctx bad N) [Tree2ArrowTowerSchema.roots bad N] = .ok r) := by
 have hd := Tree2ArrowTowerOfficial.acceptance_domain bad N ha
 subst bad
 exact ⟨rfl,Tree2ArrowTowerOfficial.lowering false N,positive_derivation N F hf,
  Tree2ArrowTowerWalk.automatic_run N F hf⟩

/-- Constructor-local budgets are retained; no growing bound is imposed on leaf. -/
theorem constructor_derivations (N F : Nat) (hf : N+5 ≤ F) :
 PosDR (checker F) (En N) (Cn N) 1
  (.ctors [] [] 2 [] [A] [Tn] [X] [(leafCV,1)]) ∧
 PosDR (checker F) (En N) (Cn N) (N+2)
  (.ctors [] [] 2 [] [A] [Tn] [X] [(Tree2ArrowTowerSchema.node false N,1)]) :=
 ⟨Tree2ArrowTowerWalk.leaf_singleton N F hf,Tree2ArrowTowerWalk.node_singleton N F hf⟩

/-- Auxiliary row and key meanings are preserved relative to allocated depth. -/
theorem auxiliary_allocation (bad : Bool) (N i : Nat) (hi : i < N) :
 (Tree2ArrowTowerSchema.target bad N).aux[i]? =
  some (Tree2TowerNative.pow (N-i) tr,Tree2TowerOfficial.freshName (i+1)) ∧
 (Tree2ArrowTowerSchema.target bad N).types[i+1]? =
  some (Tree2TowerOfficial.row N (N-i)) ∧
 (Tree2TowerOfficial.row N (N-i)).name = Tree2TowerOfficial.freshName (i+1) ∧
 Tree2TowerOfficial.R N (N-i) = Tree2TowerOfficial.auxExpr (i+1) := by
 have h := Tree2TowerOfficial.allocation_depth N i hi
 refine ⟨h.1,?_,h.2.2.1,h.2.2.2⟩
 simpa [Tree2ArrowTowerSchema.target,Tree2TowerOfficial.target] using h.2.1

#print axioms positive_derivation
#print axioms acceptance_bridge
#print axioms constructor_derivations
#print axioms auxiliary_allocation
end Tree2ArrowTowerBridge
