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

#print axioms loop_success_mono
#print axioms loop_success_unique
end Tree2EliminationDeterminism
