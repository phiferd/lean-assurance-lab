module
public import Lean
public section
set_option Elab.async false
set_option warn.sorry false
namespace TrustAssumptionPilot
set_option pp.fullNames true
set_option pp.privateNames true

theorem pure : True := True.intro
axiom explicit : True
theorem explicitMid : True := explicit
theorem explicitLeaf : True := explicitMid

theorem propextBase (p q : Prop) (h : p ↔ q) : p = q := propext h
theorem propextLeaf (p q : Prop) (h : p ↔ q) : p = q := propextBase p q h

noncomputable def choiceBase : Nat := Classical.choice (show Nonempty Nat from ⟨0⟩)
noncomputable def choiceLeaf : Nat := choiceBase

theorem sorryBase : True := by sorry
theorem sorryLeaf : True := sorryBase

theorem nativeEval : 2 + 2 = (4 : Nat) := by native_decide
theorem nativeLeaf : 2 + 2 = (4 : Nat) := nativeEval
end TrustAssumptionPilot

#print axioms TrustAssumptionPilot.pure
#print axioms TrustAssumptionPilot.explicitLeaf
#print axioms TrustAssumptionPilot.propextLeaf
#print axioms TrustAssumptionPilot.choiceLeaf
#print axioms TrustAssumptionPilot.sorryLeaf
#print axioms TrustAssumptionPilot.nativeLeaf
