import Tree2TowerWalk

/- Local AI-authored restricted official queue proof. No upstream submission. -/
namespace Tree2TowerOfficial
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative
set_option maxRecDepth 2000
set_option maxHeartbeats 1000000

def freshName (i : Nat) : Name := .num (nm "TowerAux") i

def context (N : Nat) : Official.ElimCtx :=
  {find? := (En N).find?, ctorsOf := fun c => if c == Ln then listCs else [],
   lvls := [], ps := [A], auxName := freshName}

def declaration (N : Nat) : List Official.MemberDecl :=
  [⟨Tn,treeCV.type,[leafCV.type,(node N).type]⟩]

/-- R_0 is the member; R_j has allocation index N-j+1. -/
def R (N : Nat) : Nat → Expr
  | 0 => tr
  | j+1 => .app (.const (freshName (N-j)) []) A

def row (N j : Nat) : Official.AuxType :=
  ⟨freshName (N-j+1),S,[R N j,arr (R N (j-1)) (arr (R N j) (R N j))]⟩
def rootRow (N : Nat) : Official.AuxType := ⟨Tn,S,[arr A tr,arr (R N N) tr]⟩
def target (N : Nat) : Official.ElimSt :=
  {aux := (List.range N).map (fun i => (pow (N-i) tr,freshName (i+1))),
   types := (rootRow N :: (List.range N).map (fun i => row N (N-i))).toArray,
   next := N+1}

/-- Unprocessed List instance of depth j, with original (not lowered) keys. -/
def rawRow (i j : Nat) : Official.AuxType :=
  ⟨freshName i,S,[pow j tr,arr (pow (j-1) tr) (arr (pow j tr) (pow j tr))]⟩

theorem fresh_supply (N i : Nat) :
    (En N).find? (freshName i) = none ∧ freshName i ≠ Tn ∧ freshName i ≠ Ln ∧
    ∀ j, freshName i = freshName j ↔ i = j := by
  refine ⟨rfl, ?_, ?_, ?_⟩
  · intro h; cases h
  · intro h; cases h
  · intro j
    constructor
    · intro h; exact (Name.num.inj h).2
    · intro h; subst j; rfl

theorem tower_key_injective : Function.Injective (fun n => pow n tr) := by
  intro j
  induction j with
  | zero =>
    intro k h
    cases k with
    | zero => rfl
    | succ k =>
      have hf := congrArg Expr.getAppFn h
      change Expr.const Tn [] = Expr.const Ln [.zero] at hf
      have hn : Tn ≠ Ln := by decide
      exact False.elim (hn (Expr.const.inj hf).1)
  | succ j ih =>
    intro k h
    cases k with
    | zero =>
      have hf := congrArg Expr.getAppFn h
      change Expr.const Ln [.zero] = Expr.const Tn [] at hf
      have hn : Ln ≠ Tn := by decide
      exact False.elim (hn (Expr.const.inj hf).1)
    | succ k => exact congrArg Nat.succ (ih (Expr.app.inj h).2)

theorem tower_key_closed (n : Nat) : (pow n tr).bvarB = 0 := by
  rw [Expr.bvarB_eq]
  induction n with
  | zero => rfl
  | succ n ih => simp [pow,l,Expr.bvarBound,ih]

