# Proposed title

fix: reconstruct imported inductive recursor types

# Proposed body

Stop trusting serialized recursor signatures while importing inductive blocks.

This change stages the current block without exposing its supplied recursors,
reconstructs complete ordinary, mutual, and nested recursor types from the
checked inductive types and constructors, compares the closed supplied types
with positional universe alpha-renaming and Kiota definitional equality, and
installs only reconstructed signatures. Any inference, restoration, or
conversion failure rejects the block and restores the previous environment.

The reconstruction covers:

- Lean-compatible elimination-universe, motive, minor, index, major, and result
  ordering;
- recursive hypotheses for dependent and higher-order recursive fields;
- breadth-first nested-specialization discovery and restored auxiliary
  recursor ordering;
- exact reconstructed motive/minor counts, `k`, universes, and current-group
  metadata;
- fail-closed recursive-target matching, including reducible wrappers; and
- atomic rollback of types, constructors, recursors, and ownership/group maps.

Regression coverage keeps the inherited negative/control bytes unchanged and
adds ordinary indexed, two-specialization nested, deep parametric nested, and
mutual-plus-nested cases. One older synthetic `nested-list-tree` fixture remains
byte-for-byte unchanged but is now expected to reject: it declares `List` and
`Tree` in `Type` while supplying Prop-only dummy recursors with no fresh
elimination universe, computation rules, or nested auxiliary recursor.

Validation on Kiota `9fa2c297dd700fe8fd1712a86bdbb258e1c01c42` with Rust
1.98.0, offline and locked:

- build-only test compilation: passed;
- focused reconstruction tests: 7 passed, 70 filtered out;
- candidate/control and four preservation cells: all matched their bound
  reject/accept expectations;
- complete suite: 83 unit and 77 integration tests passed (160 total), with
  zero failures or ignored tests.

The patch is source-bound to the pinned Kiota APIs and does not claim a
universal serialized-format rule or complete checker soundness.
