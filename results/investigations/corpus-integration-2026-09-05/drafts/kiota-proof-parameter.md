# Clarify constructor-result proof-parameter uniformity

Prepared locally; publication requires explicit approval for `sankalpsthakur/kiota`.

At Kiota main `2d2a9fa31cba31abdd49543c3bb667591207577e`, the default checker accepts both the unchanged control and a candidate that swaps `(p q : P)` to `(q p)` in the inductive application. The complete recursor and declaration metadata remain present. The two edited expression nodes are shared, so the swap also changes the recursor motive domain and its annotation in the rule RHS.

Pinned official Lean 4.33.0 accepts the control and rejects the candidate with `invalid return type for LALProofParameterSwap.mk`. Current Kiota checks these constructor-result parameters with `is_def_eq`; its definitional equality recognizes proof irrelevance for proofs of the same proposition. The pair therefore records a concrete policy difference, not a demonstrated proof of `False`.

Exact artifacts are `corpus/generated/lal-ordinary-inductive-proof-parameter-{control,candidate}.ndjson`. Input, binary and raw-output bindings are in `results/investigations/ecosystem-closure-2026-09-05/proof-parameter-current/result.json`. Current Arena static integration succeeds with control `accept` and candidate `either`.

Would you clarify whether Kiota intends conversion or structural parameter identity at this raw inductive-declaration boundary? If structural identity is intended, would a focused regression be useful? The project has not identified a qualified universal contract requiring rejection, so this request deliberately does not allege unsoundness.
