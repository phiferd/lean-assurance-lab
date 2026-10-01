import Tree2DomainGrammar

/- Exact source schema and independent lowering for the symbolic-domain trial. -/
namespace Tree2DomainSchema
open ConLeche Tree2Bridge Tree2TowerSupport Tree2DomainGrammar
open Tree2TowerNative (pow)

def node (D : Domain) (N : Nat) : ConstantVal :=
 ⟨nodeCV.name,[],pi S (pi (pi (D.raw 0) (pow N (t (.bvar 1)))) (t (.bvar 1)))⟩
def roots (D : Domain) (N : Nat) := [(leafCV,1),(node D N,1)]
def env (D : Domain) (N : Nat) : Env := ⟨[
 .indInfo listCV {sortZ := .never,all := [Ln],nparams := 1,ctors := [nilCV.name,consCV.name]},
 .ctorInfo nilCV 1 0,.ctorInfo consCV 1 2,
 .indInfo treeCV {sortZ := .never,all := [Tn],nparams := 1,ctors := [leafCV.name,nodeCV.name]},
 .ctorInfo leafCV 1 1,.ctorInfo (node D N) 1 1]⟩
def ctx (D : Domain) (N : Nat) : NestCtx :=
 ⟨[Tn],[],1,[0],[A],.succ .zero,(env D N).find?⟩
def context (D : Domain) (N : Nat) : Official.ElimCtx :=
 {find? := (env D N).find?,ctorsOf := fun c => if c == Ln then listCs else [],
  lvls := [],ps := [A],auxName := Tree2TowerOfficial.freshName}
def declaration (D : Domain) (N : Nat) : List Official.MemberDecl :=
 [⟨Tn,treeCV.type,[leafCV.type,(node D N).type]⟩]
def rootRow (D : Domain) (N : Nat) : Official.AuxType :=
 ⟨Tn,S,[arr A tr,arr (arr D.official (Tree2TowerOfficial.R N N)) tr]⟩
def target (D : Domain) (N : Nat) : Official.ElimSt :=
 {aux := (Tree2TowerOfficial.target N).aux,
  types := (rootRow D N :: (List.range N).map
    (fun i => Tree2TowerOfficial.row N (N-i))).toArray,next := N+1}

theorem exact_node_lookup (D : Domain) (N : Nat) :
 (env D N).find? nodeCV.name = some (.ctorInfo (node D N) 1 1) := rfl
theorem list_lookup (D : Domain) (N : Nat) :
 (env D N).find? Ln = E.find? Ln ∧
 (env D N).find? nilCV.name = E.find? nilCV.name ∧
 (env D N).find? consCV.name = E.find? consCV.name := ⟨rfl,rfl,rfl⟩
theorem node_initial (D : Domain) (N : Nat) :
 Official.instPiParams (node D N).type (context D N).ps =
 .ok (arr (arr D.official (pow N tr)) tr) := by
 simp only [node,Official.instPiParams,context,instPisWith,pi,Expr.instantiate1,
  Tree2TowerNative.pow_inst,Domain.raw_instantiate]
 rfl

def coreBound (D : Domain) (N : Nat) : Nat := max (D.height+2) (N+3)+2

#print axioms exact_node_lookup
#print axioms node_initial
end Tree2DomainSchema
