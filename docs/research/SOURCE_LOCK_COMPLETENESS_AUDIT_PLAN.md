# Source-lock completeness audit

Item `SOURCE-LOCK-COMPLETENESS-AUDIT-1` is the selected, ACTIVE successor to
`SURVIVOR-THREAD-ONE-CHILD-PANIC-REGRESSION-1`, under its committed
source-only static-audit bindings. It
does not retrieve a missing source byte, rebuild Nanoda, or reopen the bounded
child-panic result.

The initial R1 static-audit controller rejected the source-lock row shape before
reading pinned source content. R2 validated the row shape and scanned the
locked source files, but could not write beside R1's preserved error evidence.
R3 permits that existing evidence directory while still refusing to overwrite
the ledger. These repairs change no frozen source, scope or claimed disposition
and remain the same bounded audit.

## Question

Can existing, locally pinned build metadata and source bytes identify every
source file required to materialize the pinned Nanoda source tree for offline
compilation, and does the current 22-file lock omit any such dependencies?

## Frozen scope

- inspect only the existing pinned source evidence, its `Cargo.toml`,
  `Cargo.lock`, Rust source and `source-lock.json`;
- statically inspect path-valued Rust inclusion directives reachable from the
  pinned crate root, recording each literal relation and every missing locked
  source path;
- use the preserved child-panic build receipt only as a consistency check for
  the discovered `README.md` dependency;
- write one audit ledger, result and closure regression.

The audit permits at most one 30-active-minute session and eight source/setup
inspections. It permits zero network requests, Cargo builds, checker processes,
proofs, production-source edits, new export bytes, new mutation identities or
external actions. A missing byte remains a boundary, not permission to invent,
fetch or substitute it.

## Completion

Close SUCCESS with a reproducible static source-dependency ledger, explicit
locked/missing dispositions and a regression that detects the recorded missing
edge; or close BOUNDED_UNRESOLVED with the exact parser/reachability limitation.
The audit may recommend a separately authorized source-intake successor but may
not start it or claim a validation outcome.
