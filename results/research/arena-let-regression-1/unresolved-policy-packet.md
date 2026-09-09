# Arena let-value regression outcome boundary

At Arena `da7a53f8520fb072614956007d7091d0f9a1650f`, no existing static test is
byte-identical to either fixed 601-byte let artifact. The executable tutorial
binding has three positive let cases, and the only current static artifacts
with serialized `letE` nodes are broad `constlevels` and `rec-missing-ih`
fixtures. This is a coverage observation, not a claim that no semantically
equivalent test exists.

The candidate is rejected and the matching control accepted by one retained,
pinned official-observer profile. That is useful implementation evidence, but
it is not qualified semantic authority for a new Arena `reject` expectation.
Arena's `either` label requires affirmative support that both outcomes are
permitted. The existing subject-reduction `either` examples establish a
different, documented beta-erasure behavior and do not supply that support for
this pair.

Accordingly no test patch, build-test reservation, new export byte, checker or
external action is proposed. The focused question for `SEMANTIC-LET-CONTRACT-1`
is: under the relevant serialized-declaration and environment assumptions, must
a validator establish a raw let value's compatibility with its declared
annotation before zeta reduction can erase the let? That item must seek a
qualified reference/export-contract answer before any future strict Arena
outcome is proposed.
