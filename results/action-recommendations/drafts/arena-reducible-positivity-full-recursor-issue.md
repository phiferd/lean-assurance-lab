# Add full-recursor reject coverage for reducible-hidden negativity

Arena’s existing `indNegReducible` fixture checks the intended rule, but its
dummy recursor gives checkers another reason to reject and does not isolate the
strict-positivity check.

I derived a full-recursor variant from a valid export. The control constructor
field is `Unit -> I`. The candidate changes the shared domain expression to
`LALConstType Unit I`, where `LALConstType A B := A`. This one shared expression
is used by the constructor, recursor type, and recursor rule, so all serialized
reconstruction metadata remains consistent and the field type is definitionally
unchanged.

Official Lean, Nanoda, Kiota, and Lean4Lean all reject the candidate and accept
the control. A controlled Nanoda mutation omitting only strict positivity
accepts the candidate, confirming that this fixture isolates the intended rule.

Would you accept this as a focused reject test alongside the existing tutorial
case?
