import Tree2TowerCorrespondence

/- Local AI-authored finite output theorem. Historical sources unchanged. -/
namespace Tree2Execution
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial

set_option pp.deepTerms false
set_option pp.deepTerms.threshold 5
set_option pp.maxSteps 3000
-- One finite certificate list is reused while exposing successive walk stages.
set_option linter.unusedSimpArgs false
set_option maxRecDepth 2000
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
  pure (NestFieldKind.recursive 0 :: ks,(X,bm) :: nds,cur,st')) = _
 simp only [nestFields,arr,pi]
 rw [self_run]
 rfl


private theorem nil_ctor (f : Nat) (st : NestState) :
 nestCtors (Cn 2) (checker 7) (En 2)
  (fun _ => nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [holeAt 0] 3 [.zero] [X] [Ln] [Y] [(nilCV,0)] st =
 .ok ([([],Y)],{st with ctorNfs := st.ctorNfs.push innerNil}) := by
 have hn : Name.nodup nilCV.levelParams = true := by decide
 have cn : nestCrest [Ln] [.zero] [X] [Y]
   (nilCV.type.instantiateLevelParams nilCV.levelParams [.zero]) = some Y := rfl
 rw [nestCtors]
 simp only [hn,Bool.not_true,if_false,cn,unwrapOr,checker,fueledOps,
  if_true,bind,Except.bind,pure,Except.pure]
 rw [iy]
 simp only [bind,Except.bind]
 simp only [S]
 rw [es]
 simp only [bind,Except.bind]
 cbv


private theorem ciy : (checker 7).inferType (En 2) 3 Y = .ok S := iy
private theorem cic : (checker 7).inferType (En 2) 3 (arr X (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) := icons0
private theorem ces (d : Nat) (u : Level) :
 (checker 7).ensureSort (En 2) d (.sort u) = .ok u := es d u

private theorem cons_ctor (f : Nat) (st : NestState) :
 nestCtors (Cn 2) (checker 7) (En 2)
  (fun _ => nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [holeAt 0] 3 [.zero] [X] [Ln] [Y] [(consCV,2)] st =
 .ok ([([.recursive 0,.inProgress],arr X (arr Y Y))],
  {st with ctorNfs := st.ctorNfs.push innerCons}) := by
 have hc : Name.nodup consCV.levelParams = true := by decide
 have cc : nestCrest [Ln] [.zero] [X] [Y]
   (consCV.type.instantiateLevelParams consCV.levelParams [.zero]) = some (arr X (arr Y Y)) := rfl
 have hr : (nestResHead Y && Y.getAppArgs.all
  (fun x => !x.nestOcc (Cn 2).names (Cn 2).nP 3)) = true := rfl
 have hnf : nestCtorNf (Cn 2) [holeAt 0] 3 [.zero] [X] consCV [(X,bm),(Y,bm)] Y = innerCons := by cbv
 have hclose : closeTelescope [(X,bm),(Y,bm)] 3 Y = arr X (arr Y Y) := rfl
 rw [nestCtors]
 simp only [hc,if_true,cc,unwrapOr,pure_bind]
 rw [cic]
 simp only [show (Except.ok : Expr → CheckM Expr) = pure from rfl,pure_bind]
 rw [ces]
 simp only [show (Except.ok : Level → CheckM Level) = pure from rfl,pure_bind]
 rw [inner_fields]
 simp only [show (Except.ok : (List NestFieldKind × List (Expr × BinderMeta) × Expr × NestState) → CheckM _) = pure from rfl,pure_bind]
 rw [cons_u4]
 simp only [Bool.false_eq_true,if_false]
 rw [hr]
 simp only [if_true,hnf,hclose,nestCtors,pure_bind]
 rfl


private theorem ite_bind {α β : Type} (p : Prop) [Decidable p]
 (x y : CheckM α) (k : α → CheckM β) :
 ((if p then x else y) >>= k) = if p then x >>= k else y >>= k := by
 split <;> rfl

/-- Reuse the ordinary concatenation equation already proved privately in
    Tree2TowerWalk; no new positivity invariant or acceptance premise. -/
private theorem ctor_append (ctx : NestCtx) (ops : CheckerOps CheckM) (env : Env)
 (rec : Expr → List NestHole → Nat → Nat → Expr → NestState → CheckM (NestFieldKind × Expr × NestState))
 (prog : List NestHole) (hi : Nat) (us : List Level) (ds : List Expr)
 (names : List Name) (holes : List Expr) (xs ys : List (ConstantVal × Nat)) (st : NestState) :
 nestCtors ctx ops env rec prog hi us ds names holes (xs++ys) st = (do
  let (os,st') ← nestCtors ctx ops env rec prog hi us ds names holes xs st
  let (ps,st'') ← nestCtors ctx ops env rec prog hi us ds names holes ys st'
  pure (os++ps,st'')) := by
 induction xs generalizing st with
 | nil =>
  simp only [List.nil_append,nestCtors,bind,Except.bind,pure,Except.pure]
  cases nestCtors ctx ops env rec prog hi us ds names holes ys st <;> rfl
 | cons x xs ih =>
  rcases x with ⟨cv,nf⟩
  simp only [List.cons_append,nestCtors]
  simp only [ih]
  simp only [bind_assoc,ite_bind,pure_bind,List.cons_append]

/-- Actual fixed-N=2 inner List constructor execution, for any initial state
    and any fuel excess f. All kinds, crests and two appended records are exact. -/
theorem inner_ctors (f : Nat) (st : NestState) :
 nestCtors (Cn 2) (checker 7) (En 2)
  (fun _ => nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [holeAt 0] 3 [.zero] [X] [Ln] [Y] listCs st =
 .ok ([([],Y),([.recursive 0,.inProgress],arr X (arr Y Y))],
  {st with ctorNfs := (st.ctorNfs.push innerNil).push innerCons}) := by
 change nestCtors _ _ _ _ _ _ _ _ _ _ ([(nilCV,0)]++[(consCV,2)]) st = _
 rw [ctor_append,nil_ctor]
 simp only [show (Except.ok : (List (List NestFieldKind × Expr) × NestState) → CheckM _) = pure from rfl,pure_bind]
 rw [cons_ctor]
 rfl


/-- The actual inner frame emits the exact two-record update. This frame
    starts with an empty progress stack even inside an active outer frame. -/
theorem inner_frame (f : Nat) (st : NestState) :
 nestFrame (Cn 2) (checker 7) (En 2)
  (nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [] 2 [.zero] [X] 1 [(Ln,S)] st =
 .ok {st with ctorNfs := (st.ctorNfs.push innerNil).push innerCons} := by
 have hi : (checker 7).inferType (En 2) 2
  (Expr.mkAppN (.const ([(Ln,S)].headD default).1 [.zero]) [X]) = .ok S := il0
 have hg : nestGroupCtors (m := CheckM) (Cn 2) 1 ([(Ln,S)].map (·.1)) = .ok listCs := rfl
 rw [nestFrame,hi]
 simp only [show (Except.ok : Expr → CheckM Expr) = pure from rfl,pure_bind]
 rw [hg]
 simp only [show (Except.ok : List (ConstantVal × Nat) → CheckM _) = pure from rfl,pure_bind]
 change (do
  let (_,st') ← nestCtors (Cn 2) (checker 7) (En 2)
   (fun _ => nestPos (checker 7) (En 2) (Cn 2) (f+1))
   [holeAt 0] 3 [.zero] [X] [Ln] [Y] listCs st
  pure st') = _
 rw [inner_ctors]
 rfl


private theorem inner_new (f : Nat) (ns : Array NestCtorNf) :
 nestContNew (Cn 2) (checker 7) (En 2)
  (nestPos (checker 7) (En 2) (Cn 2) (f+1))
  [holeAt 1] 0 Ln [.zero] [X] 1 S
  {active := [towerKey 1],ctorNfs := ns} =
 .ok (.nested false,{keys := #[towerKey 0],active := [towerKey 1],ctorNfs := (ns.push innerNil).push innerCons}) := by
 have hw : nestWalkStack (Cn 2) [holeAt 1] [X] = [] := stack_reset 2 0 _
 have hm : nestFrameMates (Cn 2) Ln = [] := rfl
 rw [nestContNew,hw,hm]
 simp only [nestGrowGroup,pure_bind]
 change (do
  let st' ← nestFrame (Cn 2) (checker 7) (En 2)
   (nestPos (checker 7) (En 2) (Cn 2) (f+1)) [] 2 [.zero] [X] 1 [(Ln,S)]
   {active := [towerKey 0,towerKey 1],ctorNfs := ns}
  pure (NestFieldKind.nested false,{st' with active := [towerKey 1],
    keys := nestAcceptGroup [.zero] [X] [(Ln,S)] st'.keys})) = _
 rw [inner_frame]
 rfl

#print axioms inner_fields
#print axioms nil_ctor
#print axioms cons_ctor
#print axioms inner_ctors
#print axioms inner_frame
#print axioms inner_new
end Tree2Execution
