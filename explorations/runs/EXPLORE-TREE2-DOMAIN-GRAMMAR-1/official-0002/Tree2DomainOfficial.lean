import Tree2DomainSchema

/- Local AI-authored adaptation of the retained all-depth official queue proof.
    The changed root carries one function field outside all List keys. -/
namespace Tree2DomainOfficial
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2DomainGrammar
set_option maxRecDepth 2000
set_option maxHeartbeats 1000000

def freshName (D : Domain) (i : Nat) : Name := .num (nm "TowerAux") i

def context (D : Domain) (N : Nat) : Official.ElimCtx :=
  {find? := (Tree2DomainSchema.env D N).find?, ctorsOf := fun c => if c == Ln then listCs else [],
   lvls := [], ps := [A], auxName := freshName D}

def declaration (D : Domain) (N : Nat) : List Official.MemberDecl :=
  [⟨Tn,treeCV.type,[leafCV.type,(Tree2DomainSchema.node D N).type]⟩]

/-- R_0 is the member; R_j has allocation index N-j+1. -/
def R (D : Domain) (N : Nat) : Nat → Expr
  | 0 => tr
  | j+1 => .app (.const (freshName D (N-j)) []) A

def row (D : Domain) (N j : Nat) : Official.AuxType :=
  ⟨freshName D (N-j+1),S,[R D N j,arr (R D N (j-1)) (arr (R D N j) (R D N j))]⟩
def rootRow (D : Domain) (N : Nat) : Official.AuxType := ⟨Tn,S,[arr A tr,arr (arr D.official (R D N N)) tr]⟩
def target (D : Domain) (N : Nat) : Official.ElimSt :=
  {aux := (List.range N).map (fun i => (pow (N-i) tr,freshName D (i+1))),
   types := (rootRow D N :: (List.range N).map (fun i => row D N (N-i))).toArray,
   next := N+1}

/-- Unprocessed List instance of depth j, with original (not lowered) keys. -/
def rawRow (D : Domain) (i j : Nat) : Official.AuxType :=
  ⟨freshName D i,S,[pow j tr,arr (pow (j-1) tr) (arr (pow j tr) (pow j tr))]⟩

theorem fresh_supply (D : Domain) (N i : Nat) :
    (Tree2DomainSchema.env D N).find? (freshName D i) = none ∧ freshName D i ≠ Tn ∧ freshName D i ≠ Ln ∧
    ∀ j, freshName D i = freshName D j ↔ i = j := by
  refine ⟨rfl, ?_, ?_, ?_⟩
  · intro h; cases h
  · intro h; cases h
  · intro j
    constructor
    · intro h; exact (Name.num.inj h).2
    · intro h; subst j; rfl

theorem tower_key_injective (D : Domain) : Function.Injective (fun n => pow n tr) := by
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

theorem tower_key_closed (D : Domain) (n : Nat) : (pow n tr).bvarB = 0 := by
  rw [Expr.bvarB_eq]
  induction n with
  | zero => rfl
  | succ n ih => simp [pow,l,Expr.bvarBound,ih]

