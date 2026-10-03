import EtaAliasAdmissionHarness

open Lean

run_meta do
  assert! Lean.githash == "015d54649bcaaa0861f355b59761ce308e629fbb"
  let accepted ← EtaAliasAdmission.runCell
    "explicit-negative" `EtaAliasAdmission.explicitInvalid EtaAliasAdmission.explicitType
  logInfo m!"classification-input explicitAccepted={accepted}"
