import ConLeche.Complete.OfficialNested

/- Local AI-authored model lemma; no external submission. -/
namespace Tree2EliminationDeterminism
open ConLeche ConLeche.Official
set_option maxRecDepth 10000
set_option maxHeartbeats 2000000

/-- Increasing queue fuel preserves every successful result, in any context. -/
theorem loop_success_mono (c : ElimCtx) (fuel more q : Nat)
    (st out : ElimSt) (hf : fuel ≤ more)
    (h : (elimLoop c fuel q).run st = .ok ((),out)) :
    (elimLoop c more q).run st = .ok ((),out) := by
  induction fuel generalizing more q st out with
  | zero => cases h
  | succ f ih =>
    cases more with
    | zero => omega
    | succ m =>
      have hm : f ≤ m := by omega
      dsimp only [elimLoop,StateT.run,bind,StateT.bind,get,getThe,
        MonadStateOf.get,StateT.get,pure,StateT.pure,Except.bind,Except.pure] at h ⊢
      cases ht : st.types[q]? with
      | none => simpa only [ht] using h
      | some t =>
        rw [ht] at h
        dsimp only [StateT.bind,bind,Except.bind] at h ⊢
        cases hc : t.ctors.mapM (replaceAll c) st with
        | error err => rw [hc] at h; cases h
        | ok value =>
          rcases value with ⟨cs,st1⟩
          rw [hc] at h
          dsimp only [modify,modifyGet,MonadStateOf.modifyGet,StateT.modifyGet,
            StateT.bind,pure,Except.pure,bind,Except.bind] at h ⊢
          exact ih m (q+1) _ out hm h

/-- Queue execution has one successful output, regardless of sufficient fuel. -/
theorem loop_success_unique (c : ElimCtx) (f g q : Nat)
    (st a b : ElimSt)
    (ha : (elimLoop c f q).run st = .ok ((),a))
    (hb : (elimLoop c g q).run st = .ok ((),b)) : a = b := by
  have hfa := loop_success_mono c f (max f g) q st a (Nat.le_max_left _ _) ha
  have hgb := loop_success_mono c g (max f g) q st b (Nat.le_max_right _ _) hb
  have he : ((),a) = ((),b) := Except.ok.inj (hfa.symm.trans hgb)
  exact congrArg Prod.snd he

/-- Successful declaration lowering is preserved by increasing queue fuel. -/
theorem lowering_success_mono (c : ElimCtx) (decl : List MemberDecl)
    (f g : Nat) (out : ElimSt) (hf : f ≤ g)
    (h : elimNested c decl f = .ok out) :
    elimNested c decl g = .ok out := by
  unfold elimNested at h ⊢
  cases ht : decl.mapM (fun d => do
    let ty ← instPiParams d.type c.ps
    let cs ← d.ctors.mapM (fun t => instPiParams t c.ps)
    pure (⟨d.name,ty,cs⟩ : AuxType)) with
  | error err => rw [ht] at h; cases h
  | ok types =>
    rw [ht] at h
    dsimp only [bind,Except.bind,pure,Except.pure] at h ⊢
    cases hl : (elimLoop c f 0).run {types := types.toArray} with
    | error err => rw [hl] at h; cases h
    | ok value =>
      rcases value with ⟨u,st⟩
      cases u
      rw [hl] at h
      dsimp only [Except.bind,Except.pure] at h
      have hs : st = out := Except.ok.inj h
      subst st
      rw [loop_success_mono c f g 0 _ out hf hl]
      rfl

/-- Acceptance cannot choose a different successful eliminated state by fuel. -/
theorem lowering_success_unique (c : ElimCtx) (decl : List MemberDecl)
    (f g : Nat) (a b : ElimSt)
    (ha : elimNested c decl f = .ok a)
    (hb : elimNested c decl g = .ok b) : a = b := by
  have hfa := lowering_success_mono c decl f (max f g) a (Nat.le_max_left _ _) ha
  have hgb := lowering_success_mono c decl g (max f g) b (Nat.le_max_right _ _) hb
  exact Except.ok.inj (hfa.symm.trans hgb)

/-- Extract positivity checks at a separately PROVED exact lowered state.
    The exact-output equation is a prerequisite, not a conversion assumption. -/
theorem acceptance_at_exact_output (c : ElimCtx) (decl : List MemberDecl)
    (w : Nat → Expr → Except CheckError Expr) (base f : Nat) (st : ElimSt)
    (he : elimNested c decl f = .ok st)
    (ha : OfficialPosAccepts c decl w base) :
    ∀ t ∈ st.types.toList, ∀ ct ∈ t.ctors, ∃ fuel nb,
      checkCtorPos (st.oracle c w) t.name fuel nb base ct = .ok () := by
  rcases ha with ⟨g,out,hout,hchecks⟩
  have hs := lowering_success_unique c decl g f out st hout he
  subst out
  exact hchecks

#print axioms lowering_success_mono
#print axioms lowering_success_unique
#print axioms acceptance_at_exact_output

#print axioms loop_success_mono
#print axioms loop_success_unique
end Tree2EliminationDeterminism
