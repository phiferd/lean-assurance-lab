import Tree2TowerCorrespondence

/- Local AI-authored bounded acceptance-driven schema; no upstream submission. -/
namespace Tree2ArrowSchema
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial
set_option maxRecDepth 20000
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
  rw [show ((target true).oracle (context true) officialWhnf).whnf d
    (arr tr (R 2 2)) = .ok (arr tr (R 2 2)) from official_whnf_pi _ _ d]
  rfl

theorem negative_ctor (fuel nb : Nat) :
 Official.checkCtorPos ((target true).oracle (context true) officialWhnf)
 Tn fuel nb 2 (arr (arr tr (R 2 2)) tr) ≠ .ok () := by
 cases nb with
 | zero => intro h; cases h
 | succ nb =>
  change ((Official.checkPositivity ((target true).oracle (context true) officialWhnf)
    fuel 2 (arr tr (R 2 2))) >>= fun _ =>
     Official.checkCtorPos ((target true).oracle (context true) officialWhnf)
      Tn fuel nb 3 tr) ≠ .ok ()
  rw [negative_field]
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
  have ht : (target true).types[0] ∈ (target true).types.toList := List.mem_cons_self
  have hc : arr (arr tr (R 2 2)) tr ∈ ((target true).types[0]).ctors := List.mem_cons_of_mem _ (List.mem_cons_self)
  obtain ⟨fuel,nb,hcheck⟩ := hctors _ ht _ hc
  exact False.elim (negative_ctor fuel nb hcheck)

/-- Exact pure oracle facts for all lowered applications and the parameter. -/
private theorem official_whnf_A (d : Nat) : officialWhnf d A = .ok A := by
 apply whnf_mono (show 2 ≤ 16 by decide)
 change whnfBody (pureFns .verified officialEnv 1) officialEnv d A = .ok A
 unfold whnfBody whnfLoopFuel
 rfl
private theorem official_whnf_tr (d : Nat) : officialWhnf d tr = .ok tr := by
 apply whnf_mono (show 3 ≤ 16 by decide)
 change whnfBody (pureFns .verified officialEnv 2) officialEnv d tr = .ok tr
 unfold whnfBody whnfLoopFuel
 rfl
private theorem official_whnf_rows (d : Nat) : officialWhnf d (R 2 2) = .ok (R 2 2) := by
 apply whnf_mono (show 3 ≤ 16 by decide)
 change whnfBody (pureFns .verified officialEnv 2) officialEnv d (R 2 2) = .ok (R 2 2)
 unfold whnfBody whnfLoopFuel
 rfl
private theorem official_whnf_children (d : Nat) : officialWhnf d (R 2 1) = .ok (R 2 1) := by
 apply whnf_mono (show 3 ≤ 16 by decide)
 change whnfBody (pureFns .verified officialEnv 2) officialEnv d (R 2 1) = .ok (R 2 1)
 unfold whnfBody whnfLoopFuel
 rfl

private def positiveOracle := (target false).oracle (context false) officialWhnf

private theorem positive_parameter (f d : Nat) :
 Official.checkPositivity positiveOracle (f+1) d A = .ok () := by
 rw [Official.checkPositivity]
 rw [show positiveOracle.whnf d A = .ok A from official_whnf_A d]
 rfl
private theorem positive_tree (f d : Nat) :
 Official.checkPositivity positiveOracle (f+1) d tr = .ok () := by
 rw [Official.checkPositivity]
 rw [show positiveOracle.whnf d tr = .ok tr from official_whnf_tr d]
 rfl
private theorem positive_rows (f d : Nat) :
 Official.checkPositivity positiveOracle (f+1) d (R 2 2) = .ok () := by
 rw [Official.checkPositivity]
 rw [show positiveOracle.whnf d (R 2 2) = .ok (R 2 2) from official_whnf_rows d]
 rfl
