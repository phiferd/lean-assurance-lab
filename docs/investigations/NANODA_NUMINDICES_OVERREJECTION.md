# Nanoda Rejects Reference-Accepted Nested `numIndices` Metadata

Status: `CURRENT_UPSTREAM_DISAGREEMENT`

## Summary

A structure-aware mutation of Arena's accepted `nested-nonuniform-param`
artifact increments the exported nested type's `numIndices` field from zero to
one without changing its expression graph. Pinned official Lean 4.33 and
Lean4Lean accept the exact artifact. Arena-pinned Nanoda and current upstream
Nanoda reject it at `old.aux_data_ck(new)` during nested-inductive restoration.

A controlled Nanoda mutant that suppresses only that auxiliary-data assertion
accepts the artifact. This establishes a completeness or over-rejection
difference, not an unsoundness result. The mutant is classified
`REFERENCE_ALIGNED` and excluded from mutation-score denominators.

## Evidence

The witness was found on attempt 20 of a 300-attempt bounded search by:

```text
record-141:numIndices:increment:inductive.types.0.numIndices
```

Exact artifact:
`corpus/minimized/nanoda-gen-82dd1d305bfd-inductive-metadata-20260826-min.ndjson`

SHA-256:
`517f6f49958257594099fd62085c75388aa669d11600d6908af25169228130e7`

Measured outcomes:

| Validator | Artifact | Unchanged control |
| --- | --- | --- |
| Official Lean 4.33 | `ACCEPT` | `ACCEPT` |
| Lean4Lean | `ACCEPT` | `ACCEPT` |
| Arena Nanoda `6ae1f0c` | `REJECT` | `ACCEPT` |
| Upstream Nanoda `0505569` | `REJECT` | `ACCEPT` |
| Controlled Nanoda mutant | `ACCEPT` | not needed |

Kiota rejects the unchanged control and is therefore incompatible for this
case. No majority vote is used; official Lean is the designated reference.

Machine-readable evidence:

- `results/expected-outcomes/nanoda-gen-82dd1d305bfd-inductive-metadata.json`
- `results/cross-validation/nanoda-gen-82dd1d305bfd-inductive-metadata/results.json`
- `results/investigations/nanoda-numindices-overrejection/upstream-main.json`
- `results/witnesses/nanoda-gen-82dd1d305bfd-inductive-metadata-20260826/metadata.json`

## Reproduction

Build the exact upstream revision and run:

```sh
scripts/reproduce-nanoda-numindices-overrejection \
  --nanoda-checkout /path/to/nanoda_lib \
  --upstream-revision 05055695879dfebb6628a67da88ceca6cd6b0421
```

The command passes only when the reference evidence remains bound to the exact
artifact, official Lean and Lean4Lean accept it, current Nanoda rejects it, and
current Nanoda accepts the unchanged seed artifact.

## Scope

This result establishes one exact redundant-metadata disagreement. It does not
show that Nanoda accepts an invalid proof, that all `numIndices` discrepancies
should be ignored, or that the auxiliary-data check should simply be removed.
The appropriate repair may instead validate which serialized metadata is
semantically authoritative and normalize or reject it consistently earlier.
