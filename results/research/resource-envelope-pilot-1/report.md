# Resource envelope pilot 1

**What did we find?** Both checkers accepted all 24 selected cases, and all
12 empty-input baseline runs completed as expected. No configured process
limit was observed. The official checker yielded one sampled group-memory
reading in each run; Nanoda finished before the first memory sample in all
18 of its runs. Its sampled group-memory peak is therefore unknown, and this
run cannot compare sampled group memory between the checkers.

**Is it interesting?** Yes, as a reproducible finite input corpus and a
record of how these two exact checker profiles behaved. It found no checker
disagreement or observed resource boundary. The single, startup-inclusive
times and sparse memory sampling do not establish a general speed or memory
ranking, semantic correctness, or a growth law.

**Does it require more work?** Yes. A separate short-process memory audit
should test a measurement method that observes fast-exiting Nanoda processes
and quantifies its own gaps before any comparative group-memory claim. Retain
the twelve audited inputs and this result locally; no upstream issue or
contribution follows from the accepted cases. That follow-up is driven by the
measurement gap and does not reopen or extend this frozen matrix.

## Scope and controls

The fixed experiment used two closed, type-valid families, Pi and let, at
binder counts 16, 32, 64, 128, 256 and 512. An independent source/export
auditor passed every one of the twelve exact inputs before observer launch.
The two checkers received the same export bytes for each case. Official Lean
4.33.0's kernel profile and Nanoda `6ae1f0c` each checked one safe definition,
with one checker thread in the Nanoda configuration. Exact source, runtime,
command, environment and limit identities are in the
[scientific manifest](scientific-manifest.json) and
[R2 execution manifest](execution-manifest-r2.json). Construction used the
retained Lean 4.29.1 toolchain and lean4export format 3.1.0.

All 24 scientific runs exited zero, printed the profile's exact one-declaration
acceptance line, and had empty stderr. All 12 metadata-only baseline runs
exited zero, printed the exact zero-declaration line, and had empty stderr.
Every run retained complete raw output, wait4 child accounting, monitoring,
pipe-drain and process-group cleanup receipts. No timeout, above-ceiling
sample, above-ceiling post-exit child high-water, trace-gap fault or other
control pause occurred. This says no **configured limit was observed**; it
does not establish a true memory maximum below the ceiling.

The baseline invokes the same checker on a zero-declaration export. It includes
process startup, parsing and empty checking. It does not isolate import cost,
and no baseline time or memory value was subtracted from a scientific run.
The selected declarations have no dependency constants. Three baselines ran
before and three after each profile's twelve cases. Each scientific case ran
once on this host, in fixed profile/family/size order.

## Exact input size

Serialized bytes include the full export. DAG nodes count distinct nodes
reachable from the definition value; expanded nodes count shared occurrences
recursively. Both families have binder depth equal to size. The source and
graph audit, rather than checker agreement, supports their exact closure and
typing within the selected grammar.

| Family | Binders | Export bytes | Reachable DAG nodes | Expanded value nodes |
| --- | ---: | ---: | ---: | ---: |
| Pi | 16 | 2,203 | 17 | 33 |
| Pi | 32 | 4,011 | 33 | 65 |
| Pi | 64 | 7,627 | 65 | 129 |
| Pi | 128 | 14,981 | 129 | 257 |
| Pi | 256 | 29,957 | 257 | 513 |
| Pi | 512 | 59,909 | 513 | 1,025 |
| let | 16 | 2,208 | 19 | 49 |
| let | 32 | 4,000 | 35 | 97 |
| let | 64 | 7,584 | 67 | 193 |
| let | 128 | 14,876 | 131 | 385 |
| let | 256 | 29,724 | 259 | 769 |
| let | 512 | 59,420 | 515 | 1,537 |

## Scientific observations

Times are milliseconds from supervised spawn to reap, including process
startup. Child high-water is the macOS `wait4` value in MiB. Sampled group
RSS is the largest periodically sampled sum in MiB, with `—` meaning no
sample. The final column is the largest uncovered interval in milliseconds,
including spawn to first sample and last sample to reap. Every row has status
`ACCEPTED`, zero exit and empty stderr; the official output was `Accepted 1
declarations.`, and Nanoda's was `Checked 1 declarations with no errors`.
Numbers in this table are rounded for reading; raw receipts retain exact bytes
and timestamps.

