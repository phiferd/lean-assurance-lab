import EtaAdmissionHarness

open Lean

run_meta do
  let accepted ← EtaAdmissionConfirmation.runCell
    "alias-negative" `EtaAdmissionConfirmation.aliasInvalid EtaAdmissionConfirmation.aliasType
  logInfo m!"classification-input aliasAccepted={accepted}"
