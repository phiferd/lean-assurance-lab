# Source-provenance intake

`SOURCE-PROVENANCE-INTAKE-1` is the completed successor to the
source-lock completeness audit. It must not reopen that audit, alter its frozen
22-file inventory, or present a source byte as a checker result.

## Objective

Locate the exact `README.md` byte belonging to repository
`ammkrn/nanoda_lib` at revision `6ae1f0cd962f081f6c423454c5da729d841236a7`,
then record its origin, content hash, license compatibility and relationship to
the existing source lock. A later, separately bound materialization successor
would decide whether that byte may be added to a new source inventory.

## Entry gate

The owner authorized execution on 2026-09-20. Entry required one
read-only provenance intake from the named repository and revision, or an
already-local object that proves the same immutable origin. Before the first
source request, bind the exact source URL or local object identity, revision,
license record, expected path, request budget and a no-substitution rule.

## Scope and stop condition

One 45-active-minute session; at most two local or read-only source requests;
zero Cargo builds, checker processes, proofs, source substitutions, mutation
identities, source-lock edits, external writes or assurance-milestone advances.
Stop after one content-bound intake result, a provenance/availability failure,
or the request cap. The intake cannot compile Nanoda or rerun the child-panic
experiment.

## Outcome

SUCCESS. The canonical response supplied the exact 6517-byte `README.md` with
SHA-256 `4442003879ac4ac7d455df1db16e0c5646652e6c9b44451f5d877345b8ff65d2`.
The historical 22-file lock remains unchanged. A fresh confirmation item binds
this byte separately.
