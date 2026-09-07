import Contract

open Lab.CVC2 Lean4Lean

-- Named parameter lookup agrees with the positional valuation after encoding.
theorem Lab.CVC2.lookup (ps : List String) (n : String) (ρ : String → Nat)
    (h : n ∈ ps) :
    (ps.map ρ).getD ((names ps).idxOf (.str .anonymous n)) 0 = ρ n := by
  induction ps with
  | nil => simp at h
  | cons a ps ih =>
    by_cases e : a = n
    · subst a
      simp [names, List.idxOf_cons]
    · have hn : n ∈ ps := by simpa [e, Ne.symm e] using h
      simpa [names, List.idxOf_cons, e, Ne.symm e] using ih hn

theorem Lab.CVC2.encoding_preserves : Lab.CVC2.EncodingTarget := by
  intro ps u _ ho
  induction u with
  | zero => exact ⟨.zero, rfl, True.intro, fun _ => rfl⟩
  | succ u ih =>
    obtain ⟨v, hv, hw, he⟩ := ih ho
    refine ⟨.succ v, ?_, hw, ?_⟩
    · simp [encode, VLevel.ofLevel, hv]
    · intro ρ; simp [VLevel.eval, meaning, he]
  | max u w ihu ihw =>
    obtain ⟨v, hv, hw, he⟩ := ihu ho.1
    obtain ⟨z, hz, hzw, hze⟩ := ihw ho.2
    refine ⟨.max v z, ?_, ⟨hw, hzw⟩, ?_⟩
    · simp [encode, VLevel.ofLevel, hv, hz]
    · intro ρ; simp [VLevel.eval, meaning, he, hze]
  | imax u w ihu ihw =>
    obtain ⟨v, hv, hw, he⟩ := ihu ho.1
    obtain ⟨z, hz, hzw, hze⟩ := ihw ho.2
    refine ⟨.imax v z, ?_, ⟨hw, hzw⟩, ?_⟩
    · simp [encode, VLevel.ofLevel, hv, hz]
    · intro ρ; simp [VLevel.eval, meaning, he, hze, Lean.Nat.imax]
  | param n =>
    have hm : Lean.Name.str .anonymous n ∈ names ps :=
      List.mem_map.mpr ⟨n, ho, rfl⟩
    have hi := List.idxOf_lt_length_of_mem hm
    refine ⟨.param ((names ps).idxOf (.str .anonymous n)), ?_, ?_, ?_⟩
    · simp [encode, VLevel.ofLevel, hi]
    · simpa [VLevel.WF, names] using hi
    · intro ρ; exact lookup ps n ρ ho

theorem Lab.CVC2.preservation : Lab.CVC2.PreservationTarget := by
  intro a ha
  refine ⟨ha.1, ?_⟩
  obtain ⟨v, hv, _, he⟩ := encoding_preserves a.params a.valueLevel ha.1.1 ha.1.2.1
  obtain ⟨t, ht, _, hte⟩ := encoding_preserves a.params a.typeLevel ha.1.1 ha.1.2.2
  have hs : VLevel.ofLevel (names a.params) (.succ (encode a.valueLevel)) =
      some (.succ v) := by simp [VLevel.ofLevel, hv]
  intro ρ
  have eqv := VLevel.equiv_def.mp (Lean.Level.isEquiv'_wf ha.2 hs ht) (a.params.map ρ)
  simpa [VLevel.eval, he, hte] using eqv

theorem Lab.CVC2.required_acceptance : Lab.CVC2.AcceptanceTarget := by
  decide

theorem Lab.CVC2.boundary : Lab.CVC2.BoundaryTarget := by
  refine ⟨by decide, ?_, ?_, by decide, ?_⟩
  · intro h
    have bad := h.2 (fun _ => 1)
    simp [zeroBoundary, meaning] at bad
  · intro h
    have bad := (preservation zeroBoundary h).2 (fun _ => 1)
    simp [zeroBoundary, meaning] at bad
  · intro h
    have bad : ¬ Supported unownedBoundary := by decide
    exact bad h.1