private theorem positive_children (f d : Nat) :
 Official.checkPositivity positiveOracle (f+1) d (R 2 1) = .ok () := by
 rw [Official.checkPositivity]
 rw [show positiveOracle.whnf d (R 2 1) = .ok (R 2 1) from official_whnf_children d]
 rfl
private theorem positive_function (d : Nat) :
 Official.checkPositivity positiveOracle 6 d (arr A (R 2 2)) = .ok () := by
 rw [Official.checkPositivity]
 rw [show positiveOracle.whnf d (arr A (R 2 2)) = .ok (arr A (R 2 2)) from official_whnf_pi _ _ d]
 change Official.checkPositivity positiveOracle 5 (d+1) (R 2 2) = .ok ()
 exact positive_rows 4 (d+1)
private theorem return_tree (nb d : Nat) :
 Official.checkCtorPos positiveOracle Tn 6 (nb+1) d tr = .ok () := rfl
private theorem return_rows (nb d : Nat) :
 Official.checkCtorPos positiveOracle (freshName 1) 6 (nb+1) d (R 2 2) = .ok () := rfl
private theorem return_children (nb d : Nat) :
 Official.checkCtorPos positiveOracle (freshName 2) 6 (nb+1) d (R 2 1) = .ok () := rfl
private theorem ctor_pi (self : Name) (nb d : Nat) (a b : Expr)
 (hi : b.instantiate1 (.fvar d a) = b)
 (hp : Official.checkPositivity positiveOracle 6 d a = .ok ())
 (hb : Official.checkCtorPos positiveOracle self 6 nb (d+1) b = .ok ()) :
 Official.checkCtorPos positiveOracle self 6 (nb+1) d (arr a b) = .ok () := by
 change (do
  let _ ← Official.checkPositivity positiveOracle 6 d a
  Official.checkCtorPos positiveOracle self 6 nb (d+1) (b.instantiate1 (.fvar d a))) = _
 rw [hp,hi]
 exact hb

/-- The six actual lowered constructors pass the explicit pure official oracle.
    This prevents an acceptance implication with an impossible antecedent. -/
theorem positive_checks :
 Official.checkCtorPos positiveOracle Tn 6 4 2 (arr A tr) = .ok () ∧
 Official.checkCtorPos positiveOracle Tn 6 4 2 (arr (arr A (R 2 2)) tr) = .ok () ∧
 Official.checkCtorPos positiveOracle (freshName 1) 6 4 2 (R 2 2) = .ok () ∧
 Official.checkCtorPos positiveOracle (freshName 1) 6 4 2 (arr (R 2 1) (arr (R 2 2) (R 2 2))) = .ok () ∧
 Official.checkCtorPos positiveOracle (freshName 2) 6 4 2 (R 2 1) = .ok () ∧
 Official.checkCtorPos positiveOracle (freshName 2) 6 4 2 (arr tr (arr (R 2 1) (R 2 1))) = .ok () := by
 refine ⟨?_,?_,?_,?_,?_,?_⟩
 · exact ctor_pi Tn 3 2 A tr rfl (positive_parameter 5 2) (return_tree 2 3)
 · exact ctor_pi Tn 3 2 (arr A (R 2 2)) tr rfl (positive_function 2) (return_tree 2 3)
 · exact return_rows 3 2
 · apply ctor_pi (freshName 1) 3 2 (R 2 1) (arr (R 2 2) (R 2 2)) rfl (positive_children 5 2)
   exact ctor_pi (freshName 1) 2 3 (R 2 2) (R 2 2) rfl (positive_rows 5 3) (return_rows 1 4)
 · exact return_children 3 2
 · apply ctor_pi (freshName 2) 3 2 tr (arr (R 2 1) (R 2 1)) rfl (positive_tree 5 2)
   exact ctor_pi (freshName 2) 2 3 (R 2 1) (R 2 1) rfl (positive_children 5 3) (return_children 1 4)

