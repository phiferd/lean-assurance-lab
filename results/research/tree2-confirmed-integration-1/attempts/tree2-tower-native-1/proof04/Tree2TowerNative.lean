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

#print node_crest
#print axioms node_crest
#print Core.tower_core_certificate
#print axioms Core.tower_core_certificate
end Tree2TowerNative
