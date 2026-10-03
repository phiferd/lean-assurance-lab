import EtaAliasAdmissionSupport

open Lean

private def explicitType : Expr :=
  .forallE `_ (mkConst ``Bool) (mkConst ``Box) .default

private def aliasType : Expr :=
  .const ``FnAlias []

private def ctor : Expr :=
  .const ``Box.mk []

private def theoremType (storedType : Expr) : Expr :=
  .forallE `f storedType
    (mkApp3 (mkConst ``Eq [1]) storedType (.bvar 0) ctor) .default

private def theoremValue (storedType : Expr) : Expr :=
  .lam `f storedType
    (mkApp2 (mkConst ``Eq.refl [1]) storedType (.bvar 0)) .default

private def assertExplicitFunctionType (type : Expr) : MetaM Unit := do
  match type with
  | .forallE _ domain body _ =>
      assert! domain == mkConst ``Bool
      assert! body == mkConst ``Box
  | _ =>
      throwError "expected a syntactic Bool-to-Box forall type"

private def runCell (env : Environment) (label : String) (name : Name)
    (storedType : Expr) : MetaM Bool := do
  assert! env.header.trustLevel == 0
  assert! storedType == aliasType || storedType == explicitType
  if storedType == aliasType then
    assert! storedType == .const ``FnAlias []
  else
    assertExplicitFunctionType storedType
  let type := theoremType storedType
  let value := theoremValue storedType
  assert! !type.hasFVar && !type.hasMVar && !type.hasLooseBVars
  assert! !value.hasFVar && !value.hasMVar && !value.hasLooseBVars
  match type, value with
  | .forallE _ typeDomain typeBody _, .lam _ valueDomain valueBody _ =>
      assert! typeDomain == storedType
      assert! valueDomain == storedType
      assert! typeBody.isAppOfArity ``Eq 3
      assert! valueBody.isAppOfArity ``Eq.refl 2
  | _, _ =>
      throwError "fixture lost the expected forall/lambda shape"
  let typeCheck ← match Kernel.check env {} type with
    | .ok result => pure result
    | .error _ => throwError "Kernel.check failed on declaration type"
  let valueCheck ← match Kernel.check env {} value with
    | .ok result => pure result
    | .error _ => throwError "Kernel.check failed on declaration value"
  logInfo m!"cell={label} revision={Lean.githash} trustLevel={env.header.trustLevel}"
  logInfo m!"cell={label} storedType.raw={repr storedType}"
  logInfo m!"cell={label} declarationType.raw={repr type}"
  logInfo m!"cell={label} declarationValue.raw={repr value}"
  logInfo m!"cell={label} Kernel.check(type)={repr typeCheck}"
  logInfo m!"cell={label} Kernel.check(value)={repr valueCheck}"
  let decl : Declaration := .thmDecl {
    name := name
    levelParams := []
    type := type
    value := value
  }
  match env.addDeclCore 0 0 decl none with
  | .ok admittedEnv =>
      assert! admittedEnv.header.trustLevel == 0
      assert! admittedEnv.constants.contains name
      logInfo m!"cell={label} addDeclCore=ACCEPT"
      return true
  | .error _ =>
      logInfo m!"cell={label} addDeclCore=REJECT"
      return false

run_meta do
  assert! Lean.githash == "015d54649bcaaa0861f355b59761ce308e629fbb"
  let aliasEnv ← importModules #[{ module := `EtaAliasAdmissionSupport }] {} 0
  let aliasAccepted ← runCell aliasEnv "alias-negative" `EtaAliasAdmission.aliasInvalid aliasType
  let explicitEnv ← importModules #[{ module := `EtaAliasAdmissionSupport }] {} 0
  let explicitAccepted ← runCell explicitEnv "explicit-negative" `EtaAliasAdmission.explicitInvalid explicitType
  logInfo m!"classification-input aliasAccepted={aliasAccepted} explicitAccepted={explicitAccepted}"
