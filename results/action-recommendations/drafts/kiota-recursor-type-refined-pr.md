# Proposed title

fix: reconstruct imported inductive recursor types

# Proposed body

Kiota checks the shape of imported recursor signatures but stores their supplied
types without fully reconstructing them. A malformed signature can therefore
pass import validation and be used to type later declarations.

The regression changes `LALNest.rec_1`'s fifth argument type from
`LALWrap LALNest` to `LALNest` while preserving its argument count. At Kiota
`9fa2c297`, the malformed export is accepted; official Lean 4.33.0 rejects it.
A subsequent application also demonstrates that Kiota uses the incorrect
argument type. Rejecting the signature at import
closes this validation gap before other declarations can depend on it.

This change reconstructs ordinary, mutual, and nested recursor signatures from
the checked inductive types and constructors. Supplied signatures must match up
to positional universe renaming and definitional equality; only reconstructed
signatures enter the environment. Failed imports undo the current block's writes
without copying earlier declarations. The existing policy of ignoring supplied
`k` flags and recomputing K status is preserved.

The construction lives in `src/tc/recursor.rs`, with links to the corresponding
Lean 4.33.0 algorithm and an explanation of nested specialization and binder
ordering. Tests cover the original malformed/valid pair, ordinary and nested
imports, universe renaming and invalid parameters, convertible signatures,
recomputed K status, and rollback that preserves previous declarations.

One existing synthetic fixture is renamed from `nested-list-tree.accept.ndjson`
to `.reject.ndjson`, with identical content. Its Type-valued inductives have
incomplete Prop-only recursors, including a missing nested auxiliary recursor.
The real-export nested acceptance tests remain in place.

Validation against `9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`:

```sh
cargo test --offline --locked --test exports recursor_type_reconstruction
cargo test --offline --locked
```

Both commands pass with Rust 1.98.0: 15 focused tests and the full suite of
83 unit plus 85 integration tests (168 total), with no failures or ignored
tests. The malformed signature rejects; its unchanged valid control and four
ordinary/mutual/nested acceptance cases accept.
