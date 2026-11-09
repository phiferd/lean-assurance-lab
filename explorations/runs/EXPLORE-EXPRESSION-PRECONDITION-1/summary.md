# Imported-expression precondition screen — E0 result (2026-11-09)

**What did we find?** In the fixed six-input screen, both pinned checkers
accepted all three valid definitions and rejected all three definitions with
an ill-typed application argument. Lean reported the application type mismatch
in each negative. Nanoda rejected each negative at its checked equality
assertion. The screen did not test Nat imports, other checker versions, or
other expression families.

**Is it interesting?** Yes. The three positions exercise a real ordering
hazard: beta reduction discards an argument whose type fails the lambda's
domain. These observations found no candidate defect in this sample. Agreement
between the checkers does not establish their general correctness.

**Does it require more work?** No result-driven repair or confirmation follows
from these expected outcomes. The six raw inputs are a reusable local boundary
corpus. The next project queue item is separate and is selected at handoff.

Evidence class: **E0**. Outcome: **NO_SIGNAL** in 12 of 12 planned cells.
The three valid controls were accepted by both checkers; the three paired
negatives were rejected by both. The raw input audit verified exact syntax
and one changed application argument per pair before launch. Lean's official
importer printed the parsed constructors before checked trust-0 replay, and
each output matched the frozen trees. Nanoda's raw parser behavior is supported
by pinned source and byte-identical staged inputs; no runtime Nanoda AST dump
is claimed. In the pinned source, `infer_app` in checked mode infers each
argument and compares its type with the domain. Because these negatives have
no other failing application and their final declared types/values would
otherwise match after beta reduction, the Nanoda `assert_def_eq` panics are
attributable to the application-domain check, while retaining panic transport
as a diagnostic limitation.

All 28 setup, cell, and post-check commands have raw stdout/stderr, exact
argv, supervision receipts, and complete cleanup. Guest input hashes matched
after every cell. The checker container was isolated from networks with a
12 GiB memory limit and four CPU allocation. Host RSS samples refer to the
Docker client, not checker memory inside the guest. The pinned Lean 4.34.1,
Nanoda `3a240721`, exporter, and task-local runner identities are in
`protocol.json` and the E0 start event. `result.json` contains the exact cell
classification and elapsed host-observed cell time. No additional scientific
case or retry ran.
