# Consider a paired constructor-result proof-parameter fixture

Prepared locally; publication requires explicit approval for leanprover/lean-kernel-arena.

Propose the exact control/candidate pair in `corpus/generated/lal-ordinary-inductive-proof-parameter-{control,candidate}.ndjson`: swap the two proof parameters only in the constructor result, retaining the complete recursor. Current Kiota `2d2a9fa` accepts both; the pinned official observer accepts the control and rejects the candidate. Full binary/input/raw evidence is in the successor decision packet.

The current Arena `nested-nonuniform-param` test uses a Bool-valued constant in a nested occurrence, not two proof variables in an ordinary constructor result. Its `either` policy is relevant context, not authority for this different case. No exact duplicate was identified in the bounded issue/tree review. Before submission, package against the current Arena export toolchain and verify integration; agree the outcome with maintainers instead of silently assuming a universal reject contract. This proposal is deferred until that local integration and expected-semantics review is complete.
