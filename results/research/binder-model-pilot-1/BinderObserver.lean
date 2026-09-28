import Lean

open Lean

namespace BinderObserver

def liftE (x : Except String α) : IO α :=
  match x with
  | .ok a => pure a
  | .error e => throw <| IO.userError e

def field (j : Json) (key : String) : Except String Json := j.getObjVal? key
def natField (j : Json) (key : String) : Except String Nat :=
  (field j key) >>= Json.getNat?

partial def decode : Json → Except String Expr
  | .arr a => do
    if a.isEmpty then throw "empty expression"
    let tag ← a[0]!.getStr?
    match tag with
    | "b" =>
      unless a.size == 2 do throw "bvar arity"
      return .bvar (← a[1]!.getNat?)
    | "s" =>
      unless a.size == 1 do throw "sort arity"
      return .sort .zero
    | "a" =>
      unless a.size == 3 do throw "application arity"
      return .app (← decode a[1]!) (← decode a[2]!)
    | "l" =>
      unless a.size == 3 do throw "lambda arity"
      return .lam `x (← decode a[1]!) (← decode a[2]!) .default
    | "t" =>
      unless a.size == 4 do throw "let arity"
      return .letE `x (← decode a[1]!) (← decode a[2]!) (← decode a[3]!) false
    | _ => throw "unsupported expression tag"
  | _ => throw "expression must be an array"

partial def encode : Expr → Except String Json
  | .bvar i => return .arr #[.str "b", toJson i]
  | .sort .zero => return .arr #[.str "s"]
  | .app f a => return .arr #[.str "a", ← encode f, ← encode a]
  | .lam _ d b .default => return .arr #[.str "l", ← encode d, ← encode b]
  | .letE _ t v b false => return .arr #[.str "t", ← encode t, ← encode v, ← encode b]
  | _ => throw "unexpected expression from selected API"

def observe (j : Json) : Except String Json := do
  let id ← (← field j "id").getStr?
  let op ← (← field j "operation").getStr?
  let e ← decode (← field j "source")
  let args ← (← field j "arguments").getArr?
  let p ← field j "parameters"
  let outputs ← match op with
    | "LIFT" => do
      unless args.isEmpty do throw "lift argument count"
      let r := e.liftLooseBVars (← natField p "s") (← natField p "d")
      pure #[← encode r]
    | "SUBST" => do
      unless args.size == 1 do throw "subst argument count"
      let r := e.instantiate1 (← decode args[0]!)
      pure #[← encode r]
    | "LIFT_COMPOSE" => do
      unless args.isEmpty do throw "lift composition argument count"
      let r1 := e.liftLooseBVars (← natField p "s1") (← natField p "d1")
      let r2 := r1.liftLooseBVars (← natField p "s2") (← natField p "d2")
      pure #[← encode r1, ← encode r2]
    | "SUBST_COMPOSE" => do
      unless args.size == 2 do throw "subst composition argument count"
      let r1 := e.instantiate1 (← decode args[0]!)
      let r2 := r1.instantiate1 (← decode args[1]!)
      pure #[← encode r1, ← encode r2]
    | _ => throw "unknown operation"
  return Json.mkObj [("id", toJson id), ("outputs", .arr outputs)]

def run (path : String) : IO Unit := do
  let raw ← IO.FS.readFile path
  let lines := raw.splitOn "\n"
  for line in lines do
    if !line.isEmpty then
      let input ← liftE <| Json.parse line
      let output ← liftE <| observe input
      IO.println output.compress

end BinderObserver

def main (args : List String) : IO Unit := do
  match args with
  | [path] => BinderObserver.run path
  | _ => throw <| IO.userError "expected one NDJSON path"
