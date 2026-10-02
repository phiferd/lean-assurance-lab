import Lean

open Lean

run_meta do
  logInfo m!"revision={Lean.githash} version={Lean.versionString}"
