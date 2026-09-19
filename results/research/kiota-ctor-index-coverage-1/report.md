# Kiota constructor-index coverage audit — 2026-09-19

`KIOTA-CTOR-INDEX-COVERAGE-1` completes SUCCESS for one source-supported,
unexecuted existing-byte regression design at retained Kiota
`9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`. The current source already has the
owner-list/index guard; this is a test-coverage gap, not a checker defect.

The complete retained inventory contains 70 NDJSON files. Sixty-nine unique
fixtures are wired into 70 tests: 33 accepts and 36 rejects, with one fixture
used twice. `cedar-prefix-60.ndjson` is the sole unwired file. No ignored or
dynamic fixture discovery was found. The complete binding and wiring counts are
in [source-lock.json](source-lock.json) and [coverage-map.json](coverage-map.json).

Only `orphan-ctor.reject.ndjson` violates a constructor owner/list relationship.
Its `rogue` constructor names an undeclared `Orphan`, so it rejects at the
missing-owner branch (`src/parser.rs:445-457`). It never reaches the distinct
owner-present slot check at lines 458-470. Its test also accepts any
`TcError::Reject`, so it cannot attribute a future failure to that guard. Every
multi-constructor reject has correct indices; accept fixtures exercise valid
indexing but supply no negative assertion. The exhaustive static projection
found no declared-owner wrong, swapped or out-of-range index case.

The retained pair fills that exact gap. Both 6,332-byte, 105-record files differ
only at `/104/inductive/ctors/0/cidx`. `LALNest` declares one constructor,
`LALNest.node`, at slot 0. The control supplies 0; the candidate supplies 1.
At the bound source the candidate's first divergent result is therefore the
exact source-predicted rejection:

```text
constructor `LALNest.node` is not `LALNest`'s own constructor at index 1
```

Static downstream review predicts the control accepts through EOF, but no Kiota
process ran. The [design](regression-design.json) consequently requires both a
paired accept cell and an exact-message reject cell. A generic negative test
would allow a competing refusal and is not sufficient. The pair covers the
unified predicate's out-of-range manifestation, not a separate in-range
wrong-name occupant.

Seven bounded local source/inventory/duplicate requests were charged. There
were zero network requests, builds, tests, checkers, proofs, mutations, new
scientific exports or external writes. The retained archive was fetched on
September 13; all source claims are scoped to `9fa2c297`, not the current
upstream tip. Historical Kiota `58e8636` acceptance remains historical, and no
catalog, authority or universal constructor-metadata claim changed.

Select `KIOTA-CTOR-INDEX-TEST-1` READY and unstarted. It must refresh and bind
source and duplicates, freeze the exact two-cell patch/tooling/process controls,
then run focused and full tests within its separate budget. It may produce a
tested local PR draft; any external submission still needs fresh preflight and
exact human authorization. This concrete public-import regression outranks the
unchanged one-thread operational survivor for the next bounded item, while that
reserve remains READY.
