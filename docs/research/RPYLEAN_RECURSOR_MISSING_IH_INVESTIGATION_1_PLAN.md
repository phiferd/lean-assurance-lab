# Check the published rpylean change against the Arena disagreement

**What did we find?** Provisional. Julian closed PR #36 unmerged after publishing
his own implementation. On the cited commit, 80 environment tests passed and
one had its expected failure. The Lab found no case-specific verdict for
either disputed Arena file on that commit.

**Is it interesting?** Yes. The published checker derives induction rules
from each type and its constructors. Julian attributes the earlier acceptance
to a missing restriction on recursion in constructor fields. The new code
checks those fields. The cause in the historical run remains unverified.

**Does it require more work?** Yes. Keep the published revision first. Look for
a result tied to the exact checker and file before resuming work on older
source. The active source review preserves the original experiment boundaries. [Upstream review](../../results/research/rpylean-recursor-missing-ih-investigation-1/upstream-review.md)

Item: `RPYLEAN-RECURSOR-MISSING-IH-INVESTIGATION-1`, ACTIVE from 2026-11-18. [Bound inputs](../../results/research/rpylean-recursor-missing-ih-investigation-1/work-record.json).

## Published change first

The owner redirected the active investigation on November 18. The primary
revision is `a31ca02a158b9aabeb040b9984c21b1f4c8e3216`. Its parent is
`0ddcb018356e4ae59a0e37a395b3c7601b1fd68b`. Check the new defensive rules
and the independent evidence for each named case. Track the PR example and
`rec-missing-ih` separately. An ordinary passing unit test, a verdict on a
different revision, and a maintainer explanation answer different questions.
[Revision and tests](../../results/research/rpylean-recursor-missing-ih-investigation-1/upstream-inputs.json) · [Evidence](../../results/research/rpylean-recursor-missing-ih-investigation-1/upstream-review.json)

The source and unit-test review is complete. A case-specific result still
needs the exact checker revision, file digest, observed outcome and expected
outcome. Seek existing records first. A fresh scientific comparison of the
published checker requires its own prospectively bound experiment, including
a valid comparison input and recorded checker diagnostics. A correct rejection
settles the outcome for that case. Identifying the deciding check needs its
own evidence. Resume historical attribution only for a remaining maintenance
question after assessing the published behavior.

## Historical question and inputs, on hold

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
