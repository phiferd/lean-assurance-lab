# Reducible-Hidden Positivity Witness

The valid control defines `LALConstType A B := A` and a recursive inductive
whose constructor field has type `Unit -> LALReduciblePositivity`.

The candidate replaces the shared `Unit` domain expression with
`LALConstType Unit LALReduciblePositivity`. These domains are definitionally
equal, and the changed expression node is shared by the serialized constructor,
recursor type, and recursor rule. The artifact therefore remains internally
consistent after recursor reconstruction.

Baseline Nanoda rejects at `src/inductive.rs:765` with `non-positive
occurrence`; controlled omission `nanoda-0005` accepts. Both builds accept the
control. Official Lean, Kiota, and Lean4Lean all reject the candidate and accept
the control, establishing a clean mutation kill without checker disagreement.

Arena already has a reducible-hidden negative example, but its dummy recursor
causes independent rejection and does not kill this omission mutant. The
recommended action is one Arena reject-test proposal using this full-recursor
artifact. No Nanoda or other implementation issue is recommended because the
unmodified implementations behave as expected.
