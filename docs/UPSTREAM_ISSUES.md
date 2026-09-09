# Upstream issue participation

This index records public upstream issues where Lean Assurance Lab work has
either opened the issue or contributed evidence to an issue opened by someone
else. It complements the action-recommendation records, which track whether an
external action was recommended and authorized, and the research status, which
tracks any remaining local work or upstream wait.

`CREATED` means the `phiferd` account opened the issue on behalf of the project.
`CONTRIBUTED` means the project added substantive evidence to an existing issue.
An entry records participation, not agreement by upstream maintainers, semantic
authority, or a current issue-state claim.

| Relationship | Upstream issue | Project contribution | Durable local record |
| --- | --- | --- | --- |
| `CREATED` | [leanprover/lean-kernel-arena#162](https://github.com/leanprover/lean-kernel-arena/issues/162) | Asked for clarification of license and redistribution terms for generated test artifacts. | [Publication audit](PUBLICATION_AUDIT.md) |
| `CREATED` | [leanprover/lean-kernel-arena#175](https://github.com/leanprover/lean-kernel-arena/issues/175) | Proposed coverage for the two `imax` right-successor cases; this led to merged Arena PR #176. | [Research status](RESEARCH_STATUS.md) and [action recommendations](../results/action-recommendations/current.json) |
| `CREATED` | [sankalpsthakur/kiota#3](https://github.com/sankalpsthakur/kiota/issues/3) | Reported the universe-parameter ownership disagreement with official Lean. | [Investigation](investigations/KIOTA_UNIVERSE_OWNERSHIP.md) |
| `CREATED` | [sankalpsthakur/kiota#5](https://github.com/sankalpsthakur/kiota/issues/5) | Reported acceptance of a definition that refers to itself while its body is checked. | [Research status](RESEARCH_STATUS.md) |
| `CREATED` | [ammkrn/nanoda_lib#29](https://github.com/ammkrn/nanoda_lib/issues/29) | Reported rejection of a reference-accepted nested inductive whose serialized `numIndices` differs. | [Investigation](investigations/NANODA_NUMINDICES_OVERREJECTION.md) |
| `CONTRIBUTED` | [leanprover/lean4#12747](https://github.com/leanprover/lean4/issues/12747) | Added an exact serialized declaration replay, corrected control matrix, pinned source comparison, and conditional semantic evidence for the `imax` right-successor normalization case. [Comment](https://github.com/leanprover/lean4/issues/12747#issuecomment-5584574955). | [CVC-4 comparison](../results/research/conditional-validation-contracts/cvc-4-conditional/report.md) and [conditional proof](../results/research/conditional-validation-contracts/cvc-a7-repair-1/report.md) |

Pull requests and their exact submission or follow-up records remain in the
[current action recommendations](../results/action-recommendations/current.json)
and the linked closure artifacts. Add future issue comments here when they carry
substantive project evidence; routine reactions or references do not constitute
project issue participation.

## Dated contribution dispositions

The 2026-09-09 read-only portfolio review verified the following successors to
the earlier submission records. Merge is evidence of upstream contribution,
not independent semantic authority.

| Contribution | Observed disposition | Evidence |
| --- | --- | --- |
| [Arena #181](https://github.com/leanprover/lean-kernel-arena/pull/181), positivity after WHNF | Merged 2026-09-06, `91f376e4baac` | [Exact metadata and feedback](../results/research/contribution-portfolio-review-2026-09-09/arena-review.json) |
| [Arena #182](https://github.com/leanprover/lean-kernel-arena/pull/182), proof-parameter uniformity | Merged 2026-09-05, `6150cb600cc9` | [Exact metadata and feedback](../results/research/contribution-portfolio-review-2026-09-09/arena-review.json) |
| [Nanoda #32](https://github.com/ammkrn/nanoda_lib/pull/32), omitted-thread declaration checking | Open, unmerged; head `85038f436b7c` | [Metadata](../results/research/contribution-portfolio-review-2026-09-09/upstream-pr32.json), [preventive-regression recommendation correction](../results/research/contribution-portfolio-review-2026-09-09/zero-thread-recommendation-successor.json) |

PR #32 was already submitted by the owner; this review performed no external
write and does not authorize a duplicate or follow-up comment.
