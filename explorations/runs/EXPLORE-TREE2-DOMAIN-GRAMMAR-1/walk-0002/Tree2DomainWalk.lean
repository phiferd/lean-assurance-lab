import Tree2DomainNative
import Std.Data.HashMap.Lemmas

/- Local AI-authored exploratory automatic walk connection. No upstream submission. -/
namespace Tree2DomainWalk
open ConLeche Tree2Bridge Tree2TowerSupport Tree2DomainNative Tree2DomainGrammar
variable {D : Domain}
set_option maxRecDepth 2000
set_option maxHeartbeats 1000000

/- Local memo accounting, used only to bound the real upstream depth.
   No property of a replacement depth function is assumed. -/
private def height : Expr → Nat
  | .app f a => max (height f) (height a) + 1
  | .lam a b _ | .forallE a b _ => max (height a) (height b) + 1
  | .letE a v b => max (max (height a) (height v)) (height b) + 1
  | .proj _ _ a => height a + 1
  | _ => 1

private def MemoSound (m : Std.HashMap Expr Nat) : Prop :=
  ∀ e r, m[e]? = some r → r = height e

private theorem memo_insert {m : Std.HashMap Expr Nat} (hm : MemoSound m) (e : Expr) :
    MemoSound (m.insert e (height e)) := by
  intro a r hr
  rw [Std.HashMap.getElem?_insert] at hr
  split at hr
  · have h : e = a := by simpa using ‹(e == a) = true›
    subst a
    exact Option.some.inj hr.symm
  · exact hm a r hr

private theorem depthGo_sound (e : Expr) (m : Std.HashMap Expr Nat) (hm : MemoSound m) :
    (e.depthGo m).1 = height e ∧ MemoSound (e.depthGo m).2 := by
  induction e generalizing m with
  | bvar i => exact ⟨rfl,hm⟩
  | fvar i ty ih => exact ⟨rfl,hm⟩
  | sort u => exact ⟨rfl,hm⟩
  | const c us => exact ⟨rfl,hm⟩
  | lit v => exact ⟨rfl,hm⟩
  | app f a ihf iha =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨hf,hfm⟩ := ihf m hm
      obtain ⟨ha,ham⟩ := iha (f.depthGo m).2 hfm
      simp only [hf,ha,height]
      exact ⟨trivial,memo_insert ham _⟩
  | lam a b mt iha ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hb,hbm⟩ := ihb (a.depthGo m).2 ham
      simp only [ha,hb,height]
      exact ⟨trivial,memo_insert hbm _⟩
  | forallE a b mt iha ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hb,hbm⟩ := ihb (a.depthGo m).2 ham
      simp only [ha,hb,height]
      exact ⟨trivial,memo_insert hbm _⟩
  | letE a v b iha ihv ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hv,hvm⟩ := ihv (a.depthGo m).2 ham
      obtain ⟨hb,hbm⟩ := ihb (v.depthGo (a.depthGo m).2).2 hvm
      simp only [ha,hv,hb,height]
      exact ⟨trivial,memo_insert hbm _⟩
  | proj c i a iha =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      simp only [ha,height]
      exact ⟨trivial,memo_insert ham _⟩

private theorem depth_eq_height (e : Expr) : e.depth = height e :=
  (depthGo_sound e {} (by intro a r h; rw [Std.HashMap.getElem?_empty] at h; cases h)).1

theorem tower_depth_lower (n : Nat) : n+1 ≤ (tower n).depth := by
  rw [depth_eq_height]
  induction n with
  | zero => simp [tower,X,height]
  | succ n ih =>
    simp only [tower,l,height]
    have := Nat.le_max_right (height (.const Ln [.zero])) (height (tower n))
    omega




private theorem depth_pi_lower (a b : Expr) : a.depth ≤ (arr a b).depth := by
  have hp : height (arr a b) = max (height a) (height b) + 1 := rfl
  calc
    a.depth = height a := depth_eq_height a
    _ ≤ max (height a) (height b) + 1 := by
      have := Nat.le_max_left (height a) (height b)
      omega
    _ = (arr a b).depth := (Eq.trans (depth_eq_height _) hp).symm

private theorem walk_ge_depth (e : Expr) : e.depth ≤ whnfWalkFuel e :=
  Nat.le_add_right e.depth fuelSlack

