import Tree2EliminationDeterminism
import Tree2ArrowSchema

/- Local AI-authored applications; no native completeness claim for all depths. -/
namespace Tree2EliminationConsumers
open ConLeche Tree2Bridge Tree2TowerSupport

/-- Every List-tower depth: actual acceptance checks the independently proved
    exact target. No assumed exact output or native derivation premise. -/
theorem tower_acceptance_at_target (N base : Nat)
    (w : Nat → Expr → Except CheckError Expr)
    (ha : Official.OfficialPosAccepts (Tree2TowerOfficial.context N)
      (Tree2TowerOfficial.declaration N) w base) :
    ∀ t ∈ (Tree2TowerOfficial.target N).types.toList, ∀ ct ∈ t.ctors,
      ∃ fuel nb, Official.checkCtorPos
        ((Tree2TowerOfficial.target N).oracle (Tree2TowerOfficial.context N) w)
        t.name fuel nb base ct = .ok () := by
  exact Tree2EliminationDeterminism.acceptance_at_exact_output _ _ _ _ _ _
    (Tree2TowerOfficial.official_lowering_family N) ha

/-- The function-field domain restriction uses generic successful-run uniqueness,
    with the actual finite schema and reducer; no enumerated fuel argument. -/
theorem arrow_acceptance_domain (bad : Bool)
    (ha : Official.OfficialPosAccepts (Tree2ArrowSchema.context bad)
      (Tree2ArrowSchema.declaration bad) Tree2ArrowSchema.officialWhnf 2) :
    bad = false := by
  cases bad with
  | false => rfl
  | true =>
    have hc := Tree2EliminationDeterminism.acceptance_at_exact_output _ _ _ _ _ _
      (Tree2ArrowSchema.lowering true) ha
    have ht : (Tree2ArrowSchema.target true).types[0] ∈
      (Tree2ArrowSchema.target true).types.toList := List.mem_cons_self
    have hn : arr (arr Tree2TowerOfficial.tr (Tree2TowerOfficial.R 2 2))
      Tree2TowerOfficial.tr ∈ ((Tree2ArrowSchema.target true).types[0]).ctors :=
      List.mem_cons_of_mem _ List.mem_cons_self
    obtain ⟨f,nb,h⟩ := hc _ ht _ hn
    exact False.elim (Tree2ArrowSchema.negative_ctor f nb h)

#print axioms tower_acceptance_at_target
#print axioms arrow_acceptance_domain
end Tree2EliminationConsumers
