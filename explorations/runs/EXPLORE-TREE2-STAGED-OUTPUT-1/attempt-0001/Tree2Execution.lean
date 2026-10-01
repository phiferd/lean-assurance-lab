import Tree2TowerCorrespondence

/- Local AI-authored finite output theorem. Historical sources unchanged. -/
namespace Tree2Execution
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial

set_option pp.deepTerms false
set_option pp.deepTerms.threshold 5
set_option pp.maxSteps 3000
-- One finite certificate list is reused while exposing successive walk stages.
set_option linter.unusedSimpArgs false
set_option maxRecDepth 200000
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

attribute [local cbv_opaque] whnf inferTypeCore ensureSortCore

private theorem find_list : (En 2).find? Ln = some (.indInfo listCV {sortZ := .never, all := [Ln], nparams := 1, ctors := [nilCV.name,consCV.name]}) := rfl
private theorem find_nil : (En 2).find? nilCV.name = some (.ctorInfo nilCV 1 0) := rfl
private theorem find_cons : (En 2).find? consCV.name = some (.ctorInfo consCV 1 2) := rfl
private theorem find_tree : (En 2).find? Tn = some (.indInfo treeCV {sortZ := .never, all := [Tn], nparams := 1, ctors := [leafCV.name,nodeCV.name]}) := rfl
attribute [local cbv_eval] find_list find_nil find_cons find_tree

private theorem wa (d : Nat) : whnf .verified (En 2) 7 d A = .ok A := by
 apply whnf_mono (show 2 ≤ 7 by decide)
 change whnfBody (pureFns .verified (En 2) 1) (En 2) d A = .ok A
 unfold whnfBody whnfLoopFuel
 rfl
private theorem wx (d : Nat) : whnf .verified (En 2) 7 d X = .ok X :=
 whnf_mono (f' := 7) (by decide) (Core.whnf_X (N := 2) d)
private theorem wy (d : Nat) : whnf .verified (En 2) 7 d Y = .ok Y :=
 whnf_self 2 7 d (by decide)
private theorem wl (a : Expr) (d : Nat) : whnf .verified (En 2) 7 d (l a) = .ok (l a) :=
 whnf_mono (f' := 7) (by decide) (Core.whnf_list (N := 2) a d)
private theorem il (n : Nat) (h : n ≤ 2) :
 inferTypeCore .verified (En 2) 7 2 (tower n) = .ok S :=
 (Core.tower_core_certificate (N := 2) n 2 7 (by omega) (by omega)).1
private theorem il0 : inferTypeCore .verified (En 2) 7 2 (l X) = .ok S := il 1 (by decide)
private theorem il1 : inferTypeCore .verified (En 2) 7 2 (l (l X)) = .ok S := il 2 (by decide)
private theorem il3 : inferTypeCore .verified (En 2) 7 3 (l X) = .ok S :=
 (Core.tower_core_certificate (N := 2) 1 3 7 (by omega) (by omega)).1
private theorem iy : inferTypeCore .verified (En 2) 7 3 Y = .ok S :=
 inferTypeCore_mono (f' := 7) (by decide) (Core.infer_Y (N := 2) 3 (by decide))
private theorem ileaf : inferTypeCore .verified (En 2) 7 2 (arr A X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) := leaf_infer 2 7 (by decide)
private theorem inode : inferTypeCore .verified (En 2) 7 2 (arr (l (l X)) X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) :=
 Core.node_crest_certificate (N := 2) 2 2 7 (by decide) (by decide)
private theorem icons0 : inferTypeCore .verified (En 2) 7 3 (arr X (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) :=
 Core.cons_crest_certificate (N := 2) 0 3 7 (by decide) (by decide)
private theorem icons1 : inferTypeCore .verified (En 2) 7 3 (arr (l X) (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) :=
 Core.cons_crest_certificate (N := 2) 1 3 7 (by decide) (by decide)
private theorem es (d : Nat) (u : Level) : ensureSortCore .verified (En 2) 7 d (.sort u) = .ok u :=
 ensure_sort 2 7 d u (by decide)
attribute [local cbv_eval] wa wx wy wl il0 il1 il3 iy ileaf inode icons0 icons1 es

attribute [local cbv_opaque] nestPos
private theorem ordinary_run (f d : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [] d 0 A st =
 .ok (.ordinary,A,st) := by
 rw [nestPos]
 simp only [checker,fueledOps]
 rw [wa]
 cbv
private theorem member_run (f : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [holeAt 0] 3 0 X st =
 .ok (.recursive 0,X,st) := by
 rw [nestPos]
 simp only [checker,fueledOps]
 rw [wx]
 simp only [Cn,nestArity,find_tree]
 cbv
private theorem self_run (f k : Nat) (st : NestState) :
 nestPos (checker 7) (En 2) (Cn 2) (f+1) [holeAt k] 4 0 Y st =
 .ok (.inProgress,Y,st) := by
 rw [nestPos]
 simp only [checker,fueledOps]
 rw [wy]
 simp only [Cn,nestArity,find_list]
 cbv
attribute [local cbv_eval] ordinary_run member_run self_run

private def innerNil : NestCtorNf := ⟨nilCV.name,[.zero],[tr],l tr⟩
private def innerCons : NestCtorNf := ⟨consCV.name,[.zero],[tr],arr tr (arr (l tr) (l tr))⟩
private def outerNil : NestCtorNf := ⟨nilCV.name,[.zero],[l tr],l (l tr)⟩
private def outerCons : NestCtorNf :=
 ⟨consCV.name,[.zero],[l tr],arr (l tr) (arr (l (l tr)) (l (l tr)))⟩



private theorem inner_fields (f : Nat) (st : NestState) (err : CheckError) :
 nestFields (nestPos (checker 7) (En 2) (Cn 2) (f+1)) [holeAt 0] 3 err
  2 0 (arr X (arr Y Y)) st =
 .ok ([.recursive 0,.inProgress],[(X,bm),(Y,bm)],Y,st) := by
 simp only [nestFields,arr,pi]
 rw [member_run]
 simp only [bind,Except.bind]
 change (do
  let (ks,nds,cur,st') ← nestFields (nestPos (checker 7) (En 2) (Cn 2) (f+1))
   [holeAt 0] 3 err 1 1 (arr Y Y) st
  pure (.recursive 0 :: ks,(X,bm) :: nds,cur,st')) = _
 simp only [nestFields,arr,pi]
 rw [self_run]
 rfl

theorem inner_ctors (f : Nat) (st : NestState) :
 nestCtors (Cn 2) (checker 7) (En 2)
  (fun _ => nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [holeAt 0] 3 [.zero] [X] [Ln] [Y] listCs st =
 .ok ([([],Y),([.recursive 0,.inProgress],arr X (arr Y Y))],
   {st with ctorNfs := (st.ctorNfs.push innerNil).push innerCons}) := by
 have hn : Name.nodup nilCV.levelParams = true := by decide
 have hc : Name.nodup consCV.levelParams = true := by decide
 have cn : nestCrest [Ln] [.zero] [X] [Y]
   (nilCV.type.instantiateLevelParams nilCV.levelParams [.zero]) = some Y := rfl
 have cc : nestCrest [Ln] [.zero] [X] [Y]
   (consCV.type.instantiateLevelParams consCV.levelParams [.zero]) = some (arr X (arr Y Y)) := rfl
 simp only [listCs,nestCtors,hn,hc,Bool.not_true,if_false,cn,cc,unwrapOr,
  checker,fueledOps,iy,icons0,es,bind,Except.bind,pure,Except.pure]
 trace_state

#print axioms inner_fields
#print axioms inner_ctors
end Tree2Execution
