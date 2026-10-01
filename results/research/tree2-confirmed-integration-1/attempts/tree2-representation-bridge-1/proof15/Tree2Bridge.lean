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

set_option maxRecDepth 20000
set_option maxHeartbeats 1000000

attribute [local cbv_eval] Expr.bvarB_eq Expr.fvarB_eq ConLeche.Expr.Expr.hasLP_eq
attribute [local cbv_opaque] Expr.bvarB Expr.fvarB Expr.hasLP

theorem nested_outer : Official.isNestedApp O [Tn] (l (l tr)) =
 .ok (some (Ln,[.zero],1,[l tr])) := by
 simp [Official.isNestedApp, O, E, Env.find?, ConstantInfo.name, ConstantInfo.toConstantVal, listCV, listCs, Ln, Tn, nm, tr, t, l, Expr.getAppFn, Expr.getAppArgs, Expr.nestOcc, Expr.bvarB_eq, Expr.bvarBound, quotName, A]
 rfl
attribute [local cbv_eval] nested_outer

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
 · unfold nestWalkStack
   have h : [X].all (fun x => x.fvarB ≤ C.hiAt 0) = true := by
     simp [Expr.fvarB_eq, Expr.fvarRange, X, C, NestCtx.hiAt]
   rw [h]
   rfl
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

-- Native derivations are constructed from the rules, never extracted from runs.
theorem ordinary (act : List NestKey) (prog : List NestHole) (d : Nat) :
 PosDR ops E C 1 (.field act prog d 0 A .ordinary A) := by
 apply PosDR.const (w := A) (n := 0)
 · cbv
 · cbv

theorem member (act : List NestKey) (prog : List NestHole) (d : Nat) :
 PosDR ops E C 1 (.field act prog d 0 X (.recursive 0) X) := by
 apply PosDR.hole (w := X) (i := 1) (ty := S) (n := 0)
 · cbv
 · simp [X, Expr.nestOcc, C, NestCtx.hiAt]; omega
 · rfl
 · cbv
 · cbv
 · cbv
 · simp [X, Expr.getAppArgs]

theorem self (act : List NestKey) (ds : Expr) (d : Nat) :
 PosDR ops E C 1 (.field act [⟨⟨Ln,[.zero],[ds]⟩,2⟩] d 0 Y .inProgress Y) := by
 apply PosDR.frameHole (w := Y) (i := 2) (ty := S)
   (h := ⟨⟨Ln,[.zero],[ds]⟩,2⟩) (n := 0)
 · cbv
 · cbv
 · rfl
 · cbv
 · cbv
 · cbv
 · simp [Y, Expr.getAppArgs]
 · cbv

theorem inner_tele : PosDR ops E C 1
 (.tele [Ki,Ko] [Hi] 3 2 0 (arr X (arr Y Y))
   [.recursive 0,.inProgress] [(X,bm),(Y,bm)] Y) := by
 apply PosDR.teleCons (m₁ := 1) (m₃ := 1)
 · omega
 · exact member _ _ _
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact self _ X _
   · omega
   · exact PosDR.teleNil

theorem inner_ctors : PosDR ops E C 1
 (.ctors [Ki,Ko] [Hi] 3 [.zero] [X] [Ln] [Y] listCs) := by
 apply PosDR.ctorsCons (crest := Y) (ty := S) (sv := .succ .zero)
   (m₁ := 0) (m₂ := 1) (ks := []) (nds := []) (cur := Y)
 · cbv
 · exact rfl
 · cbv
 · cbv
 · omega
 · exact PosDR.teleNil
 · cbv
 · cbv
 · cbv
 · omega
 · apply PosDR.ctorsCons (crest := arr X (arr Y Y))
     (ty := .sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero))))
     (sv := .imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))
     (m₁ := 1) (m₂ := 0) (ks := [.recursive 0,.inProgress])
     (nds := [(X,bm),(Y,bm)]) (cur := Y)
   · cbv
   · exact container_crests.2
   · exact infer_inner
   · cbv
   · omega
   · exact inner_tele
   · cbv
   · cbv
   · cbv
   · omega
   · exact PosDR.ctorsNil

theorem inner_frame : PosDR ops E C 1 (.frame [Ko] [] [.zero] [X] [(Ln,S)]) := by
 apply PosDR.frame (m := 1) (ctors := listCs)
 · simp
 · constructor
   · cbv
   · decide
 · exact ⟨listCs,by cbv⟩
 · simp
 · intro p hp
   simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
   subst p
   exact ⟨0,by cbv⟩
 · simp
 · cbv
 · cbv
 · exact ⟨S,infer_lX⟩
 · omega
 · exact inner_ctors

