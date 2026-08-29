# Constructor result parameter uniformity can be bypassed for proof parameters

Hi, I found a small inductive-declaration disagreement while testing exact
constructor result parameters.

The artifact declares an inductive with parameters `(P : Prop) (p q : P)`.
Its constructor returns the same inductive with `p` and `q` swapped. The export
is derived from a valid Lean export by changing only those two constructor
result argument references; the original recursor metadata and rule remain.

Official Lean and Lean4Lean reject the candidate, while Kiota accepts it. All
three accept the unchanged control. I also reproduced the acceptance on Kiota
main at `686063c13b22ce379c05dfe7fc03656655ac60e5`.

The subtlety appears to be proof irrelevance: later definitional equality can
identify `p` and `q`, but Lean's inductive formation rule still requires the
constructor result parameters to be the original parameter variables in their
original order.

Would a focused reject fixture or a patch adding an exact constructor-result
parameter check be useful here? I can prepare either form.
