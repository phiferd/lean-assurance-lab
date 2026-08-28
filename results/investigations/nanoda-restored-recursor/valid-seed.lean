import Lean

inductive LALWrap (alpha : Type) : Type where
  | mk (value : alpha)

inductive LALNest : Type where
  | node (children : LALWrap LALNest)