private theorem walk_ge_slack (e : Expr) : fuelSlack ≤ whnfWalkFuel e :=
  Nat.le_add_left fuelSlack e.depth

theorem node_walk_budget (n : Nat) : n+2 ≤ whnfWalkFuel (arr (arr D.native (tower n)) X) := by
 have ht := tower_depth_lower n
 have hp : (tower n).depth + 1 ≤ (arr D.native (tower n)).depth := by
  rw [depth_eq_height,depth_eq_height]
  change height (tower n) + 1 ≤ max (height D.native) (height (tower n)) + 1
  exact Nat.add_le_add_right (Nat.le_max_right _ _) 1
 have ho := depth_pi_lower (arr D.native (tower n)) X
 have hw := walk_ge_depth (arr (arr D.native (tower n)) X)
 omega

theorem leaf_walk_budget : 1 ≤ whnfWalkFuel (arr A X) := by
 have h := walk_ge_slack (arr A X)
 unfold fuelSlack at h
 omega

def node (D : Domain) (N : Nat) := Tree2DomainSchema.node D N
def roots (D : Domain) (N : Nat) := [(leafCV,1),(node D N,1)]

theorem root_ok (N : Nat) : NestRootOk (Cn D N) := by
  refine ⟨rfl, ?_, ?_⟩
  · intro x hx
    have hx' : x = A := by simpa [Cn,Tree2DomainSchema.ctx] using hx
    subst x
    exact ⟨0,S,rfl,by change 0 < 1; decide⟩
  · intro j hj
    have hj' : j < 1 := hj
    have hj0 : j = 0 := by omega
    subst j
    rfl

theorem root_holes (N : Nat) : nestHoles (Cn D N) = some [X] := by rfl

theorem node_canon (N : Nat) :
 nestRootCanon (Cn D N) (node D N) = some (arr (arr D.crest (Tree2TowerNative.pow N Q)) Q) := by
 change nestCanonCrest [Tn] [] 1
  ((node D N).type.instantiateLevelParams [] []) = _
 rw [Expr.instantiateLevelParams_eq_self (show (node D N).type.hasLevelParam = false from Tree2DomainNative.node_no_levels N)]
 unfold nestCanonCrest
 change ((instPisWith [P] (pi S (pi (pi (D.raw 0)
  (Tree2TowerNative.pow N (t (.bvar 1)))) (t (.bvar 1))))).map
  (·.replaceApps (nestCanonSub [Tn] [] 1) 0 1)) = _
 simp only [instPisWith,pi,Expr.instantiate1,Tree2TowerNative.pow_inst,Domain.raw_instantiate]
 change some ((arr (arr (D.encode P (t P)) (Tree2TowerNative.pow N (t P))) (t P)).replaceApps
  (nestCanonSub [Tn] [] 1) 0 1) = _
 have hq : (t P).replaceApps (nestCanonSub [Tn] [] 1) 0 1 = Q := rfl
 simp only [arr,pi,Expr.replaceApps,Tree2TowerNative.pow_canon,hq,Domain.canonicalize]

theorem pow_uniform (N : Nat) : (Tree2TowerNative.pow N Q).nestOcc [Tn] 0 0 = false := by
  induction N with
  | zero => rfl
  | succ N ih =>
    simp only [Tree2TowerNative.pow,l,Expr.nestOcc,ih]
    rfl

theorem uniform_leaf (N : Nat) : nestUniformOk (Cn D N) leafCV = true := by rfl

theorem crest_uniform (D : Domain) : D.crest.nestOcc [Tn] 0 0=false := by
 induction D with
 | param => rfl
 | self => rfl
 | arrow a b ia ib => simp only [Domain.crest,Domain.encode,arr,pi,Expr.nestOcc] at *; rw [ia,ib]; rfl

theorem uniform_node (N : Nat) : nestUniformOk (Cn D N) (node D N) = true := by
  unfold nestUniformOk
  rw [node_canon]
  have hdom : (node D N).type.piDomsOcc (Cn D N).names (Cn D N).nP
      ((Cn D N).hiAt 0) (Cn D N).nP = false := by rfl
  rw [hdom]
  simp only [Cn,Tree2DomainSchema.ctx,arr,pi,Expr.nestOcc]
  rw [pow_uniform,crest_uniform]
  rfl

