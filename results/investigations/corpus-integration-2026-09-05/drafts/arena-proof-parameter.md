# Add an `either` characterization pair for proof-parameter order

Prepared locally; publication requires explicit approval for `leanprover/lean-kernel-arena`.

This pair characterizes an ordinary inductive whose parameters include `(P : Prop) (p q : P)`. The candidate swaps `p` and `q` in the inductive application. The complete recursor and declaration metadata remain present, but the edited expression nodes are shared into the recursor motive domain and rule annotation. The control is unchanged.

Pinned official Lean 4.33.0 accepts the control and rejects the candidate. Kiota `2d2a9fa` accepts both because its constructor-result check uses definitional equality, which recognizes proof irrelevance here. No qualified source reviewed by this project establishes a universal rejection obligation.

Proposed outcomes: control `accept`, candidate `either`. This preserves the implementation-profile difference while excluding the unsettled candidate from completeness and soundness scoring. The current Arena harness at `abc55357` successfully materializes both static files. Arena's existing nested-nonuniform case uses a `W`-valued constant in a nested occurrence; it is useful context but not an exact duplicate or normative precedent.
