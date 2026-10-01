import Tree2TowerCore

/- Local AI-authored exploratory family derivation; no upstream submission. -/
namespace Tree2TowerNative
open ConLeche Tree2Bridge Tree2TowerSupport

def pow : Nat → Expr → Expr
  | 0, e => e
  | k+1, e => l (pow k e)

def node (N : Nat) : ConstantVal :=
  ⟨nodeCV.name, [], pi S (pi (pow N (t (.bvar 0))) (t (.bvar 1)))⟩
def roots (N : Nat) : List (ConstantVal × Nat) := [(leafCV,1),(node N,1)]
def En (N : Nat) : Env := ⟨[
  .indInfo listCV {sortZ := .never, all := [Ln], nparams := 1, ctors := [nilCV.name,consCV.name]},
  .ctorInfo nilCV 1 0, .ctorInfo consCV 1 2,
  .indInfo treeCV {sortZ := .never, all := [Tn], nparams := 1, ctors := [leafCV.name,(node N).name]},
  .ctorInfo leafCV 1 1, .ctorInfo (node N) 1 1]⟩
def Cn (N : Nat) : NestCtx := ⟨[Tn], [], 1, [0], [A], .succ .zero, (En N).find?⟩
def checker (fuel : Nat) : CheckerOps CheckM := fueledOps .verified fuel

/-- Exact interface; the actual family node is stored and changes with N. -/
theorem lookup_interface (N : Nat) :
  (En N).find? Ln = E.find? Ln ∧
  (En N).find? nilCV.name = E.find? nilCV.name ∧
  (En N).find? consCV.name = E.find? consCV.name ∧
  (En N).find? Tn = E.find? Tn ∧
  (En N).find? nodeCV.name = some (.ctorInfo (node N) 1 1) := by
  exact ⟨rfl,rfl,rfl,rfl,rfl⟩

theorem pow_X (n : Nat) : pow n X = tower n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [pow, tower, ih]


/- The checked Core argument is explicitly strengthened to the new exact
   family environment. Only the fixed List lookup is read by these calls;
   this is rechecked below, never inferred from arbitrary environment success. -/
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

theorem pow_inst (n : Nat) (e v : Expr) (d : Nat) :
  (pow n e).instantiate1 v d = pow n (e.instantiate1 v d) := by
  induction n with
  | zero => rfl
  | succ n ih => simp [pow, l, Expr.instantiate1, ih]

theorem pow_no_levels (n : Nat) (e : Expr) (h : e.hasLevelParam = false) :
  (pow n e).hasLevelParam = false := by
  induction n with
  | zero => exact h
  | succ n ih => simp [pow, l, Expr.hasLevelParam, Level.hasParam, ih]

theorem list_not_canonical_hit (e : Expr) :
  (l e).appHole? (nestCanonSub [Tn] [] 1) 0 1 = none := by
  cases e <;> simp [l, Expr.appHole?, Expr.phApp?, nestCanonSub]

theorem pow_canon (n : Nat) (e : Expr) :
  (pow n e).replaceApps (nestCanonSub [Tn] [] 1) 0 1 =
    pow n (e.replaceApps (nestCanonSub [Tn] [] 1) 0 1) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change (l (pow n e)).replaceApps _ 0 1 = l _
    rw [show l (pow n e) = Expr.app (.const Ln [.zero]) (pow n e) from rfl,
      Expr.replaceApps_app]
    rw [show (Expr.app (.const Ln [.zero]) (pow n e)).appHole?
      (nestCanonSub [Tn] [] 1) 0 1 = none from list_not_canonical_hit _]
    change l ((pow n e).replaceApps _ 0 1) = l _
    rw [ih]

theorem pow_fvars (n : Nat) (e : Expr) (f : Nat → Option Expr) :
  (pow n e).replaceFVars f = pow n (e.replaceFVars f) := by
  induction n with
  | zero => rfl
  | succ n ih => simp [pow, l, Expr.replaceFVars, ih]

theorem node_no_levels (n : Nat) : (node n).type.hasLevelParam = false := by
  have hp := pow_no_levels n (t (.bvar 0)) (by rfl)
  simp only [node, pi, Expr.hasLevelParam]
  rw [hp]
  rfl

