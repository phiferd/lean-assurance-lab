import Tree2Bridge

/- Local AI-authored exploratory supporting lemmas. No upstream submission.
   Tree2Bridge and the pinned upstream source are unchanged. -/
namespace Tree2TowerSupport
open ConLeche Tree2Bridge

/-- Zero List layers is the root member itself. -/
def tower : Nat → Expr
  | 0 => X
  | k + 1 => l (tower k)

/-- Index k denotes List (List^k X), not List^k X. -/
def towerKey (k : Nat) : NestKey := ⟨Ln, [.zero], [tower k]⟩

theorem tower_range (k : Nat) : (tower k).fvarRange = 2 := by
  induction k with
  | zero => rfl
  | succ k ih => simp [tower, l, Expr.fvarRange, ih]

theorem tower_injective : Function.Injective tower := by
  intro j
  induction j with
  | zero =>
    intro k h
    cases k with
    | zero => rfl
    | succ k => cases h
  | succ j ih =>
    intro k h
    cases k with
    | zero => cases h
    | succ k =>
      have inner : tower j = tower k := (Expr.app.inj h).2
      exact congrArg Nat.succ (ih inner)

/-- Root-only parameters reset the progress stack, for every depth and prior
    progress stack. The environment lookup is irrelevant to this operation. -/
theorem tower_key_frame (k : Nat) (prog : List NestHole) :
    (tower k).fvarB = 2 ∧
    nestWalkStack C prog [tower k] = [] ∧
    ∀ j, towerKey j = towerKey k ↔ j = k := by
  have hr : (tower k).fvarB = 2 := by rw [Expr.fvarB_eq, tower_range]
  refine ⟨hr, ?_, ?_⟩
  · simp [nestWalkStack, hr, C, NestCtx.hiAt]
  · intro j
    constructor
    · intro h
      have hd : [tower j] = [tower k] := congrArg NestKey.ds h
      exact tower_injective (List.cons.inj hd).1
    · intro h
      subst j
      rfl

/-- Raw syntactic substitution. `replaceFVars` does not lift bvars or recurse
    into inserted expressions. This equation alone is NOT capture avoidance. -/
theorem canonical_list_crest_substitution (d h : Expr) :
    nestCrest [Ln] [.zero] [d] [h]
      (nilCV.type.instantiateLevelParams [un] [.zero]) = some h ∧
    nestCrest [Ln] [.zero] [d] [h]
      (consCV.type.instantiateLevelParams [un] [.zero]) =
        some (arr d (arr h h)) := by
  constructor
  · change (nestCanonCrest [Ln] [.zero] 1
      (nilCV.type.instantiateLevelParams [un] [.zero])).map
        (·.replaceFVars (nestKeyMap [d] [h])) = some h
    rw [canonical_list.1]
    simp [Expr.replaceFVars, Q, nestKeyMap]
  · change (nestCanonCrest [Ln] [.zero] 1
      (consCV.type.instantiateLevelParams [un] [.zero])).map
        (·.replaceFVars (nestKeyMap [d] [h])) = some (arr d (arr h h))
    rw [canonical_list.2]
    simp [arr, pi, Expr.replaceFVars, P, Q, nestKeyMap]

/-- An independently stated sufficient condition: each inserted expression has
    no loose bound variables BEFORE insertion. Thus no surrounding binder can
    capture an externally referring bvar. Fvar annotations follow the model's
    standard opaque traversal convention. This is not a typing theorem. -/
theorem canonical_list_crest_closed (d h : Expr)
    (hd : d.looseBVarsBounded 0 = true)
    (hh : h.looseBVarsBounded 0 = true) :
    nestCrest [Ln] [.zero] [d] [h]
      (nilCV.type.instantiateLevelParams [un] [.zero]) = some h ∧
    nestCrest [Ln] [.zero] [d] [h]
      (consCV.type.instantiateLevelParams [un] [.zero]) =
        some (arr d (arr h h)) ∧
    (arr d (arr h h)).looseBVarsBounded 0 = true ∧
    ∀ depth, d.looseBVarsBounded depth = true ∧
      h.looseBVarsBounded depth = true := by
  have db : d.bvarBound = 0 := Nat.eq_zero_of_le_zero (Expr.looseBVarsBounded_iff.mp hd)
  have hb : h.bvarBound = 0 := Nat.eq_zero_of_le_zero (Expr.looseBVarsBounded_iff.mp hh)
  refine ⟨(canonical_list_crest_substitution d h).1,
    (canonical_list_crest_substitution d h).2, ?_, ?_⟩
  · apply Expr.looseBVarsBounded_iff.mpr
    simp [arr, pi, Expr.bvarBound, db, hb]
  · intro depth
    constructor <;> apply Expr.looseBVarsBounded_iff.mpr <;> simp [db, hb]

theorem tower_closed (k : Nat) : (tower k).looseBVarsBounded 0 = true := by
  apply Expr.looseBVarsBounded_iff.mpr
  suffices (tower k).bvarBound = 0 by omega
  induction k with
  | zero => rfl
  | succ k ih => simp [tower, l, Expr.bvarBound, ih]

/-- Safe specialization for every tower key: parameter remains the whole
    tower and the self hole remains Y; no enumeration of depths. -/
theorem tower_list_crest (k : Nat) :
    nestCrest [Ln] [.zero] [tower k] [Y]
      (nilCV.type.instantiateLevelParams [un] [.zero]) = some Y ∧
    nestCrest [Ln] [.zero] [tower k] [Y]
      (consCV.type.instantiateLevelParams [un] [.zero]) =
        some (arr (tower k) (arr Y Y)) ∧
    (arr (tower k) (arr Y Y)).looseBVarsBounded 0 = true := by
  have hy : Y.looseBVarsBounded 0 = true := rfl
  have hc := canonical_list_crest_closed (tower k) Y (tower_closed k) hy
  exact ⟨hc.1, hc.2.1, hc.2.2.1⟩

/-- Without the input condition, substitution can capture a loose bvar even
    when its entire output is closed. The raw equation still holds. -/
theorem loose_self_capture_example :
    nestCrest [Ln] [.zero] [S] [.bvar 0]
      (consCV.type.instantiateLevelParams [un] [.zero]) =
        some (arr S (arr (.bvar 0) (.bvar 0))) ∧
    (Expr.bvar 0).looseBVarsBounded 0 = false ∧
    (arr S (arr (.bvar 0) (.bvar 0))).looseBVarsBounded 0 = true :=
  ⟨(canonical_list_crest_substitution S (.bvar 0)).2, rfl, rfl⟩

#print tower_key_frame
#print canonical_list_crest_substitution
#print canonical_list_crest_closed
#print tower_list_crest
#print loose_self_capture_example
#print axioms tower_range
#print axioms tower_injective
#print axioms tower_key_frame
#print axioms canonical_list_crest_substitution
#print axioms canonical_list_crest_closed
#print axioms tower_closed
#print axioms tower_list_crest
#print axioms loose_self_capture_example
end Tree2TowerSupport