theorem tower_root_occ (n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    (pow n tr).nestOcc names 0 0 = true := by
  induction n with
  | zero => simp only [pow,tr,t,Expr.nestOcc,hn,Bool.true_or]
  | succ n ih => simp [pow,l,Expr.nestOcc,ih]

/-- The fixed copied List constructors before any lowering. -/
theorem copied_list (d : Expr) :
    Official.instPiParams (listCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok S ∧
    Official.instPiParams (nilCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok (l d) ∧
    Official.instPiParams (consCV.type.instantiateLevelParams [un] [.zero]) [d] =
      .ok (arr d (arr (l d) (l d))) := by
  exact ⟨rfl,rfl,rfl⟩

/-- Detection needs only the root-name occurrence and closed original key. -/
theorem nested_tower (N n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    Official.isNestedApp (context N) names (pow (n+1) tr) =
      .ok (some (Ln,[.zero],1,[pow n tr])) := by
  have ho := tower_root_occ n names hn
  have hb := tower_key_closed n
  simp only [pow,l,Official.isNestedApp,Expr.getAppFn,Expr.getAppArgs]
  change (if Ln == quotName then Except.ok none else
    if 1 < 1 then Except.ok none else
    if !([pow n tr].any (·.nestOcc names 0 0)) then Except.ok none else
    if [pow n tr].any (·.bvarB != 0) then
      Except.error (.invalid "official: nested inductive datatypes parameters cannot contain local variables")
    else Except.ok (some (Ln,[.zero],1,[pow n tr]))) =
      (Except.ok (some (Ln,[.zero],1,[pow n tr])) :
        Except CheckError (Option (Name × List Level × Nat × List Expr)))
  simp only [ho,hb,List.any_cons,List.any_nil]
  rfl


def copiedState (st : Official.ElimSt) (n : Nat) : Official.ElimSt :=
  {aux := st.aux ++ [(pow (n+1) tr,freshName st.next)],
   types := st.types.push (rawRow st.next (n+1)), next := st.next+1}

theorem copy_tower (N n : Nat) (st : Official.ElimSt) :
    (Official.copyBlock (context N) [.zero] [pow n tr] [Ln]).run st =
      .ok ((),copiedState st n) := by rfl

theorem replace_hit (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceIfNested (context N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const a []) A),st) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower N n _ hn]
  dsimp only [Except.pure,StateT.pure,context,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = some a := hk
  rw [hk']
  rfl


theorem copied_lookup (n : Nat) (st : Official.ElimSt)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (copiedState st n).aux.lookup (pow (n+1) tr) = some (freshName st.next) := by
  simp only [copiedState,List.lookup_append,hk,List.lookup_cons_self,Option.or]

theorem replace_miss (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceIfNested (context N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const (freshName st.next) []) A),copiedState st n) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower N n _ hn]
  dsimp only [Except.pure,StateT.pure,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = none := hk
  rw [hk']
  have hb : Official.blockOf (context N) Ln = [Ln] := rfl
  rw [hb]
  have hcopy : Official.copyBlock (context N) [.zero] [pow n tr] [Ln] =
      fun st => Except.ok ((),copiedState st n) := by
    funext st
    exact copy_tower N n st
  rw [hcopy]
  dsimp only [StateT.bind,StateT.get,StateT.pure,pure,Except.pure,bind,Except.bind]
  have hnew : (copiedState st n).aux.lookup
      (Expr.app (.const Ln [.zero]) (pow n tr)) = some (freshName st.next) :=
    copied_lookup n st hk
  rw [hnew]
  rfl


private theorem all_replaced (N : Nat) (f a w : Expr) (st st' : Official.ElimSt)
    (h : (Official.replaceIfNested (context N) (.app f a)).run st = .ok (some w,st')) :
    (Official.replaceAll (context N) (.app f a)).run st = .ok (w,st') := by
  dsimp only [Official.replaceAll,StateT.run,bind,StateT.bind,Except.bind]
  have h' : Official.replaceIfNested (context N) (.app f a) st = .ok (some w,st') := h
  rw [h']
  rfl

theorem all_hit (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceAll (context N) (pow (n+1) tr)).run st =
      .ok (.app (.const a []) A,st) :=
  all_replaced N _ _ _ st st (replace_hit N n st a hn hk)

theorem all_miss (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceAll (context N) (pow (n+1) tr)).run st =
      .ok (.app (.const (freshName st.next) []) A,copiedState st n) :=
  all_replaced N _ _ _ st (copiedState st n) (replace_miss N n st hn hk)

theorem all_member (N : Nat) (st : Official.ElimSt) :
    (Official.replaceAll (context N) tr).run st = .ok (tr,st) := by rfl

private theorem all_arr (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context N) b).run st1 = .ok (b',st2)) :
    (Official.replaceAll (context N) (arr a b)).run st = .ok (arr a' b',st2) := by
  dsimp only [arr,pi,Official.replaceAll,StateT.run,bind,StateT.bind,pure,
    StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']
  rfl

/-- A self row is rewritten without allocation, once its key is recorded. -/
theorem self_tail (N n : Nat) (st : Official.ElimSt) (i : Nat)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some (freshName i)) :
    (Official.replaceAll (context N) (arr (pow (n+1) tr) (pow (n+1) tr))).run st =
      .ok (arr (.app (.const (freshName i) []) A) (.app (.const (freshName i) []) A),st) :=
  all_arr N _ _ _ _ st st st (all_hit N n st _ hn hk) (all_hit N n st _ hn hk)

#print axioms fresh_supply
#print axioms tower_key_injective
#print axioms tower_key_closed
#print axioms copied_list
#print axioms nested_tower
#print axioms copy_tower
#print axioms replace_hit
#print axioms replace_miss
#print axioms all_hit
#print axioms all_miss
#print axioms all_member
#print axioms self_tail
end Tree2TowerOfficial
