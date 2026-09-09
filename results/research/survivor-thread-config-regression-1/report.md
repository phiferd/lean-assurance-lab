# Zero-thread declaration-checking regression result

The controlled fixed pair reproduced the source prediction at pinned Nanoda
`6ae1f0cd962f081f6c423454c5da729d841236a7`. Both independently built observers
accepted the exact 601-byte matching control. On the exact 601-byte invalid
candidate, the baseline failed at the bound type-equality assertion and retained
`infer`/`check_declar` attribution, while `nanoda-gen-93b21593b0d8` returned the
exact clean success message.

This is executable evidence that public `num_threads = 0` changes from serial
checking in the baseline to zero-worker check elision in the mutant. It is
strictly scoped to the committed source, mutation, configuration and fixed pair.
It is not a claim about current upstream Nanoda, semantic authority, or the
historical one-thread mutation-testing profile.

Two offline builds and four checker calls completed with process-group cleanup
and immutable raw receipts. Scientific process time was 30.36 seconds; no
network, Lean proof, new export byte, mutation identity or external action was
used. Canonical mutation and survivor state and every modeled mutation metric
remain unchanged because the predecessor already recorded the scoped meaningful
classification while preserving the historical survival result. The generated
assurance snapshot refreshed only its producing repository revision.

The next selected item is a bounded current-upstream readiness assessment. It
may inspect current source and duplicate-report state and prepare a minimal
regression/issue draft, but it may not submit or modify anything upstream.