| Profile | Family | Binders | Elapsed ms | Child high-water MiB | Sampled group RSS MiB | Samples | Largest gap ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| official | Pi | 16 | 29.063 | 36.062 | 3.750 | 1 | 23.557 |
| official | Pi | 32 | 28.615 | 36.266 | 4.000 | 1 | 22.562 |
| official | Pi | 64 | 28.473 | 36.312 | 3.641 | 1 | 22.374 |
| official | Pi | 128 | 29.584 | 36.344 | 3.516 | 1 | 22.758 |
| official | Pi | 256 | 30.070 | 36.250 | 3.609 | 1 | 22.681 |
| official | Pi | 512 | 30.600 | 36.578 | 3.984 | 1 | 22.892 |
| official | let | 16 | 29.407 | 36.406 | 6.766 | 1 | 24.070 |
| official | let | 32 | 29.471 | 36.281 | 5.625 | 1 | 24.201 |
| official | let | 64 | 29.496 | 36.266 | 3.953 | 1 | 22.945 |
| official | let | 128 | 30.665 | 36.453 | 4.453 | 1 | 24.187 |
| official | let | 256 | 29.801 | 36.547 | 4.266 | 1 | 22.971 |
| official | let | 512 | 30.636 | 36.797 | 4.438 | 1 | 22.923 |
| Nanoda | Pi | 16 | 3.928 | 2.016 | — | 0 | 3.928 |
| Nanoda | Pi | 32 | 4.024 | 1.828 | — | 0 | 4.024 |
| Nanoda | Pi | 64 | 3.977 | 1.844 | — | 0 | 3.977 |
| Nanoda | Pi | 128 | 4.378 | 1.875 | — | 0 | 4.378 |
| Nanoda | Pi | 256 | 3.977 | 1.922 | — | 0 | 3.977 |
| Nanoda | Pi | 512 | 4.383 | 2.094 | — | 0 | 4.383 |
| Nanoda | let | 16 | 4.216 | 1.828 | — | 0 | 4.216 |
| Nanoda | let | 32 | 3.855 | 1.828 | — | 0 | 3.855 |
| Nanoda | let | 64 | 4.017 | 1.844 | — | 0 | 4.017 |
| Nanoda | let | 128 | 4.090 | 1.875 | — | 0 | 4.090 |
| Nanoda | let | 256 | 3.959 | 1.953 | — | 0 | 3.959 |
| Nanoda | let | 512 | 4.615 | 2.141 | — | 0 | 4.615 |

`wait4` child high-water covers OS-accounted child lifetime and may include
accounted-for descendants. It is not an exclusive target-process peak or a
simultaneous group peak. Sampled group sums may miss short peaks, may count
shared pages more than once, and are not atomic snapshots. The official runs
had only one sample each, with 22–24 ms uncovered gaps during roughly
28–31 ms lifetimes. Each Nanoda run had no sample, so its entire 3.855–4.615
ms lifetime is uncovered by this sampled measure. The two memory columns
measure different things and cannot be subtracted or directly equated.

## Empty-input baselines

All listed values are the three individual runs in chronological order.
Medians describe those observations only. A dash in group RSS means no
sample; all six Nanoda baselines had full-lifetime uncovered gaps.

| Profile | Phase | Elapsed ms (three runs) | Median ms | Child high-water MiB (three runs) | Sampled group RSS MiB (three runs) | Samples per run | Largest gap ms (three runs) |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| official | before | 29.749, 28.290, 29.377 | 29.377 | 35.953, 35.922, 36.047 | 3.531, 3.562, 3.562 | 1, 1, 1 | 21.895, 22.270, 22.601 |
| official | after | 29.579, 29.957, 29.562 | 29.579 | 35.781, 36.047, 35.891 | 4.234, 4.562, 7.703 | 1, 1, 1 | 23.373, 23.737, 24.040 |
| Nanoda | before | 4.064, 3.922, 4.167 | 4.064 | 1.688, 1.688, 1.688 | —, —, — | 0, 0, 0 | 4.064, 3.922, 4.167 |
| Nanoda | after | 3.851, 3.851, 3.978 | 3.851 | 1.688, 1.688, 1.688 | —, —, — | 0, 0, 0 | 3.851, 3.851, 3.978 |

The baseline elapsed ranges overlap their profile's scientific ranges. These
are startup-inclusive observations from one host and one run per case. They
do not support an isolated cost per added binder, an import-cost estimate,
an asymptotic claim or a general checker performance ranking.

## Evidence and repair history

The [canonical result](science-run-0001/science-result.json) contains the
ordered 36-slot ledger, each input binding and every disposition. The
[sealed corpus](corpus-lock.json), [independent corpus review](independent-corpus-review.json),
[smoke result](smoke-result.json), [scientific launch review](independent-prelaunch-review.json)
and [independent scientific result review](independent-scientific-result-review.json)
are separate gates. The result and its raw process streams, rather than this
rounded table, govern exact measurements.

The original construction attempt stopped at Lean's default frontend
recursion guard while building Pi 256. Its four completed input packages
were preserved. R2 changed only the construction Lake recursion option to
8,192 and replayed those four packages byte for byte. A subsequent sandbox
attempt stopped before its first build because `/bin/ps` monitoring and
cleanup were denied. That failure remains preserved. The actual-host retry
began before a separate post-failure cleanup reconciliation; this sequencing
incident is recorded explicitly. Later host checks found no surviving process
in the failed group. The successful actual-host construction then produced
and independently audited all twelve inputs with valid monitoring and cleanup.
Neither construction failure is a scientific checker limit or a result about
term validity. The construction and scientific manifests remain unchanged
across the observer launch.

Run `python3 scripts/validate-resource-envelope-pilot-1-result` from a
checkout to re-audit the exact corpus, ledger, all 36 raw observer outcomes,
and all 73 retained process receipts without launching an observer. The
portable evidence gate also checks this family from a foreign checkout.
