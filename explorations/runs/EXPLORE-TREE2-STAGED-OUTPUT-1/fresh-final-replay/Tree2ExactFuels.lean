import Tree2TowerWalk
/- Local finite numeric certificates. The identifier macro only references
   an existing pinned private theorem; ordinary Lean kernel checking remains. -/
namespace Tree2ExactFuels
open ConLeche Tree2Bridge
macro "existingDepthHeight" : term =>
 return ⟨Lean.mkIdent (Lean.Name.str (Lean.Name.str
  (Lean.Name.num (Lean.Name.str (Lean.Name.str .anonymous "_private") "Tree2TowerWalk") 0)
  "Tree2TowerWalk") "depth_eq_height")⟩
theorem leaf_depth : (arr A X).depth = 2 :=
 (existingDepthHeight (arr A X)).trans (by rfl)
theorem node_depth : (arr (l (l X)) X).depth = 4 :=
 (existingDepthHeight (arr (l (l X)) X)).trans (by rfl)
private theorem fuel_of_depth {e : Expr} {d : Nat} (h : e.depth = d) :
 whnfWalkFuel e = d + fuelSlack := by
 unfold whnfWalkFuel
 exact congrArg (fun n : Nat => n + fuelSlack) h

theorem walk_fuels : whnfWalkFuel (arr A X) = 1026 ∧
 whnfWalkFuel (arr (l (l X)) X) = 1028 :=
 ⟨fuel_of_depth leaf_depth,fuel_of_depth node_depth⟩
#print axioms leaf_depth
#print axioms node_depth
#print axioms walk_fuels
end Tree2ExactFuels
