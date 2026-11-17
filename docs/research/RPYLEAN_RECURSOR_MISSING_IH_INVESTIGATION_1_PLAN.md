# Attribute rpylean's current rec-missing-ih acceptance

The completed bounded rule-argument repair does not reject Arena's separate
`rec-missing-ih` static export. The unmodified pinned rpylean revision accepts
the same file, so this is not a regression from the patch. Yes, the mismatch is
interesting because the Arena oracle is an official Lean repair and the export
contains parameterized, indexed and K-like recursors outside the completed
patch's claimed fragment. It needs source attribution before any additional
checker change; no repair is authorized by this item.

Item: `RPYLEAN-RECURSOR-MISSING-IH-INVESTIGATION-1`, READY and unstarted.

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
