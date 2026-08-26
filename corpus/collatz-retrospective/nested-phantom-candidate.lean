import Lean
open Lean Elab Command

structure RetrospectiveCarrier where
  payload : Nat

structure RetrospectiveClaim where
  payload : Bool

inductive RetrospectiveContainer (alpha : Type) (phantom : Nat) : Type where
  | mk

meta def buildRetrospectiveCandidate : CommandElabM Unit := do
  let add (declaration : Declaration) : CommandElabM Unit :=
    liftCoreM <| withOptions (debug.skipKernelTC.set · true) <| addDecl declaration
  let carrier := mkBVar 0
  let family := mkApp (mkConst `RetrospectiveFamily) carrier
  let wrongProjection := mkProj ``RetrospectiveClaim 0 carrier
  let nested := mkApp2 (mkConst ``RetrospectiveContainer) family wrongProjection
  let familyType := mkForall `carrier .default (mkConst ``RetrospectiveCarrier) (mkSort 1)
  let constructorType := mkForall `carrier .default (mkConst ``RetrospectiveCarrier) <|
    mkForall `nested .default nested (mkApp (mkConst `RetrospectiveFamily) (mkBVar 1))
  add <| .inductDecl [] 1 [{
    name := `RetrospectiveFamily
    type := familyType
    ctors := [{ name := `RetrospectiveFamily.mk, type := constructorType }]
  }] false

elab "build_retrospective_candidate" : command => buildRetrospectiveCandidate
build_retrospective_candidate
