# Kefir recursor ownership transfer result

## What did we find?

Kefir accepted both valid files and declined the malformed restored-recursor
ownership case at the exact inductive record that was changed. The candidate
received `outcome=decline` and `code=support.semantic`; it was not accepted, but
it was also not semantically rejected.

## Is it interesting?

Unclear. The result shows safe refusal on this malformed input and the pinned
source contains a direct check comparing restored rules with prior constructor
associations. Kefir's published contract says a decline makes no claim about
the proof, however, so this run cannot count as evidence that its checked
admission rejects the ownership violation.

## Does it require more work?

A separate Pestka trial using the now-frozen association case would answer
whether another architecture gives an attributed accept or reject verdict.
That would be a new registered trial; it was not started here. No production
Kefir change or broader Arena campaign follows from this result.

## Technical result

The unchanged export and relationship-preserving whole-block reorder each
returned `accept / checked`, with ten checked declarations and no assumed
axioms. The candidate changes only record 119:
`LALNest.rec_1.rules[0].ctor` changes from `LALWrap.mk` to unrelated earlier
constructor `LALMarker.mark`. Kefir declined at record 119, declaration 3 after
two checked declarations. No cell timed out or wrote stderr.

The source review binds Arena
`87190f9c4f956a42553e37c78a2a7a9a4f4709e9` and Kefir
`e05e1b0d731b1677c32ee6a777ec66877c61287b`. The candidate is informed E0
assurance evidence, not historical or independent discovery. Repository
publication remains blocked by the missing exact 236-file Gate 8 payload.
