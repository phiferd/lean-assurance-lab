# Nanoda Restored-Recursor Type Search

Mutant: `nanoda-gen-7b603be7dc87`

The mutation skips
`self.assert_def_eq(original.info.ty, restored.info.ty)` in
`check_restored_recursor1` at `src/inductive.rs:1689`.

The source-derived search reuses the valid 105-record `LALWrap`/`LALNest`
nested-inductive seed. Its nested block contains a restored auxiliary recursor
and a base recursor, both with independently well-formed serialized types. The
first candidate changes only the auxiliary recursor's `type` expression ID from
its original type to the base recursor's type expression ID. This preserves
parseability and standalone type formation while making the exported auxiliary
recursor type disagree with Nanoda's reconstruction.

## Result

The first candidate kills the mutant. It changes only the restored auxiliary
recursor's `type` expression ID from `49` to `68`, the independently well-formed
type of the base recursor in the same nested block:

- control: `corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson`
- witness: `corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson`
- differential: `aux-type-reproduction.json`

The test passes without the mutation and fails with it: baseline Nanoda rejects
the type mismatch, while mutant Nanoda accepts. The unchanged control passes
both builds.

Official Lean establishes `REJECT` and Lean4Lean confirms it. Kiota accepts the
witness, reproducing the same broad restored-recursor validation disagreement
seen for the adjacent `k` metadata witness. The cross-validation record
preserves that disagreement without majority voting.
