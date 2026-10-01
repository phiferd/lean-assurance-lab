import Tree2ArrowNative

/- Local AI-authored bounded official-acceptance-to-native bridge. -/
namespace Tree2ArrowBridge
open ConLeche Tree2Bridge Tree2TowerSupport
open Tree2ArrowSchema Tree2ArrowNative
set_option maxRecDepth 3000
set_option maxHeartbeats 2000000
set_option linter.unusedSimpArgs false

private theorem positive_root_ok : NestRootOk (ctx false) := by
 refine ⟨rfl,?_,?_⟩
 · intro x hx
   have he : x = A := by simpa [ctx] using hx
   subst x
   exact ⟨0,S,rfl,by decide⟩
 · intro j hj
   have hj' : j < 1 := hj
   have h0 : j = 0 := by omega
   subst j
   rfl

private theorem leaf_singleton :
 PosDR (checker 16) (env false) (ctx false) 1
 (.ctors [] [] 2 [] [A] [Tn] [X] [(leafCV,1)]) := by
 apply PosDR.ctorsCons (crest := arr A X)
  (ty := .sort (.imax (.succ .zero) (.succ .zero)))
  (sv := .imax (.succ .zero) (.succ .zero))
  (m₁ := 1) (m₂ := 0) (ks := [.ordinary]) (nds := [(A,bm)]) (cur := X)
 · decide
 · exact root_crests.1
 · exact leaf_infer 2 16 (by omega)
 · exact ensure_sort 2 16 2 _ (by omega)
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact ordinary_field 2 16 (by omega)
   · omega
   · exact PosDR.teleNil
 · rfl
 · rfl
 · rfl
 · omega
 · exact PosDR.ctorsNil

private theorem node_singleton :
 PosDR (checker 16) (env false) (ctx false) 4
 (.ctors [] [] 2 [] [A] [Tn] [X] [(node false,1)]) := by
 apply PosDR.ctorsCons (crest := arr (arr A (l (l X))) X)
  (ty := .sort (.imax (.imax (.succ .zero) (.succ .zero)) (.succ .zero)))
  (sv := .imax (.imax (.succ .zero) (.succ .zero)) (.succ .zero))
  (m₁ := 4) (m₂ := 0) (ks := [.nested true])
  (nds := [(arr A (l (l X)),bm)]) (cur := X)
 · rfl
 · exact node_crest false
 · exact function_crest_infer
 · exact ensure_sort 2 16 2 _ (by omega)
 · omega
 · apply PosDR.teleCons (m₁ := 4) (m₃ := 0)
   · omega
   · exact function_field
   · omega
   · exact PosDR.teleNil
 · exact node_u4 (arr A (l (l X))) (.nested true)
 · rfl
 · rfl
 · omega
 · exact PosDR.ctorsNil

/-- One common bound is safe for this bounded depth2 family, but the actual
    singleton obligations remain leaf1/node4; no all-depth common-bound claim. -/
private theorem positive_derivation :
 PosDR (checker 16) (env false) (ctx false) 4
 (.ctors [] [] 2 [] [A] [Tn] [X] (roots false)) := by
 apply PosDR.ctorsCons (crest := arr A X)
  (ty := .sort (.imax (.succ .zero) (.succ .zero)))
  (sv := .imax (.succ .zero) (.succ .zero))
  (m₁ := 1) (m₂ := 4) (ks := [.ordinary]) (nds := [(A,bm)]) (cur := X)
 · decide
 · exact root_crests.1
 · exact leaf_infer 2 16 (by omega)
 · exact ensure_sort 2 16 2 _ (by omega)
 · omega
 · apply PosDR.teleCons (m₁ := 1) (m₃ := 0)
   · omega
   · exact ordinary_field 2 16 (by omega)
   · omega
   · exact PosDR.teleNil
 · rfl
 · rfl
 · rfl
 · omega
 · exact node_singleton

private theorem walk_budget (e : Expr) : 4 ≤ whnfWalkFuel e := by
 unfold whnfWalkFuel fuelSlack
 omega

private theorem positive_success :
 ∃ r, nestedBlockPositivity (checker 16) (env false) (ctx false) [roots false] = .ok r := by
 apply nestedBlockPositivity_complete positive_root_ok (show nestHoles (ctx false) = some [X] from rfl)
 · intro cs hcs cv hcv
   have he : cs = roots false := by simpa using hcs
   subst cs
   have hv : cv = (leafCV,1) ∨ cv = (node false,1) := by simpa [roots] using hcv
   rcases hv with rfl | rfl <;> cbv
 · intro cs hcs
   have he : cs = roots false := by simpa using hcs
   subst cs
   exact ⟨4,by intro x hx crest hc; exact walk_budget crest,positive_derivation⟩

/-- Acceptance is consumed to infer the parameter domain; every native
    schema/typing/frame/sideguard/budget fact is proved in the fixed instance. -/
theorem acceptance_bridge (bad : Bool)
 (ha : Official.OfficialPosAccepts (context bad) (declaration bad) officialWhnf 2) :
 bad = false ∧
 PosDR (checker 16) (env bad) (ctx bad) 4
  (.ctors [] [] 2 [] [A] [Tn] [X] (roots bad)) ∧
 (∃ r, nestedBlockPositivity (checker 16) (env bad) (ctx bad) [roots bad] = .ok r) := by
 have hd := acceptance_domain bad ha
 subst bad
 exact ⟨rfl,positive_derivation,positive_success⟩

/-- Positive and negative controls plus the acceptance-driven bridge, all in
    the actual explicit fixed environments, with no unproved converter input. -/
theorem bounded_completeness :
 Official.OfficialPosAccepts (context false) (declaration false) officialWhnf 2 ∧
 ¬ Official.OfficialPosAccepts (context true) (declaration true) officialWhnf 2 ∧
 (∀ bad, Official.OfficialPosAccepts (context bad) (declaration bad) officialWhnf 2 →
  bad = false ∧
  PosDR (checker 16) (env bad) (ctx bad) 4
   (.ctors [] [] 2 [] [A] [Tn] [X] (roots bad)) ∧
  ∃ r, nestedBlockPositivity (checker 16) (env bad) (ctx bad) [roots bad] = .ok r) := by
 refine ⟨positive_acceptance,?_,acceptance_bridge⟩
 intro ha
 have h := acceptance_domain true ha
 cases h

#print axioms leaf_singleton
#print axioms node_singleton
#print axioms positive_success
#print axioms acceptance_bridge
#print axioms bounded_completeness
end Tree2ArrowBridge
