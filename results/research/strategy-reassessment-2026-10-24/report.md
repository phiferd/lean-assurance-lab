# Research priorities after the October upstream repairs

**What did we find?** The upstream records confirm the Lean repair merged and
two independently reported Nanoda recursor faults were repaired. The Lab's
original Lean witness has not been replayed after merge. Its contribution index
had two outdated states and omitted three published contributions. No checker
experiment ran in this reassessment.

**Is it interesting?** Yes. These are concrete incorrect-acceptance boundaries,
and the Lean discussion explicitly credits the Lab's report for a repair and
added assertions. They offer more information than another confirmation that
the universe-parameter testcase behaves as expected. That testcase remains a
valid local asset; no present checker defect was found by its experiments.

**Does it require more work?** First replay the preserved Lean witness against
the exact merged revision. Next assess whether unchanged pre-disclosure Lab
assets detect the two historical recursor faults. Defer Arena universe-test
confirmation until current coverage and a concrete consumer benefit justify it.
Pestka/Kefir transfer is a separate planned screen after a semantic target is
selected. This turn selects these items; it starts none of them.

## Verified corrections and credit

- [Lean #15373](https://github.com/leanprover/lean4/pull/15373) merged on October
  20 from `e5aed18a894735d1e20bd96048a308eae3dc1840` as
  `7632b2cf35e51ec5d92d9cdd86296a8481dcb01e`. The
  [author's response](https://github.com/leanprover/lean4/pull/15373#issuecomment-5969992190)
  acknowledges the missing normalization call and added invariant assertions.
  This supports credit for the Lab's report, not authorship of the overall PR
  or a fresh local verification of the merged repair.
- The Nanoda reports are [#60](https://github.com/ammkrn/nanoda_lib/issues/60),
  fixed by [#63](https://github.com/ammkrn/nanoda_lib/pull/63), and
  [#64](https://github.com/ammkrn/nanoda_lib/issues/64), fixed by
  [#65](https://github.com/ammkrn/nanoda_lib/pull/65), all on October 23.
  The second report is about relocating a nested recursor past validation;
  neither Lean #15373 nor Lab commit `3a116a7` identifies that fix.
- The shared regression is [Arena #285](https://github.com/leanprover/lean-kernel-arena/pull/285).
  [Pestka #278](https://github.com/leanprover/lean-kernel-arena/pull/278),
  [Kefir #289](https://github.com/leanprover/lean-kernel-arena/pull/289) and
  [Kiota update #277](https://github.com/leanprover/lean-kernel-arena/pull/277)
  also merged. Coverage and reproduction claims in those PRs remain
  author-reported; no published witness was executed here.
- [Kiota #11](https://github.com/sankalpsthakur/kiota/pull/11) merged October 7.
  Nanoda #41 and #43 closed without merging October 10. Their comments raised
  clarity concerns; this is evidence to improve explanations, not proof that
  maintainers reject mutation testing or all preventive tests.
- Nanoda #32, #33, #42 and Kiota #13/#14 remain open at this observation.
  Nanoda #38 is an open dependency by another contributor, so it is recorded
  with #42 and excluded from the Lab contribution count. The index now includes
  previously omitted #41, #42 and the Lab's report comment on Lean #15373;
  the comment is explicitly distinguished from authorship of the PR.
- Kiota #14's current head differs from the Lab's original tested head. The
  refreshed ledger records that fact without extending the old validation claim.
  [CI for the starting Lab commit](https://github.com/phiferd/lean-assurance-lab/actions/runs/39616987625)
  passed. This observation does not cover the new delivery commit.

## Selection and information gain

The highest-value feasible next item is `LEAN-ETA-MERGED-REPLAY-1`: the original
negative pair and valid controls already exist, the semantic expectation was
independently reviewed, and the exact merged target is known. Fresh runtime
evidence closes a specific gap. Its new launch bindings and applicable E1 gates
remain necessary; a merge cannot replace them.

`E0-RECURSOR-HISTORICAL-GAP-1` asks a different question: can the unchanged Lab
assets at pre-disclosure commit `3a116a7` expose these fault mechanisms without
importing the published witnesses? Freeze the selection rules before execution.
Knowing the mechanisms prevents calling this a blind discovery or holdout.
Report existing coverage separately from any informed new detector. A useful
negative result is a precise, executable gap, not an obligation to manufacture
a new defect. The [prospective plan](../../../docs/research/RECURSOR_HISTORICAL_GAP_AND_TRANSFER_PLAN.md)
sets the contamination and generalization boundaries.

`CONFIRM-ARENA-UNIVERSE-GUARD-1` is DEFERRED, unstarted. Its October 21 pinned
compatibility result remains valid at those inputs; Arena subsequently changed.
No source audit here proves redundancy or current compatibility. Before further
confirmation, demonstrate distinct current protection and a concrete consumer
benefit using public source/guidance; contacting maintainers remains a separate
authorized action. Preserve the candidate and all earlier raw evidence.

The new-checker screen is PLANNED behind a specific recursor invariant and
working pinned recipes. It does not remove the independent holdout intake's
external-input/custody gate. Existing blocked build-profile, CVC and holdout
work retains its gates. Memory accounting and further Tree2 expansion do not
outrank these direct correctness questions. Reuse existing runners and E0 tools;
no new harness framework, workflow rule or assurance milestone is selected.

The Comparator result remains useful evidence about binding the intended proof
to the actual checker execution, not a Comparator defect. Its retained summary
records 158 supervised commands and 5,584.508 seconds of observed wall span
(about 93 minutes). This is substantial screen overhead; future E0 work should
reuse infrastructure and make one campaign-level decision, not convert each
expected result into another confirmation project. No retrospective cap or
discarding of failed attempts follows. A passing preventive test can still be
valuable when its consumer and incremental protection are concrete.

## Evidence and validation scope

`upstream/verified-metadata.json` and `ledger-observations/` contain dated primary
source observations. `result.json` records this reassessment, and the canonical
queue binds the strategic comparison. Historical scientific reports remain
unchanged. Validate queue/status agreement, the generated contribution/project
views, the exploration ledger and the repository's current/historical tests.
This is maintenance and selection, not an E0 experiment: do not fabricate an E0
trial or use its handoff exception to skip applicable checks.

The generated contribution view now separates merged Lab pull requests from
reports on other authors' work. A focused regression protects this distinction;
the full current/historical test path applies to this small shared-tool change.

Usage coverage: one bounded delegate checked upstream metadata and reviewed the
reassessment; no scientific
checker/build launches occurred. Aggregate parent/delegate model-token use and
complete session cost are unavailable. No transcript export or cost estimate.
