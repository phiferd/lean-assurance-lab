# Supplied and reconstructed declaration metadata — 2026-09-13

`SEMANTIC-IMPORT-CONTRACT-1` completes **SUCCESS for one source-qualified
clarification packet**. Universal metadata obligations remain **UNRESOLVED**.
The result explains four different importer policies and prepares one
[local grouped documentation question](maintainer-question.md), coordinated with
the existing lean4export #48 discussion. No new Kiota defect issue is recommended.
No checker was run and no catalog or authority decision changed.

## What the evidence establishes

The exact [historical replay](historical-observations.json) verifies four pairs,
each differing at one scalar while preserving all name/expression nodes:
`LALNest.rec_1.k` false to true; its type pointer 49 to existing pointer 68;
`LALNest.node.cidx` 0 to 1; and `E.numIndices` 0 to 1. The type-pointer change
shares an existing type, rather than editing a shared expression node. This is
syntactic isolation, not a proof about all downstream semantic interactions.

For the first three pairs, pinned official Lean 4.33.0 and Lean4Lean `ecb3b666`
rejected while Kiota `58e8636c` accepted; all their controls accepted. The two Lean
observers share lineage and are not two independent semantic specifications.
Separate Nanoda reproduction records preserve their rejection diagnostics but
lack a complete baseline source/binary identity in those receipts. They are
not promoted into fully identified current observations.

For `numIndices`, official/Lean4Lean accepted both bytes. The separately bound
Nanoda `0505569` run accepted the control and rejected the candidate. Kiota
rejected the control for a nested-parameter compatibility issue, so its candidate
result is null: **INCOMPATIBLE, not an observed rejection or acceptance**.
The [dated Nanoda maintainer explanation](https://github.com/ammkrn/nanoda_lib/issues/29#issuecomment-5489276523)
connects its stricter check to retaining supplied declarations in the permanent
environment. That is scoped implementation policy, not a universal format rule
or a reason to reopen the old issue. The exact control was retained byte-for-byte.

## Source profiles

Current exporter `411dce7d` and Kiota `9fa2c297` are bound by fresh tip receipts,
archives and complete 13/90-file inventories. The reference replay file is bound
to exact retrieved content at the `v4.34.0-rc2` release-tag URL; this item did not
independently attest that tag to a full Git commit. The current exporter parser
is byte-identical to the Arena parser locked at `f297dfe2`. Current source and
old executable observations remain separate.

The reference column describes the safe, nonpartial declaration replay path;
unsafe and partial constants are skipped by its entry filter.

| Field | Inspected Lean replay profile | Inspected Kiota `9fa2c297` profile |
| --- | --- | --- |
| Recursor `k` | Compare supplied recursor record with the generated record | Retain flag but recompute the K-like reduction condition; README documents ignoring exported `k` |
| Recursor `type` | Compare postponed recursor record using its `==` operation | Retain supplied type; validate arity/count and elimination constraints; constant inference uses the retained type |
| Constructor `cidx` | Compare supplied constructor record with generated record | Check index against the owning constructor list, then retain it |
| Inductive `numIndices` | Derive through core inductive input; no supplied inductive-record comparison on this path | Retain supplied count, check telescope/result arity, and use it downstream |

These are source descriptions, not current candidate/control outcomes. In
particular, the current Kiota owner-list guard statically excludes the historical
bad `cidx`; the old ACCEPT is stale as a current-behavior claim. Its `k` policy is
documented, so ignoring that serialized flag is not an unexplained missing check.
Both types in the old recursor-type pair have five manifest Pi binders; arity
checking alone does not distinguish them. No current acceptance, complete safety
proof or defect follows from that observation. The full source paths and limits
are in [reference-source-review.json](reference-source-review.json) and
[current-kiota-review.json](current-kiota-review.json).

The current format describes recursor types and other generated fields as
redundant information. It does not specify one field-by-field acceptance relation
for every independent checker. Parsing a field, reconstructing it, comparing it
and consuming a retained field are different operations. The useful documentation
question is which of those operations each profile promises, including the
comparison used for retained types. Neither an all-fields identity requirement
nor unrestricted permission to trust or ignore metadata has been established.

## Contribution decision and limits

Eight charged read-only requests include one wrong-repository 404, corrected
using the canonical target and retained remote. All requests and raw receipts
are preserved. The bounded searches returned six exporter and two Kiota issue
bodies, with null state/comment fields and no complete inventory attestation.
They reveal adjacent lean4export #48 but supply no exact four-field answer.
No live disposition or complete absence of duplicate discussions is claimed.
The current Kiota archive contains 70 NDJSON fixtures with no exact hash match
to these historical candidates; that does not establish missing equivalent tests.

Recommend one grouped documentation appendix for the export/import contract,
held locally and coordinated with #48 after fresh discussion review and exact
owner approval. The four-field table is useful documentation now; publication
and universal-policy qualification are separate steps. Do not submit another
Kiota bug report based on the old matrix, and retain the existing Kiota submission
deferral. No PR candidate or external action was created, so the PR ledger remains
unchanged. The related proof-parameter example keeps its documented shared-node
qualification and supplies no universal ordinary-inductive obligation.

## Handoff and reproduction

Select `NANODA-NESTED-REGRESSION-1` READY and unstarted. Its independent current
suite/traversal audit can yield one supported reserved-prefix regression design
under its existing 90-minute/eight-request/no-launch scope. It is feasible while
the theorem companion still lacks a demonstrated distinct refusal risk. Further
cache execution lacks its exact outcome witness; CVC/independent-transfer gates
and all original historical boundaries remain unchanged. The project-wide review
compares those alternatives and concrete blocker-removal options; no pause or
second item execution is needed.

Reproduce retained observations with
`python3 results/research/semantic-import-contract-1/replay-historical-evidence.py --check`.
The closure validator checks exact source archives, frozen entry/request state,
four-field scope, no-launch claims, cumulative work and the historical handoff.
Required full-payload Lab validation is recorded in `validation.json`; scientific
builds/checkers/proofs/mutations/new export generation and external research writes
remain zero. The retained control is existing-byte reuse, not a new witness.
