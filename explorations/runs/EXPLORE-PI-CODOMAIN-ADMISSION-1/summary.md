# Pi codomain admission screen — E0 result (2026-11-09)

**What did we find?** In eight fixed checked-definition cells, pinned Lean
4.34.1 and Nanoda `3a240721` each accepted the two valid controls and
rejected the two definitions whose dependent-function result was a well-typed
term rather than a type. Lean printed each exact parsed tree and reported a
kernel “type expected” error on the negatives. Nanoda accepted both controls
and rejected both negatives at its `infer_sort_of` assertion. No unexpected
acceptance or cross-checker disagreement appeared in this sample. Newer
checker executables and other expression families were not tested.

**Is it interesting?** Yes, as narrow coverage of a distinct precondition.
The invalid codomain lambda has a function type, while a Pi codomain must
infer a universe sort. The observed rejections occur during checked formation
before final value/type comparison. This is E0 `NO_SIGNAL`, not a correctness
proof or an estimate of defect prevalence; checker agreement is not semantic
authority.

**Does it require more work?** No repair or E1 confirmation follows from these
expected outcomes. Retain the four raw inputs as local boundary cases. The
next project queue item is separate and is selected at campaign handoff.

The [result](result.json), [protocol](protocol.json) and [input review](input-review.md)
bind the exact eight cells and independent structural/typing audit. The four
inputs contain one safe ordinary definition each, with no constants, axioms,
applications, lets, recursors, free variables or universe parameters. The A
pair places the Pi in the declared type; the B pair places it in the value.
Each negative changes only that Pi's codomain `Sort 1` to `F = fun (_ : Sort
1) => Sort 0`, whose inferred type is a Pi rather than a sort. The controls
establish the surrounding declarations are accepted. No semantic comparison
result on an ill-typed expression is treated as an admission result.

The task-local analyzer checked all 20 supervised setup, cell and post-cell
receipts, complete cleanup, no accounting or monitor errors, each staged and
post-cell input hash, Lean's parsed names/type/value, and the attributable
diagnostics. Four controls were accepted and four negatives rejected. The
aggregate host-observed cell time was 3.667304 seconds. No scientific cell
needed retry. One prelaunch ledger append failed because the plan lacked the
required standalone `Evidence class: E0` line; its output is retained in
[`prelaunch/start-append-attempt-1.log`](prelaunch/start-append-attempt-1.log).
The plan and prospective hashes were repaired, the ledger start appended, and
only then were any checker cells launched.

Nanoda's parser shape is supported by pinned source and byte-identical staged
inputs; no independent runtime Nanoda AST dump is claimed. Nanoda's panic is
retained as a diagnostic transport limitation, though its exact `infer_sort_of`
site and the sole malformed Pi support attribution. The host RSS observations
track Docker clients rather than guest checker memory. Current upstream Lean
and Nanoda source tips were reviewed for material path drift, but this run
binds only the older exact executable profiles. Model/token usage is
unavailable, and no dollar cost is inferred. No external action, frozen
history edit, production checker change or assurance milestone advance
occurred.