theorem scoped_outer : ProgScoped C [Ho] := by
 have h : ∀ x ∈ [l X], Expr.WScoped (C.hiAt 0) x := by
   intro x hx
   simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
   subst x
   cbv
 exact ProgScoped.push (us := [.zero]) (ds := [l X]) ProgScoped.nil h [(Ln,S)]

theorem inner_field : PosDR ops E C 2
 (.field [Ko] [Ho] 3 0 (l X) (.nested false) (l X)) := by
 apply PosDR.cont (w := l X) (c := Ln) (us := [.zero]) (L := listCs)
   (nPc := 1) (nI := 0) (cty := S) (grp := [(Ln,S)]) (m := 1)
 · cbv
 · cbv
 · rfl
 · cbv
 · cbv
 · cbv
 · decide
 · simp [l, Expr.getAppArgs]
 · intro x hx
   have hh : x = X := by simpa [l, Expr.getAppArgs] using hx
   subst x
   cbv
 · intro x hx
   have hh : x = X := by simpa [l, Expr.getAppArgs] using hx
   subst x
   cbv
 · exact scoped_outer
 · cbv
 · change Ki ∉ [Ko]
   simpa using frame_reset.2.2
 · rfl
 · omega
 · change PosDR ops E C 1 (.frame [Ko] (nestWalkStack C [Ho] [X]) [.zero] [X] [(Ln,S)])
   rw [frame_reset.1]
   exact inner_frame

theorem outer_tele : PosDR ops E C 2
 (.tele [Ko] [Ho] 3 2 0 (arr (l X) (arr Y Y))
   [.nested false,.inProgress] [(l X,bm),(Y,bm)] Y) := by
 apply PosDR.teleCons (m₁ := 2) (m₃ := 1)
 · omega
 · exact inner_field
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact self _ (l X) _
   · omega
   · exact PosDR.teleNil

theorem outer_ctors : PosDR ops E C 2
 (.ctors [Ko] [Ho] 3 [.zero] [l X] [Ln] [Y] listCs) := by
 apply PosDR.ctorsCons (crest := Y) (ty := S) (sv := .succ .zero)
   (m₁ := 0) (m₂ := 2) (ks := []) (nds := []) (cur := Y)
 · cbv
 · exact rfl
 · cbv
 · cbv
 · omega
 · exact PosDR.teleNil
 · cbv
 · cbv
 · cbv
 · omega
 · apply PosDR.ctorsCons (crest := arr (l X) (arr Y Y))
     (ty := .sort (.imax (.succ .zero) (.imax (.succ .zero) (.succ .zero))))
     (sv := .imax (.succ .zero) (.imax (.succ .zero) (.succ .zero)))
     (m₁ := 2) (m₂ := 0) (ks := [.nested false,.inProgress])
     (nds := [(l X,bm),(Y,bm)]) (cur := Y)
   · cbv
   · exact container_crests.1
   · exact infer_outer
   · cbv
   · omega
   · exact outer_tele
   · cbv
   · cbv
   · cbv
   · omega
   · exact PosDR.ctorsNil

theorem outer_frame : PosDR ops E C 2 (.frame [] [] [.zero] [l X] [(Ln,S)]) := by
 apply PosDR.frame (m := 2) (ctors := listCs)
 · simp
 · constructor
   · cbv
   · decide
 · exact ⟨listCs,by cbv⟩
 · simp
 · intro p hp
   simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
   subst p
   exact ⟨0,by cbv⟩
 · simp
 · cbv
 · cbv
 · exact ⟨S,infer_llX⟩
 · omega
 · exact outer_ctors

theorem outer_field : PosDR ops E C 3
 (.field [] [] 2 0 (l (l X)) (.nested false) (l (l X))) := by
 apply PosDR.cont (w := l (l X)) (c := Ln) (us := [.zero]) (L := listCs)
   (nPc := 1) (nI := 0) (cty := S) (grp := [(Ln,S)]) (m := 2)
 · cbv
 · cbv
 · rfl
 · cbv
 · cbv
 · cbv
 · decide
 · simp [l, Expr.getAppArgs]
 · intro x hx
   have hh : x = l X := by simpa [l, Expr.getAppArgs] using hx
   subst x
   cbv
 · intro x hx
   have hh : x = l X := by simpa [l, Expr.getAppArgs] using hx
   subst x
   cbv
 · exact ProgScoped.nil
 · cbv
 · simp
 · rfl
 · omega
 · change PosDR ops E C 2 (.frame [] (nestWalkStack C [] [l X]) [.zero] [l X] [(Ln,S)])
   have h : nestWalkStack C [] [l X] = [] := by unfold nestWalkStack; split <;> rfl
   rw [h]
   exact outer_frame

