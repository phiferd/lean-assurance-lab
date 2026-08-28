# Arena good tests 094 and 095 are rejected on the current arena branch

The current Lean4Lean `arena` branch rejects Lean Kernel Arena tutorial good
tests `094_projMaybeProp` and `095_projMaybePropPast`. Official Lean and Kiota
accept both cases. All tested checkers reject the related definite-`Prop` data
projection, and all accept a structure-matched non-projection control.

Current-head reproduction:

- Lean4Lean arena revision: `bce3448115f7819fc12d647fadd3bb090666637e`
- `projection-maybe-prop.ndjson`: `REJECT`
- `projection-maybe-prop-past.ndjson`: `REJECT`
- matched non-projection control: `ACCEPT`

Arena explains why the possibly-`Prop` projections are valid in
`tutorial/Tutorial.lean` next to tests 094 and 095. The field universe bound is
preserved at every instantiation where the structure becomes a proposition.

Artifacts and current-head results:

- https://github.com/phiferd/lean-assurance-lab/tree/main/corpus/generated
- https://github.com/phiferd/lean-assurance-lab/tree/main/results/investigations/upstream-action-preflight
- https://github.com/phiferd/lean-assurance-lab/blob/main/results/investigations/nanoda-projection-typing-contract-matrix.md

Would Lean4Lean be interested in supporting these existing Arena good tests?
This appears to be an over-rejection/compatibility gap, not an acceptance or
soundness report.