theorem tower_root_occ (D : Domain) (n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    (pow n tr).nestOcc names 0 0 = true := by
  induction n with
  | zero => simp only [pow,tr,t,Expr.nestOcc,hn,Bool.true_or]
  | succ n ih => simp [pow,l,Expr.nestOcc,ih]

/-- The fixed copied List constructors before any lowering. -/
theorem copied_list (D : Domain) (d : Expr) :
    Official.instPiParams (listCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok S ∧
    Official.instPiParams (nilCV.type.instantiateLevelParams [un] [.zero]) [d] = .ok (l d) ∧
    Official.instPiParams (consCV.type.instantiateLevelParams [un] [.zero]) [d] =
      .ok (arr d (arr (l d) (l d))) := by
  exact ⟨rfl,rfl,rfl⟩

/-- Detection needs only the root-name occurrence and closed original key. -/
theorem nested_tower (D : Domain) (N n : Nat) (names : List Name) (hn : names.contains Tn = true) :
    Official.isNestedApp (context D N) names (pow (n+1) tr) =
      .ok (some (Ln,[.zero],1,[pow n tr])) := by
  have ho := tower_root_occ D n names hn
  have hb := tower_key_closed D n
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


def copiedState (D : Domain) (st : Official.ElimSt) (n : Nat) : Official.ElimSt :=
  {aux := st.aux ++ [(pow (n+1) tr,freshName D st.next)],
   types := st.types.push (rawRow D st.next (n+1)), next := st.next+1}

theorem copy_tower (D : Domain) (N n : Nat) (st : Official.ElimSt) :
    (Official.copyBlock (context D N) [.zero] [pow n tr] [Ln]).run st =
      .ok ((),copiedState D st n) := by rfl

theorem replace_hit (D : Domain) (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceIfNested (context D N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const a []) A),st) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower D N n _ hn]
  dsimp only [Except.pure,StateT.pure,context,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = some a := hk
  rw [hk']
  rfl


theorem copied_lookup (D : Domain) (n : Nat) (st : Official.ElimSt)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (copiedState D st n).aux.lookup (pow (n+1) tr) = some (freshName D st.next) := by
  simp only [copiedState,List.lookup_append,hk,List.lookup_cons_self,Option.or]

theorem replace_miss (D : Domain) (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceIfNested (context D N) (pow (n+1) tr)).run st =
      .ok (some (.app (.const (freshName D st.next) []) A),copiedState D st n) := by
  dsimp only [Official.replaceIfNested,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,liftM,monadLift,
    MonadLift.monadLift,StateT.lift,Except.pure]
  rw [nested_tower D N n _ hn]
  dsimp only [Except.pure,StateT.pure,Expr.mkAppN,List.take,List.drop]
  have hk' : st.aux.lookup (Expr.app (.const Ln [.zero]) (pow n tr)) = none := hk
  rw [hk']
  have hb : Official.blockOf (context D N) Ln = [Ln] := rfl
  rw [hb]
  have hcopy : Official.copyBlock (context D N) [.zero] [pow n tr] [Ln] =
      fun st => Except.ok ((),copiedState D st n) := by
    funext st
    exact copy_tower D N n st
  rw [hcopy]
  dsimp only [StateT.bind,StateT.get,StateT.pure,pure,Except.pure,bind,Except.bind]
  have hnew : (copiedState D st n).aux.lookup
      (Expr.app (.const Ln [.zero]) (pow n tr)) = some (freshName D st.next) :=
    copied_lookup D n st hk
  rw [hnew]
  rfl


private theorem all_replaced (D : Domain) (N : Nat) (f a w : Expr) (st st' : Official.ElimSt)
    (h : (Official.replaceIfNested (context D N) (.app f a)).run st = .ok (some w,st')) :
    (Official.replaceAll (context D N) (.app f a)).run st = .ok (w,st') := by
  dsimp only [Official.replaceAll,StateT.run,bind,StateT.bind,Except.bind]
  have h' : Official.replaceIfNested (context D N) (.app f a) st = .ok (some w,st') := h
  rw [h']
  rfl

theorem all_hit (D : Domain) (N n : Nat) (st : Official.ElimSt) (a : Name)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some a) :
    (Official.replaceAll (context D N) (pow (n+1) tr)).run st =
      .ok (.app (.const a []) A,st) :=
  all_replaced D N _ _ _ st st (replace_hit D N n st a hn hk)

theorem all_miss (D : Domain) (N n : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = none) :
    (Official.replaceAll (context D N) (pow (n+1) tr)).run st =
      .ok (.app (.const (freshName D st.next) []) A,copiedState D st n) :=
  all_replaced D N _ _ _ st (copiedState D st n) (replace_miss D N n st hn hk)

theorem all_member (D : Domain) (N : Nat) (st : Official.ElimSt) :
    (Official.replaceAll (context D N) tr).run st = .ok (tr,st) := by rfl

private theorem all_arr (D : Domain) (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context D N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context D N) b).run st1 = .ok (b',st2)) :
    (Official.replaceAll (context D N) (arr a b)).run st = .ok (arr a' b',st2) := by
  dsimp only [arr,pi,Official.replaceAll,StateT.run,bind,StateT.bind,pure,
    StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context D N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context D N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']

/-- A self row D is rewritten without allocation, once its key is recorded. -/
theorem self_tail (D : Domain) (N n : Nat) (st : Official.ElimSt) (i : Nat)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow (n+1) tr) = some (freshName D i)) :
    (Official.replaceAll (context D N) (arr (pow (n+1) tr) (pow (n+1) tr))).run st =
      .ok (arr (.app (.const (freshName D i) []) A) (.app (.const (freshName D i) []) A),st) :=
  all_arr D N _ _ _ _ st st st (all_hit D N n st _ hn hk) (all_hit D N n st _ hn hk)


private theorem map_two (D : Domain) (N : Nat) (a b a' b' : Expr) (st st1 st2 : Official.ElimSt)
    (ha : (Official.replaceAll (context D N) a).run st = .ok (a',st1))
    (hb : (Official.replaceAll (context D N) b).run st1 = .ok (b',st2)) :
    ([a,b].mapM (Official.replaceAll (context D N))).run st = .ok ([a',b'],st2) := by
  simp only [List.mapM_cons,List.mapM_nil]
  dsimp only [StateT.run,bind,StateT.bind,pure,StateT.pure,Except.bind,Except.pure]
  have ha' : Official.replaceAll (context D N) a st = .ok (a',st1) := ha
  have hb' : Official.replaceAll (context D N) b st1 = .ok (b',st2) := hb
  rw [ha']
  dsimp only
  rw [hb']

theorem copied_preserves (D : Domain) (n : Nat) (st : Official.ElimSt) (e : Expr) (a : Name)
    (h : st.aux.lookup e = some a) : (copiedState D st n).aux.lookup e = some a := by
  simp only [copiedState,List.lookup_append,h,Option.or]

theorem copied_root_name (D : Domain) (n : Nat) (st : Official.ElimSt)
    (h : (st.types.toList.map (·.name)).contains Tn = true) :
    ((copiedState D st n).types.toList.map (·.name)).contains Tn = true := by
  simp only [copiedState,Array.toList_push,List.map_append,List.map_cons,List.map_nil,
    List.contains_append,h,Bool.true_or]

def auxExpr (D : Domain) (i : Nat) : Expr := .app (.const (freshName D i) []) A

/-- Exact terminal row D transition (List T): only its recorded self key is used. -/
theorem terminal_row (D : Domain) (N i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hk : st.aux.lookup (pow 1 tr) = some (freshName D i)) :
    ((rawRow D i 1).ctors.mapM (Official.replaceAll (context D N))).run st =
      .ok ([auxExpr D i,arr tr (arr (auxExpr D i) (auxExpr D i))],st) := by
  exact map_two D N _ _ _ _ st st st (all_hit D N 0 st _ hn hk)
    (all_arr D N _ _ _ _ st st st (all_member D N st) (self_tail D N 0 st i hn hk))

/-- Exact positive-depth row D transition: one new element row D, self tails reused. -/
theorem descending_row (D : Domain) (N n i : Nat) (st : Official.ElimSt)
    (hn : (st.types.toList.map (·.name)).contains Tn = true)
    (hself : st.aux.lookup (pow (n+2) tr) = some (freshName D i))
    (hnext : st.aux.lookup (pow (n+1) tr) = none) :
    ((rawRow D i (n+2)).ctors.mapM (Official.replaceAll (context D N))).run st =
      .ok ([auxExpr D i,arr (auxExpr D st.next) (arr (auxExpr D i) (auxExpr D i))],copiedState D st n) := by
  exact map_two D N _ _ _ _ st st (copiedState D st n)
    (all_hit D N (n+1) st _ hn hself)
    (all_arr D N _ _ _ _ st (copiedState D st n) (copiedState D st n)
      (all_miss D N n st hn hnext)
      (self_tail D N (n+1) (copiedState D st n) i (copied_root_name D n st hn)
        (copied_preserves D n st _ _ hself)))

/-- Recorded keys D after p allocations; allocation i+1 has depth N-i. -/
def keys (D : Domain) (N p : Nat) : List (Expr × Name) :=
  (List.range p).map (fun i => (pow (N-i) tr,freshName D (i+1)))

theorem keys_fresh (D : Domain) (N p k : Nat) (hp : p ≤ N) (hk : k ≤ N-p) :
    (keys D N p).lookup (pow k tr) = none := by
  rw [List.lookup_eq_none_iff]
  intro pair hpair
  obtain ⟨i,hi,rfl⟩ := List.mem_map.mp hpair
  have hi' : i < p := List.mem_range.mp hi
  simp only [bne_iff_ne]
  intro he
  have he' : k = N-i := tower_key_injective D he
  omega

theorem keys_succ (D : Domain) (N p : Nat) :
    keys D N (p+1) = keys D N p ++ [(pow (N-p) tr,freshName D (p+1))] := by
  simp [keys,List.range_succ]

theorem keys_hit (D : Domain) (N p j : Nat) (hp : p ≤ N) (hj : j < p) :
    (keys D N p).lookup (pow (N-j) tr) = some (freshName D (j+1)) := by
  induction p with
  | zero => omega
  | succ p ih =>
    rw [keys_succ D,List.lookup_append]
    by_cases hjp : j < p
    · rw [ih (by omega) hjp]
      rfl
    · have hj0 : j = p := by omega
      subst j
      rw [keys_fresh D N p (N-p) (by omega) (by omega),List.lookup_cons_self]
      rfl


def front (D : Domain) (N p : Nat) : List Official.AuxType :=
  rootRow D N :: (List.range p).map (fun i => row D N (N-i))

/-- The one-pending-row D invariant, independently described by processed depth. -/
def queue (D : Domain) (N p : Nat) : Official.ElimSt :=
  {aux := keys D N (min (p+1) N),
   types := (front D N p ++ if p < N then [rawRow D (p+1) (N-p)] else []).toArray,
   next := min (p+1) N + 1}

theorem prefix_length (D : Domain) (N p : Nat) : (front D N p).length = p+1 := by
  simp [front]

theorem prefix_succ (D : Domain) (N p : Nat) :
    front D N (p+1) = front D N p ++ [row D N (N-p)] := by
  simp [front,List.range_succ]

theorem queue_pending (D : Domain) (N p : Nat) (hp : p < N) :
    queue D N p = {aux := keys D N (p+1), types := (front D N p ++ [rawRow D (p+1) (N-p)]).toArray,next := p+2} := by
  simp only [queue,if_pos hp,Nat.min_eq_left (show p+1 ≤ N by omega)]

theorem queue_done (D : Domain) (N : Nat) : queue D N N = target D N := by
  simp [queue,keys,front,target]

theorem queue_root_name (D : Domain) (N p : Nat) :
    ((queue D N p).types.toList.map (·.name)).contains Tn = true := by
  simp [queue,front,rootRow]

private theorem loop_step (D : Domain) (N fuel q : Nat) (st st1 : Official.ElimSt)
    (t : Official.AuxType) (cs : List Expr)
    (ht : st.types[q]? = some t)
    (hc : (t.ctors.mapM (Official.replaceAll (context D N))).run st = .ok (cs,st1)) :
    (Official.elimLoop (context D N) (fuel+1) q).run st =
      (Official.elimLoop (context D N) fuel (q+1)).run
        {st1 with types := st1.types.set! q {t with ctors := cs}} := by
  dsimp only [Official.elimLoop,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure]
  rw [ht]
  have hc' : t.ctors.mapM (Official.replaceAll (context D N)) st = .ok (cs,st1) := hc
  dsimp only [StateT.bind,bind,Except.bind]
  rw [hc']
  dsimp only [modify,modifyGet,MonadStateOf.modifyGet,StateT.modifyGet,StateT.bind,
    pure,Except.pure,bind,Except.bind]

private theorem set_pending (D : Domain) (pre : List Official.AuxType) (old new : Official.AuxType)
    (tail : List Official.AuxType) :
    (pre ++ old::tail).toArray.set! pre.length new = (pre ++ new::tail).toArray := by
  simp [Array.set!_eq_setIfInBounds,List.setIfInBounds_toArray,List.set_append_right]

private theorem row_terminal (D : Domain) (p : Nat) :
    row D (p+1) 1 = ⟨freshName D (p+1),S,[auxExpr D (p+1),
      arr tr (arr (auxExpr D (p+1)) (auxExpr D (p+1)))]⟩ := by
  simp [row,R,auxExpr]

private theorem row_descending (D : Domain) (p n : Nat) :
    row D (p+n+2) (n+2) = ⟨freshName D (p+1),S,[auxExpr D (p+1),
      arr (auxExpr D (p+2)) (arr (auxExpr D (p+1)) (auxExpr D (p+1)))]⟩ := by
  have h0 : p+n+2-(n+2)+1 = p+1 := by omega
  have h1 : p+n+2-(n+1) = p+1 := by omega
  have h2 : p+n+2-n = p+2 := by omega
  have hs : n+2-1 = n+1 := by omega
  simp only [row,hs,R,auxExpr,h0,h1,h2]


theorem pending_at (D : Domain) (N p : Nat) (hp : p < N) :
    (queue D N p).types[p+1]? = some (rawRow D (p+1) (N-p)) := by
  rw [queue_pending D N p hp]
  simp only [List.getElem?_toArray]
  rw [List.getElem?_append_right (by rw [prefix_length D]; omega)]
  rw [prefix_length D]
  simp

theorem processed_end (D : Domain) (N : Nat) : (queue D N N).types[N+1]? = none := by
  rw [queue_done D]
  simp only [target,List.getElem?_toArray]
  apply List.getElem?_eq_none
  simp

/-- Terminal frontier: its final row D is updated, with no allocation. -/
theorem terminal_frontier (D : Domain) (p : Nat) :
    (Official.elimLoop (context D (p+1)) 2 (p+1)).run (queue D (p+1) p) =
      (Official.elimLoop (context D (p+1)) 1 (p+2)).run (queue D (p+1) (p+1)) := by
  have hpend := pending_at D (p+1) p (by omega)
  have hk : (queue D (p+1) p).aux.lookup (pow 1 tr) = some (freshName D (p+1)) := by
    rw [queue_pending D _ _ (by omega)]
    have h := keys_hit D (p+1) (p+1) p (by omega) (by omega)
    simpa using h
  have hc := terminal_row D (p+1) (p+1) (queue D (p+1) p) (queue_root_name D _ _) hk
  have hdepth : p+1-p = 1 := by omega
  rw [hdepth] at hpend
  rw [loop_step D (p+1) 1 (p+1) _ _ _ _ hpend hc]
  apply congrArg (fun st : Official.ElimSt =>
    (Official.elimLoop (context D (p+1)) 1 (p+2)).run st)
  rw [queue_pending D _ _ (by omega),queue_done D]
  dsimp only [target]
  simp only [Official.ElimSt.mk.injEq]
  refine ⟨by rfl,?_,trivial⟩
  rw [hdepth]
  have hr : {rawRow D (p+1) 1 with ctors := [auxExpr D (p+1),
      arr tr (arr (auxExpr D (p+1)) (auxExpr D (p+1)))]} = row D (p+1) 1 := by
    rw [row_terminal D]
    rfl
  rw [hr]
  have hs := set_pending D (front D (p+1) p) (rawRow D (p+1) 1) (row D (p+1) 1) []
  rw [prefix_length D] at hs
  rw [hs]
  change (front D (p+1) p ++ [row D (p+1) 1]).toArray = (front D (p+1) (p+1)).toArray
  rw [prefix_succ D,hdepth]


private theorem descending_state (D : Domain) (p n : Nat) :
    {copiedState D (queue D (p+n+2) p) n with types := (copiedState D (queue D (p+n+2) p) n).types.set! (p+1) {rawRow D (p+1) (n+2) with ctors := [auxExpr D (p+1),arr (auxExpr D (p+2)) (arr (auxExpr D (p+1)) (auxExpr D (p+1)))]}} =
      queue D (p+n+2) (p+1) := by
  rw [queue_pending D _ p (by omega),queue_pending D _ (p+1) (by omega)]
  have hd : p+n+2-p = n+2 := by omega
  have hn : p+n+2-(p+1) = n+1 := by omega
  dsimp only [copiedState]
  simp only [Official.ElimSt.mk.injEq]
  refine ⟨?_,?_,?_⟩
  · have h := keys_succ D (p+n+2) (p+1)
    rw [hn] at h
    exact h.symm
  · rw [hd,hn,List.push_toArray,List.append_assoc]
    have hr : {rawRow D (p+1) (n+2) with ctors := [auxExpr D (p+1),
        arr (auxExpr D (p+2)) (arr (auxExpr D (p+1)) (auxExpr D (p+1)))]} =
        row D (p+n+2) (n+2) := by rw [row_descending D]; rfl
    rw [hr]
    have hs := set_pending D (front D (p+n+2) p) (rawRow D (p+1) (n+2))
      (row D (p+n+2) (n+2)) [rawRow D (p+2) (n+1)]
    rw [prefix_length D] at hs
    simp only [List.cons_append,List.nil_append]
    rw [hs,prefix_succ D,hd,List.append_assoc]
    rfl
  · trivial

theorem descending_frontier (D : Domain) (p n fuel : Nat) :
    (Official.elimLoop (context D (p+n+2)) (fuel+1) (p+1)).run (queue D (p+n+2) p) =
      (Official.elimLoop (context D (p+n+2)) fuel (p+2)).run (queue D (p+n+2) (p+1)) := by
  have hpend := pending_at D (p+n+2) p (by omega)
  have hd : p+n+2-p = n+2 := by omega
  rw [hd] at hpend
  have hself : (queue D (p+n+2) p).aux.lookup (pow (n+2) tr) = some (freshName D (p+1)) := by
    rw [queue_pending D _ _ (by omega)]
    have h := keys_hit D (p+n+2) (p+1) p (by omega) (by omega)
    simpa only [hd] using h
  have hnext : (queue D (p+n+2) p).aux.lookup (pow (n+1) tr) = none := by
    rw [queue_pending D _ _ (by omega)]
    exact keys_fresh D _ _ _ (by omega) (by omega)
  have hc := descending_row D (p+n+2) n (p+1) (queue D (p+n+2) p)
    (queue_root_name D _ _) hself hnext
  have hi : (queue D (p+n+2) p).next = p+2 := by
    rw [queue_pending D _ _ (by omega)]
  rw [hi] at hc
  rw [loop_step D (p+n+2) fuel (p+1) _ _ _ _ hpend hc]
  rw [descending_state D]

private theorem loop_finished (D : Domain) (N q : Nat) (st : Official.ElimSt)
    (ht : st.types[q]? = none) :
    (Official.elimLoop (context D N) 1 q).run st = .ok ((),st) := by
  dsimp only [Official.elimLoop,StateT.run,bind,StateT.bind,get,getThe,
    MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure]
  rw [ht]
  rfl

/-- The restricted queue D induction: r pending depths require r+1 queue D fuel. -/
theorem queue_run (D : Domain) (p r : Nat) :
    (Official.elimLoop (context D (p+r)) (r+1) (p+1)).run (queue D (p+r) p) =
      .ok ((),target D (p+r)) := by
  induction r generalizing p with
  | zero =>
    simp only [Nat.add_zero]
    rw [loop_finished D _ _ _ (processed_end D p),queue_done D]
  | succ r ih =>
    cases r with
    | zero =>
      rw [terminal_frontier D,loop_finished D _ _ _ (processed_end D (p+1)),queue_done D]
    | succ n =>
      have hN : p+(n+1+1) = p+n+2 := by omega
      have hF : n+1+1+1 = n+2+1 := by omega
      rw [hN,hF]
      rw [descending_frontier D p n (n+2)]
      have he : p+1+(n+1) = p+n+2 := by omega
      simpa only [he] using ih (p+1)


def initial (D : Domain) (N : Nat) : Official.ElimSt :=
  {types := #[⟨Tn,S,[arr A tr,arr (arr D.official (pow N tr)) tr]⟩]}

theorem node_initial (D : Domain) (N : Nat) :
 Official.instPiParams (Tree2DomainSchema.node D N).type (context D N).ps =
 .ok (arr (arr D.official (pow N tr)) tr) :=
 Tree2DomainSchema.node_initial D N

private theorem leaf_all (D : Domain) (N : Nat) (st : Official.ElimSt) :
    (Official.replaceAll (context D N) (arr A tr)).run st = .ok (arr A tr,st) :=
  all_arr D N A tr A tr st st st (by rfl) (all_member D N st)

/-- Domain replacement is structurally state-preserving; no auxiliary key is introduced. -/
private theorem domain_all (D E : Domain) (N : Nat) (st : Official.ElimSt) :
 (Official.replaceAll (context D N) E.official).run st=.ok (E.official,st) := by
 induction E with
 | param => rfl
 | self => rfl
 | arrow a b ia ib =>
  exact all_arr D N _ _ _ _ st st st ia ib

private theorem root_zero (D : Domain) :
    ((initial D 0).types[0]!.ctors.mapM (Official.replaceAll (context D 0))).run (initial D 0) =
      .ok ((rootRow D 0).ctors,initial D 0) :=
  map_two D 0 _ _ _ _ _ _ _ (leaf_all D _ _)
    (all_arr D 0 _ _ _ _ _ _ _
      (all_arr D 0 _ _ _ _ _ _ _ (domain_all D D _ _) (all_member D _ _))
      (all_member D _ _))

private theorem root_positive (D : Domain) (n : Nat) :
    ((initial D (n+1)).types[0]!.ctors.mapM (Official.replaceAll (context D (n+1)))).run (initial D (n+1)) =
      .ok ([arr A tr,arr (arr D.official (auxExpr D 1)) tr],copiedState D (initial D (n+1)) n) := by
  exact map_two D (n+1) _ _ _ _ _ _ _ (leaf_all D _ _)
    (all_arr D (n+1) _ _ _ _ _ _ _
      (all_arr D (n+1) _ _ _ _ _ _ _ (domain_all D D _ _)
        (all_miss D (n+1) n (initial D (n+1)) (by rfl) (by rfl)))
      (all_member D _ _))

private theorem root_positive_state (D : Domain) (n : Nat) :
    {copiedState D (initial D (n+1)) n with types := (copiedState D (initial D (n+1)) n).types.set! 0 {name := Tn,type := S,ctors := [arr A tr,arr (arr D.official (auxExpr D 1)) tr]}} = queue D (n+1) 0 := by
  rw [queue_pending D _ _ (by omega)]
  have hi : n+1-n = 1 := by omega
  simp [copiedState,initial,front,keys,rootRow,R,auxExpr,hi]

/-- Processing the declaration D root establishes the independent queue D frontier. -/
theorem root_frontier (D : Domain) (N fuel : Nat) :
    (Official.elimLoop (context D N) (fuel+1) 0).run (initial D N) =
      (Official.elimLoop (context D N) fuel 1).run (queue D N 0) := by
  cases N with
  | zero =>
    have ht : (initial D 0).types[0]? = some ⟨Tn,S,[arr A tr,arr (arr D.official tr) tr]⟩ := rfl
    rw [loop_step D 0 fuel 0 _ _ _ _ ht (root_zero D)]
    rfl
  | succ n =>
    have ht : (initial D (n+1)).types[0]? = some ⟨Tn,S,[arr A tr,arr (arr D.official (pow (n+1) tr)) tr]⟩ := rfl
    rw [loop_step D (n+1) fuel 0 _ _ _ _ ht (root_positive D n)]
    rw [root_positive_state D]

private theorem elimination_start (D : Domain) (N fuel : Nat) :
    Official.elimNested (context D N) (declaration D N) fuel = (do
      let ((),st) ← (Official.elimLoop (context D N) fuel 0).run (initial D N)
      pure st) := by
  simp only [Official.elimNested,declaration,List.mapM_cons,List.mapM_nil]
  dsimp only [bind,Except.bind,pure,Except.pure]
  rw [node_initial D]
  rfl

theorem official_lowering_family (D : Domain) (N : Nat) :
    Official.elimNested (context D N) (declaration D N) (N+2) = .ok (target D N) := by
  rw [elimination_start D,root_frontier D N (N+1)]
  have h := queue_run D 0 N
  simp only [Nat.zero_add] at h
  rw [h]
  rfl



/-- Schema-facing exact equation; both independently described states reduce alike. -/
theorem lowering (D : Domain) (N : Nat) :
 Official.elimNested (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (N+2) =
 .ok (Tree2DomainSchema.target D N) := by
 change Official.elimNested (context D N) (declaration D N) (N+2) = .ok (target D N)
 exact official_lowering_family D N

def officialEnv := Tree2ArrowTowerOfficial.officialEnv
def officialWhnf := Tree2ArrowTowerOfficial.officialWhnf

private theorem official_whnf_pi (N : Nat) (a b : Expr) (d : Nat) :
 officialWhnf N d (arr a b)=.ok (arr a b) := by
 apply whnf_mono (show 2 ≤ 16 by decide)
 change whnfBody (pureFns .verified (officialEnv N) 1) (officialEnv N) d (arr a b)=.ok (arr a b)
 unfold whnfBody whnfLoopFuel
 rfl
private def names (N : Nat) := Tn :: (List.range N).map
 (fun i => Tree2TowerOfficial.freshName (i+1))
private def info (N : Nat) (n : Name) : ConstantInfo :=
 .indInfo ⟨n,[],pi S S⟩ {sortZ := .never,all := names N,nparams := 1,ctors := []}
private def refName (N : Nat) : Nat → Name
 | 0 => Tn
 | j+1 => Tree2TowerOfficial.freshName (N-j)
private theorem reference (N j : Nat) :
 Tree2TowerOfficial.R N j = .app (.const (refName N j) []) A := by
 cases j <;> rfl
private theorem ref_mem (N j : Nat) (hj : j ≤ N) : refName N j ∈ names N := by
 cases j with
 | zero => exact List.mem_cons_self
 | succ j =>
  apply List.mem_cons_of_mem
  apply List.mem_map.mpr
  refine ⟨N-j-1,List.mem_range.mpr (by omega),?_⟩
  have he : N-j-1+1=N-j := by omega
  simp only [refName,he]
private theorem map_find (N : Nat) (ns : List Name) (n : Name) (hn : n ∈ ns) :
 ((ns.map (info N)).find? (fun ci => ci.name == n)) = some (info N n) := by
 induction ns with
 | nil => cases hn
 | cons a ns ih =>
  change (match a == n with
   | true => some (info N a)
   | false => (ns.map (info N)).find? (fun ci => ci.name == n)) = _
  by_cases he : a=n
  · subst a; rw [show (n==n)=true from BEq.rfl]
  · have hm : n ∈ ns := by simpa [List.mem_cons,Ne.symm he] using hn
    rw [show (a==n)=false from by simp [he]]
    exact ih hm
private theorem ref_lookup (N j : Nat) (hj : j ≤ N) :
 (officialEnv N).find? (refName N j) = some (info N (refName N j)) := by
 have hm := map_find N (names N) (refName N j) (ref_mem N j hj)
 cases j with
 | zero => exact hm
 | succ j => exact hm
private theorem whnf_reference (N j d : Nat) (hj : j ≤ N) :
 officialWhnf N d (Tree2TowerOfficial.R N j) = .ok (Tree2TowerOfficial.R N j) := by
 rw [reference]
 apply whnf_mono (show 3 ≤ 16 by decide)
 change whnfBody (pureFns .verified (officialEnv N) 2) (officialEnv N) d
  (.app (.const (refName N j) []) A) = .ok _
 unfold whnfBody whnfLoopFuel
 rw [whnfLoop]
 dsimp only [whnfStep,pureFns,coreKnot,id,whnfCoreBody,pure,Except.pure,
  bind,Except.bind,iotaRec,Expr.getAppFn]
 rw [ref_lookup N j hj]
 dsimp only [info,reduceNat,unfoldDefinition,Expr.getAppFn]
 rw [ref_lookup N j hj]
 cases j <;> rfl
private def positiveOracle (D : Domain) (N : Nat) :=
 (Tree2DomainSchema.target D N).oracle (Tree2DomainSchema.context D N) (officialWhnf N)
private theorem target_type (D : Domain) (N : Nat) (ty : Official.AuxType)
 (ht : ty ∈ (Tree2DomainSchema.target D N).types.toList) : ty.type=S := by
 simp only [Tree2DomainSchema.target,List.toList_toArray,List.mem_cons] at ht
 rcases ht with rfl | ht
 · rfl
 · obtain ⟨i,hi,rfl⟩ := List.mem_map.mp ht
   rfl
private theorem indices_zero (D : Domain) (N : Nat) (n : Name) : (positiveOracle D N).nIdx n=0 := by
 unfold positiveOracle Official.ElimSt.oracle
 dsimp only
 cases hf : (Tree2DomainSchema.target D N).types.toList.find? (fun t => t.name == n) with
 | none => rfl
 | some ty =>
  have hs := target_type D N ty (List.mem_of_find?_eq_some hf)
  simp only [hs]
  rfl
private theorem oracle_names (D : Domain) (N : Nat) : (positiveOracle D N).names=names N := by
 simp [positiveOracle,Official.ElimSt.oracle,Tree2DomainSchema.target,
  Tree2DomainSchema.rootRow,Tree2TowerOfficial.row,List.map_map,names]
 intro i hi
 have he : N-(N-i)+1=i+1 := by omega
 simp only [Function.comp_apply,he]
private theorem valid_reference (D : Domain) (N j : Nat) (hj : j ≤ N) :
 (positiveOracle D N).validAt (refName N j) (Tree2TowerOfficial.R N j)=true := by
 rw [reference]
 simp only [Official.PosOracle.validAt,Expr.getAppFn,Expr.getAppArgs,indices_zero D]
 change ((.const (refName N j) [] : Expr)==.const (refName N j) []) &&
  true && true && true = true
 simp only [BEq.rfl,Bool.true_and]
 rfl
private theorem positive_reference (D : Domain) (N j f d : Nat) (hj : j ≤ N) :
 Official.checkPositivity (positiveOracle D N) (f+1) d (Tree2TowerOfficial.R N j)=.ok () := by
 rw [Official.checkPositivity]
 rw [show (positiveOracle D N).whnf d (Tree2TowerOfficial.R N j)=.ok _ from whnf_reference N j d hj]
 have hv : (positiveOracle D N).valid (Tree2TowerOfficial.R N j)=true := by
  apply List.any_eq_true.mpr
  refine ⟨refName N j,?_,valid_reference D N j hj⟩
  rw [oracle_names D]; exact ref_mem N j hj
 cases j <;> simp only [Tree2TowerOfficial.R,tr,t,bind,Except.bind] at hv ⊢
 all_goals simp only [hv]
 all_goals split <;> rfl
private theorem parameter_positive (D : Domain) (N f d : Nat) :
 Official.checkPositivity (positiveOracle D N) (f+1) d A=.ok () := by
 rw [Official.checkPositivity]
 have hw : officialWhnf N d A=.ok A := by
  apply whnf_mono (show 2 ≤ 16 by decide)
  change whnfBody (pureFns .verified (officialEnv N) 1) (officialEnv N) d A=.ok A
  unfold whnfBody whnfLoopFuel
  rfl
 rw [show (positiveOracle D N).whnf d A=.ok A from hw]
 rfl
private theorem domain_occ (D : Domain) (N : Nat) :
 (positiveOracle D N).occ D.official=D.hasSelf := by
 apply Domain.official_occ D
 rw [oracle_names]; rfl
private theorem function_positive (D : Domain) (N d : Nat) (ha : D.hasSelf=false) :
 Official.checkPositivity (positiveOracle D N) 6 d (arr D.official (Tree2TowerOfficial.R N N))=.ok () := by
 rw [Official.checkPositivity]
 rw [show (positiveOracle D N).whnf d (arr D.official (Tree2TowerOfficial.R N N))=.ok _
  from official_whnf_pi _ _ _ d]
 have hi : (Tree2TowerOfficial.R N N).instantiate1 (.fvar d D.official)=Tree2TowerOfficial.R N N := by
  rw [reference]; rfl
 have ho : (positiveOracle D N).occ D.official=false := (domain_occ D N).trans ha
 change (if !(positiveOracle D N).occ (arr D.official (Tree2TowerOfficial.R N N)) then .ok ()
  else if (positiveOracle D N).occ D.official then .error (.invalid "official: non positive occurrence of the datatypes being declared")
  else Official.checkPositivity (positiveOracle D N) 5 (d+1)
   ((Tree2TowerOfficial.R N N).instantiate1 (.fvar d D.official)))=.ok ()
 rw [ho]
 split
 · rfl
 · rw [hi]; exact positive_reference D N N 4 (d+1) (Nat.le_refl _)
private theorem return_reference (D : Domain) (N j f nb d : Nat) (hj : j ≤ N) :
 Official.checkCtorPos (positiveOracle D N) (refName N j) f (nb+1) d
  (Tree2TowerOfficial.R N j)=.ok () := by
 rw [reference]
 change (if (positiveOracle D N).validAt (refName N j) (.app (.const (refName N j) []) A)
  then Except.ok () else Except.error (.invalid "official: invalid return type"))=(Except.ok () : Except CheckError Unit)
 rw [← reference,valid_reference D N j hj]
 rfl
private theorem ctor_pi_pos (D : Domain) (N : Nat) (self : Name) (nb d : Nat) (a b : Expr)
 (hi : b.instantiate1 (.fvar d a)=b)
 (hp : Official.checkPositivity (positiveOracle D N) 6 d a=.ok ())
 (hb : Official.checkCtorPos (positiveOracle D N) self 6 nb (d+1) b=.ok ()) :
 Official.checkCtorPos (positiveOracle D N) self 6 (nb+1) d (arr a b)=.ok () := by
 change (do
  let _ ← Official.checkPositivity (positiveOracle D N) 6 d a
  Official.checkCtorPos (positiveOracle D N) self 6 nb (d+1) (b.instantiate1 (.fvar d a)))=_
 rw [hp,hi]
 exact hb

private theorem root_checks (D : Domain) (N : Nat) (ha : D.hasSelf=false) (ct : Expr)
 (hc : ct ∈ (Tree2DomainSchema.rootRow D N).ctors) :
 Official.checkCtorPos (positiveOracle D N) Tn 6 4 2 ct=.ok () := by
 have hc' : ct=arr A tr ∨ ct=arr (arr D.official (Tree2TowerOfficial.R N N)) tr := by
  simpa [Tree2DomainSchema.rootRow,List.mem_cons,List.not_mem_nil] using hc
 rcases hc' with rfl | rfl
 · exact ctor_pi_pos D N Tn 3 2 A tr rfl (parameter_positive D N 5 2)
    (return_reference D N 0 6 2 3 (Nat.zero_le _))
 · exact ctor_pi_pos D N Tn 3 2 (arr D.official (Tree2TowerOfficial.R N N)) tr rfl
    (function_positive D N 2 ha) (return_reference D N 0 6 2 3 (Nat.zero_le _))
private theorem row_name (N j : Nat) (h1 : 1 ≤ j) (hj : j ≤ N) :
 (Tree2TowerOfficial.row N j).name=refName N j := by
 cases j with
 | zero => omega
 | succ k =>
  have he : N-(k+1)+1=N-k := by omega
  simp only [Tree2TowerOfficial.row,refName,he]
private theorem row_checks (D : Domain) (N j : Nat) (h1 : 1 ≤ j) (hj : j ≤ N) (ct : Expr)
 (hc : ct ∈ (Tree2TowerOfficial.row N j).ctors) :
 Official.checkCtorPos (positiveOracle D N) (Tree2TowerOfficial.row N j).name 6 4 2 ct=.ok () := by
 rw [row_name N j h1 hj]
 have hc' : ct=Tree2TowerOfficial.R N j ∨ ct=arr (Tree2TowerOfficial.R N (j-1))
  (arr (Tree2TowerOfficial.R N j) (Tree2TowerOfficial.R N j)) := by
  simpa [Tree2TowerOfficial.row,List.mem_cons,List.not_mem_nil] using hc
 rcases hc' with rfl | rfl
 · exact return_reference D N j 6 3 2 hj
 · apply ctor_pi_pos D N (refName N j) 3 2 (Tree2TowerOfficial.R N (j-1))
    (arr (Tree2TowerOfficial.R N j) (Tree2TowerOfficial.R N j))
   · simp only [reference]; rfl
   · exact positive_reference D N (j-1) 5 2 (by omega)
   · apply ctor_pi_pos D N (refName N j) 2 3 (Tree2TowerOfficial.R N j) (Tree2TowerOfficial.R N j)
     · rw [reference]; rfl
     · exact positive_reference D N j 5 3 hj
     · exact return_reference D N j 6 1 4 hj

/-- Every depth has an actual positive official witness, using its exact lowered
    constructors and the explicit verified opaque environment. -/
theorem positive_acceptance (D : Domain) (N : Nat) (ha : D.hasSelf=false) :
 Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (officialWhnf N) 2 := by
 refine ⟨N+2,Tree2DomainSchema.target D N,lowering D N,?_⟩
 intro ty hty ct hct
 have ht : ty=Tree2DomainSchema.rootRow D N ∨
  ty ∈ (List.range N).map (fun i => Tree2TowerOfficial.row N (N-i)) := by
  simpa [Tree2DomainSchema.target,List.mem_cons] using hty
 rcases ht with rfl | ht
 · exact ⟨6,4,root_checks D N ha ct hct⟩
 · obtain ⟨i,hi,rfl⟩ := List.mem_map.mp ht
   have hi' := List.mem_range.mp hi
   exact ⟨6,4,row_checks D N (N-i) (by omega) (by omega) ct hct⟩


/-- The OUTER function domain rejects any member occurrence anywhere in the
    grammar expression, without inspecting its internal polarity. -/
theorem negative_field (D : Domain) (N fuel d : Nat) (hd : D.hasSelf=true) :
 Official.checkPositivity (positiveOracle D N) fuel d
  (arr D.official (Tree2TowerOfficial.R N N)) =
 .error (if fuel=0 then .notImplemented "official spec: positivity fuel"
  else .invalid "official: non positive occurrence of the datatypes being declared") := by
 cases fuel with
 | zero => rfl
 | succ f =>
  rw [Official.checkPositivity]
  rw [show (positiveOracle D N).whnf d (arr D.official (Tree2TowerOfficial.R N N))=.ok _
   from official_whnf_pi _ _ _ d]
  have ho : (positiveOracle D N).occ D.official=true := (domain_occ D N).trans hd
  have ht : (positiveOracle D N).occ (arr D.official (Tree2TowerOfficial.R N N))=true := by
   change D.official.nestOcc (positiveOracle D N).names 0 0 ||
    (Tree2TowerOfficial.R N N).nestOcc (positiveOracle D N).names 0 0=true
   change D.official.nestOcc (positiveOracle D N).names 0 0=true at ho
   rw [ho]; rfl
  change (if !(positiveOracle D N).occ (arr D.official (Tree2TowerOfficial.R N N))
   then Except.ok () else if (positiveOracle D N).occ D.official
   then Except.error (.invalid "official: non positive occurrence of the datatypes being declared")
   else Official.checkPositivity (positiveOracle D N) f (d+1)
    ((Tree2TowerOfficial.R N N).instantiate1 (.fvar d D.official)))= _
  rw [ht,ho]
  rfl

theorem negative_ctor (D : Domain) (N fuel nb : Nat) (hd : D.hasSelf=true) :
 Official.checkCtorPos (positiveOracle D N) Tn fuel nb 2
  (arr (arr D.official (Tree2TowerOfficial.R N N)) tr) ≠ .ok () := by
 cases nb with
 | zero => intro h; cases h
 | succ nb =>
  change ((Official.checkPositivity (positiveOracle D N) fuel 2
    (arr D.official (Tree2TowerOfficial.R N N))) >>= fun _ =>
     Official.checkCtorPos (positiveOracle D N) Tn fuel nb 3 tr) ≠ .ok ()
  rw [negative_field D N fuel 2 hd]
  cases fuel <;> (intro h; cases h)

/-- Actual official acceptance yields the grammar admissibility certificate.
    No native derivation or assumed reducer facts occur in the premises. -/
theorem acceptance_domain (D : Domain) (N : Nat)
 (ha : Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (officialWhnf N) 2) : D.hasSelf=false := by
 by_cases hf : D.hasSelf=false
 · exact hf
 · have ht : D.hasSelf=true := by cases hh : D.hasSelf <;> simp_all
   have hc := Tree2EliminationDeterminism.acceptance_at_exact_output
    _ _ _ _ _ _ (lowering D N) ha
   have hm : Tree2DomainSchema.rootRow D N ∈
    (Tree2DomainSchema.target D N).types.toList := List.mem_cons_self
   have hn : arr (arr D.official (Tree2TowerOfficial.R N N)) tr ∈
    (Tree2DomainSchema.rootRow D N).ctors := List.mem_cons_of_mem _ List.mem_cons_self
   obtain ⟨fuel,nb,hcheck⟩ := hc _ hm _ hn
   exact False.elim (negative_ctor D N fuel nb ht hcheck)

/-- Infinite-domain and infinite-depth, nonvacuous official admissibility classification. -/
theorem acceptance_iff (D : Domain) (N : Nat) :
 Official.OfficialPosAccepts (Tree2DomainSchema.context D N)
  (Tree2DomainSchema.declaration D N) (officialWhnf N) 2 ↔ D.hasSelf=false :=
 ⟨acceptance_domain D N,positive_acceptance D N⟩

#print axioms negative_field
#print axioms negative_ctor
#print axioms acceptance_domain
#print axioms acceptance_iff

#print axioms lowering
#print axioms positive_acceptance
end Tree2DomainOfficial
