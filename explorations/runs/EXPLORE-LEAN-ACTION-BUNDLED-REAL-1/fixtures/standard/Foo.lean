theorem standard_prop (p q : Prop) (h : p ↔ q) : p = q := propext h
noncomputable def standard_choice (α : Sort u) (h : Nonempty α) : α := Classical.choice h
theorem standard_quot {α : Sort u} (r : α → α → Prop) (a b : α) (h : r a b) : Quot.mk r a = Quot.mk r b := Quot.sound h
#print axioms standard_prop
#print axioms standard_choice
#print axioms standard_quot
