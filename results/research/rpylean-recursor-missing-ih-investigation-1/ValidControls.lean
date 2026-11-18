import Init

namespace ValidControls

universe u v

-- Adapted from List in Lean 4.34.1's Init/Prelude.lean.
inductive Trail (α : Type u) where
  | finish : Trail α
  | mark (label : α) (rest : Trail α) : Trail α

def Trail.total (weight : α → Nat) : Trail α → Nat
  | .finish => 0
  | .mark label rest => weight label + rest.total weight

example : Trail.total Nat.succ (.mark 2 (.mark 4 .finish)) = 8 := rfl

-- Adapted from Eq in Init/Prelude.lean.
inductive SameStop {α : Sort u} (start : α) : α → Prop where
  | here : SameStop start start

def transportStop {α : Sort u} (family : α → Sort v) {start dest : α}
    (same : SameStop start dest) (value : family start) : family dest := by
  cases same
  exact value

example : transportStop (fun n : Nat => Fin (n + 1)) (SameStop.here (start := 2)) 1 = 1 :=
  rfl

-- Adapted from Acc and its induction principle in Init/WF.lean.
inductive AccessibleStop {α : Sort u} (before : α → α → Prop) : α → Prop where
  | node (dest : α) (prior : ∀ src, before src dest → AccessibleStop before src) :
      AccessibleStop before dest

theorem accessibleInduction {α : Sort u} {before : α → α → Prop} (holds : α → Prop)
    (step : ∀ dest, (∀ src, before src dest → holds src) → holds dest)
    {dest : α} (accessible : AccessibleStop before dest) : holds dest := by
  induction accessible with
  | node dest _ ih => exact step dest ih

end ValidControls
