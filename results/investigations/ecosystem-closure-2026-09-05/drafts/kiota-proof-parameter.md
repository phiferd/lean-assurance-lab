# Review constructor-result proof-parameter uniformity

Prepared locally; publication requires explicit approval for sankalpsthakur/kiota.

At Kiota main `2d2a9fa31cba31abdd49543c3bb667591207577e`, the default checker accepts both the unchanged control and the export swapping `(p q : P)` to `(q p)` in the constructor result. The original complete recursor is retained. The pinned official Lean observer accepts the control and rejects the candidate with `invalid return type for LALProofParameterSwap.mk`.

Exact artifacts: `corpus/generated/lal-ordinary-inductive-proof-parameter-{control,candidate}.ndjson`. Raw outputs, binary hashes, revision, build log and four-launch budget: `results/investigations/ecosystem-closure-2026-09-05/proof-parameter-current/result.json`. The completed run manifest is `config/authorized-runs/proof-pair.json`; its run ID must not be recycled. For an independently authorized reproduction, invoke the built Kiota binary on each named NDJSON file as its sole argument, with `KIOTA_*` variables unset. Exit 0 records acceptance; the paired raw evidence retains the exact official command inputs and rejection diagnostic.

The read-only issue inventory includes merged PR #8's broad hardening work; its description does not identify this exact proof-parameter swap. The disagreement persists after that merge. Proof irrelevance can make the swapped proofs definitionally equal. This is a request to clarify the intended inductive-formation contract and add a focused regression if that contract requires exact parameter order. It is not a demonstrated proof of False or an assertion that observer agreement is semantic authority.