/-- Nonvacuous positive control, using actual elimination and constructor checks. -/
theorem positive_acceptance :
 Official.OfficialPosAccepts (context false) (declaration false) officialWhnf 2 := by
 refine ⟨4,target false,lowering false,?_⟩
 intro ty hty ct hct
 have ht : ty = (target false).types[0] ∨ ty = row 2 2 ∨ ty = row 2 1 := by
  simpa [target,List.mem_cons,List.not_mem_nil,or_false] using hty
 rcases ht with rfl | rfl | rfl
 · have hc : ct = arr A tr ∨ ct = arr (arr A (R 2 2)) tr := by
    simpa [target,List.mem_cons,List.not_mem_nil,or_false] using hct
   rcases hc with rfl | rfl
   · exact ⟨6,4,positive_checks.1⟩
   · exact ⟨6,4,positive_checks.2.1⟩
 · have hc : ct = R 2 2 ∨ ct = arr (R 2 1) (arr (R 2 2) (R 2 2)) := by
    simpa [Tree2TowerOfficial.row,R,List.mem_cons,List.not_mem_nil,or_false] using hct
   rcases hc with rfl | rfl
   · exact ⟨6,4,positive_checks.2.2.1⟩
   · exact ⟨6,4,positive_checks.2.2.2.1⟩
 · have hc : ct = R 2 1 ∨ ct = arr tr (arr (R 2 1) (R 2 1)) := by
    simpa [Tree2TowerOfficial.row,R,List.mem_cons,List.not_mem_nil,or_false] using hct
   rcases hc with rfl | rfl
   · exact ⟨6,4,positive_checks.2.2.2.2.1⟩
   · exact ⟨6,4,positive_checks.2.2.2.2.2⟩

/-- Exact root and fixed ordinary List schema/lookup table for both encoders. -/
theorem lookup_schema (bad : Bool) :
 (env bad).find? Ln = some (.indInfo listCV {sortZ := .never,all := [Ln],nparams := 1,ctors := [nilCV.name,consCV.name]}) ∧
 (env bad).find? nilCV.name = some (.ctorInfo nilCV 1 0) ∧
 (env bad).find? consCV.name = some (.ctorInfo consCV 1 2) ∧
 (env bad).find? nodeCV.name = some (.ctorInfo (node bad) 1 1) := ⟨rfl,rfl,rfl,rfl⟩
theorem freshness (bad : Bool) (i : Nat) :
 (env bad).find? (freshName i) = none ∧ freshName i ≠ Tn ∧ freshName i ≠ Ln := by
 refine ⟨rfl,?_,?_⟩ <;> (intro h; cases h)

theorem encoding_never (bad : Bool) :
 Tree2TowerCorrespondence.neverBinders (node bad).type = true := by
 cases bad <;> rfl

/-- Frame-relative native node readback, not an assertion of emitted records. -/
theorem node_readback (bad : Bool) :
 (nestCtorNf (ctx bad) [] 2 [] [A] (node bad)
  [(arr (domain bad) (l (l X)),bm)] X).ty =
 arr (arr (if bad then tr else A) (l (l tr))) tr := by
 cases bad <;> cbv

/-- Restore the actual lowered node expression from the independently read-back
    native crest; replacement leaves completed allocation unchanged. -/
theorem node_restoration (bad : Bool) :
 (Official.replaceAll (context bad)
  (arr (arr (if bad then tr else A) (l (l tr))) tr)).run (target bad) =
 .ok (arr (arr (if bad then tr else A) (R 2 2)) tr,target bad) := by
 cases bad <;> cbv

#print axioms node_crest
#print axioms lowering
#print axioms successful_lowering
#print axioms negative_field
#print axioms acceptance_domain
#print axioms positive_checks
#print axioms positive_acceptance
#print axioms lookup_schema
#print axioms freshness
#print axioms encoding_never
#print axioms node_readback
#print axioms node_restoration
end Tree2ArrowSchema
