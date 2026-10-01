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

/-- A self row is rewritten without allocation, once its key is recorded. -/
theorem self_tail (N n : Nat) (st : Official.ElimSt) (i : Nat)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some (freshName i)) :
    (Official.replaceAll (context N) (arr (pow (n+1) tr) (pow (n+1) tr))).run st =
      .ok (arr (.app (.const (freshName i) []) A) (.app (.const (freshName i) []) A),st) :=
  all_arr N _ _ _ _ st st st (all_hit N n st _ hn hk) (all_hit N n st _ hn hk)


private theorem map_two (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context N) b).run st1 = .ok (b',st2)) :
    ([a,b].mapM (Official.replaceAll (context N))).run st = .ok ([a',b'],st2) := by
  simp only [List.mapM_cons,List.mapM_nil]
  dsimp only [StateT.run,bind,StateT.bind,pure,StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']

theorem copied_preserves (n : Nat) (st : Official.ElimSt) (e : Expr) (a : Name)
    (h : st.aux.lookup e = some a) : (copiedState st n).aux.lookup e = some a := by
  simp only [copiedState,List.lookup_append,h,Option.or]

theorem copied_root_name (n : Nat) (st : Official.ElimSt)
    (h : (st.types.toList.map (·.name)).contains Tn = true) :
    ((copiedState st n).types.toList.map (·.name)).contains Tn = true := by
  simp only [copiedState,Array.toList_push,List.map_append,List.map_cons,List.map_nil,
    List.contains_append,h,Bool.true_or]

def auxExpr (i : Nat) : Expr := .app (.const (freshName i) []) A

/-- Exact terminal row transition (List T): only its recorded self key is used. -/
theorem terminal_row (N i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow 1 tr) = some (freshName i)) :
    ((rawRow i 1).ctors.mapM (Official.replaceAll (context N))).run st =
      .ok ([auxExpr i,arr tr (arr (auxExpr i) (auxExpr i))],st) := by
  exact map_two N _ _ _ _ st st st (all_hit N 0 st _ hn hk)
    (all_arr N _ _ _ _ st st st (all_member N st) (self_tail N 0 st i hn hk))

/-- Exact positive-depth row transition: one new element row, self tails reused. -/
theorem descending_row (N n i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hself : st.aux.lookup (pow (n+2) tr) = some (freshName i))
    (hnext : st.aux.lookup (pow (n+1) tr) = none) :
    ((rawRow i (n+2)).ctors.mapM (Official.replaceAll (context N))).run st =
      .ok ([auxExpr i,arr (auxExpr st.next) (arr (auxExpr i) (auxExpr i))],copiedState st n) := by
  exact map_two N _ _ _ _ st st (copiedState st n)
    (all_hit N (n+1) st _ hn hself)
    (all_arr N _ _ _ _ st (copiedState st n) (copiedState st n)
      (all_miss N n st hn hnext)
      (self_tail N (n+1) (copiedState st n) i (copied_root_name n st hn)
        (copied_preserves n st _ _ hself)))

/-- Recorded keys after p allocations; allocation i+1 has depth N-i. -/
def keys (N p : Nat) : List (Expr × Name) :=
  (List.range p).map (fun i => (pow (N-i) tr,freshName (i+1)))

theorem keys_fresh (N p k : Nat) (hp : p ≤ N) (hk : k ≤ N-p) :
    (keys N p).lookup (pow k tr) = none := by
  rw [List.lookup_eq_none_iff]
  intro pair hpair
  obtain ⟨i,hi,rfl⟩ := List.mem_map.mp hpair
  have hi' : i < p := List.mem_range.mp hi
  simp only [bne_iff_ne]
  intro he
  have he' : k = N-i := tower_key_injective he
  omega

theorem keys_succ (N p : Nat) :
    keys N (p+1) = keys N p ++ [(pow (N-p) tr,freshName (p+1))] := by
  simp [keys,List.range_succ]

theorem keys_hit (N p j : Nat) (hp : p ≤ N) (hj : j < p) :
    (keys N p).lookup (pow (N-j) tr) = some (freshName (j+1)) := by
  induction p with
  | zero => omega
  | succ p ih =>
    rw [keys_succ,List.lookup_append]
    by_cases hjp : j < p
    · rw [ih (by omega) hjp]
      rfl
    · have hj0 : j = p := by omega
      subst j
      rw [keys_fresh N p (N-p) (by omega) (by omega),List.lookup_cons_self]
      rfl


def prefix (N p : Nat) : List Official.AuxType :=
  rootRow N :: (List.range p).map (fun i => row N (N-i))

/-- The one-pending-row invariant, independently described by processed depth. -/
def queue (N p : Nat) : Official.ElimSt :=
  {aux := keys N (min (p+1) N),
   types := (prefix N p ++ if p < N then [rawRow (p+1) (N-p)] else []).toArray,
   next := min (p+1) N + 1}

theorem prefix_length (N p : Nat) : (prefix N p).length = p+1 := by
  simp [prefix]

theorem prefix_succ (N p : Nat) :
    prefix N (p+1) = prefix N p ++ [row N (N-p)] := by
  simp [prefix,List.range_succ]

theorem queue_pending (N p : Nat) (hp : p < N) :
    queue N p = {aux := keys N (p+1),
      types := (prefix N p ++ [rawRow (p+1) (N-p)]).toArray,next := p+2} := by
  simp only [queue,if_pos hp,Nat.min_eq_left (show p+1 ≤ N by omega)]

theorem queue_done (N : Nat) : queue N N = target N := by
  simp [queue,keys,prefix,target]

theorem queue_root_name (N p : Nat) :
    ((queue N p).types.toList.map (·.name)).contains Tn = true := by
  simp [queue,prefix,rootRow]

private theorem loop_step (N fuel q : Nat) (st st1 : Official.ElimSt)
    (t : Official.AuxType) (cs : List Expr)
    (ht : st.types[q]? = some t)
    (hc : (t.ctors.mapM (Official.replaceAll (context N))).run st = .ok (cs,st1)) :
    (Official.elimLoop (context N) (fuel+1) q).run st =
      (Official.elimLoop (context N) fuel (q+1)).run
        {st1 with types := st1.types.set! q {t with ctors := cs}} := by
  dsimp only [Official.elimLoop,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure]
  rw [ht]
  have hc' : t.ctors.mapM (Official.replaceAll (context N)) st = .ok (cs,st1) := hc
  dsimp only
  rw [hc']
  dsimp only [modify,modifyGet,MonadStateOf.modifyGet,StateT.modifyGet,StateT.bind,
    pure,Except.pure,bind,Except.bind]

private theorem set_pending (pre : List Official.AuxType) (old new : Official.AuxType)
    (tail : List Official.AuxType) :
    (pre ++ old::tail).toArray.set! pre.length new = (pre ++ new::tail).toArray := by
  simp [Array.set!_eq_setIfInBounds,List.setIfInBounds_toArray,List.set_append_right]

private theorem row_terminal (p : Nat) :
    row (p+1) 1 = ⟨freshName (p+1),S,[auxExpr (p+1),
      arr tr (arr (auxExpr (p+1)) (auxExpr (p+1)))]⟩ := by
  simp [row,R,auxExpr]

private theorem row_descending (p n : Nat) :
    row (p+n+2) (n+2) = ⟨freshName (p+1),S,[auxExpr (p+1),
      arr (auxExpr (p+2)) (arr (auxExpr (p+1)) (auxExpr (p+1)))]⟩ := by
  have h0 : p+n+2-(n+2)+1 = p+1 := by omega
  have h1 : p+n+2-(n+1) = p+1 := by omega
  have h2 : p+n+2-n = p+2 := by omega
  simp only [row,R,auxExpr,h0,h1,h2,Nat.add_sub_cancel]

#print axioms fresh_supply
#print axioms tower_key_injective
#print axioms nested_tower
#print axioms copy_tower
#print axioms replace_hit
#print axioms replace_miss
#print axioms terminal_row
#print axioms descending_row
#print axioms keys_fresh
#print axioms keys_hit
#print axioms queue_pending
#print axioms queue_done
#print axioms loop_step
#print axioms set_pending
#print axioms row_descending
end Tree2TowerOfficial
