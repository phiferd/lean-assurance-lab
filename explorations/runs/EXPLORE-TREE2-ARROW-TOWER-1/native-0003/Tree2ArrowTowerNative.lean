import Tree2ArrowTowerSchema

/- Local AI-authored parametric native facts. Core/frame proof text reused from
   the prior checked family and rechecked against the actual new function node
   stored at every N. Final certificates discharge all finite Core subcalls. -/
namespace Tree2ArrowTowerNative
open ConLeche Tree2Bridge Tree2TowerSupport
set_option maxRecDepth 20000
set_option maxHeartbeats 1000000

def En (N : Nat) : Env := Tree2ArrowTowerSchema.env false N
def Cn (N : Nat) : NestCtx := Tree2ArrowTowerSchema.ctx false N
def checker (fuel : Nat) : CheckerOps CheckM := fueledOps .verified fuel

namespace Core
variable {N : Nat}
theorem infer_list_head (d : Nat) :
    inferTypeCore .verified (En N) 1 d (.const Ln [.zero]) = .ok (arr S S) := by
  rfl

theorem whnf_former (d : Nat) :
    whnf .verified (En N) 2 d (arr S S) = .ok (arr S S) := by
  change whnfBody (pureFns .verified (En N) 1) (En N) d (arr S S) = .ok (arr S S)
  unfold whnfBody whnfLoopFuel
  rfl

theorem whnf_list (a : Expr) (d : Nat) :
    whnf .verified (En N) 3 d (l a) = .ok (l a) := by
  change whnfBody (pureFns .verified (En N) 2) (En N) d (l a) = .ok (l a)
  unfold whnfBody whnfLoopFuel
  rfl

theorem whnf_X (d : Nat) : whnf .verified (En N) 2 d X = .ok X := by
  change whnfBody (pureFns .verified (En N) 1) (En N) d X = .ok X
  unfold whnfBody whnfLoopFuel
  rfl

theorem defeq_S (d : Nat) : isDefEqCore .verified (En N) 1 d S S = .ok true := by
  change defeqBody .verified (pureFns .verified (En N) 0) (En N) d S S = .ok true
  unfold defeqBody defeqLoopFuel
  rfl

theorem infer_X (d : Nat) (hd : 2 ≤ d) :
    inferTypeCore .verified (En N) 1 d X = .ok S := by
  have hs : 1 < d := by omega
  rw [inferTypeCore_succ]
  simp [inferBody, X, hs]
  rfl

/-- One List layer: all Core subcalls are proved for this explicit environment.
    The argument success is an induction interface, not a final premise. -/
theorem infer_list_step (a : Expr) (d f : Nat) (hf : 2 ≤ f)
    (ha : inferTypeCore .verified (En N) f d a = .ok S) :
    inferTypeCore .verified (En N) (f+1) d (l a) = .ok S := by
  have hc := inferTypeCore_mono (mode := .verified) (show 1 ≤ f by omega) (infer_list_head (N := N) d)
  have hw := whnf_mono (mode := .verified) hf (whnf_former (N := N) d)
  have he := isDefEqCore_mono (mode := .verified) (show 1 ≤ f by omega) (defeq_S (N := N) d)
  rw [inferTypeCore_succ]
  simp only [l, inferBody, infer_def, whnf_def, defeq_def]
  rw [hc]
  simp only [bind, Except.bind]
  rw [hw]
  simp only [arr, pi]
  rw [ha]
  simp only
  rw [he]
  rfl

/-- A conservative, derived inference bound: base3; each app adds one. -/
theorem infer_tower_at_bound (n d : Nat) (hd : 2 ≤ d) :
    inferTypeCore .verified (En N) (n+3) d (tower n) = .ok S := by
  induction n with
  | zero =>
    exact inferTypeCore_mono (by omega) (infer_X (N := N) d hd)
  | succ n ih =>
    exact infer_list_step (N := N) (tower n) d (n+3) (by omega) ih

/-- Uniform head-only reduction: the parameter tower is never traversed. -/
theorem whnf_tower_at_bound (n d : Nat) :
    whnf .verified (En N) 3 d (tower n) = .ok (tower n) := by
  cases n with
  | zero => exact whnf_mono (by omega) (whnf_X (N := N) d)
  | succ n => exact whnf_list (N := N) (tower n) d

