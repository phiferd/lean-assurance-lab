import Tree2EliminationDeterminism
import Tree2ArrowSchema

/- Local AI-authored exact parametric source; prior archives remain unchanged. -/
namespace Tree2ArrowTowerSchema
open ConLeche Tree2Bridge Tree2TowerSupport
open Tree2TowerNative (pow)

def node (bad : Bool) (N : Nat) : ConstantVal :=
 ⟨nodeCV.name,[],pi S (pi
  (pi (if bad then t (.bvar 0) else .bvar 0) (pow N (t (.bvar 1))))
  (t (.bvar 1)))⟩
def roots (bad : Bool) (N : Nat) := [(leafCV,1),(node bad N,1)]
def env (bad : Bool) (N : Nat) : Env := ⟨[
 .indInfo listCV {sortZ := .never,all := [Ln],nparams := 1,ctors := [nilCV.name,consCV.name]},
 .ctorInfo nilCV 1 0,.ctorInfo consCV 1 2,
 .indInfo treeCV {sortZ := .never,all := [Tn],nparams := 1,ctors := [leafCV.name,nodeCV.name]},
 .ctorInfo leafCV 1 1,.ctorInfo (node bad N) 1 1]⟩
def ctx (bad : Bool) (N : Nat) : NestCtx :=
 ⟨[Tn],[],1,[0],[A],.succ .zero,(env bad N).find?⟩
def context (bad : Bool) (N : Nat) : Official.ElimCtx :=
 {find? := (env bad N).find?,ctorsOf := fun c => if c == Ln then listCs else [],
  lvls := [],ps := [A],auxName := Tree2TowerOfficial.freshName}
def declaration (bad : Bool) (N : Nat) : List Official.MemberDecl :=
 [⟨Tn,treeCV.type,[leafCV.type,(node bad N).type]⟩]
def domain (bad : Bool) : Expr := if bad then X else A
def rootRow (bad : Bool) (N : Nat) : Official.AuxType :=
 ⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) (Tree2TowerOfficial.R N N)) tr]⟩
def target (bad : Bool) (N : Nat) : Official.ElimSt :=
 {aux := (Tree2TowerOfficial.target N).aux,
  types := (rootRow bad N :: (List.range N).map
    (fun i => Tree2TowerOfficial.row N (N-i))).toArray,next := N+1}

theorem exact_node_lookup (bad : Bool) (N : Nat) :
 (env bad N).find? nodeCV.name = some (.ctorInfo (node bad N) 1 1) := rfl

theorem list_lookup (bad : Bool) (N : Nat) :
 (env bad N).find? Ln = E.find? Ln ∧
 (env bad N).find? nilCV.name = E.find? nilCV.name ∧
 (env bad N).find? consCV.name = E.find? consCV.name := ⟨rfl,rfl,rfl⟩

#print axioms exact_node_lookup
#print axioms list_lookup
end Tree2ArrowTowerSchema
