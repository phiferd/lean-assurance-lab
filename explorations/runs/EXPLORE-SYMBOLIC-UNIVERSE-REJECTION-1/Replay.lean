import Export.Parse
import Lean

-- Print raw constructors after parsing, before any normalization or kernel replay.
def levelText : Lean.Level → String
  | .zero => "0"
  | .param n => n.toString
  | .succ l => "(succ " ++ levelText l ++ ")"
  | .max l r => "(max " ++ levelText l ++ " " ++ levelText r ++ ")"
  | .imax l r => "(imax " ++ levelText l ++ " " ++ levelText r ++ ")"
  | .mvar _ => "UNEXPECTED-MVAR"

def exprText : Lean.Expr → String
  | .sort l => "(sort " ++ levelText l ++ ")"
  | .bvar n => "(bvar " ++ toString n ++ ")"
  | .forallE n t b _ => "(forallE " ++ n.toString ++ " " ++ exprText t ++ " " ++ exprText b ++ ")"
  | .letE n t v b _ => "(letE " ++ n.toString ++ " " ++ exprText t ++ " " ++ exprText v ++ " " ++ exprText b ++ ")"
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
  IO.println "Accepted 1 declaration; empty environment; trust level 0."