theorem root_derivation : PosDR ops E C 3 (.ctors [] [] 2 [] [A] [Tn] [X] rootCs) := by
 apply PosDR.ctorsCons (crest := arr A X)
   (ty := .sort (.imax (.succ .zero) (.succ .zero)))
   (sv := .imax (.succ .zero) (.succ .zero))
   (m₁ := 1) (m₂ := 3) (ks := [.ordinary]) (nds := [(A,bm)]) (cur := X)
 · cbv
 · exact root_crests.1
 · exact infer_leaf
 · cbv
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact ordinary _ _ _
   · omega
   · exact PosDR.teleNil
 · cbv
 · cbv
 · cbv
 · omega
 · apply PosDR.ctorsCons (crest := arr (l (l X)) X)
     (ty := .sort (.imax (.succ .zero) (.succ .zero)))
     (sv := .imax (.succ .zero) (.succ .zero))
     (m₁ := 3) (m₂ := 0) (ks := [.nested false]) (nds := [(l (l X),bm)]) (cur := X)
   · cbv
   · exact root_crests.2
   · exact infer_node
   · cbv
   · omega
   · apply PosDR.teleCons (m₁ := 3) (m₃ := 0)
     · omega
     · exact outer_field
     · omega
     · exact PosDR.teleNil
   · cbv
   · cbv
   · cbv
   · omega
   · exact PosDR.ctorsNil

-- A finite interpretation of constructor fields, indexed by the actual frame key.
-- These labels are independently specified signature positions, not global fvar names.
inductive Slot where
 | parameter | tree | rows | children
 deriving DecidableEq, Repr

def nativeSlot (frame : Option NestKey) (e : Expr) : Option Slot :=
 match e with
 | .fvar 0 _ => some .parameter
 | .fvar 1 _ => some .tree
 | .fvar 2 _ => if frame == some Ko then some .rows
   else if frame == some Ki then some .children else none
 | _ => if e == l (l X) then some .rows else if e == l X then some .children else none

def officialSlot (e : Expr) : Option Slot :=
 if e == A then some .parameter else if e == tr then some .tree
 else if e == rows then some .rows else if e == children then some .children else none

def row (decode : Expr → Option Slot) (e : Expr) : Option (List Slot × Slot) := do
 let fields ← e.piBinders.1.mapM (fun p => decode p.1)
 let result ← decode e.piBinders.2
 pure (fields,result)

def signature : List (List (List Slot × Slot)) :=
 [[([.parameter],.tree),([.rows],.tree)],
  [([],.rows),([.children,.rows],.rows)],
  [([],.children),([.tree,.children],.children)]]

def nativeRows : List (List (Option (List Slot × Slot))) :=
 [[row (nativeSlot none) (arr A X),row (nativeSlot none) (arr (l (l X)) X)],
  [row (nativeSlot (some Ko)) Y,row (nativeSlot (some Ko)) (arr (l X) (arr Y Y))],
  [row (nativeSlot (some Ki)) Y,row (nativeSlot (some Ki)) (arr X (arr Y Y))]]

theorem row_correspondence :
 lowered.types.toList.map (fun ty => ty.ctors.map (row officialSlot)) =
   signature.map (List.map some) ∧
 nativeRows = signature.map (List.map some) := by constructor <;> rfl

theorem reused_index_has_distinct_meanings :
 nativeSlot (some Ko) Y = some .rows ∧
 nativeSlot (some Ki) Y = some .children ∧
 nativeSlot none Y = none := by exact ⟨rfl,rfl,rfl⟩

theorem root_ok : NestRootOk C := by
 constructor
 · rfl
 constructor
 · intro x hx
   simp only [C, List.mem_cons, List.not_mem_nil, or_false] at hx
   subst x
   exact ⟨0,S,rfl,by decide⟩
 · intro i hi
   have h : i = 0 := by change i < 1 at hi; omega
   subst i
   cbv

theorem walk_fuels : whnfWalkFuel (arr A X) = 1026 ∧
 whnfWalkFuel (arr (l (l X)) X) = 1028 := by constructor <;> rfl

-- Existing completeness is used only after independent derivation construction.
theorem native_run_complete :
 RunOK ops E C 3 (.ctors [] [] 2 [] [A] [Tn] [X] rootCs) :=
 posDR_run root_ok root_derivation

/-- Finite representation bridge: exact queue output, constructed native derivation,
 and independent key-relative constructor-row interpretation. No premises. -/
theorem tree2_bridge :
 Official.elimNested O decl 4 = .ok lowered ∧
 PosDR ops E C 3 (.ctors [] [] 2 [] [A] [Tn] [X] rootCs) ∧
 lowered.types.toList.map (fun ty => ty.ctors.map (row officialSlot)) =
   signature.map (List.map some) ∧
 nativeRows = signature.map (List.map some) :=
 ⟨official_lowering,root_derivation,row_correspondence⟩

#print tree2_bridge
#print axioms official_lowering
#print axioms root_derivation
#print axioms row_correspondence
#print axioms native_run_complete
#print axioms tree2_bridge
end Tree2Bridge
