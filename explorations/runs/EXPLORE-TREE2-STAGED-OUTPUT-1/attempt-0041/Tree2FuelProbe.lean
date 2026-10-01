import Tree2TowerWalk
/- Resolve a pinned imported private lemma's numeric Name component.
   This macro only builds an identifier; it creates no proof or declaration. -/
macro "existingDepthHeight" : term =>
 return ⟨Lean.mkIdent (Lean.Name.str (Lean.Name.str
  (Lean.Name.num (Lean.Name.str (Lean.Name.str .anonymous "_private") "Tree2TowerWalk") 0)
  "Tree2TowerWalk") "depth_eq_height")⟩
#check existingDepthHeight
open ConLeche Tree2Bridge
example : (arr A X).depth = 2 := by
 exact (existingDepthHeight (arr A X)).trans (by rfl)
#print axioms _private.Tree2FuelProbe
