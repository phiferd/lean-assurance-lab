# Prelaunch input review — 2026-11-09

**What did we find?** Six raw, closed, one-definition inputs match the fixed
three-position sample. In each pair, the negative changes only the argument
index in one application node. No checker observation was made for this review.

**Is it interesting?** Yes. `Sort 0 : Sort 1`, while `Sort 1 : Sort 2`, so the
negative's argument fails the lambda's `Sort 1` domain even though beta
reduction discards it. This is a typing precondition that a final semantic
comparison alone cannot establish.

**Does it require more work?** Yes. Run the twelve fixed checked-definition
cells and classify their raw outputs; this review is an input gate only.

The task-local `audit.py` independently decodes all six 3.1.0 streams and
asserts exact syntax trees, metadata, one ordinary definition, no universe
parameters, the three single-field paired edits, and Nanoda configuration.
It completed with `PASS` before trial start. The only expression constructors
are sort, lambda, application and Pi. There are no constants, axioms, recursors,
metavariables or free variables. The definition name differs by placement, not
by validity within a pair.

The pinned Lean `type_checker.cpp` checked `infer_app` infers the argument then
compares its type to the function domain before substitution. The pinned
Nanoda `tc.rs` `infer_app` similarly infers the argument under `Check` and
asserts domain equality. These are source observations, not a runtime result.
The raw importer prints parsed name, parameters, type and value before the
trust-0 empty-environment replay. Nanoda's parser was reviewed at the retained
source revision; no independent Nanoda AST trace is claimed. All runtime
hashes in `protocol.json` were matched inside the isolated container before
launch. The container has no attached network, a 12 GiB limit, four CPUs and
512 PID limit. Guest checker output and host supervision remain to be measured.

The earlier Nat-based scope sketch is replaced prospectively because this
replay has no Nat declarations. No Nat or imported library case has run under
this trial identity. The six sort-only controls and negatives retain the fixed
V/T/B placement question. This avoids overlap with the completed symbolic
universe screen, merged-Lean eta replay and historical recursor audit.
