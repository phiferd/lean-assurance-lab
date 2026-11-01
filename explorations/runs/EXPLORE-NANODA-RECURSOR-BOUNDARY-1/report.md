# E0 recursor boundary mutation result

## Result

The six registered cells produced an **E0 SIGNAL**. Nanoda at the exact faulty
revision `8199c74c8166dc1fff1be3b4bd144cb725268628` accepted all three fixtures.
The exact repaired revision `a3ef25a863f689d339277090588599dceb741149`
accepted the unchanged control and the valid whole-block reorder, then rejected
the cross-block candidate at line 119 because recursor 17 did not list the
marker block's type.

## Independent relation and consumer

The [fixture audit](fixture-audit.json) shows that the candidate differs from
the valid reorder only at its adjacent `LALNest` and `LALMarker` inductive
records. `LALNest.rec_1` retains `all=[LALNest]` but is installed in the block
whose type set is `[LALMarker]`. This violates the frozen ownership oracle
without relying on checker disagreement.

The exported theorem `LALNest.auxConsumer_iota` applies `LALNest.rec_1` to
`LALWrap.mk`, expects the `mk` branch to reduce to `11`, and closes with `rfl`.
Every accepted cell therefore includes a checked downstream equality consumer,
rather than only environment presence.

## Controls and limits

Both versions accepted the unchanged export and a relationship-preserving
variant that moves the independent marker block as a whole. Each accepted cell
checked 24 declarations. The pretty printer reported one axioms warning after
type checking; no control failed or timed out.

This was an informed prospective assurance experiment against a known repaired
target. It is not evidence of historical selection, independent discovery or
general checker soundness. The retained binaries are new exact-source builds,
not historical binary bytes. Setup smoke runs before E0 registration are
disclosed and excluded; the result uses the separately retained registered
cells. Repository publication remains blocked by the pre-existing absence of
the exact 236-file frozen Gate 8 payload.
