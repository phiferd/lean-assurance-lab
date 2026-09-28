import Lean

open Lean

namespace StatefulPilot

def liftE (x : Except String α) : IO α :=
  match x with
  | .ok a => pure a
  | .error e => throw <| IO.userError e

def levelOfNat : Nat → Level
  | 0 => .zero
  | n+1 => .succ (levelOfNat n)

def levelNat : Level → Except String Nat
  | .zero => pure 0
  | .succ l => return (← levelNat l) + 1
  | _ => throw "non-numeric universe in observation"

partial def decodeExpr (j : Json) : Except String Expr := do
  let a ← j.getArr?
  let tag ← (← j.getArrVal? 0).getStr?
  match tag with
  | "sort" =>
    unless a.size == 2 do throw "sort arity"
    return .sort (levelOfNat (← a[1]!.getNat?))
  | "var" =>
    unless a.size == 2 do throw "var arity"
    return .bvar (← a[1]!.getNat?)
  | "const" =>
    unless a.size == 2 do throw "const arity"
    return .const (← a[1]!.getStr?).toName []
  | "pi" | "lam" =>
    unless a.size == 3 do throw "binder arity"
    let domain ← decodeExpr a[1]!
    let body ← decodeExpr a[2]!
    return if tag == "pi" then .forallE `x domain body .default
           else .lam `x domain body .default
  | _ => throw "unsupported expression constructor"

partial def encodeExpr : Expr → Except String Json
  | .sort l => return .arr #[.str "sort", toJson (← levelNat l)]
  | .bvar i => return .arr #[.str "var", toJson i]
  | .const n [] => return .arr #[.str "const", .str n.toString]
  | .forallE _ d b .default => return .arr #[.str "pi", ← encodeExpr d, ← encodeExpr b]
  | .lam _ d b .default => return .arr #[.str "lam", ← encodeExpr d, ← encodeExpr b]
  | _ => throw "unexpected expression in observation"

def exceptionTag : Kernel.Exception → String
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

def declarationJSON (d : DefinitionVal) : Except String Json := do
  unless d.safety == .safe && d.levelParams.isEmpty do
    throw "unexpected safety or universe parameters"
  return Json.mkObj [
    ("name", toJson d.name.toString), ("type", ← encodeExpr d.type),
    ("value", ← encodeExpr d.value), ("safety", toJson "safe"),
    ("levelParams", .arr #[])]

def snapshot (env : Kernel.Environment) : Except String Json := do
  let constants := env.constants.toList.mergeSort (fun a b => a.1.toString ≤ b.1.toString)
  let mut entries := #[]
  for (_, info) in constants do
    match info with
    | .defnInfo d => entries := entries.push (← declarationJSON d)
    | _ => throw "unexpected non-definition in environment"
  return .arr entries

def emit (j : Json) : IO Unit := IO.println j.compress

def run (path : String) : IO Unit := do
  let doc ← liftE <| Json.parse (← IO.FS.readFile path)
  let comparison ← liftE <| (← liftE <| doc.getObjVal? "comparison").getStr?
  let side ← liftE <| (← liftE <| doc.getObjVal? "side").getStr?
  let requests ← liftE <| (← liftE <| doc.getObjVal? "requests").getArr?
  let opts := ({} : Options).setBool `debug.skipKernelTC false
    |>.setNat `maxRecDepth 1000 |>.setNat `maxHeartbeats 200000
  if debug.skipKernelTC.get opts then throw <| IO.userError "checking disabled"
  let mut env := (← mkEmptyEnvironment 0).toKernelEnv
  emit <| Json.mkObj [
    ("kind", toJson "begin"), ("comparison", toJson comparison), ("side", toJson side),
    ("api", toJson "Lean.Kernel.Environment.addDecl"),
    ("skipKernelTC", toJson (debug.skipKernelTC.get opts)),
    ("trustLevel", toJson env.header.trustLevel.toNat), ("environment", ← liftE <| snapshot env)]
  for index in [:requests.size] do
    let req := requests[index]!
    let id ← liftE <| (← liftE <| req.getObjVal? "id").getStr?
    let name ← liftE <| (← liftE <| req.getObjVal? "name").getStr?
    let type ← liftE <| decodeExpr (← liftE <| req.getObjVal? "type")
    let value ← liftE <| decodeExpr (← liftE <| req.getObjVal? "value")
    let d : DefinitionVal := {
      name := name.toName
      levelParams := []
      type := type
      value := value
      hints := .abbrev
      safety := .safe
    }
    let actual := Json.mkObj [("id", toJson id), ("name", toJson d.name.toString),
      ("type", ← liftE <| encodeExpr d.type), ("value", ← liftE <| encodeExpr d.value)]
    let outcome ← match env.addDecl opts (.defnDecl d) with
      | .ok next => do env := next; pure "ACCEPT"
      | .error e => pure (exceptionTag e)
    emit <| Json.mkObj [("kind", toJson "step"), ("comparison", toJson comparison),
      ("side", toJson side), ("index", toJson index), ("request", actual),
      ("outcome", toJson outcome), ("environment", ← liftE <| snapshot env)]
  emit <| Json.mkObj [("kind", toJson "end"), ("comparison", toJson comparison),
    ("side", toJson side), ("steps", toJson requests.size)]

end StatefulPilot

def main (args : List String) : IO Unit := do
  match args with
  | [path] => StatefulPilot.run path
  | _ => throw <| IO.userError "expected exactly one history path"
