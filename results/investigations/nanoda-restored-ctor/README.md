# Nanoda Restored-Constructor Metadata Search

Mutant: `nanoda-gen-a59d7fa2cfb3`

The mutation skips `old_ctor.aux_data_ck(&new_ctor)` in
`check_restored_ctor1` at `src/inductive.rs:1736`. The comparison checks the
constructor name, parent inductive, constructor index, parameter count, and
field count. Constructor type equality is checked separately afterward.

The source-derived candidate reuses the accepted 105-record
`LALWrap`/`LALNest` nested-inductive seed and changes only the exported
`LALNest.node` constructor index from `0` to `1`:

- control: `corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-control.ndjson`
- witness: `corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-ctor-index.ndjson`
- differential: `ctor-index-reproduction.json`

The first candidate kills the mutant. The test passes without the mutation and
fails with it: baseline Nanoda rejects at `src/inductive.rs:1736`, while mutant
Nanoda accepts. The unchanged control passes both builds.

Official Lean establishes `REJECT` and Lean4Lean confirms it. Kiota accepts,
matching the restored-recursor `k` and type disagreements. These cases should
be discussed as one restored nested declaration-validation gap rather than
filed as separate field-level issues.
