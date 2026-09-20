# One-thread child-panic regression closure

**Outcome:** `BOUNDED_UNRESOLVED`

The protocol produced no control or candidate observation. The first actual,
offline baseline build ran under the bound 600-second / 2 GiB supervision and
exited 101 after 7.893 seconds. Its compiler stderr reports that the pinned
`src/main.rs` requires `../README.md`, while the frozen 22-file source inventory
does not contain `README.md`.

The exact required README byte is absent from the pinned evidence. Adding a
substitute would change the fixed source tree; retrieving it would require a
network request outside this item's authority. The mutant build and all four
checker cells were therefore not launched.

The earlier R1 controller import error is preserved separately: it occurred
before the supervisor or Cargo process began and is not a scientific result.
The R2 failure has complete request, raw-output, RSS-monitor and cleanup
receipts. This closure establishes only a source-materialization boundary, not
an acceptance, semantic, soundness, current-upstream or thread-safety claim.

See [the canonical result](result.json) and
[the source-materialization audit](source-materialization-closure-audit.json).
