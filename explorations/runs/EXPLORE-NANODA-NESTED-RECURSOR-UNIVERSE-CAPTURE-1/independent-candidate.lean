import Lean

inductive LALWrap (alpha : Type) : Type where
  | mk (value : alpha)

inductive LALNest : Type where
  | node (children : LALWrap LALNest)

universe u

noncomputable def candidateReductDoesNotCheck
    (motive_1 : LALNest → Type)
    (motive_2 : LALWrap LALNest → Type)
    (node : ∀ children, motive_2 children → motive_1 (.node children))
    (mk : ∀ value, motive_1 value → motive_2 (.mk value))
    (children : LALWrap LALNest) : motive_1 (.node children) :=
  node children
    (@LALNest.rec_1.{u} motive_1 motive_2 node mk children)
