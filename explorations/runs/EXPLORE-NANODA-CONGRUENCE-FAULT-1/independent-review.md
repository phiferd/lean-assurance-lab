# Independent scientific review

**PASS for the bounded scientific claim.** No material fixture or causal defect found.

- **Independent invalidity:** `candidate.ndjson` encodes `F X := X`, distinct opaque types `A,B`, and `v : F A`, then declares `bad : F B := v`. The permitted axioms introduce no conversion rule equating `A` and `B`. The control changes the final type to `F A` and is valid.
- **Causality/public reachability:** the clean source is revision `3a240721…`. Baseline/fault production sources differ solely by the conjunct retained in `fault.patch`. Declaration checking compares inferred `F A` with declared `F B`; the helper's surviving guards permit immediate acceptance when argument equality is omitted. `attempts/baseline-candidate` rejects at `assert_def_eq`; `fault-candidate` accepts; both control attempts accept. This supports source-based causal attribution without claiming an instrumented branch trace.
- **Coverage gap:** `attempts/fault-cargo-test/stdout.log` records all **44 active tests passing** under the fault, with eight ignored doctests. This establishes insensitivity of that executed suite to this exact fault—not absence of coverage throughout every external corpus.
- **Non-vacuous regression:** `regression.patch` checks the candidate through `check_all_declars` with a specific expected assertion panic. `baseline-regression-test-r2` actually runs one passing test; `fault-regression-test` runs it and fails because no panic occurs. `baseline-full-with-regression` passes all 45 active tests.

Retain these qualifications:

1. Initial `baseline-regression-test` ran **zero tests**; only its corrected `-r2` supports regression success.
2. Initial `baseline-build/receipt.json` reports `MONITOR_FAULT`, exit -9, and `cleanup_complete=false`; do not claim all attempts cleaned successfully. Successful outcome receipts are complete and their stream hashes match.
3. The NDJSON is hand-authored; its embedded Lean/exporter metadata is not evidence that Lean generated or validated it.

The useful result is a regression detecting one intentional congruence fault, not a defect in unchanged Nanoda, universal assurance, or an official-Lean execution result. No edits, builds, or checker runs were performed during review.
