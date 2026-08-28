import Lean

universe u v

inductive LALIMaxBoundary (A : Sort (imax u v + 1)) : Sort (imax u v + 1) where
  | mk (value : A)
