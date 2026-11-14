# Confirmed checked-import cases — 2026-11-14

**What did we find?** All ten unchanged known cases produced their independently
derived outcomes on both pinned checker profiles, and a separate fresh replay
reproduced every cell. Across 40 attributable cells, the five valid controls
accounted for 20 accepts and the five paired negatives accounted for 20
boundary-specific rejects. The intended declaration identity was visible for
every accept. No unexpected behavior or previously unknown defect was found.
Current checker tips, arbitrary imported terms and defects outside these two
typing preconditions were not tested.

**Is it interesting?** Yes, modestly. The result turns two exploratory samples
into a reproducible known-case package for detecting changes in ordinary
application-argument and Pi-codomain checking during a profile upgrade. It is
not a correctness proof, a fresh holdout, a defect-yield estimate, or evidence
that checker agreement supplies semantic authority.

**Does it require more work?** Yes. The result-driven follow-up is the separate
`CHECKED-IMPORT-REGRESSION-PACK-1` E2 integration: expose one supported manual
command and prove its fail-closed controls for missing, changed, substituted,
unattributable and stale evidence. This E1 result does not itself authorize
shared regression integration or any external action. The independent
assurance-case disposition item remains a separate READY project output.

## Result

The fixed package contains six application-precondition cases and four
Pi-codomain cases. Each phase ran one fresh, networkless, read-only ARM64
container per case/profile cell from image
`sha256:1a144bf428c8c7dd7ed1df886273b77ca331079cb17ebfb9712e1ea2ea643b73`.
All containers were absent after their cell. Initial checker processes consumed
18.542110332 host-observed seconds; replay checker processes consumed
15.202277622 seconds. These timings observe the supervised Docker client/process
group, not guest checker peak memory.

| Family | Cases | Initial | Replay | Disposition |
| --- | ---: | ---: | ---: | --- |
| Application argument precondition | 6 | 6 accepts/rejects across 12 cells | exact 12-cell reproduction | Three controls accepted; three paired negatives rejected per profile at the application-domain check. |
| Pi codomain sort precondition | 4 | 4 accepts/rejects across 8 cells | exact 8-cell reproduction | Two controls accepted; two paired negatives rejected per profile at Pi-codomain sort inference. |

The table’s phrase “accepts/rejects” counts profile cells: application has six
control accepts and six negative rejects per phase; Pi has four of each per
phase. The canonical cell-level result is
[`result.json`](result.json), with distinct
[`initial/result.json`](initial/result.json) and
[`replay/result.json`](replay/result.json) inputs.

## Evidence and attribution

- The exact 20-cell-per-phase contract, input/config hashes, decoded trees,
  runtime identities and classification rules are frozen in
  [`execution-manifest.json`](execution-manifest.json).
- A separate reviewer re-derived all five accept and five reject expectations
  from the raw syntax and typing rules. The review is explicitly corroborative,
  not blinded, because mandatory status and retained case files disclose prior
  outcomes. See
  [`independent-expectation-review.json`](independent-expectation-review.json).
- Lean controls showed the exact parsed name/type/value and completed trust-0
  empty-environment replay. Nanoda controls printed the named definition and
  completed one-declaration checking.
- Lean application negatives reported kernel application type mismatch; Nanoda
  reached its pinned domain-equality assertion. Lean Pi negatives reported a
  type-expected failure during replay; Nanoda reached the pinned
  `infer_sort_of` assertion. This satisfies the special `pi/A-negative` guard:
  generic later value/type rejection would have been unresolved.
- Raw command, stdout, stderr and supervision receipts remain under `initial/`
  and `replay/`. Every process had complete accounting and cleanup with no
  monitor, pipe or trace-gap fault.

## Runtime and tooling repairs

The historical tools lived in a 15.3 GB container writable layer. A direct
snapshot failed when Docker storage filled while copying unrelated Mathlib
artifacts. A selective exact-runtime export removed unrelated work/output
caches and produced a 3.7 GB immutable image plus an ignored 851 MiB compressed
archive. Fresh-container verification matched the four pinned executable and
importer hashes. See [`runtime-recovery.md`](runtime-recovery.md).

The process preflight’s first absence check expected one Docker diagnostic
spelling; revision 2 accepted the installed client’s equivalent spelling and
passed identity, ordinary completion, intentional timeout, forced cleanup and
post-cleanup absence. After the 20 initial cells, the frozen analyzer similarly
rejected Docker’s harmless `[]` stdout on failed inspect. The original analyzer
and raw cells remain unchanged; `analyze_r2.py` accepts only that empty-array
form while preserving exit-code and explicit absence-diagnostic requirements.
Its focused regression passed. Neither repair changed a scientific input,
expected result, runtime or checker cell.

## Scope limits and recommendation

This package covers two typing preconditions in ten closed sort-only ordinary
definitions on historical Lean 4.34.1 and Nanoda `3a240721`. The runtime archive
is ignored external custody and must accompany a portable recovery. Upgraded
profiles require fresh identity binding and cannot inherit this outcome.

Retain this E1 package and advance only through the separately reviewed E2
integration contract. No checker change, upstream report, current-tip claim,
assurance milestone change or default-CI decision follows from this result.
