import EtaAdmissionHarness

open Lean

run_meta do
  let accepted ← EtaAdmissionConfirmation.runCell
    "explicit-negative" `EtaAdmissionConfirmation.explicitInvalid EtaAdmissionConfirmation.explicitType
  logInfo m!"classification-input explicitAccepted={accepted}"