/-- Actual verified outcomes for all larger fuels. No successful-operation,
    positivity, or acceptance premise appears in this certificate. -/
theorem tower_core_certificate (n d fuel : Nat) (hd : 2 ≤ d)
    (hf : n+3 ≤ fuel) :
    inferTypeCore .verified (En N) fuel d (tower n) = .ok S ∧
    whnf .verified (En N) fuel d (tower n) = .ok (tower n) ∧
    (tower n).fvarB ≤ d ∧ (tower n).looseBVarsBounded 0 = true := by
  refine ⟨inferTypeCore_mono hf (infer_tower_at_bound (N := N) n d hd),
    whnf_mono (by omega) (whnf_tower_at_bound (N := N) n d), ?_, tower_closed n⟩
  rw [Expr.fvarB_eq, tower_range]
  exact hd

theorem whnf_sort (u : Level) (d : Nat) :
    whnf .verified (En N) 2 d (.sort u) = Except.ok (Expr.sort u) := by
  change whnfBody (pureFns .verified (En N) 1) (En N) d (.sort u) = Except.ok (Expr.sort u)
  unfold whnfBody whnfLoopFuel
  rfl

theorem whnf_S (d : Nat) : whnf .verified (En N) 2 d S = .ok S :=
  whnf_sort (N := N) (.succ .zero) d

theorem infer_Y (d : Nat) (hd : 3 ≤ d) :
    inferTypeCore .verified (En N) 1 d Y = .ok S := by
  have hs : 2 < d := by omega
  rw [inferTypeCore_succ]
  simp [inferBody, Y, hs]
  rfl

/-- Root node crest; the inferred sort is the actual imax, not Sort1. -/
theorem infer_node_crest_at_bound (n d : Nat) (hd : 2 ≤ d) :
    inferTypeCore .verified (En N) (n+4) d (arr (tower n) X) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.succ .zero))) := by
  have ht := infer_tower_at_bound (N := N) n d hd
  have hx := inferTypeCore_mono (mode := .verified)
    (show 1 ≤ n+3 by omega) (infer_X (N := N) (d+1) (by omega))
  have hs := whnf_mono (mode := .verified)
    (show 2 ≤ n+3 by omega) (whnf_S (N := N) d)
  have hb := whnf_mono (mode := .verified)
    (show 2 ≤ n+3 by omega) (whnf_S (N := N) (d+1))
  rw [show n+4 = (n+3)+1 by omega, inferTypeCore_succ]
  simp only [arr, pi, inferBody, infer_def, whnf_def, ensureSort]
  rw [ht]
  simp only [bind, Except.bind]
  rw [hs]
  simp only
  change (do
    let bty ← inferTypeCore .verified (En N) (n+3) (d+1) X
    let v ← (do
      match ← whnf .verified (En N) (n+3) (d+1) bty with
      | .sort v => pure v
      | _ => throw (CheckError.invalid "expected a sort"))
    if Level.zeronessOf v == bm.pw then
      pure (Expr.sort (.imax (.succ .zero) v))
    else throw (CheckError.notImplemented "sort-annotation mismatch (forall-cod)")) =
    Except.ok (Expr.sort (.imax (.succ .zero) (.succ .zero)))
  rw [hx]
  simp only [bind, Except.bind]
  rw [hb]
  rfl

theorem infer_self_arrow (d : Nat) (hd : 3 ≤ d) :
    inferTypeCore .verified (En N) 4 d (arr Y Y) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.succ .zero))) := by
  have hy := inferTypeCore_mono (mode := .verified) (show 1 ≤ 3 by omega) (infer_Y (N := N) d hd)
  have hyb := inferTypeCore_mono (mode := .verified) (show 1 ≤ 3 by omega) (infer_Y (N := N) (d+1) (by omega))
  have hs := whnf_mono (mode := .verified) (show 2 ≤ 3 by omega) (whnf_S (N := N) d)
  have hsb := whnf_mono (mode := .verified) (show 2 ≤ 3 by omega) (whnf_S (N := N) (d+1))
  rw [inferTypeCore_succ]
  simp only [arr, pi, inferBody, infer_def, whnf_def, ensureSort]
  rw [hy]
  simp only [bind, Except.bind]
  rw [hs]
  simp only
  change (do
    let bty ← inferTypeCore .verified (En N) 3 (d+1) Y
    let v ← (do
      match ← whnf .verified (En N) 3 (d+1) bty with
      | .sort v => pure v
      | _ => throw (CheckError.invalid "expected a sort"))
    if Level.zeronessOf v == bm.pw then pure (Expr.sort (.imax (.succ .zero) v))
    else throw (CheckError.notImplemented "sort-annotation mismatch (forall-cod)")) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.succ .zero)))
  rw [hyb]
  simp only [bind, Except.bind]
  rw [hsb]
  rfl

