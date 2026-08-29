def LALConstType (A B : Type) : Type := A

inductive LALReduciblePositivity : Type where
  | mk (f : Unit -> LALReduciblePositivity) : LALReduciblePositivity
