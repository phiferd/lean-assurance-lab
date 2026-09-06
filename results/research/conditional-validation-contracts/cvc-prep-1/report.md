# CVC-PREP-1: exact upstream dependency preparation

**BOUNDED_UNRESOLVED** — `DEPENDENCY_PREPARATION_STOPPED`.

27 of 37 modules completed in 27 compiler launches, charging 25.374 compilation seconds. The exact execution checkpoint is `a28939bf7a06e98d0316adc53523aa9567539247`. Sources, runtime, commands, reservations, raw logs and outputs are bound.

Availability of exact upstream dependency products only. No Lab signature or proof was elaborated. No theorem, axiom closure, executable-validator refinement, normative authority, or binary/OS correctness is established.

**Stop:** The checkpoint controller compares inventories using inconsistent ordering: Path-component order from sorted(Path.rglob) versus lexicographic path-string order for expected receipts. After Batteries.CodeAction created outputs beside the Batteries/CodeAction directory, all 119 output paths, sizes and hashes still matched, but list order differed. It stopped before reserving module 28 (Batteries.Data.Array.Lemmas). This is a characterized controller defect, not an upstream compilation failure. No retry or controller repair occurred under CVC-PREP-1.

Preparation used 34.46 active minutes and 14 reserved inert process attempts, including failed starts and fixture children. All fit the two 90-minute sessions, 37 launches, 300 seconds per launch and 6600 compilation-second caps. Runner development and proof costs remain zero; preparation cost is retained for aggregate reporting.

Preserve unresolved references in bundled tools outside the bin/lean static load graph. All installed bin/lib bytes remain bound. The permitted command uses OS /usr/lib/libc++.dylib; bundled lib/libc/libc++.dylib is not statically reachable. This is a static loader characterization, not a guarantee about arbitrary dynamic loading. A missing dynamic companion or native compiler requirement at launch is a charged first-failure stop.

The initial inventory assembler failure and early engineering/test failures remain in the diagnostic and validation records. The final controller/runtime acceptance tests passed before the first Lean launch.

The immutable checkpoint receipt lists 9 runtime tests; its bound raw log records 8. A separate receipt erratum preserves that counting error. Actual prelaunch totals were 20 controller plus 8 runtime tests, all passing.

**Recommendation:** Implement the explicit CVC-PREP-2 controller successor and complete only the remaining 10 upstream modules using the exact 27 prior successes as immutable inputs. Target: CVC-U1 complete 37-module upstream dependency bundle. Priority: HIGHEST_ELIGIBLE_NEXT. Prerequisites: Validated, committed and pushed CVC-PREP-1 bounded-unresolved closure; All 37 sources, full runtime and 119 predecessor outputs revalidate; Successor mixed-module/namespace and process/budget tests pass; Exact CVC-U1-DEPS-0002 manifest/controller/tests and ledger committed before 10 permitted launches.

Validate tracked evidence with `python3 results/research/conditional-validation-contracts/cvc-prep-1/validate-evidence.py`; add `--check-local` to verify the installed runtime and isolated payloads. No validator invocation launches Lean.