/-- List cons crest: one symbolic parameter and the current frame self tail. -/
theorem infer_cons_crest_at_bound (n d : Nat) (hd : 3 ≤ d) :
    inferTypeCore .verified (En N) (n+5) d (arr (tower n) (arr Y Y)) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) := by
  have ht := inferTypeCore_mono (mode := .verified) (show n+3 ≤ n+4 by omega)
    (infer_tower_at_bound (N := N) n d (by omega))
  have hi := inferTypeCore_mono (mode := .verified) (show 4 ≤ n+4 by omega)
    (infer_self_arrow (N := N) (d+1) (by omega))
  have hs := whnf_mono (mode := .verified) (show 2 ≤ n+4 by omega)
    (whnf_S (N := N) d)
  have hsb := whnf_mono (mode := .verified) (show 2 ≤ n+4 by omega)
    (whnf_sort (N := N) (.imax (.succ .zero) (.succ .zero)) (d+1))
  rw [show n+5 = (n+4)+1 by omega, inferTypeCore_succ]
  simp only [arr, pi, inferBody, infer_def, whnf_def, ensureSort]
  rw [ht]
  simp only [bind, Except.bind]
  rw [hs]
  simp only
  change (do
    let bty ← inferTypeCore .verified (En N) (n+4) (d+1) (arr Y Y)
    let v ← (do
      match ← whnf .verified (En N) (n+4) (d+1) bty with
      | .sort v => pure v
      | _ => throw (CheckError.invalid "expected a sort"))
    if Level.zeronessOf v == bm.pw then pure (Expr.sort (.imax (.succ .zero) v))
    else throw (CheckError.notImplemented "sort-annotation mismatch (forall-cod)")) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero))))
  rw [hi]
  simp only [bind, Except.bind]
  rw [hsb]
  rfl

theorem node_crest_certificate (n d fuel : Nat) (hd : 2 ≤ d) (hf : n+4 ≤ fuel) :
    inferTypeCore .verified (En N) fuel d (arr (tower n) X) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.succ .zero))) :=
  inferTypeCore_mono hf (infer_node_crest_at_bound (N := N) n d hd)

theorem cons_crest_certificate (n d fuel : Nat) (hd : 3 ≤ d) (hf : n+5 ≤ fuel) :
    inferTypeCore .verified (En N) fuel d (arr (tower n) (arr Y Y)) =
      Except.ok (Expr.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) :=
  inferTypeCore_mono hf (infer_cons_crest_at_bound (N := N) n d hd)

end Core

def fieldKind (k : Nat) (kb : Nat := 0) : NestFieldKind :=
 match k with
 | 0 => if kb = 0 then .recursive 0 else .reflexive 0
 | _+1 => .nested (kb != 0)
def holeAt (k : Nat) : NestHole := ⟨towerKey k,2⟩
def FreshBelow (k : Nat) (act : List NestKey) : Prop :=
  ∀ i, i < k → towerKey i ∉ act

theorem fresh_push (k : Nat) (act : List NestKey) (h : FreshBelow (k+1) act) :
  FreshBelow k (towerKey k :: act) := by
  intro i hi hm
  simp only [List.mem_cons] at hm
  rcases hm with he | hm
  · have hh := ((tower_key_frame k []).2.2 i).mp he
    omega
  · exact h i (by omega) hm

theorem tower_occ (N k : Nat) (prog : List NestHole) :
  (tower k).nestOcc (Cn N).names (Cn N).nP ((Cn N).hiAt prog.length) = true := by
  induction k with
  | zero => simp [tower, X, Expr.nestOcc, Cn, Tree2ArrowTowerSchema.ctx, NestCtx.hiAt]; omega
  | succ k ih =>
    simp [tower, l, Expr.nestOcc, Cn, Tree2ArrowTowerSchema.ctx, Ln, Tn, nm] at ih ⊢
    exact ih

