# rpylean recursor-rule argument repair result

## Plain-language result

**What did we find?** The pinned current rpylean revision accepted the exact
Arena #350 export: all 27 declarations, including the proof of `False`, checked.
The retained patch changes that result to rejection and keeps both a valid
field-dependent rule and a valid direct-recursive rule accepted. The repair is
deliberately bounded; complex recursor shapes remain untested by the complete
comparison and are still a known gap.

**Is it interesting?** Yes. This is not a new defect discovery—Arena #350 is
the prior public source—but it is a current, source-derived repair with a direct
fault-sensitive regression. The checker now compares the complete derived
minor application in its stated fragment instead of trusting the imported rule
after checking only its head.

**Does it require more work?** Adoption is optional external follow-up: a
maintainer can review the prepared patch and draft, but submission requires the
owner's explicit authorization. Expanding validation to parameterized, indexed,
mutual, nested, multiple-motive or higher-order-recursive rules is separate work
and should not be inferred from this result. No additional confirmation follows
from this item.

## Evidence

- Base: rpylean `b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb`.
- Public source: Arena `6c2d82164f1a2b1ac94aee62290fe78a3c3853fb`.
- Frozen export: 21,042 bytes, 363 lines, SHA-256
  `cf3b02e4dc0c8a3adcf912f09e81a2e467c7cc667b5c5c545b50ad03760eccc9`.
- Baseline end to end: exit 0, 27/27 declarations checked.
- Repaired end to end: exit 1, rejected at `W.rec` with a derived-rule mismatch.
- Focused tests: 12 passed, including a forged-binder proof-irrelevance bypass
  found and repaired during independent review.
- Full upstream CI-equivalent suite: 815 passed, 1 skipped, 1 pre-existing
  xfailed.
- Translation: passed after retaining the failed dynamic-varargs attempt and
  replacing it with an RPython-compatible loop.
- Translated suite: 9 passed.
- Local sibling-Arena run: one pre-existing `rec-missing-ih` failure was
  reproduced unchanged on the unmodified base; it is not attributed to this
  patch.

Detailed commands and failed attempts are in [validation.json](validation.json).
The exact patch is
[rpylean-recursor-rule-argument-repair.patch](rpylean-recursor-rule-argument-repair.patch),
and the supported boundary is in [implementation-note.md](implementation-note.md).

No external action occurred.