theorem node_crest (n : Nat) :
  nestCrest [Tn] [] [A] [X]
    ((node n).type.instantiateLevelParams [] []) = some (arr (tower n) X) := by
  rw [Expr.instantiateLevelParams_eq_self (node_no_levels n)]
  unfold nestCrest nestCanonCrest
  change ((instPisWith [P] (pi S (pi (pow n (t (.bvar 0))) (t (.bvar 1))))).map
    (·.replaceApps (nestCanonSub [Tn] [] 1) 0 1)).map
    (·.replaceFVars (nestKeyMap [A] [X])) = some (arr (tower n) X)
  simp only [instPisWith, pi, Expr.instantiate1, pow_inst]
  change some ((arr (pow n (t P)) (t P)).replaceApps
    (nestCanonSub [Tn] [] 1) 0 1 |>.replaceFVars (nestKeyMap [A] [X])) =
      some (arr (tower n) X)
  have hq : (t P).replaceApps (nestCanonSub [Tn] [] 1) 0 1 = Q := rfl
  simp only [arr, pi, Expr.replaceApps, pow_canon, hq]
  simp only [Expr.replaceFVars, pow_fvars]
  have hx : Q.replaceFVars (nestKeyMap [A] [X]) = X := rfl
  rw [hx, pow_X]

def fieldKind : Nat → NestFieldKind
  | 0 => .recursive 0
  | _+1 => .nested false
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
  | zero => simp [tower, X, Expr.nestOcc, Cn, NestCtx.hiAt]; omega
  | succ k ih => simp [tower, l, Expr.nestOcc, ih, Cn, Ln, Tn, nm]

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
  (act : List NestKey) (prog : List NestHole) (d : Nat) :
  PosDR (checker F) (En N) (Cn N) 1
    (.field act prog d 0 X (.recursive 0) X) := by
  apply PosDR.hole (w := X) (i := 1) (ty := S) (n := 0)
  · exact whnf_mono hf (Core.whnf_X (N := N) d)
  · exact tower_occ N 0 prog
  · rfl
  · decide
  · decide
  · rfl
  · simp [X, Expr.getAppArgs]

theorem self_field (N F k : Nat) (hf : 2 ≤ F) (act : List NestKey) (d : Nat) :
  PosDR (checker F) (En N) (Cn N) 1
    (.field act [holeAt k] d 0 Y .inProgress Y) := by
  apply PosDR.frameHole (w := Y) (i := 2) (ty := S) (h := holeAt k) (n := 0)
  · exact whnf_self N F d hf
  · decide
  · rfl
  · decide
  · decide
  · rfl
  · simp [Y, Expr.getAppArgs]
  · rfl

theorem cons_u4 (a : Expr) (k : NestFieldKind) :
  ((List.range 2).any fun i => [k,.inProgress].getD i .ordinary != .ordinary &&
    structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 i) = false := by
  have h0 : structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 0 = false := rfl
  have h1 : structUsedLater (closeTelescope [(a,bm),(Y,bm)] 3 Y) 0 1 = false := rfl
  simp [List.range_succ, h0, h1]

theorem node_u4 (a : Expr) (k : NestFieldKind) :
  ((List.range 1).any fun i => [k].getD i .ordinary != .ordinary &&
    structUsedLater (closeTelescope [(a,bm)] 2 X) 0 i) = false := by
  have h0 : structUsedLater (closeTelescope [(a,bm)] 2 X) 0 0 = false := rfl
  simp [List.range_succ, h0]

/-- A field tower under arbitrary scoped progress and active ancestors.
    The strengthened freshness invariant supplies every inner container key. -/
theorem tower_field (N F : Nat) (hf : N+5 ≤ F) (k : Nat) (hk : k ≤ N)
    (act : List NestKey) (prog : List NestHole) (d : Nat)
    (ha : FreshBelow k act) (hp : ProgScoped (Cn N) prog) :
    PosDR (checker F) (En N) (Cn N) (k+1)
      (.field act prog d 0 (tower k) (fieldKind k) (tower k)) := by
  induction k generalizing act prog d with
  | zero => exact member_field N F (by omega) act prog d
  | succ k ih =>
    have hfr : PosDR (checker F) (En N) (Cn N) (k+1)
        (.frame act [] [.zero] [tower k] [(Ln,S)]) := by
      apply PosDR.frame (m := k+1) (ctors := listCs)
      · simp
      · exact ⟨by decide, by decide⟩
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
                (fresh_push k act ha) (frame_scoped N k)
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
    · decide
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

#print tower_field
#print axioms tower_field
#print axioms node_crest
#print axioms Core.tower_core_certificate
end Tree2TowerNative
