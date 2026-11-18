# Attribute rpylean's current rec-missing-ih acceptance

**What did we find?** Provisional. The earlier study reported that the named
Arena case was accepted on both the original and repaired checker. The two
retained test caches corroborate the test name. The exact bytes read during
the old run and the cause of acceptance remain unresolved.

**Is it interesting?** Yes. The fixed public export and fresh valid examples
can inform a maintenance decision about legitimate forms of induction beyond
the existing repair's scope.

**Does it require more work?** Yes. The attribution question is open.
[Provisional report](../../results/research/rpylean-recursor-missing-ih-investigation-1/report.md)

Item: `RPYLEAN-RECURSOR-MISSING-IH-INVESTIGATION-1`, ACTIVE from 2026-11-18. [Bound inputs](../../results/research/rpylean-recursor-missing-ih-investigation-1/work-record.json).

## Fixed question and inputs

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

## Boundaries and deliverable

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
