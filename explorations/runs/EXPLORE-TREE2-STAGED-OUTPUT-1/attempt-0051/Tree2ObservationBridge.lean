import Tree2Execution
import Tree2CtorReadback

/- Local AI-authored exact-output bridge for depth two. No upstream submission. -/
namespace Tree2ObservationBridge
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial

/-- Explicitly regroup the actual depth-first output into T/Rows/Children order. -/
def groupedTypes (r : NestedPositivity) : List Expr :=
 [r.ctorNfs[0]!.ty,r.ctorNfs[5]!.ty,r.ctorNfs[1]!.ty,
  r.ctorNfs[4]!.ty,r.ctorNfs[2]!.ty,r.ctorNfs[3]!.ty]

/-- Observe first; apply the official replacement only to returned records. -/
def observedLowering : CheckM (List Expr × Official.ElimSt) := do
 let r ← nestedBlockPositivity (checker 7) (En 2) (Cn 2) [roots 2]
 (groupedTypes r |>.mapM (Official.replaceAll (context 2))).run (target 2)

theorem actual_records : Tree2Execution.expected.ctorNfs = Tree2CtorReadback.expected := rfl

theorem actual_lowering : observedLowering =
  .ok (Tree2CtorReadback.loweredTypes,target 2) := by
 unfold observedLowering
 rw [Tree2Execution.actual_output]
 change ((groupedTypes Tree2Execution.expected).mapM (Official.replaceAll (context 2))).run (target 2) = _
 change (Tree2CtorReadback.groupedTypes.mapM (Official.replaceAll (context 2))).run (target 2) = _
 exact Tree2CtorReadback.readback_lowering

/-- Fixed-depth package: exact official lowering, constructed PosDR, exact native
    observation, and official replacement of the returned constructor rows. -/
theorem fixed_bridge :
 Official.elimNested (context 2) (declaration 2) 4 = .ok (target 2) ∧
 PosDR (checker 7) (En 2) (Cn 2) 3
  (.ctors [] [] 2 [] [A] [Tn] [X] (roots 2)) ∧
 nestedBlockPositivity (checker 7) (En 2) (Cn 2) [roots 2] =
  .ok Tree2Execution.expected ∧
 observedLowering = .ok (Tree2CtorReadback.loweredTypes,target 2) :=
 ⟨official_lowering_family 2,native_family 2 7 (by decide),
  Tree2Execution.actual_output,actual_lowering⟩

#print axioms actual_records
#print axioms actual_lowering
#print axioms fixed_bridge
end Tree2ObservationBridge