theorem leaf_singleton (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) :
  PosDR (checker F) (En D N) (Cn D N) 1
    (.ctors [] [] 2 [] [A] [Tn] [X] [(leafCV,1)]) := by
  have hfN : N+5 ≤ F := by unfold Tree2DomainSchema.coreBound at hf; omega
  apply PosDR.ctorsCons (crest := arr A X)
    (ty := .sort (.imax (.succ .zero) (.succ .zero)))
    (sv := .imax (.succ .zero) (.succ .zero))
    (m₁ := 1) (m₂ := 0) (ks := [.ordinary]) (nds := [(A,bm)]) (cur := X)
  · decide
  · exact root_crests.1
  · exact leaf_infer N F (by omega)
  · exact ensure_sort N F 2 _ (by omega)
  · omega
  · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
    · omega
    · exact ordinary_field N F (by omega)
    · omega
    · exact PosDR.teleNil
  · rfl
  · rfl
  · rfl
  · omega
  · exact PosDR.ctorsNil

theorem node_singleton (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) (ha : D.hasSelf=false) :
 PosDR (checker F) (En D N) (Cn D N) (N+2)
  (.ctors [] [] 2 [] [A] [Tn] [X] [(node D N,1)]) := by
 have hfN : N+5 ≤ F := by unfold Tree2DomainSchema.coreBound at hf; omega
 apply PosDR.ctorsCons (crest := arr (arr D.native (tower N)) X)
  (ty := .sort (.imax (.imax D.sortLevel (.succ .zero)) (.succ .zero)))
  (sv := .imax (.imax D.sortLevel (.succ .zero)) (.succ .zero))
  (m₁ := N+2) (m₂ := 0) (ks := [functionKind N])
  (nds := [(arr D.native (tower N),bm)]) (cur := X)
 · rfl
 · exact node_crest N
 · exact function_crest_infer N F hf
 · exact ensure_sort N F 2 _ (by omega)
 · omega
 · apply PosDR.teleCons (m₁ := N+2) (m₃ := 0)
   · omega
   · exact function_field N F hf ha
   · omega
   · exact PosDR.teleNil
 · exact node_u4 (arr D.native (tower N)) (functionKind N)
 · rfl
 · rfl
 · omega
 · exact PosDR.ctorsNil

/-- The run carries its actual automatically chosen walk budget. -/
def ctorLoop (D : Domain) (N F : Nat) :=
  nestCtors (Cn D N) (checker F) (En D N)
    (fun crest => nestPos (checker F) (En D N) (Cn D N) (whnfWalkFuel crest))
    [] 2 [] [A] [Tn] [X]

theorem leaf_run (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) (st : NestState)
    (hs : RInv (Cn D N) st []) :
    ∃ os st', ctorLoop D N F [(leafCV,1)] st = .ok (os,st') ∧
      RInv (Cn D N) st' [] := by
  obtain ⟨os,st',hr,hi,_⟩ :=
    posDR_run (root_ok N) (leaf_singleton N F hf) whnfWalkFuel (by
      intro x hx crest hc
      have hx' : x = (leafCV,1) := by simpa using hx
      subst x
      change nestCrest [Tn] [] [A] [X] leafCV.type = some crest at hc
      rw [root_crests.1] at hc
      have h : arr A X = crest := Option.some.inj hc
      subst crest
      exact leaf_walk_budget) st hs
  exact ⟨os,st',hr,hi⟩

theorem node_run (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) (ha : D.hasSelf=false) (st : NestState)
    (hs : RInv (Cn D N) st []) :
    ∃ os st', ctorLoop D N F [(node D N,1)] st = .ok (os,st') ∧
      RInv (Cn D N) st' [] := by
  obtain ⟨os,st',hr,hi,_⟩ :=
    posDR_run (root_ok N) (node_singleton N F hf ha) whnfWalkFuel (by
      intro x hx crest hc
      have hx' : x = (node D N,1) := by simpa using hx
      subst x
      change nestCrest [Tn] [] [A] [X]
        ((node D N).type.instantiateLevelParams [] []) = some crest at hc
      have hn : nestCrest [Tn] [] [A] [X]
        ((node D N).type.instantiateLevelParams [] []) = some (arr (arr D.native (tower N)) X) := Tree2DomainNative.node_crest N
      rw [hn] at hc
      have h : arr (arr D.native (tower N)) X = crest := Option.some.inj hc
      subst crest
      exact node_walk_budget N) st hs
  exact ⟨os,st',hr,hi⟩

