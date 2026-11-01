import Lean

inductive LALWrap (alpha : Type) : Type where
  | mk (value : alpha)

inductive LALNest : Type where
  | node (children : LALWrap LALNest)

inductive LALMarker : Type where
  | mark

theorem LALNest.auxConsumer_iota (value : LALNest) :
    LALNest.rec_1
      (motive_1 := fun _ => Nat)
      (motive_2 := fun _ => Nat)
      (fun _ _ => 7)
      (fun _ _ => 11)
      (LALWrap.mk value) = 11 := rfl
