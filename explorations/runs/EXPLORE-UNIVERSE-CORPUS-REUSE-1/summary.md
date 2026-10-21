# Reuse value of nine universe fixtures

One case warrants a small contribution: rejecting a definition that uses a
universe parameter absent from its parameter list. The pinned Arena tutorial
tests duplicate parameters, which is a different rule. Our max-commutation
case already has an equivalent Arena source contract; the other seven cases
have related coverage but no demonstrated reason to contribute them now.
No literal file duplicates were found, which does not imply semantic novelty.

This is a useful, narrow test-coverage finding, not a checker defect. The
comparison covered nine fixtures, 148 archived source/resource files, and a
static ownership walk over 260 declaration occurrences in committed exports.
It ran no checkers. Runtime sensitivity, exported tutorial bytes, and generated
external-library corpora remain unmeasured.

Recommend one normal-priority Arena rejection testcase:
`tests/undeclared-universe-parameter.ndjson` and its YAML metadata. Reuse the
retained missing-parameter case and P1 positive control; avoid a nine-case
package or a parallel Nanoda PR. The separate local integration item is READY
and unstarted. No patch, submission, issue or contact was made in this assessment.

| Fixture | Source comparison | Disposition |
|---|---|---|
| P1 | Named-universe declarations already exist; exact minimal control differs | Keep as local valid control |
| P2 | Arena checks let typing/reduction at closed levels | Keep locally; named-level combination alone does not justify a contribution |
| M1 | Existing max identities and offset tests are related, not the exact distribution assertion | Keep locally |
| M2 | Arena `levelMaxComm` states the same source contract | Do not add a duplicate contract |
| I1 | Existing dependent Pi and imax tests cover related rules | Keep locally |
| I2 | Existing imax/max tests overlap components, not this exact combined operand | Keep locally |
| P1-invalid | No omitted-used-parameter case identified in the inspected suites | Recommend one rejection case |
| M1-invalid | Arena has Sort mismatch and imax-offset rejection tests | Keep locally; no distinct contribution need established |
| I1-invalid | Arena and Nanoda already test imax zero/offset behavior | Keep locally; exact Pi spelling is not demonstrated equivalent coverage |

The complete judgments and precise source ranges are in
[coverage-map.json](coverage-map.json). Related coverage is intentionally kept
separate from equivalent source contracts; none of these static classifications
proves runtime branch coverage.

## Why the one omission is useful

Arena's [duplicate-parameter case](https://github.com/leanprover/lean-kernel-arena/blob/37f7525b732808a49b746dc6999d53c3717db124/tutorial/Tutorial.lean#L112)
checks uniqueness of the declared list. It does not check that every parameter
used by the type/value belongs to that list. Its constant-level-arity regression
addresses a different condition again. The missing-membership case reaches
Nanoda's explicit `all_uparams_defined` assertion in `src/tc.rs:552–557`, as
already observed by the preceding rejection screen. Neither implementation
needs a fix on the available evidence.

The existing reference walker found no omitted used parameter in any of the
252 Arena and eight Nanoda committed export-declaration occurrences, with no
unresolved expression/level reference. It finds the omission in P1-invalid and
none in the other eight LAL cases. This is a static reachability check, not a
typing model or proof that every possible test is absent. Review of raw Lean
parameter constructions and Nanoda test assertions found no additional negative
membership contract in the inspected snapshots.

A shared Arena file testcase is the smallest useful consumer: its standard
file/YAML convention can expose the same boundary to multiple validators.
Existing positive parameter declarations can remain controls; the prior P1
fixture supplies a particularly small local matched control. The proposed
integration must still check target duplication, metadata/discovery and actual
compatibility before preparing a submission candidate. No external action is
authorized by this recommendation.

## Existing coverage and limits

Arena's [levelMaxComm](https://github.com/leanprover/lean-kernel-arena/blob/37f7525b732808a49b746dc6999d53c3717db124/tutorial/Tutorial.lean#L134)
has the same value/type contract as M2, modulo naming. `good_def` registers an
expected-accept test through `Tutorial.Meta` and `TestCaseEnv`; `lka.py:978–1006`
maps generated good/bad directories to accept/reject expectations. We inspected
that registration path, but did not build or inspect newly exported tutorial
bytes. Elaboration/export may normalize raw universe expressions.

Nanoda's `src/tests/level.rs` directly checks named parameters, imax zero,
successor ordering and imax/max equality for positive right operands. These
helper assertions do not establish end-to-end declaration rejection coverage.
Its pretty-printer tests do not type-check the rendered binders. Arena's
`level-imax-leq` and `level-imax-normalization` are explicit rejection contracts
for other zero/offset mistakes; neither is silently relabeled as our exact
Pi-ascription test.

The complete tracked-path inventory has 31 Nanoda files and 194 Arena files.
We retained all 27 Nanoda files selected by the source/test rule and 121 Arena
textual test/tutorial/discovery files, totaling 1,074,237 bytes before archive
compression. The inventory records all exclusions, including generated binary
artifacts. Arena's Init/Std/Mathlib/CSLib/Cedar exports are generated or external;
their metadata was inspected, their complete exported contents were not. The
gap claim applies to the inspected pinned test contracts and committed exports,
not every historical, current or external suite. Narrow spelling differences
in the other seven cases are not claimed as valuable coverage gaps.

## Evidence and cost

The E0 start bound the nine fixture bytes, source revisions, inventory rules
and classification criteria before comparison. Git blobs were read at exact
commits, not from mutable worktrees. The archived sources preserve original
bytes and headers; [source-inventory.json](source-inventory.json) records blob
IDs and content hashes. [ownership-observations.json](ownership-observations.json)
retains the static reference results. Keyword/test-declaration search files
are leads, not semantic authorities.

The one timed inventory command completed in **2.309 seconds**. Static-walk
and model-reading time were not separately measured; task token/cost accounting
is unavailable. No delegate, checker build, checker call, proof, mutant or model
call in a deterministic loop occurred. The activation commit's configured CI
suite passed; no assurance evidence was regenerated for this assessment.

The canonical result is [result.json](result.json), classified E0 `SIGNAL` for
one actionable reuse gap, not unexpected checker acceptance. `verify.py`
checks retained archive hashes, Git blob identities, fixture hashes, citations
and counts without running checkers. `inventory.py` and `inspect_ownership.py`
are task-local recipes using the existing reference walker; reproduce into a
fresh run directory rather than overwriting this frozen evidence.