theorem tower_scope (k d : Nat) (hd : 2 ≤ d) : Expr.WScoped d (tower k) := by
  induction k with
  | zero => simp [tower, X, S, Expr.WScoped]; omega
  | succ k ih => simp [tower, l, Expr.WScoped, ih]

theorem tower_bvar (k : Nat) : (tower k).bvarB = 0 := by
  rw [Expr.bvarB_eq]
  exact Nat.eq_zero_of_le_zero (Expr.looseBVarsBounded_iff.mp (tower_closed k))

theorem frame_scoped (N k : Nat) : ProgScoped (Cn N) [holeAt k] := by
  have hp : ∀ x ∈ [tower k], Expr.WScoped ((Cn N).hiAt 0) x := by
    intro x hx
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
    subst x
    exact tower_scope k 2 (by omega)
  exact ProgScoped.push (ctx := Cn N) (us := [.zero]) (ds := [tower k])
    ProgScoped.nil hp [(Ln,S)]

theorem stack_reset (N k : Nat) (prog : List NestHole) :
  nestWalkStack (Cn N) prog [tower k] = [] :=
  (tower_key_frame k prog).2.1

theorem list_container (N : Nat) : nestContainer (Cn N) Ln = some (1,listCs) := by rfl
theorem list_inst (N k hi : Nat) :
  nestInstType (m := CheckM) (Cn N) hi (towerKey k) = .ok (0,S) := by rfl

theorem ensure_sort (N F d : Nat) (u : Level) (hf : 2 ≤ F) :
  (checker F).ensureSort (En N) d (.sort u) = .ok u := by
  change ensureSort (pureFns .verified (En N) F) (En N) d (.sort u) = .ok u
  unfold ensureSort
  rw [whnf_def, whnf_mono hf (Core.whnf_sort (N := N) u d)]
  rfl

theorem whnf_self (N F d : Nat) (hf : 2 ≤ F) :
  (checker F).whnf (En N) d Y = .ok Y := by
  apply whnf_mono hf
  change whnfBody (pureFns .verified (En N) 1) (En N) d Y = .ok Y
  unfold whnfBody whnfLoopFuel
  rfl

theorem member_field (N F : Nat) (hf : 2 ≤ F)
  (act : List NestKey) (prog : List NestHole) (d : Nat) (kb : Nat := 0) :
  PosDR (checker F) (En N) (Cn N) 1
    (.field act prog d kb X (if kb = 0 then .recursive 0 else .reflexive 0) X) := by
  apply PosDR.hole (w := X) (i := 1) (ty := S) (n := 0)
  · exact whnf_mono hf (Core.whnf_X (N := N) d)
  · exact tower_occ N 0 prog
  · rfl
  · change 1 ≤ 1; omega
  · change 1 < 2; omega
  · rfl
  · simp [X, Expr.getAppArgs]

theorem self_field (N F k : Nat) (hf : 2 ≤ F) (act : List NestKey) (d : Nat) :
  PosDR (checker F) (En N) (Cn N) 1
    (.field act [holeAt k] d 0 Y .inProgress Y) := by
  apply PosDR.frameHole (w := Y) (i := 2) (ty := S) (h := holeAt k) (n := 0)
  · exact whnf_self N F d hf
  · rfl
  · rfl
  · change 2 ≤ 2; omega
  · change 2 < 3; omega
  · rfl
  · simp [Y, Expr.getAppArgs]
  · rfl

theorem cons_u4 (a : Expr) (k : NestFieldKind) :
  ((List.range 2).any fun i => [k,.inProgress].getD i .ordinary != .ordinary &&
    structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 i) = false := by
  have hc : closeTelescope [(a,bm),(Y,bm)] 3 Y = arr a (arr Y Y) := rfl
  have hy : Y.hasLooseBVarB 0 = false := by
    rw [Expr.hasLooseBVarB.eq_def, Expr.bvarB_eq]
    rfl
  have hyy : (arr Y Y).hasLooseBVarB 0 = false := by
    rw [Expr.hasLooseBVarB.eq_def, Expr.bvarB_eq]
    have hb : (arr Y Y).bvarBound = 0 := rfl
    rw [hb]
    rfl
  have h0 : structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 0 = false := by
    rw [hc]; exact hyy
  have h1 : structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 1 = false := by
    rw [hc]; exact hy
  simp [List.range_succ, h0, h1]

