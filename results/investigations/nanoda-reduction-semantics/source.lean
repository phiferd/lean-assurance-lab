/- Exact candidate/control pairs for the bounded reduction-semantics matrix. -/

theorem lalReductionBetaCandidate : (fun x : Nat => x) 1 = 1 := rfl
theorem lalReductionBetaControl : (1 : Nat) = 1 := rfl

theorem lalReductionZetaCandidate : (let x : Nat := 1; x) = 1 := rfl
theorem lalReductionZetaControl : (1 : Nat) = 1 := rfl

structure LALReductionPair where
  first : Nat
  second : Nat

theorem lalReductionProjectionCandidate :
    (LALReductionPair.mk 1 2).second = 2 := rfl
theorem lalReductionProjectionControl : (2 : Nat) = 2 := rfl

theorem lalReductionRecursorCandidate :
    Nat.rec (motive := fun _ => Nat) 7 (fun _ ih => ih) 0 = 7 := rfl
theorem lalReductionRecursorControl : (7 : Nat) = 7 := rfl

theorem lalReductionNatBleCandidate : Nat.ble 3 4 = true := rfl
theorem lalReductionNatBleControl : true = true := rfl

theorem lalReductionNatLandCandidate : Nat.land 3 1 = 1 := rfl
theorem lalReductionNatLandControl : (1 : Nat) = 1 := rfl
