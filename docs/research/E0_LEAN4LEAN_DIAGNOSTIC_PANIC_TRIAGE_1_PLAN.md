# Lean4Lean error-formatting triage

Evidence class: E0

What did we find? Three intentionally ill-typed targets were rejected, but the
retained Lean4Lean adapter emitted environment-extension panics while printing
each error. This is an incidental diagnostic observation from the completed
six-trial campaign, not an invalid-proof acceptance or current-upstream finding.
Is it interesting? Yes: usable rejection diagnostics help distinguish semantic
rejection from infrastructure failure, and the raw stacks identify a concrete
source route to inspect.
Does it require more work? Select this source-only screen READY and unstarted
to determine whether a small regression or fresh confirmation is worth preparing.

## Fixed question and inputs

Can the exact retained adapter source and its original binary provenance explain
the error-formatting panic and identify a minimal diagnostic regression target?
Use the three original invalid-target fixtures, their official and Lean4Lean raw
receipts, the campaign's baseline, and the exact source/build bindings for those
binaries. Inspect the retained Replay.throwKernelException, environment creation,
message formatting and Arena adapter entry route. Bind every source used before
its interpretation. A nearby checkout without demonstrated binary correspondence
cannot supply a causal claim about the observed executable.

Record one trial start before source observations. No process launch, compilation,
new importer, implementation patch, external lookup/write, or frozen-evidence edit
is authorized. Deterministic source extraction and hash verification are permitted.
Retain all missing-source/version boundaries; do not invent current-tip behavior.

## Classification and completion

SIGNAL means the exact source route supports a concrete diagnostic regression or
separate fresh confirmation proposal. NO_SIGNAL means the complete bound route
shows expected diagnostics and no useful distinct follow-through. INCONCLUSIVE
names missing provenance or unresolved source/formatting behavior. Source judgment
is not semantic authority or causal execution proof. Close with a small retained
source map, a scoped explanation and a concrete recommendation; any confirmation
requires a separate identity, fresh processes and its own gates. Use E0 ledger,
diff and campaign handoff checks, compare other feasible project work once, and
leave the next successor unstarted. No general assurance refresh follows solely
from this screen.
