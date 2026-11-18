# Published rpylean change verified on three Arena files

**What did we find?** On Julian’s published checker revision, both disputed
Arena files were rejected and the valid proof-parameter example passed.
All three matched the predictions recorded before execution. The reason for
acceptance on the historical checker remains unverified.

**Is it interesting?** Yes. The checker reported an invalid recursive occurrence
in a constructor field for one file and a mismatched induction rule for the
other. This establishes the observed behavior for the exact files on the
untranslated checker.

**Does it require more work?** The three-case question is closed. No repeat
repair or PR submission is warranted. The separate next item will assess
whether Arena can adopt a released rpylean version containing the change. [Verification](../../results/research/rpylean-published-three-case-verification-1/report.md)

Item `RPYLEAN-RECURSOR-MISSING-IH-INVESTIGATION-1` completed on 2026-11-18. The source-only review and its historical inputs retain their original scope. The separately preregistered experiment settled the published-version question. The result supplies no remaining maintenance reason to pursue historical attribution.

[Source review](../../results/research/rpylean-recursor-missing-ih-investigation-1/upstream-review.md) · [Prospective experiment](../../results/research/rpylean-published-three-case-verification-1/inputs.json)

The following was the original source question. It is retained for provenance.

## Original historical question and scope

Explain why rpylean `b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb` accepts the
Arena static export `tests/rec-missing-ih.ndjson` (SHA-256
`8a240552317ba17d44d175c10531e5f988f55569db5eff734701735ce598fa73`),
and identify the smallest current validation boundary that would have to change
to reject it independently. Compare the unmodified source with the retained
bounded repair only to distinguish pre-existing behavior; do not rerun the
completed repair study.

Freeze the exact export, YAML, source commits and relevant parser, recursor
validation and reduction blobs before analysis. Inventory the export's
inductives, recursors, parameter/index/motive counts, K flags, rule fields and
declaration ordering deterministically. Trace the first malformed rule from
parse through validation to possible reduction. Create fresh valid
source-derived controls for the implicated shape so a recommendation cannot
amount to rejecting all complex recursors.

## Boundaries of the historical attribution step

This is current source attribution, not a replay of the completed historical
recursor audit and not independent discovery of Lean's fixed defect. Do not
modify rpylean, build a regression package, launch another scientific
confirmation, or contact upstream. Preserve whether the acceptance comes from
incomplete-environment skipping, parameter/index derivation, K-like handling,
higher-order recursive IH construction, proof irrelevance/cache behavior, or a
different observed path; do not choose one in advance.

Complete with an exact declaration/shape inventory, source/dataflow trace,
fresh valid controls, attributable result or explicit inconclusive boundary,
and one concrete recommendation: implement a separately scoped repair, retain
the limitation, or stop because the checker does not support the required
shape. Select no implementation until that result is recorded.
