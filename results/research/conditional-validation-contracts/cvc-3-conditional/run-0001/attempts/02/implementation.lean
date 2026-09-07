import Lean4Lean.Verify.Level

-- Generated from the source-reviewed baseline-expectations.json; uncompiled in preparation.
-- The counted baseline prints imported and independently written expected types.
open Lean4Lean
open private isExplicitSubsumedAux from Lean.Level

noncomputable def cvcA7ExpectedIsEquivWf
    (h : Lean.Level.isEquiv' u v)
    (hu : VLevel.ofLevel ls u = some u') (hv : VLevel.ofLevel ls v = some v') : u' ≈ v' :=
  Lean.Level.isEquiv'_wf h hu hv

noncomputable def cvcA7ExpectedIsEquivComplete
    (hu : VLevel.ofLevel ls u = some u') (hv : VLevel.ofLevel ls v = some v') :
    Lean.Level.isEquiv' u v ↔ u' ≈ v' :=
  Lean.Level.isEquiv'_complete hu hv

noncomputable def cvcA7ExpectedPropext {a b : Prop} : (a ↔ b) → a = b := propext

noncomputable def cvcA7ExpectedChoice {α : Sort u} : Nonempty α → α := Classical.choice

noncomputable def cvcA7ExpectedQuotSound {α : Sort u} {r : α → α → Prop} {a b : α}
    : r a b → Quot.mk r a = Quot.mk r b := Quot.sound

noncomputable def cvcA7ExpectedLawfulBEqLevel : LawfulBEq Lean.Level := Lean.Level.instLawfulBEqLevel

noncomputable def cvcA7ExpectedExplicitSubsumed :
    isExplicitSubsumedAux = Lean.Level.Total.isExplicitSubsumedAux :=
  Lean.Level.isExplicitSubsumedAux_eq

noncomputable def cvcA7ExpectedNormalize : Lean.Level.normalize = Lean.Level.Total.normalize :=
  Lean.Level.normalize_eq

noncomputable def cvcA7ExpectedTreeMapAll {α : Type u} {β : Type v}
    {cmp : α → α → Ordering} {t : Std.TreeMap α β cmp} {p : α → β → Bool} :
    t.all p = t.toList.all (fun a => p a.1 a.2) := Std.TreeMap.all_eq_all_toList

set_option pp.universes true
set_option pp.explicit true
set_option pp.fullNames true
set_option pp.all true
#check @Lean.Level.isEquiv'_wf
#check @cvcA7ExpectedIsEquivWf
#check @Lean.Level.isEquiv'_complete
#check @cvcA7ExpectedIsEquivComplete
#check @propext
#check @cvcA7ExpectedPropext
#check @Classical.choice
#check @cvcA7ExpectedChoice
#check @Quot.sound
#check @cvcA7ExpectedQuotSound
#check @Lean.Level.instLawfulBEqLevel
#check @cvcA7ExpectedLawfulBEqLevel
#check @Lean.Level.isExplicitSubsumedAux_eq
#check @cvcA7ExpectedExplicitSubsumed
#check @Lean.Level.normalize_eq
#check @cvcA7ExpectedNormalize
#check @Std.TreeMap.all_eq_all_toList
#check @cvcA7ExpectedTreeMapAll

#print axioms Lean.Level.isEquiv'_wf
#print axioms Lean.Level.isEquiv'_complete
