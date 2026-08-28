# Nanoda Restored-Recursor Witness

Mutant: `nanoda-gen-8237cd6d3cb2`

The mutation skips `original.aux_data_ck(&restored)` while checking restored
nested recursors at `src/inductive.rs:1687`.

## Coverage Refresh

The first audit attempt on 2026-08-27 stopped before executing tests because
the saved coverage source digest was stale. The baseline inventory was also
missing the newly built `definition-self-reference` test. Nanoda was run on
that case, its `REJECT` result was added through the normal Arena result
normalizer, and the exact built-test inventory check passed with 198 records.

The portable coverage collector then reused 197 records and collected the new
case. The refreshed snapshot contains 198 tests, uses repository-relative
source locations, and passed the `proj-of-prop` sentinel.

## Scheduled Comparison

The refreshed line-coverage schedule selected all nine tests covering
`src/inductive.rs:1687`. The run completed all nine with zero normalized
outcome differences and recorded `ALL_COVERING_TESTS_MATCH`:

`results/mutants/nanoda-gen-8237cd6d3cb2/scheduled-runs/20260827T154902Z/comparison.json`

The runner restored and rebuilt the baseline checker after the comparison.

## Status

The mutant survives the current 198-test corpus, but a source-derived test now
kills it. Starting from a valid 105-record nested-inductive export, the witness
changes only the restored auxiliary recursor's serialized `k` field from
`false` to `true`:

- control: `corpus/generated/nanoda-gen-8237cd6d3cb2-valid-control.ndjson`
- witness: `corpus/generated/nanoda-gen-8237cd6d3cb2-valid-aux-k.ndjson`
- differential: `valid-aux-k-reproduction.json`

The test passes without the mutation and fails with it: baseline Nanoda rejects
at `src/inductive.rs:1687`, while mutant Nanoda accepts. The byte-identical
control export is accepted by both builds.

Official Lean establishes `REJECT` as the exact expected outcome, and Lean4Lean
also rejects. Kiota accepts the witness, so that checker disagreement remains
explicit in
`results/cross-validation/nanoda-gen-8237cd6d3cb2-restored-aux-k/results.json`.
It does not invalidate the mutation kill and must not be resolved by majority
vote.