private theorem ite_bind {α β : Type} (p : Prop) [Decidable p]
    (a b : CheckM α) (f : α → CheckM β) :
    (if p then a else b) >>= f = if p then a >>= f else b >>= f := by
  split <;> rfl

/-- Ordinary constructor-loop concatenation; no walk bound is modified. -/
private theorem ctor_append (ctx : NestCtx) (ops : CheckerOps CheckM) (env : Env)
    (rec : Expr → List NestHole → Nat → Nat → Expr → NestState →
      CheckM (NestFieldKind × Expr × NestState))
    (prog : List NestHole) (hi : Nat) (us : List Level) (ds : List Expr)
    (names : List Name) (holes : List Expr) (xs ys : List (ConstantVal × Nat))
    (st : NestState) :
    nestCtors ctx ops env rec prog hi us ds names holes (xs++ys) st = (do
      let (os,st') ← nestCtors ctx ops env rec prog hi us ds names holes xs st
      let (ps,st'') ← nestCtors ctx ops env rec prog hi us ds names holes ys st'
      pure (os++ps,st'')) := by
  induction xs generalizing st with
  | nil =>
    simp only [List.nil_append,nestCtors,bind,Except.bind,pure,Except.pure]
    cases nestCtors ctx ops env rec prog hi us ds names holes ys st <;> rfl
  | cons x xs ih =>
    rcases x with ⟨cv,nf⟩
    simp only [List.cons_append,nestCtors]
    simp only [ih]
    simp only [bind_assoc,ite_bind,pure_bind,List.cons_append]


theorem constructors_run (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) (ha : D.hasSelf=false) (st : NestState)
    (hs : RInv (Cn D N) st []) :
    ∃ os st', ctorLoop D N F (roots D N) st = .ok (os,st') ∧
      RInv (Cn D N) st' [] := by
  obtain ⟨lo,st1,hl,hi1⟩ := leaf_run N F hf st hs
  obtain ⟨no,st2,hn,hi2⟩ := node_run N F hf ha st1 hi1
  refine ⟨lo++no,st2,?_,hi2⟩
  change ctorLoop D N F ([(leafCV,1)]++[(node D N,1)]) st = _
  unfold ctorLoop at hl hn ⊢
  rw [ctor_append,hl]
  simp only [bind,Except.bind]
  rw [hn]
  rfl

theorem uniform_roots (N : Nat) : nestUniform (m := CheckM) (Cn D N) [roots D N] = .ok () := by
  unfold nestUniform roots
  simp only [List.findSome?,List.find?]
  rw [uniform_leaf,uniform_node]
  rfl

/-- Actual native model automatic positivity succeeds, for every tower depth. -/
theorem automatic_run (N F : Nat) (hf : Tree2DomainSchema.coreBound D N ≤ F) (ha : D.hasSelf=false) :
    ∃ r, nestedBlockPositivity (checker F) (En D N) (Cn D N) [roots D N] = .ok r := by
  obtain ⟨os,st',hr,_⟩ := constructors_run N F hf ha {} rfl
  have hroot : nestRoot (checker F) (En D N) (Cn D N) [X] [roots D N] {} = .ok ([os],st') := by
    simp only [nestRoot,bind,Except.bind,pure,Except.pure]
    change (do
      let (o,st) ← ctorLoop D N F (roots D N) {}
      pure ([o],st)) = .ok ([os],st')
    rw [hr]
    rfl
  unfold nestedBlockPositivity
  rw [root_holes]
  simp only [unwrapOr,bind,Except.bind,pure,Except.pure]
  rw [uniform_roots]
  rw [hroot]
  exact ⟨_,rfl⟩


#print axioms node_crest
#print axioms uniform_node
#print axioms function_field
#print axioms leaf_singleton
#print axioms node_singleton
#print axioms node_walk_budget
#print axioms automatic_run
end Tree2DomainWalk
