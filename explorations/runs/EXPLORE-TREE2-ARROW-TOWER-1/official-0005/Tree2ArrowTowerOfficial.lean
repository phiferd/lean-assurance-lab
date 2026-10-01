import Tree2ArrowTowerSchema

/- Local AI-authored restricted official queue bad proof. No upstream submission. -/
namespace Tree2ArrowTowerOfficial
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative
set_option maxRecDepth 2000
set_option maxHeartbeats 1000000

def freshName (bad : Bool) (i : Nat) : Name := .num (nm "TowerAux") i

def context (bad : Bool) (N : Nat) : Official.ElimCtx :=
  {find? := (Tree2ArrowTowerSchema.env bad N).find?, ctorsOf := fun c => if c == Ln then listCs else [],
   lvls := [], ps := [A], auxName := freshName bad}

def declaration (bad : Bool) (N : Nat) : List Official.MemberDecl :=
  [⟨Tn,treeCV.type,[leafCV.type,(Tree2ArrowTowerSchema.node bad N).type]⟩]

/-- R_0 is the member; R_j has allocation index N-j+1. -/
def R (bad : Bool) (N : Nat) : Nat → Expr
  | 0 => tr
  | j+1 => .app (.const (freshName bad (N-j)) []) A

def row (bad : Bool) (N j : Nat) : Official.AuxType :=
  ⟨freshName bad (N-j+1),S,[R bad N j,arr (R bad N (j-1)) (arr (R bad N j) (R bad N j))]⟩
def rootRow (bad : Bool) (N : Nat) : Official.AuxType := ⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) (R bad N N)) tr]⟩
def target (bad : Bool) (N : Nat) : Official.ElimSt :=
  {aux := (List.range N).map (fun i => (pow (N-i) tr,freshName bad (i+1))),
   types := (rootRow bad N :: (List.range N).map (fun i => row bad N (N-i))).toArray,
   next := N+1}

/-- Unprocessed List instance of depth j, with original (not lowered) keys bad. -/
def rawRow (bad : Bool) (i j : Nat) : Official.AuxType :=
  ⟨freshName bad i,S,[pow j tr,arr (pow (j-1) tr) (arr (pow j tr) (pow j tr))]⟩

theorem fresh_supply (bad : Bool) (N i : Nat) :
    (Tree2ArrowTowerSchema.env bad N).find? (freshName bad i) = none ∧ freshName bad i ≠ Tn ∧ freshName bad i ≠ Ln ∧
    ∀ j, freshName bad i = freshName bad j ↔ i = j := by
  refine ⟨rfl, ?_, ?_, ?_⟩
  · intro h; cases h
  · intro h; cases h
  · intro j
    constructor
    · intro h; exact (Name.num.inj h).2
    · intro h; subst j; rfl

theorem tower_key_injective (bad : Bool) : Function.Injective (fun n => pow n tr) := by
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

theorem tower_key_closed (bad : Bool) (n : Nat) : (pow n tr).bvarB = 0 := by
  rw [Expr.bvarB_eq]
  induction n with
  | zero => rfl
  | succ n ih => simp [pow,l,Expr.bvarBound,ih]

