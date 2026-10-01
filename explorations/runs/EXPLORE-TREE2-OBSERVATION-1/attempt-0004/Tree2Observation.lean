import Tree2TowerCorrespondence

/- Local AI-authored finite output theorem. Historical sources unchanged. -/
namespace Tree2Observation
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial

set_option pp.maxDepth 8
set_option maxRecDepth 20000
set_option maxHeartbeats 2000000
attribute [local cbv_eval] Expr.bvarB_eq Expr.fvarB_eq ConLeche.Expr.Expr.hasLP_eq
attribute [local cbv_opaque] Expr.bvarB Expr.fvarB Expr.hasLP

/-- Explicit expected observation, independent of the run. Keys are child-first;
    ctor records are in actual depth-first walk order. -/
def expected : NestedPositivity :=
 { keys := #[towerKey 0,towerKey 1]
   kinds := [[[.ordinary],[.nested false]]]
   normals := [[arr A X,arr (tower 2) X]]
   ctorNfs := #[
    ⟨leafCV.name,[],[A],arr A tr⟩,
    ⟨nilCV.name,[.zero],[l tr],l (l tr)⟩,
    ⟨nilCV.name,[.zero],[tr],l tr⟩,
    ⟨consCV.name,[.zero],[tr],arr tr (arr (l tr) (l tr))⟩,
    ⟨consCV.name,[.zero],[l tr],arr (l tr) (arr (l (l tr)) (l (l tr)))⟩,
    ⟨nodeCV.name,[],[A],arr (l (l tr)) tr⟩] }

attribute [local cbv_opaque] checker

private theorem wa (d : Nat) : (checker 7).whnf (En 2) d A = .ok A := by
 apply whnf_mono (show 2 ≤ 7 by decide)
 change whnfBody (pureFns .verified (En 2) 1) (En 2) d A = .ok A
 unfold whnfBody whnfLoopFuel
 rfl
private theorem wx (d : Nat) : (checker 7).whnf (En 2) d X = .ok X :=
 whnf_mono (by decide) (Core.whnf_X (N := 2) d)
private theorem wy (d : Nat) : (checker 7).whnf (En 2) d Y = .ok Y :=
 whnf_self 2 7 d (by decide)
private theorem wl (a : Expr) (d : Nat) : (checker 7).whnf (En 2) d (l a) = .ok (l a) :=
 whnf_mono (by decide) (Core.whnf_list (N := 2) a d)
private theorem il (n : Nat) (h : n ≤ 2) :
 (checker 7).inferType (En 2) 2 (tower n) = .ok S :=
 (Core.tower_core_certificate (N := 2) n 2 7 (by omega) (by omega)).1
private theorem il0 : (checker 7).inferType (En 2) 2 (l X) = .ok S := il 1 (by decide)
private theorem il1 : (checker 7).inferType (En 2) 2 (l (l X)) = .ok S := il 2 (by decide)
private theorem il3 : (checker 7).inferType (En 2) 3 (l X) = .ok S :=
 (Core.tower_core_certificate (N := 2) 1 3 7 (by omega) (by omega)).1
private theorem iy : (checker 7).inferType (En 2) 3 Y = .ok S :=
 inferTypeCore_mono (by decide) (Core.infer_Y (N := 2) 3 (by decide))
private theorem ileaf : (checker 7).inferType (En 2) 2 (arr A X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) := leaf_infer 2 7 (by decide)
private theorem inode : (checker 7).inferType (En 2) 2 (arr (l (l X)) X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) :=
 Core.node_crest_certificate (N := 2) 2 2 7 (by decide) (by decide)
private theorem icons0 : (checker 7).inferType (En 2) 3 (arr X (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) :=
 Core.cons_crest_certificate (N := 2) 0 3 7 (by decide) (by decide)
private theorem icons1 : (checker 7).inferType (En 2) 3 (arr (l X) (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) :=
 Core.cons_crest_certificate (N := 2) 1 3 7 (by decide) (by decide)
private theorem es (d : Nat) (u : Level) : (checker 7).ensureSort (En 2) d (.sort u) = .ok u :=
 ensure_sort 2 7 d u (by decide)
attribute [local cbv_eval] wa wx wy wl il0 il1 il3 iy ileaf inode icons0 icons1 es

attribute [local cbv_opaque] nestPos

private theorem ordinary_run (f d : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [] d 0 A st =
 .ok (.ordinary,A,st) := by
 rw [nestPos]
 cbv
private theorem member_run (f : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [holeAt 0] 3 0 X st =
 .ok (.recursive 0,X,st) := by
 rw [nestPos]
 cbv
private theorem self_run (f k : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [holeAt k] 4 0 Y st =
 .ok (.inProgress,Y,st) := by
 rw [nestPos]
 cbv
attribute [local cbv_eval] ordinary_run member_run self_run

private def innerNil : NestCtorNf := ⟨nilCV.name,[.zero],[tr],l tr⟩
private def innerCons : NestCtorNf := ⟨consCV.name,[.zero],[tr],arr tr (arr (l tr) (l tr))⟩
private def outerNil : NestCtorNf := ⟨nilCV.name,[.zero],[l tr],l (l tr)⟩
private def outerCons : NestCtorNf :=
 ⟨consCV.name,[.zero],[l tr],arr (l tr) (arr (l (l tr)) (l (l tr)))⟩

private theorem inner_run (f : Nat) (ns : Array NestCtorNf) :
 nestPos (checker 7) (En 2) (Cn 2) (f+2) [holeAt 1] 3 0 (l X)
 {active := [towerKey 1],ctorNfs := ns} =
 .ok (.nested false,l X,{keys := #[towerKey 0],active := [towerKey 1],
   ctorNfs := (ns.push innerNil).push innerCons}) := by
 rw [nestPos]
 cbv
attribute [local cbv_eval] inner_run

private theorem outer_run (f : Nat) (ns : Array NestCtorNf) :
 nestPos (checker 7) (En 2) (Cn 2) (f+3) [] 2 0 (l (l X))
 {ctorNfs := ns} =
 .ok (.nested false,l (l X),{keys := #[towerKey 0,towerKey 1],
   ctorNfs := (((ns.push outerNil).push innerNil).push innerCons).push outerCons}) := by
 rw [nestPos]
 cbv
attribute [local cbv_eval] outer_run

/-- Exact actual return record, no acceptance or derivation hypothesis. -/
theorem actual_output :
 nestedBlockPositivity (checker 7) (En 2) (Cn 2) [roots 2] = .ok expected := by
 cbv

#print axioms actual_output
end Tree2Observation
