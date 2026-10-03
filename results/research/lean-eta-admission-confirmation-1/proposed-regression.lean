import Lean

open Lean

structure EtaAdmissionBox where
  val : Bool

@[reducible] def EtaAdmissionAlias := Bool → EtaAdmissionBox

private def explicitType : Expr :=
  .forallE `_ (mkConst ``Bool) (mkConst ``EtaAdmissionBox) .default

private def aliasType : Expr :=
  .const ``EtaAdmissionAlias []

private def theoremType (domain : Expr) : Expr :=
  .forallE `f domain
    (mkApp3 (mkConst ``Eq [1]) domain (.bvar 0)
      (.const ``EtaAdmissionBox.mk []))
    .default

private def theoremValue (domain : Expr) : Expr :=
  .lam `f domain
    (mkApp2 (mkConst ``Eq.refl [1]) domain (.bvar 0))
    .default

private def expectDeclTypeMismatch
    (env : Environment) (name : Name) (domain : Expr) : MetaM Unit := do
  let type := theoremType domain
  let value := theoremValue domain
  assert! !type.hasFVar && !type.hasMVar && !type.hasLooseBVars
  assert! !value.hasFVar && !value.hasMVar && !value.hasLooseBVars
  let decl : Declaration := .thmDecl {
    name := name
    levelParams := []
    type := type
    value := value
  }
  match env.addDeclCore 0 0 decl none (doCheck := true) with
  | .ok _ =>
      throwError m!"BUG: checked admission accepted invalid declaration {name}"
  | .error (.declTypeMismatch ..) =>
      pure ()
  | .error e =>
      throwError m!"unexpected kernel exception for {name}: {e.toMessageData {}}"

run_meta do
  let env ← getEnv
  assert! env.header.trustLevel == 0
  expectDeclTypeMismatch env `etaAliasMustReject aliasType
  expectDeclTypeMismatch env `etaExplicitMustReject explicitType

