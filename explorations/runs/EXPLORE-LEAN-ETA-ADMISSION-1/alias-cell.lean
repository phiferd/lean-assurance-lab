import EtaAliasAdmissionHarness

open Lean

run_meta do
  assert! Lean.githash == "015d54649bcaaa0861f355b59761ce308e629fbb"
  let accepted ← EtaAliasAdmission.runCell
    "alias-negative" `EtaAliasAdmission.aliasInvalid EtaAliasAdmission.aliasType
  logInfo m!"classification-input aliasAccepted={accepted}"
