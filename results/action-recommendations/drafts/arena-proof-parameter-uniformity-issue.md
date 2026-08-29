# Add reject coverage for swapped proof parameters in a constructor result

I found a narrow inductive-formation boundary that the existing malformed
constructor-result fixture does not isolate because that fixture uses a dummy
recursor.

Starting from a valid exported inductive with parameters
`(P : Prop) (p q : P)`, change only the constructor result from the inductive
applied to `P p q` to the same inductive applied to `P q p`. Keep the complete
exporter-generated recursor and rule unchanged.

Official Lean and Lean4Lean reject this artifact, and Nanoda rejects it at its
exact constructor-result parameter check. Kiota accepts it. All checkers accept
the unchanged control.

This makes a useful reject test because proof irrelevance allows later
definitional-equality checks to identify `p` and `q`; the fixture therefore
isolates the requirement that constructor result parameters are the original
variables in their original order.