theorem tower_root_occ (bad : Bool) (n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    (pow n tr).nestOcc names 0 0 = true := by
  induction n with
  | zero => simp only [pow,tr,t,Expr.nestOcc,hn,Bool.true_or]
  | succ n ih => simp [pow,l,Expr.nestOcc,ih]

/-- The fixed copied List constructors before any lowering. -/
theorem copied_list (bad : Bool) (d : Expr) :
    Official.instPiParams (listCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok S ∧
    Official.instPiParams (nilCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok (l d) ∧
    Official.instPiParams (consCV.type.instantiateLevelParams [un] [.zero]) [d] =
      .ok (arr d (arr (l d) (l d))) := by
  exact ⟨rfl,rfl,rfl⟩

/-- Detection needs only the root-name occurrence and closed original key. -/
theorem nested_tower (bad : Bool) (N n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    Official.isNestedApp (context bad N) names (pow (n+1) tr) =
      .ok (some (Ln,[.zero],1,[pow n tr])) := by
  have ho := tower_root_occ bad n names hn
  have hb := tower_key_closed bad n
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


def copiedState (bad : Bool) (st : Official.ElimSt) (n : Nat) : Official.ElimSt :=
  {aux := st.aux ++ [(pow (n+1) tr,freshName bad st.next)],
   types := st.types.push (rawRow bad st.next (n+1)), next := st.next+1}

theorem copy_tower (bad : Bool) (N n : Nat) (st : Official.ElimSt) :
    (Official.copyBlock (context bad N) [.zero] [pow n tr] [Ln]).run st =
      .ok ((),copiedState bad st n) := by rfl

theorem replace_hit (bad : Bool) (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceIfNested (context bad N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const a []) A),st) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower bad N n _ hn]
  dsimp only [Except.pure,StateT.pure,context,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = some a := hk
  rw [hk']
  rfl


theorem copied_lookup (bad : Bool) (n : Nat) (st : Official.ElimSt)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (copiedState bad st n).aux.lookup (pow (n+1) tr) = some (freshName bad st.next) := by
  simp only [copiedState,List.lookup_append,hk,List.lookup_cons_self,Option.or]

theorem replace_miss (bad : Bool) (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceIfNested (context bad N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const (freshName bad st.next) []) A),copiedState bad st n) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower bad N n _ hn]
  dsimp only [Except.pure,StateT.pure,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = none := hk
  rw [hk']
  have hb : Official.blockOf (context bad N) Ln = [Ln] := rfl
  rw [hb]
  have hcopy : Official.copyBlock (context bad N) [.zero] [pow n tr] [Ln] =
      fun st => Except.ok ((),copiedState bad st n) := by
    funext st
    exact copy_tower bad N n st
  rw [hcopy]
  dsimp only [StateT.bind,StateT.get,StateT.pure,pure,Except.pure,bind,Except.bind]
  have hnew : (copiedState bad st n).aux.lookup
      (Expr.app (.const Ln [.zero]) (pow n tr)) = some (freshName bad st.next) :=
    copied_lookup bad n st hk
  rw [hnew]
  rfl


private theorem all_replaced (bad : Bool) (N : Nat) (f a w : Expr) (st st' : Official.ElimSt)
    (h : (Official.replaceIfNested (context bad N) (.app f a)).run st = .ok (some w,st')) :
    (Official.replaceAll (context bad N) (.app f a)).run st = .ok (w,st') := by
  dsimp only [Official.replaceAll,StateT.run,bind,StateT.bind,Except.bind]
  have h' : Official.replaceIfNested (context bad N) (.app f a) st = .ok (some w,st') := h
  rw [h']
  rfl

theorem all_hit (bad : Bool) (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceAll (context bad N) (pow (n+1) tr)).run st =
      .ok (.app (.const a []) A,st) :=
  all_replaced bad N _ _ _ st st (replace_hit bad N n st a hn hk)

theorem all_miss (bad : Bool) (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceAll (context bad N) (pow (n+1) tr)).run st =
      .ok (.app (.const (freshName bad st.next) []) A,copiedState bad st n) :=
  all_replaced bad N _ _ _ st (copiedState bad st n) (replace_miss bad N n st hn hk)

theorem all_member (bad : Bool) (N : Nat) (st : Official.ElimSt) :
    (Official.replaceAll (context bad N) tr).run st = .ok (tr,st) := by rfl

private theorem all_arr (bad : Bool) (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context bad N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context bad N) b).run st1 = .ok (b',st2)) :
    (Official.replaceAll (context bad N) (arr a b)).run st = .ok (arr a' b',st2) := by
  dsimp only [arr,pi,Official.replaceAll,StateT.run,bind,StateT.bind,pure,
    StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context bad N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context bad N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']

/-- A self row bad is rewritten without allocation, once its key is recorded. -/
theorem self_tail (bad : Bool) (N n : Nat) (st : Official.ElimSt) (i : Nat)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some (freshName bad i)) :
    (Official.replaceAll (context bad N) (arr (pow (n+1) tr) (pow (n+1) tr))).run st =
      .ok (arr (.app (.const (freshName bad i) []) A) (.app (.const (freshName bad i) []) A),st) :=
  all_arr bad N _ _ _ _ st st st (all_hit bad N n st _ hn hk) (all_hit bad N n st _ hn hk)


private theorem map_two (bad : Bool) (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context bad N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context bad N) b).run st1 = .ok (b',st2)) :
    ([a,b].mapM (Official.replaceAll (context bad N))).run st = .ok ([a',b'],st2) := by
  simp only [List.mapM_cons,List.mapM_nil]
  dsimp only [StateT.run,bind,StateT.bind,pure,StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context bad N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context bad N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']

theorem copied_preserves (bad : Bool) (n : Nat) (st : Official.ElimSt) (e : Expr) (a : Name)
    (h : st.aux.lookup e = some a) : (copiedState bad st n).aux.lookup e = some a := by
  simp only [copiedState,List.lookup_append,h,Option.or]

theorem copied_root_name (bad : Bool) (n : Nat) (st : Official.ElimSt)
    (h : (st.types.toList.map (·.name)).contains Tn = true) :
    ((copiedState bad st n).types.toList.map (·.name)).contains Tn = true := by
  simp only [copiedState,Array.toList_push,List.map_append,List.map_cons,List.map_nil,
    List.contains_append,h,Bool.true_or]

def auxExpr (bad : Bool) (i : Nat) : Expr := .app (.const (freshName bad i) []) A

/-- Exact terminal row bad transition (List T): only its recorded self key is used. -/
theorem terminal_row (bad : Bool) (N i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow 1 tr) = some (freshName bad i)) :
    ((rawRow bad i 1).ctors.mapM (Official.replaceAll (context bad N))).run st =
      .ok ([auxExpr bad i,arr tr (arr (auxExpr bad i) (auxExpr bad i))],st) := by
  exact map_two bad N _ _ _ _ st st st (all_hit bad N 0 st _ hn hk)
    (all_arr bad N _ _ _ _ st st st (all_member bad N st) (self_tail bad N 0 st i hn hk))

/-- Exact positive-depth row bad transition: one new element row bad, self tails reused. -/
theorem descending_row (bad : Bool) (N n i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hself : st.aux.lookup (pow (n+2) tr) = some (freshName bad i))
    (hnext : st.aux.lookup (pow (n+1) tr) = none) :
    ((rawRow bad i (n+2)).ctors.mapM (Official.replaceAll (context bad N))).run st =
      .ok ([auxExpr bad i,arr (auxExpr bad st.next) (arr (auxExpr bad i) (auxExpr bad i))],copiedState bad st n) := by
  exact map_two bad N _ _ _ _ st st (copiedState bad st n)
    (all_hit bad N (n+1) st _ hn hself)
    (all_arr bad N _ _ _ _ st (copiedState bad st n) (copiedState bad st n)
      (all_miss bad N n st hn hnext)
      (self_tail bad N (n+1) (copiedState bad st n) i (copied_root_name bad n st hn)
        (copied_preserves bad n st _ _ hself)))

/-- Recorded keys bad after p allocations; allocation i+1 has depth N-i. -/
def keys (bad : Bool) (N p : Nat) : List (Expr × Name) :=
  (List.range p).map (fun i => (pow (N-i) tr,freshName bad (i+1)))

theorem keys_fresh (bad : Bool) (N p k : Nat) (hp : p ≤ N) (hk : k ≤ N-p) :
    (keys bad N p).lookup (pow k tr) = none := by
  rw [List.lookup_eq_none_iff]
  intro pair hpair
  obtain ⟨i,hi,rfl⟩ := List.mem_map.mp hpair
  have hi' : i < p := List.mem_range.mp hi
  simp only [bne_iff_ne]
  intro he
  have he' : k = N-i := tower_key_injective bad he
  omega

theorem keys_succ (bad : Bool) (N p : Nat) :
    keys bad N (p+1) = keys bad N p ++ [(pow (N-p) tr,freshName bad (p+1))] := by
  simp [keys,List.range_succ]

theorem keys_hit (bad : Bool) (N p j : Nat) (hp : p ≤ N) (hj : j < p) :
    (keys bad N p).lookup (pow (N-j) tr) = some (freshName bad (j+1)) := by
  induction p with
  | zero => omega
  | succ p ih =>
    rw [keys_succ bad,List.lookup_append]
    by_cases hjp : j < p
    · rw [ih (by omega) hjp]
      rfl
    · have hj0 : j = p := by omega
      subst j
      rw [keys_fresh bad N p (N-p) (by omega) (by omega),List.lookup_cons_self]
      rfl


def front (bad : Bool) (N p : Nat) : List Official.AuxType :=
  rootRow bad N :: (List.range p).map (fun i => row bad N (N-i))

/-- The one-pending-row bad invariant, independently described by processed depth. -/
def queue (bad : Bool) (N p : Nat) : Official.ElimSt :=
  {aux := keys bad N (min (p+1) N),
   types := (front bad N p ++ if p < N then [rawRow bad (p+1) (N-p)] else []).toArray,
   next := min (p+1) N + 1}

theorem prefix_length (bad : Bool) (N p : Nat) : (front bad N p).length = p+1 := by
  simp [front]

theorem prefix_succ (bad : Bool) (N p : Nat) :
    front bad N (p+1) = front bad N p ++ [row bad N (N-p)] := by
  simp [front,List.range_succ]

theorem queue_pending (bad : Bool) (N p : Nat) (hp : p < N) :
    queue bad N p = {aux := keys bad N (p+1), types := (front bad N p ++ [rawRow bad (p+1) (N-p)]).toArray,next := p+2} := by
  simp only [queue,if_pos hp,Nat.min_eq_left (show p+1 ≤ N by omega)]

theorem queue_done (bad : Bool) (N : Nat) : queue bad N N = target bad N := by
  simp [queue,keys,front,target]

theorem queue_root_name (bad : Bool) (N p : Nat) :
    ((queue bad N p).types.toList.map (·.name)).contains Tn = true := by
  simp [queue,front,rootRow]

private theorem loop_step (bad : Bool) (N fuel q : Nat) (st st1 : Official.ElimSt)
    (t : Official.AuxType) (cs : List Expr)
    (ht : st.types[q]? = some t)
    (hc : (t.ctors.mapM (Official.replaceAll (context bad N))).run st = .ok (cs,st1)) :
    (Official.elimLoop (context bad N) (fuel+1) q).run st =
      (Official.elimLoop (context bad N) fuel (q+1)).run
        {st1 with types := st1.types.set! q {t with ctors := cs}} := by
  dsimp only [Official.elimLoop,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure]
  rw [ht]
  have hc' : t.ctors.mapM (Official.replaceAll (context bad N)) st = .ok (cs,st1) := hc
  dsimp only [StateT.bind,bind,Except.bind]
  rw [hc']
  dsimp only [modify,modifyGet,MonadStateOf.modifyGet,StateT.modifyGet,StateT.bind,
    pure,Except.pure,bind,Except.bind]

private theorem set_pending (bad : Bool) (pre : List Official.AuxType) (old new : Official.AuxType)
    (tail : List Official.AuxType) :
    (pre ++ old::tail).toArray.set! pre.length new = (pre ++ new::tail).toArray := by
  simp [Array.set!_eq_setIfInBounds,List.setIfInBounds_toArray,List.set_append_right]

private theorem row_terminal (bad : Bool) (p : Nat) :
    row bad (p+1) 1 = ⟨freshName bad (p+1),S,[auxExpr bad (p+1),
      arr tr (arr (auxExpr bad (p+1)) (auxExpr bad (p+1)))]⟩ := by
  simp [row,R,auxExpr]

private theorem row_descending (bad : Bool) (p n : Nat) :
    row bad (p+n+2) (n+2) = ⟨freshName bad (p+1),S,[auxExpr bad (p+1),
      arr (auxExpr bad (p+2)) (arr (auxExpr bad (p+1)) (auxExpr bad (p+1)))]⟩ := by
  have h0 : p+n+2-(n+2)+1 = p+1 := by omega
  have h1 : p+n+2-(n+1) = p+1 := by omega
  have h2 : p+n+2-n = p+2 := by omega
  have hs : n+2-1 = n+1 := by omega
  simp only [row,hs,R,auxExpr,h0,h1,h2]


theorem pending_at (bad : Bool) (N p : Nat) (hp : p < N) :
    (queue bad N p).types[p+1]? = some (rawRow bad (p+1) (N-p)) := by
  rw [queue_pending bad N p hp]
  simp only [List.getElem?_toArray]
  rw [List.getElem?_append_right (by rw [prefix_length bad]; omega)]
  rw [prefix_length bad]
  simp

theorem processed_end (bad : Bool) (N : Nat) : (queue bad N N).types[N+1]? = none := by
  rw [queue_done bad]
  simp only [target,List.getElem?_toArray]
  apply List.getElem?_eq_none
  simp

/-- Terminal frontier: its final row bad is updated, with no allocation. -/
theorem terminal_frontier (bad : Bool) (p : Nat) :
    (Official.elimLoop (context bad (p+1)) 2 (p+1)).run (queue bad (p+1) p) =
      (Official.elimLoop (context bad (p+1)) 1 (p+2)).run (queue bad (p+1) (p+1)) := by
  have hpend := pending_at bad (p+1) p (by omega)
  have hk : (queue bad (p+1) p).aux.lookup (pow 1 tr) = some (freshName bad (p+1)) := by
    rw [queue_pending bad _ _ (by omega)]
    have h := keys_hit bad (p+1) (p+1) p (by omega) (by omega)
    simpa using h
  have hc := terminal_row bad (p+1) (p+1) (queue bad (p+1) p) (queue_root_name bad _ _) hk
  have hdepth : p+1-p = 1 := by omega
  rw [hdepth] at hpend
  rw [loop_step bad (p+1) 1 (p+1) _ _ _ _ hpend hc]
  apply congrArg (fun st : Official.ElimSt =>
    (Official.elimLoop (context bad (p+1)) 1 (p+2)).run st)
  rw [queue_pending bad _ _ (by omega),queue_done bad]
  dsimp only [target]
  simp only [Official.ElimSt.mk.injEq]
  refine ⟨by rfl,?_,trivial⟩
  rw [hdepth]
  have hr : {rawRow bad (p+1) 1 with ctors := [auxExpr bad (p+1),
      arr tr (arr (auxExpr bad (p+1)) (auxExpr bad (p+1)))]} = row bad (p+1) 1 := by
    rw [row_terminal bad]
    rfl
  rw [hr]
  have hs := set_pending bad (front bad (p+1) p) (rawRow bad (p+1) 1) (row bad (p+1) 1) []
  rw [prefix_length bad] at hs
  rw [hs]
  change (front bad (p+1) p ++ [row bad (p+1) 1]).toArray = (front bad (p+1) (p+1)).toArray
  rw [prefix_succ bad,hdepth]


private theorem descending_state (bad : Bool) (p n : Nat) :
    {copiedState bad (queue bad (p+n+2) p) n with types := (copiedState bad (queue bad (p+n+2) p) n).types.set! (p+1) {rawRow bad (p+1) (n+2) with ctors := [auxExpr bad (p+1),arr (auxExpr bad (p+2)) (arr (auxExpr bad (p+1)) (auxExpr bad (p+1)))]}} =
      queue bad (p+n+2) (p+1) := by
  rw [queue_pending bad _ p (by omega),queue_pending bad _ (p+1) (by omega)]
  have hd : p+n+2-p = n+2 := by omega
  have hn : p+n+2-(p+1) = n+1 := by omega
  dsimp only [copiedState]
  simp only [Official.ElimSt.mk.injEq]
  refine ⟨?_,?_,?_⟩
  · have h := keys_succ bad (p+n+2) (p+1)
    rw [hn] at h
    exact h.symm
  · rw [hd,hn,List.push_toArray,List.append_assoc]
    have hr : {rawRow bad (p+1) (n+2) with ctors := [auxExpr bad (p+1),
        arr (auxExpr bad (p+2)) (arr (auxExpr bad (p+1)) (auxExpr bad (p+1)))]} =
        row bad (p+n+2) (n+2) := by rw [row_descending bad]; rfl
    rw [hr]
    have hs := set_pending bad (front bad (p+n+2) p) (rawRow bad (p+1) (n+2))
      (row bad (p+n+2) (n+2)) [rawRow bad (p+2) (n+1)]
    rw [prefix_length bad] at hs
    simp only [List.cons_append,List.nil_append]
    rw [hs,prefix_succ bad,hd,List.append_assoc]
    rfl
  · trivial

theorem descending_frontier (bad : Bool) (p n fuel : Nat) :
    (Official.elimLoop (context bad (p+n+2)) (fuel+1) (p+1)).run (queue bad (p+n+2) p) =
      (Official.elimLoop (context bad (p+n+2)) fuel (p+2)).run (queue bad (p+n+2) (p+1)) := by
  have hpend := pending_at bad (p+n+2) p (by omega)
  have hd : p+n+2-p = n+2 := by omega
  rw [hd] at hpend
  have hself : (queue bad (p+n+2) p).aux.lookup (pow (n+2) tr) = some (freshName bad (p+1)) := by
    rw [queue_pending bad _ _ (by omega)]
    have h := keys_hit bad (p+n+2) (p+1) p (by omega) (by omega)
    simpa only [hd] using h
  have hnext : (queue bad (p+n+2) p).aux.lookup (pow (n+1) tr) = none := by
    rw [queue_pending bad _ _ (by omega)]
    exact keys_fresh bad _ _ _ (by omega) (by omega)
  have hc := descending_row bad (p+n+2) n (p+1) (queue bad (p+n+2) p)
    (queue_root_name bad _ _) hself hnext
  have hi : (queue bad (p+n+2) p).next = p+2 := by
    rw [queue_pending bad _ _ (by omega)]
  rw [hi] at hc
  rw [loop_step bad (p+n+2) fuel (p+1) _ _ _ _ hpend hc]
  rw [descending_state bad]

private theorem loop_finished (bad : Bool) (N q : Nat) (st : Official.ElimSt)
    (ht : st.types[q]? = none) :
    (Official.elimLoop (context bad N) 1 q).run st = .ok ((),st) := by
  dsimp only [Official.elimLoop,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure]
  rw [ht]
  rfl

/-- The restricted queue bad induction: r pending depths require r+1 queue bad fuel. -/
theorem queue_run (bad : Bool) (p r : Nat) :
    (Official.elimLoop (context bad (p+r)) (r+1) (p+1)).run (queue bad (p+r) p) =
      .ok ((),target bad (p+r)) := by
  induction r generalizing p with
  | zero =>
    simp only [Nat.add_zero]
    rw [loop_finished bad _ _ _ (processed_end bad p),queue_done bad]
  | succ r ih =>
    cases r with
    | zero =>
      rw [terminal_frontier bad,loop_finished bad _ _ _ (processed_end bad (p+1)),queue_done bad]
    | succ n =>
      have hN : p+(n+1+1) = p+n+2 := by omega
      have hF : n+1+1+1 = n+2+1 := by omega
      rw [hN,hF]
      rw [descending_frontier bad p n (n+2)]
      have he : p+1+(n+1) = p+n+2 := by omega
      simpa only [he] using ih (p+1)


def initial (bad : Bool) (N : Nat) : Official.ElimSt :=
  {types := #[⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) (pow N tr)) tr]⟩]}

theorem node_initial (bad : Bool) (N : Nat) :
    Official.instPiParams (Tree2ArrowTowerSchema.node bad N).type (context bad N).ps =
     .ok (arr (arr (if bad then tr else A) (pow N tr)) tr) := by
  cases bad <;> simp only [Tree2ArrowTowerSchema.node,Official.instPiParams,
    context,instPisWith,pi,Expr.instantiate1,pow_inst] <;> rfl

private theorem leaf_all (bad : Bool) (N : Nat) (st : Official.ElimSt) :
    (Official.replaceAll (context bad N) (arr A tr)).run st = .ok (arr A tr,st) :=
  all_arr bad N A tr A tr st st st (by rfl) (all_member bad N st)

private theorem domain_all (bad : Bool) (N : Nat) (st : Official.ElimSt) :
 (Official.replaceAll (context bad N) (if bad then tr else A)).run st =
 .ok ((if bad then tr else A),st) := by cases bad <;> rfl

private theorem root_zero (bad : Bool) :
    ((initial bad 0).types[0]!.ctors.mapM (Official.replaceAll (context bad 0))).run (initial bad 0) =
      .ok ((rootRow bad 0).ctors,initial bad 0) :=
  map_two bad 0 _ _ _ _ _ _ _ (leaf_all bad _ _)
    (all_arr bad 0 _ _ _ _ _ _ _
      (all_arr bad 0 _ _ _ _ _ _ _ (domain_all bad _ _) (all_member bad _ _))
      (all_member bad _ _))

private theorem root_positive (bad : Bool) (n : Nat) :
    ((initial bad (n+1)).types[0]!.ctors.mapM (Official.replaceAll (context bad (n+1)))).run (initial bad (n+1)) =
      .ok ([arr A tr,arr (arr (if bad then tr else A) (auxExpr bad 1)) tr],copiedState bad (initial bad (n+1)) n) := by
  exact map_two bad (n+1) _ _ _ _ _ _ _ (leaf_all bad _ _)
    (all_arr bad (n+1) _ _ _ _ _ _ _
      (all_arr bad (n+1) _ _ _ _ _ _ _ (domain_all bad _ _)
        (all_miss bad (n+1) n (initial bad (n+1)) (by rfl) (by rfl)))
      (all_member bad _ _))

private theorem root_positive_state (bad : Bool) (n : Nat) :
    {copiedState bad (initial bad (n+1)) n with types := (copiedState bad (initial bad (n+1)) n).types.set! 0 {name := Tn,type := S,ctors := [arr A tr,arr (arr (if bad then tr else A) (auxExpr bad 1)) tr]}} = queue bad (n+1) 0 := by
  rw [queue_pending bad _ _ (by omega)]
  have hi : n+1-n = 1 := by omega
  simp [copiedState,initial,front,keys,rootRow,R,auxExpr,hi]

/-- Processing the declaration bad root establishes the independent queue bad frontier. -/
theorem root_frontier (bad : Bool) (N fuel : Nat) :
    (Official.elimLoop (context bad N) (fuel+1) 0).run (initial bad N) =
      (Official.elimLoop (context bad N) fuel 1).run (queue bad N 0) := by
  cases N with
  | zero =>
    have ht : (initial bad 0).types[0]? = some ⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) tr) tr]⟩ := rfl
    rw [loop_step bad 0 fuel 0 _ _ _ _ ht (root_zero bad)]
    rfl
  | succ n =>
    have ht : (initial bad (n+1)).types[0]? = some ⟨Tn,S,[arr A tr,arr (arr (if bad then tr else A) (pow (n+1) tr)) tr]⟩ := rfl
    rw [loop_step bad (n+1) fuel 0 _ _ _ _ ht (root_positive bad n)]
    rw [root_positive_state bad]

private theorem elimination_start (bad : Bool) (N fuel : Nat) :
    Official.elimNested (context bad N) (declaration bad N) fuel = (do
      let ((),st) ← (Official.elimLoop (context bad N) fuel 0).run (initial bad N)
      pure st) := by
  simp only [Official.elimNested,declaration,List.mapM_cons,List.mapM_nil]
  dsimp only [bind,Except.bind,pure,Except.pure]
  rw [node_initial bad]
  rfl

theorem official_lowering_family (bad : Bool) (N : Nat) :
    Official.elimNested (context bad N) (declaration bad N) (N+2) = .ok (target bad N) := by
  rw [elimination_start bad,root_frontier bad N (N+1)]
  have h := queue_run bad 0 N
  simp only [Nat.zero_add] at h
  rw [h]
  rfl



#print axioms official_lowering_family
end Tree2ArrowTowerOfficial
