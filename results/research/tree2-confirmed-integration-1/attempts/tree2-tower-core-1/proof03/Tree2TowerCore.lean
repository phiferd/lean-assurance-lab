import Tree2TowerSupport
import ConLeche.Verify.Mono

/- Local AI-authored exploratory pure-Core certificate. No upstream submission.
   Both completed artifacts and the pinned upstream source remain unchanged. -/
namespace Tree2TowerCore
open ConLeche Tree2Bridge Tree2TowerSupport

/-- The actual pure Core sees the exact List former after level instantiation. -/
theorem infer_list_head (d : Nat) :
    inferTypeCore .verified E 1 d (.const Ln [.zero]) = .ok (arr S S) := by
  rfl

theorem whnf_former (d : Nat) :
    whnf .verified E 2 d (arr S S) = .ok (arr S S) := by
  change whnfBody (pureFns .verified E 1) E d (arr S S) = .ok (arr S S)
  unfold whnfBody whnfLoopFuel
  rfl

theorem whnf_list (a : Expr) (d : Nat) :
    whnf .verified E 3 d (l a) = .ok (l a) := by
  change whnfBody (pureFns .verified E 2) E d (l a) = .ok (l a)
  unfold whnfBody whnfLoopFuel
  rfl

theorem whnf_X (d : Nat) : whnf .verified E 2 d X = .ok X := by
  change whnfBody (pureFns .verified E 1) E d X = .ok X
  unfold whnfBody whnfLoopFuel
  rfl

theorem defeq_S (d : Nat) : isDefEqCore .verified E 1 d S S = .ok true := by
  change defeqBody .verified (pureFns .verified E 0) E d S S = .ok true
  unfold defeqBody defeqLoopFuel
  rfl

theorem infer_X (d : Nat) (hd : 2 ≤ d) :
    inferTypeCore .verified E 1 d X = .ok S := by
  have hs : 1 < d := by omega
  rw [inferTypeCore_succ]
  simp [inferBody, X, hs]
  rfl

/-- One List layer: all Core subcalls are proved for this explicit environment.
    The argument success is an induction interface, not a final premise. -/
theorem infer_list_step (a : Expr) (d f : Nat) (hf : 2 ≤ f)
    (ha : inferTypeCore .verified E f d a = .ok S) :
    inferTypeCore .verified E (f+1) d (l a) = .ok S := by
  have hc := inferTypeCore_mono (mode := .verified) (show 1 ≤ f by omega) (infer_list_head d)
  have hw := whnf_mono (mode := .verified) hf (whnf_former d)
  have he := isDefEqCore_mono (mode := .verified) (show 1 ≤ f by omega) (defeq_S d)
  rw [inferTypeCore_succ]
  simp only [l, inferBody, infer_def, whnf_def, defeq_def]
  rw [hc]
  simp only [bind, Except.bind]
  rw [hw]
  simp only [arr, pi]
  rw [ha]
  simp only [Except.bind]
  rw [he]
  rfl

/-- A conservative, derived inference bound: base3; each app adds one. -/
theorem infer_tower_at_bound (n d : Nat) (hd : 2 ≤ d) :
    inferTypeCore .verified E (n+3) d (tower n) = .ok S := by
  induction n with
  | zero =>
    exact inferTypeCore_mono (by omega) (infer_X d hd)
  | succ n ih =>
    exact infer_list_step (tower n) d (n+3) (by omega) ih

/-- Uniform head-only reduction: the parameter tower is never traversed. -/
theorem whnf_tower_at_bound (n d : Nat) :
    whnf .verified E 3 d (tower n) = .ok (tower n) := by
  cases n with
  | zero => exact whnf_mono (by omega) (whnf_X d)
  | succ n => exact whnf_list (tower n) d

/-- Actual verified outcomes for all larger fuels. No successful-operation,
    positivity, or acceptance premise appears in this certificate. -/
theorem tower_core_certificate (n d fuel : Nat) (hd : 2 ≤ d)
    (hf : n+3 ≤ fuel) :
    inferTypeCore .verified E fuel d (tower n) = .ok S ∧
    whnf .verified E fuel d (tower n) = .ok (tower n) ∧
    (tower n).fvarB ≤ d ∧ (tower n).looseBVarsBounded 0 = true := by
  refine ⟨inferTypeCore_mono hf (infer_tower_at_bound n d hd),
    whnf_mono (by omega) (whnf_tower_at_bound n d), ?_, tower_closed n⟩
  rw [Expr.fvarB_eq, tower_range]
  exact hd

#print tower_core_certificate
#print infer_tower_at_bound
#print whnf_tower_at_bound
#print axioms infer_list_head
#print axioms whnf_former
#print axioms whnf_list
#print axioms whnf_X
#print axioms defeq_S
#print axioms infer_X
#print axioms infer_list_step
#print axioms infer_tower_at_bound
#print axioms whnf_tower_at_bound
#print axioms tower_core_certificate
end Tree2TowerCore
