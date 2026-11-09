import Export.Parse
import Lean

-- Show the parsed constructors before normalization or checked replay.
def levelText : Lean.Level → String
  | .zero => "0"
  | .succ l => "(succ " ++ levelText l ++ ")"
  | _ => "UNEXPECTED-LEVEL"

def exprText : Lean.Expr → String
  | .sort l => "(sort " ++ levelText l ++ ")"
  | .bvar n => "(bvar " ++ toString n ++ ")"
  | .app f a => "(app " ++ exprText f ++ " " ++ exprText a ++ ")"
  | .lam n t b _ => "(lam " ++ n.toString ++ " " ++ exprText t ++ " " ++ exprText b ++ ")"
  | .forallE n t b _ => "(forallE " ++ n.toString ++ " " ++ exprText t ++ " " ++ exprText b ++ ")"
  | _ => "UNEXPECTED-EXPR"

def main (args : List String) : IO Unit := do
  let [path] := args | throw (IO.userError "one NDJSON path required")
  let handle ← IO.FS.Handle.mk path .read
  let solution ← Export.parseStream (.ofHandle handle)
  unless solution.constMap.size == 1 do throw (IO.userError "expected exactly one declaration")
  for (_, c) in solution.constMap.toList do
    let .defnInfo d := c | throw (IO.userError "expected a definition")
    IO.println s!"NAME {d.name}"
    IO.println s!"PARAMS {String.intercalate "," (d.levelParams.map Lean.Name.toString)}"
    IO.println s!"TYPE {exprText d.type}"
    IO.println s!"VALUE {exprText d.value}"
  let env ← Lean.mkEmptyEnvironment (trustLevel := 0)
  let _ ← env.toKernelEnv.replay solution.constMap
  IO.println "Accepted 1 definition; empty environment; trust level 0."
