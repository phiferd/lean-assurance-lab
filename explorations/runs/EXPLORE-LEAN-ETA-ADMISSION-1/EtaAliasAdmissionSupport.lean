import Lean

structure Box where
  val : Bool

@[reducible] def FnAlias := Bool → Box