theorem node_u4 (a : Expr) (k : NestFieldKind) :
  ((List.range 1).any fun i => [k].getD i .ordinary != .ordinary &&
    structUsedLater (closeTelescope [(a,bm)] 2 X) 0 i) = false := by
  have h0 : structUsedLater (closeTelescope [(a,bm)] 2 X) 0 0 = false := by
    change X.hasLooseBVarB 0 = false
    rw [Expr.hasLooseBVarB.eq_def, Expr.bvarB_eq]
    rfl
  simp [List.range_succ, h0]

/-- A field tower under arbitrary scoped progress and active ancestors.
    The strengthened freshness invariant supplies every inner container key. -/
theorem tower_field (N F : Nat) (hf : N+5 ≤ F) (k : Nat) (hk : k ≤ N)
    (act : List NestKey) (prog : List NestHole) (d : Nat)
    (ha : FreshBelow k act) (hp : ProgScoped (Cn N) prog) (kb : Nat := 0) :
    PosDR (checker F) (En N) (Cn N) (k+1)
      (.field act prog d kb (tower k) (fieldKind k kb) (tower k)) := by
  induction k generalizing act prog d kb with
  | zero => exact member_field N F (by omega) act prog d kb
  | succ k ih =>
    have hfr : PosDR (checker F) (En N) (Cn N) (k+1)
        (.frame act [] [.zero] [tower k] [(Ln,S)]) := by
      apply PosDR.frame (m := k+1) (ctors := listCs)
      · simp
      · exact ⟨by rfl, by decide⟩
      · exact ⟨listCs,list_container N⟩
      · simp
      · intro p hpm
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hpm
        subst p
        exact ⟨0,list_inst N k 2⟩
      · simp
      · rfl
      · rfl
      · exact ⟨S, (Core.tower_core_certificate (N := N) (k+1) 2 F
          (by omega) (by omega)).1⟩
      · omega
      · change PosDR (checker F) (En N) (Cn N) (k+1)
          (.ctors (towerKey k :: act) [holeAt k] 3 [.zero] [tower k] [Ln] [Y] listCs)
        apply PosDR.ctorsCons (crest := Y) (ty := S) (sv := .succ .zero)
          (m₁ := 0) (m₂ := k+1) (ks := []) (nds := []) (cur := Y)
        · decide
        · exact (tower_list_crest k).1
        · exact inferTypeCore_mono (by omega) (Core.infer_Y (N := N) 3 (by omega))
        · exact ensure_sort N F 3 (.succ .zero) (by omega)
        · omega
        · exact PosDR.teleNil
        · rfl
        · rfl
        · rfl
        · omega
        · apply PosDR.ctorsCons (crest := arr (tower k) (arr Y Y))
            (ty := .sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero))))
            (sv := .imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))
            (m₁ := k+1) (m₂ := 0) (ks := [fieldKind k,.inProgress])
            (nds := [(tower k,bm),(Y,bm)]) (cur := Y)
          · decide
          · exact (tower_list_crest k).2.1
          · exact Core.cons_crest_certificate (N := N) k 3 F (by omega) (by omega)
          · exact ensure_sort N F 3 _ (by omega)
          · omega
          · apply PosDR.teleCons (m₁ := k+1) (m₃ := 1)
            · omega
            · exact ih (by omega) (towerKey k :: act) [holeAt k] 3
                (fresh_push k act ha) (frame_scoped N k) 0
            · omega
            · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
              · omega
              · exact self_field N F k (by omega) _ 4
              · omega
              · exact PosDR.teleNil
          · exact cons_u4 (tower k) (fieldKind k)
          · rfl
          · rfl
          · omega
          · exact PosDR.ctorsNil
    apply PosDR.cont (w := tower (k+1)) (c := Ln) (us := [.zero]) (L := listCs)
      (nPc := 1) (nI := 0) (cty := S) (grp := [(Ln,S)]) (m := k+1)
    · exact whnf_mono (by omega) (Core.whnf_tower_at_bound (N := N) (k+1) d)
    · exact tower_occ N (k+1) prog
    · rfl
    · rfl
    · exact list_container N
    · rfl
    · decide
    · simp [tower, l, Expr.getAppArgs]
    · intro x hx
      have hxx : x = tower k := by simpa [tower, l, Expr.getAppArgs] using hx
      subst x
      refine ⟨tower_bvar k, ?_⟩
      rw [Expr.fvarB_eq, tower_range]
      change 2 ≤ 2 + prog.length
      omega
    · intro x hx
      have hxx : x = tower k := by simpa [tower, l, Expr.getAppArgs] using hx
      subst x
      exact tower_scope k _ (by change 2 ≤ 2 + prog.length; omega)
    · exact hp
    · exact list_inst N k _
    · exact ha k (by omega)
    · rfl
    · omega
    · change PosDR (checker F) (En N) (Cn N) (k+1)
        (.frame act (nestWalkStack (Cn N) prog [tower k]) [.zero] [tower k] [(Ln,S)])
      rw [stack_reset]
      exact hfr

