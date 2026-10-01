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

/-- All successful queue-fuel choices have the same exact output. -/
theorem lowering_all_fuels (bad : Bool) (fuel : Nat) :
 Official.elimNested (context bad) (declaration bad) fuel =
 if 4 ≤ fuel then .ok (target bad)
 else .error (.notImplemented "official spec: elimination fuel") := by
 cases bad <;> (cases fuel with
 | zero => rfl
 | succ f => cases f with
   | zero => cbv
   | succ f => cases f with
     | zero => cbv
     | succ f => cases f with
       | zero => cbv
       | succ f => cbv)

theorem successful_lowering (bad : Bool) (fuel : Nat) (st : Official.ElimSt)
 (h : Official.elimNested (context bad) (declaration bad) fuel = .ok st) :
 st = target bad := by
 rw [lowering_all_fuels] at h
 split at h
 · exact (Except.ok.inj h).symm
 · cases h

private theorem official_whnf_pi (a b : Expr) (d : Nat) :
 officialWhnf d (arr a b) = .ok (arr a b) := by
 apply whnf_mono (show 2 ≤ 16 by decide)
 change whnfBody (pureFns .verified officialEnv 1) officialEnv d (arr a b) = .ok (arr a b)
 unfold whnfBody whnfLoopFuel
 rfl

/-- The official negative-domain branch rejects for EVERY field fuel. -/
theorem negative_field (fuel d : Nat) :
 Official.checkPositivity ((target true).oracle (context true) officialWhnf)
 fuel d (arr tr (R 2 2)) =
 .error (if fuel = 0 then .notImplemented "official spec: positivity fuel"
  else .invalid "official: non positive occurrence of the datatypes being declared") := by
 cases fuel with
 | zero => rfl
 | succ f =>
  rw [Official.checkPositivity]
  change (do
   let e ← officialWhnf d (arr tr (R 2 2))
   if !((target true).oracle (context true) officialWhnf).occ e then pure ()
   else match e with
    | .forallE a b _ =>
      if ((target true).oracle (context true) officialWhnf).occ a then
       throw (.invalid "official: non positive occurrence of the datatypes being declared")
      else Official.checkPositivity _ f (d+1) (b.instantiate1 (.fvar d a))
    | _ => if ((target true).oracle (context true) officialWhnf).valid e then pure ()
      else throw (.invalid "official: non valid occurrence of the datatypes being declared")) = _
  rw [official_whnf_pi]
  rfl

theorem negative_ctor (fuel nb : Nat) :
 Official.checkCtorPos ((target true).oracle (context true) officialWhnf)
 Tn fuel nb 2 (arr (arr tr (R 2 2)) tr) ≠ .ok () := by
 cases nb with
 | zero => intro h; cases h
 | succ nb =>
  rw [Official.checkCtorPos,negative_field]
  cases fuel <;> (intro h; cases h)

/-- Acceptance is actually consumed: its node constructor check excludes
    the admitted negative schema, after identifying its real elimination output. -/
theorem acceptance_domain (bad : Bool)
 (ha : Official.OfficialPosAccepts (context bad) (declaration bad) officialWhnf 2) :
 bad = false := by
 cases bad with
 | false => rfl
 | true =>
  obtain ⟨f,st,helim,hctors⟩ := ha
  have he := successful_lowering true f st helim
  subst st
  have ht : (target true).types[0] ∈ (target true).types.toList := List.mem_cons_self _ _
  have hc : arr (arr tr (R 2 2)) tr ∈ ((target true).types[0]).ctors := List.mem_cons_of_mem _ (List.mem_cons_self _ _)
  obtain ⟨fuel,nb,hcheck⟩ := hctors _ ht _ hc
  exact False.elim (negative_ctor fuel nb hcheck)

#print axioms node_crest
#print axioms lowering
#print axioms successful_lowering
#print axioms negative_field
#print axioms acceptance_domain
end Tree2ArrowSchema
