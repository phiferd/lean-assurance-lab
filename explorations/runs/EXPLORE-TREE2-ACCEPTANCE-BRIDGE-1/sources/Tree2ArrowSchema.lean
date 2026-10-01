import Tree2TowerCorrespondence

/- Local AI-authored bounded acceptance-driven schema; no upstream submission. -/
namespace Tree2ArrowSchema
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial
set_option maxRecDepth 3000
set_option maxHeartbeats 2000000
attribute [local cbv_eval] Expr.bvarB_eq Expr.fvarB_eq ConLeche.Expr.Expr.hasLP_eq
attribute [local cbv_opaque] Expr.bvarB Expr.fvarB Expr.hasLP

/-- true selects the admitted negative domain; false the parameter domain. -/
def domain (bad : Bool) : Expr := if bad then X else A
def node (bad : Bool) : ConstantVal :=
 ⟨nodeCV.name,[],pi S (pi
  (pi (if bad then t (.bvar 0) else .bvar 0) (l (l (t (.bvar 1)))))
  (t (.bvar 1)))⟩
def roots (bad : Bool) : List (ConstantVal × Nat) := [(leafCV,1),(node bad,1)]
def env (bad : Bool) : Env := ⟨[
 .indInfo listCV {sortZ := .never,all := [Ln],nparams := 1,ctors := [nilCV.name,consCV.name]},
 .ctorInfo nilCV 1 0,.ctorInfo consCV 1 2,
 .indInfo treeCV {sortZ := .never,all := [Tn],nparams := 1,ctors := [leafCV.name,nodeCV.name]},
 .ctorInfo leafCV 1 1,.ctorInfo (node bad) 1 1]⟩
def ctx (bad : Bool) : NestCtx := ⟨[Tn],[],1,[0],[A],.succ .zero,(env bad).find?⟩
def context (bad : Bool) : Official.ElimCtx :=
 {find? := (env bad).find?,ctorsOf := fun c => if c == Ln then listCs else [],
  lvls := [],ps := [A],auxName := freshName}
def declaration (bad : Bool) : List Official.MemberDecl :=
 [⟨Tn,treeCV.type,[leafCV.type,(node bad).type]⟩]
def target (bad : Bool) : Official.ElimSt :=
 {Tree2TowerOfficial.target 2 with types := #[
  ⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) (R 2 2)) tr]⟩,
  row 2 2,row 2 1]}
/-- New root/auxiliary types are opaque, without constructors, as the official
    positivity environment requires; fixed ordinary List is retained. -/
def officialEnv : Env := ⟨[
 .indInfo listCV {sortZ := .never,all := [Ln],nparams := 1,ctors := [nilCV.name,consCV.name]},
 .ctorInfo nilCV 1 0,.ctorInfo consCV 1 2,
 .indInfo treeCV {sortZ := .never,all := [Tn,freshName 1,freshName 2],nparams := 1,ctors := []},
 .indInfo ⟨freshName 1,[],pi S S⟩ {sortZ := .never,all := [Tn,freshName 1,freshName 2],nparams := 1,ctors := []},
 .indInfo ⟨freshName 2,[],pi S S⟩ {sortZ := .never,all := [Tn,freshName 1,freshName 2],nparams := 1,ctors := []}]⟩
def officialWhnf (d : Nat) (e : Expr) : CheckM Expr := whnf .verified officialEnv 16 d e

theorem node_crest (bad : Bool) :
 nestCrest [Tn] [] [A] [X] ((node bad).type.instantiateLevelParams [] []) =
 some (arr (arr (domain bad) (l (l X))) X) := by
 cases bad <;> cbv

theorem lowering (bad : Bool) :
 Official.elimNested (context bad) (declaration bad) 4 = .ok (target bad) := by
 cases bad <;> cbv

#print axioms node_crest
#print axioms lowering
end Tree2ArrowSchema
