# Proposed title

test: cover reserved nested namespace traversal and declaration guards

# Proposed body

Add six tests for the reserved `_nested` namespace checks. Existing prefix tests
cover root-name extraction; these additions exercise detection through every
name-bearing expression position and its use during inductive checking.

Paired expressions distinguish `_nested` from the similar `_nestedX` root.
Additional controls cover hierarchical and numeric names, ignored binder names,
and repeated DAG nodes. The declaration tests reuse the complete `PUnit` portion
of the existing `ProjFromProp` fixture: the unchanged declaration must pass, and
in-memory reserved constants in its type or constructor type must produce the
exact corresponding namespace assertion. A later missing-declaration or type
panic cannot satisfy those checks.

This is a test-only change. Serialized fixtures and production code are unchanged.
It protects an existing implementation safety check and makes no current-defect
or universal Lean acceptance-policy claim. Mutual-peer guard isolation is outside
this patch.

Validation on Nanoda `4c544ed4099c8227f07d5de77ad1e69fb0740a27`:

- `cargo test --offline --locked nested -- --nocapture`: 6 passed.
- `cargo test --offline --locked -- --nocapture`: all 44 library tests passed;
  the binary suite has no tests and eight existing doc examples remain ignored.
