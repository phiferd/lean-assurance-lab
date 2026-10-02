import EtaAdmissionSupport

open Lean

namespace EtaAdmissionConfirmation

def explicitType : Expr :=
  .forallE `_ (mkConst ``Bool) (mkConst ``Box) .default

def aliasType : Expr :=
  .const ``FnAlias []

def ctor : Expr :=
  .const ``Box.mk []

def theoremType (storedType : Expr) : Expr :=
  .forallE `f storedType
    (mkApp3 (mkConst ``Eq [1]) storedType (.bvar 0) ctor) .default

def theoremValue (storedType : Expr) : Expr :=
  .lam `f storedType
    (mkApp2 (mkConst ``Eq.refl [1]) storedType (.bvar 0)) .default

private def assertExplicitFunctionType (type : Expr) : MetaM Unit := do
  match type with
  | .forallE _ domain body _ =>
      assert! domain == mkConst ``Bool
      assert! body == mkConst ``Box
  | _ =>
      throwError "expected a syntactic Bool-to-Box forall type"

private def exceptionKind : Kernel.Exception → String
  | .unknownConstant .. => "unknownConstant"
  | .alreadyDeclared .. => "alreadyDeclared"
  | .declTypeMismatch .. => "declTypeMismatch"
  | .declHasMVars .. => "declHasMVars"
  | .declHasFVars .. => "declHasFVars"
  | .funExpected .. => "funExpected"
  | .typeExpected .. => "typeExpected"
  | .letTypeMismatch .. => "letTypeMismatch"
  | .exprTypeMismatch .. => "exprTypeMismatch"
  | .appTypeMismatch .. => "appTypeMismatch"
  | .invalidProj .. => "invalidProj"
  | .thmTypeIsNotProp .. => "thmTypeIsNotProp"
  | .other .. => "other"
  | .deterministicTimeout => "deterministicTimeout"
  | .excessiveMemory => "excessiveMemory"
  | .deepRecursion => "deepRecursion"
  | .interrupted => "interrupted"

private def isSemanticRejection : Kernel.Exception → Bool
  | .declTypeMismatch .. => true
  | .funExpected .. => true
  | .typeExpected .. => true
  | .letTypeMismatch .. => true
  | .exprTypeMismatch .. => true
  | .appTypeMismatch .. => true
  | .invalidProj .. => true
  | .thmTypeIsNotProp .. => true
  | _ => false

def runCell (label : String) (name : Name) (storedType : Expr) : MetaM Bool := do
  let env ← getEnv
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
    | .error e => throwError m!"Kernel.check failed on declaration type: {e.toMessageData {}}"
  let valueCheck ← match Kernel.check env {} value with
    | .ok result => pure result
    | .error e => throwError m!"Kernel.check failed on declaration value: {e.toMessageData {}}"
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
  match env.addDeclCore 0 0 decl none (doCheck := true) with
  | .ok admittedEnv =>
      assert! admittedEnv.header.trustLevel == 0
      match admittedEnv.find? name with
      | some (.thmInfo info) =>
          assert! info.type == type
          assert! info.value == value
      | _ => throwError "accepted declaration was not stored as the submitted theorem"
      logInfo m!"cell={label} addDeclCore=ACCEPT"
      return true
  | .error e =>
      let kind := exceptionKind e
      logInfo m!"cell={label} exception.kind={kind}"
      logInfo m!"cell={label} exception.message={e.toMessageData {}}"
      unless isSemanticRejection e do
        throwError m!"non-semantic addDeclCore failure ({kind})"
      logInfo m!"cell={label} addDeclCore=REJECT"
      return false

end EtaAdmissionConfirmation
