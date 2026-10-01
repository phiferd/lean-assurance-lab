import Tree2TowerCorrespondence

/- Local AI-authored finite readback seam; no upstream submission.
   This does not assert that nestedBlockPositivity emits these records. -/
namespace Tree2CtorReadback
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial
set_option maxRecDepth 20000
attribute [local cbv_eval] Expr.bvarB_eq Expr.fvarB_eq ConLeche.Expr.Expr.hasLP_eq
attribute [local cbv_opaque] Expr.bvarB Expr.fvarB Expr.hasLP
set_option maxHeartbeats 2000000

/-- Checker walk order, specified independently of any run. -/
def expected : Array NestCtorNf := #[
 ⟨leafCV.name,[],[A],arr A tr⟩,
 ⟨nilCV.name,[.zero],[l tr],l (l tr)⟩,
 ⟨nilCV.name,[.zero],[tr],l tr⟩,
 ⟨consCV.name,[.zero],[tr],arr tr (arr (l tr) (l tr))⟩,
 ⟨consCV.name,[.zero],[l tr],arr (l tr) (arr (l (l tr)) (l (l tr)))⟩,
 ⟨nodeCV.name,[],[A],arr (l (l tr)) tr⟩]

/-- The same raw fvar 2 reads differently in the two actual frames. -/
theorem distinct_frame_images :
 nestHoleImg (Cn 2) [holeAt 0] 2 = some (l tr) ∧
 nestHoleImg (Cn 2) [holeAt 1] 2 = some (l (l tr)) ∧
 l tr ≠ l (l tr) := by
 constructor
 · rfl
 constructor
 · rfl
 · intro h
   have hh := congrArg Expr.getAppArgs h
   simp [l,tr,t,Expr.getAppArgs] at hh

/-- Exact finite readback of the six walked telescopes, using each frame's
    own key. No assumed checker acceptance or assumed PosDR. -/
theorem constructor_readbacks :
 #[nestCtorNf (Cn 2) [] 2 [] [A] leafCV [(A,bm)] X,
   nestCtorNf (Cn 2) [holeAt 1] 3 [.zero] [l X] nilCV [] Y,
   nestCtorNf (Cn 2) [holeAt 0] 3 [.zero] [X] nilCV [] Y,
   nestCtorNf (Cn 2) [holeAt 0] 3 [.zero] [X] consCV [(X,bm),(Y,bm)] Y,
   nestCtorNf (Cn 2) [holeAt 1] 3 [.zero] [l X] consCV [(l X,bm),(Y,bm)] Y,
   nestCtorNf (Cn 2) [] 2 [] [A] (node 2) [(l (l X),bm)] X] = expected := by
 cbv

/-- Group the depth-first records into official T/Rows/Children order. -/
def groupedTypes : List Expr :=
 [expected[0]!.ty,expected[5]!.ty,expected[1]!.ty,
  expected[4]!.ty,expected[2]!.ty,expected[3]!.ty]
def loweredTypes : List Expr := (target 2).types.toList.flatMap (·.ctors)

/-- Readback then existing official replacement gives the actual six lowered
    constructor types, without allocating or changing the completed state. -/
theorem readback_lowering :
 (groupedTypes.mapM (Official.replaceAll (context 2))).run (target 2) =
 .ok (loweredTypes,target 2) := by
 cbv

#print axioms distinct_frame_images
#print axioms constructor_readbacks
#print axioms readback_lowering
end Tree2CtorReadback
