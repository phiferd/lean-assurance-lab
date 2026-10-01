import ConLeche.Complete.OfficialNested
import ConLeche.Complete.PosDerivComplete

/- Local AI-authored exploratory proof. No upstream submission authorized. -/
namespace Tree2Bridge
open ConLeche

def nm (s : String) : Name := .str .anonymous s
def Tn := nm "Tree2"
def Ln := nm "List"
def un := nm "u"
def rn := nm "Rows"
def cn := nm "Children"
def S : Expr := .sort (.succ .zero)
def bm : BinderMeta := ⟨.never⟩
def pi (a b : Expr) : Expr := .forallE a b bm
def arr := pi
def l (a : Expr) : Expr := .app (.const Ln [.zero]) a
def t (a : Expr) : Expr := .app (.const Tn []) a
def A : Expr := .fvar 0 S
def X : Expr := .fvar 1 S
def Y : Expr := .fvar 2 S
def P : Expr := .fvar 0 (.sort .zero)
def Q : Expr := .fvar 1 (.sort .zero)
def listCV : ConstantVal := ⟨Ln, [un], pi (.sort (.succ (.param un))) (.sort (.succ (.param un)))⟩
def nilCV : ConstantVal := ⟨nm "List.nil", [un], pi (.sort (.succ (.param un)))
  (.app (.const Ln [.param un]) (.bvar 0))⟩
def consCV : ConstantVal := ⟨nm "List.cons", [un], pi (.sort (.succ (.param un)))
  (pi (.bvar 0) (pi (.app (.const Ln [.param un]) (.bvar 1))
    (.app (.const Ln [.param un]) (.bvar 2))))⟩
def treeCV : ConstantVal := ⟨Tn, [], pi S S⟩
def leafCV : ConstantVal := ⟨nm "Tree2.leaf", [], pi S (pi (.bvar 0) (t (.bvar 1)))⟩
def nodeCV : ConstantVal := ⟨nm "Tree2.node", [], pi S (pi (l (l (t (.bvar 0)))) (t (.bvar 1)))⟩
def listCs : List (ConstantVal × Nat) := [(nilCV,0),(consCV,2)]
def rootCs : List (ConstantVal × Nat) := [(leafCV,1),(nodeCV,1)]
def E : Env := ⟨[.indInfo listCV {all := [Ln], nparams := 1, ctors := [nilCV.name,consCV.name]}, .ctorInfo nilCV 1 0, .ctorInfo consCV 1 2,
  .indInfo treeCV {all := [Tn], nparams := 1, ctors := [leafCV.name,nodeCV.name]}]⟩
def C : NestCtx := ⟨[Tn], [], 1, [0], [A], .succ .zero, E.find?⟩
def ops : CheckerOps CheckM := fueledOps .verified 64
def Ko : NestKey := ⟨Ln, [.zero], [l X]⟩
def Ki : NestKey := ⟨Ln, [.zero], [X]⟩
def Ho : NestHole := ⟨Ko,2⟩
def Hi : NestHole := ⟨Ki,2⟩
def O : Official.ElimCtx :=
 {find? := E.find?, ctorsOf := fun n => if n == Ln then listCs else [],
  lvls := [], ps := [A], auxName := fun i => if i == 1 then rn else cn}
def decl : List Official.MemberDecl := [⟨Tn,treeCV.type,[leafCV.type,nodeCV.type]⟩]
def tr : Expr := t A
def rows : Expr := .app (.const rn []) A
def children : Expr := .app (.const cn []) A
def lowered : Official.ElimSt :=
 {aux := [(l (l tr),rn),(l tr,cn)], next := 3,
  types := #[⟨Tn,S,[arr A tr,arr rows tr]⟩,
    ⟨rn,S,[rows,arr children (arr rows rows)]⟩,
    ⟨cn,S,[children,arr tr (arr children children)]⟩]}

set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

theorem official_lowering : Official.elimNested O decl 4 = .ok lowered := by cbv

theorem canonical_list :
 nestCanonCrest [Ln] [.zero] 1 (nilCV.type.instantiateLevelParams [un] [.zero]) = some Q ∧
 nestCanonCrest [Ln] [.zero] 1 (consCV.type.instantiateLevelParams [un] [.zero]) =
   some (arr P (arr Q Q)) := by exact ⟨rfl,rfl⟩

theorem root_crests :
 nestCrest [Tn] [] [A] [X] leafCV.type = some (arr A X) ∧
 nestCrest [Tn] [] [A] [X] nodeCV.type = some (arr (l (l X)) X) := by exact ⟨rfl,rfl⟩

theorem container_crests :
 nestCrest [Ln] [.zero] [l X] [Y] (consCV.type.instantiateLevelParams [un] [.zero]) =
   some (arr (l X) (arr Y Y)) ∧
 nestCrest [Ln] [.zero] [X] [Y] (consCV.type.instantiateLevelParams [un] [.zero]) =
   some (arr X (arr Y Y)) := by exact ⟨rfl,rfl⟩

theorem frame_reset : nestWalkStack C [Ho] [X] = [] ∧
 grpKeys [.zero] [X] [(Ln,S)] ++ [Ko] = [Ki,Ko] ∧ Ki ≠ Ko := by
 constructor
 · cbv
 constructor
 · cbv
 intro h
 have hds := congrArg NestKey.ds h
 have hx : X = l X := (List.cons.inj hds).1
 have hh := congrArg Expr.getAppFn hx
 change Expr.fvar 1 S = Expr.const Ln [.zero] at hh
 cases hh

-- Concrete pure-Core checks; no successful-operation hypotheses.
theorem infer_A : ops.inferType E 2 A = .ok S := by cbv
theorem infer_lX : ops.inferType E 2 (l X) = .ok S := by cbv
theorem infer_llX : ops.inferType E 2 (l (l X)) = .ok S := by cbv
theorem infer_leaf : ops.inferType E 2 (arr A X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) := by cbv
theorem infer_node : ops.inferType E 2 (arr (l (l X)) X) =
 .ok (.sort (.imax (.succ .zero) (.succ .zero))) := by cbv
theorem infer_outer : ops.inferType E 3 (arr (l X) (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) := by cbv
theorem infer_inner : ops.inferType E 3 (arr X (arr Y Y)) =
 .ok (.sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))) := by cbv

#print axioms official_lowering
#print axioms canonical_list
#print axioms root_crests
#print axioms container_crests
#print axioms frame_reset
#print axioms infer_outer
end Tree2Bridge