theorem leaf_infer (N F : Nat) (hf : 4 ≤ F) :
  (checker F).inferType (En N) 2 (arr A X) =
    .ok (.sort (.imax (.succ .zero) (.succ .zero))) := by
  apply inferTypeCore_mono hf
  change inferTypeCore .verified (En N) 4 2 (arr A X) = _
  cbv

theorem ordinary_field (N F : Nat) (hf : 2 ≤ F) :
  PosDR (checker F) (En N) (Cn N) 1 (.field [] [] 2 0 A .ordinary A) := by
  apply PosDR.const (w := A) (n := 0)
  · apply whnf_mono hf
    change whnfBody (pureFns .verified (En N) 1) (En N) 2 A = .ok A
    unfold whnfBody whnfLoopFuel
    rfl
  · rfl


/-- A finite Core Pi certificate interface; its subcall premises are discharged
    on exact terms below, never assumed in the final bridge. -/
private theorem infer_arr (N : Nat) (a b : Expr) (u v : Level) (d f : Nat) (hf : 2 ≤ f)
 (ha : inferTypeCore .verified (En N) f d a = .ok (.sort u))
 (hb : inferTypeCore .verified (En N) f (d+1) b = .ok (.sort v))
 (hi : b.instantiate1 (.fvar d a) = b) (hv : Level.zeronessOf v = bm.pw) :
 inferTypeCore .verified (En N) (f+1) d (arr a b) = .ok (.sort (.imax u v)) := by
 have wu := whnf_mono hf (Core.whnf_sort (N := N) u d)
 have wv := whnf_mono hf (Core.whnf_sort (N := N) v (d+1))
 rw [inferTypeCore_succ]
 simp only [arr,pi,inferBody,infer_def,whnf_def,ensureSort]
 rw [ha]
 simp only [bind,Except.bind]
 rw [wu]
 simp only
 rw [hi,hb]
 simp only [bind,Except.bind]
 rw [wv]
 change (if Level.zeronessOf v == bm.pw then Except.ok (Expr.sort (.imax u v))
  else Except.error (CheckError.notImplemented "sort-annotation mismatch (forall-cod)")) = _
 rw [hv]
 simp only [BEq.rfl]
 rfl

private theorem infer_A (N : Nat) (d f : Nat) (hd : 1 ≤ d) (hf : 1 ≤ f) :
 inferTypeCore .verified (En N) f d A = .ok S := by
 apply inferTypeCore_mono hf
 rw [inferTypeCore_succ]
 have h : 0 < d := by omega
 simp [inferBody,A,h]
 rfl

theorem function_infer (N d F : Nat) (hd : 2 ≤ d) (hf : N+4 ≤ F) :
 inferTypeCore .verified (En N) F d (arr A (tower N)) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) := by
 cases F with
 | zero => omega
 | succ f =>
  apply infer_arr N A (tower N) (.succ .zero) (.succ .zero) d f (by omega)
  · exact infer_A N d f (by omega) (by omega)
  · exact (Core.tower_core_certificate (N := N) N (d+1) f (by omega) (by omega)).1
  · exact Expr.instantiate1_eq_self (tower_closed N)
  · rfl

theorem function_crest_infer (N F : Nat) (hf : N+5 ≤ F) :
 (checker F).inferType (En N) 2 (arr (arr A (tower N)) X) =
 .ok (.sort (.imax (.imax (.succ .zero) (.succ .zero)) (.succ .zero))) := by
 cases F with
 | zero => omega
 | succ f =>
  apply infer_arr N (arr A (tower N)) X (.imax (.succ .zero) (.succ .zero))
   (.succ .zero) 2 f (by omega)
  · exact function_infer N 2 f (by omega) (by omega)
  · exact inferTypeCore_mono (show 1 ≤ f by omega) (Core.infer_X (N := N) 3 (by omega))
  · rfl
  · rfl

def functionKind (N : Nat) : NestFieldKind := fieldKind N 1

theorem function_field (N F : Nat) (hf : N+5 ≤ F) :
 PosDR (checker F) (En N) (Cn N) (N+2)
 (.field [] [] 2 0 (arr A (tower N)) (functionKind N) (arr A (tower N))) := by
 have hab : (tower N).abstract1 2 = tower N :=
  Expr.abstract1_of_fvarRange_le _ _ _ (by rw [tower_range]; omega)
 have hpi : PosDR (checker F) (En N) (Cn N) (N+2)
  (.field [] [] 2 0 (arr A (tower N)) (functionKind N)
   (.forallE A ((tower N).abstract1 2) bm)) := by
  apply PosDR.pi (a := A) (b := tower N) (bm := bm) (nb := tower N) (m := N+1)
  · apply whnf_mono (show 2 ≤ F by omega)
    change whnfBody (pureFns .verified (En N) 1) (En N) 2 (arr A (tower N)) = _
    unfold whnfBody whnfLoopFuel
    rfl
  · have h := tower_occ N N []
    simpa [arr,pi,Expr.nestOcc,Cn,Tree2ArrowTowerSchema.ctx,A] using h
  · rfl
  · omega
  · rw [Expr.instantiate1_eq_self (tower_closed N)]
    exact tower_field N F hf N (by omega) [] [] 3
      (by intro i hi; simp) ProgScoped.nil 1
 simpa only [hab,arr,pi] using hpi

open Tree2TowerNative (pow pow_no_levels pow_inst pow_canon pow_fvars pow_X)

theorem node_no_levels (N : Nat) :
 (Tree2ArrowTowerSchema.node false N).type.hasLevelParam = false := by
 have h := pow_no_levels N (t (.bvar 1)) (by rfl)
 simp only [Tree2ArrowTowerSchema.node,pi,Expr.hasLevelParam,Bool.false_eq_true,if_false]
 rw [h]
 rfl

theorem node_crest (N : Nat) :
 nestCrest [Tn] [] [A] [X]
  ((Tree2ArrowTowerSchema.node false N).type.instantiateLevelParams [] []) =
 some (arr (arr A (tower N)) X) := by
 rw [Expr.instantiateLevelParams_eq_self (node_no_levels N)]
 unfold nestCrest nestCanonCrest
 change ((instPisWith [P] (pi S (pi (pi (.bvar 0) (pow N (t (.bvar 1)))) (t (.bvar 1))))).map
   (·.replaceApps (nestCanonSub [Tn] [] 1) 0 1)).map
   (·.replaceFVars (nestKeyMap [A] [X])) = _
 simp only [instPisWith,pi,Expr.instantiate1,pow_inst]
 change some ((arr (arr P (pow N (t P))) (t P)).replaceApps
   (nestCanonSub [Tn] [] 1) 0 1 |>.replaceFVars (nestKeyMap [A] [X])) = _
 have hq : (t P).replaceApps (nestCanonSub [Tn] [] 1) 0 1 = Q := rfl
 simp only [arr,pi,Expr.replaceApps,pow_canon,hq]
 simp only [Expr.replaceFVars,pow_fvars]
 have hx : Q.replaceFVars (nestKeyMap [A] [X]) = X := rfl
 rw [hx,pow_X]
 rfl

#print axioms function_infer
#print axioms function_crest_infer
#print axioms function_field
#print axioms node_crest
#print axioms tower_field
end Tree2ArrowTowerNative
