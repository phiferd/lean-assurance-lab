# Nanoda constant-application congruence fault screen

What did we find? A one-line intentional fault in current Nanoda changes one explicit invalid declaration from rejection to acceptance, while its matched valid control remains accepted. Nanoda's existing 44 unit tests all pass under that fault. A minimal local regression test passes on baseline, fails under the fault, and the baseline full suite passes with 45 tests.

Is it interesting? Yes, as a narrow corpus-coverage result. It shows that the public declaration path reaches an equality helper excluded from the current mutation surface and that the existing tests do not protect this argument-congruence condition. It does not identify a defect in production Nanoda: the bad behavior exists only after deliberately deleting a required check.

Does it require more work? The three-file regression candidate is useful enough for a separate human review and, if desired, fresh confirmation before any upstream proposal. E0 itself authorizes no upstream action. No broader mutation campaign is justified by this single result.

## Evidence

The exact source is `ammkrn/nanoda_lib` `3a2407216ee84a75f9e1aead6803d0578be06ae7`. The retained fault removes only the `all(self.def_eq)` application-argument conjunct from `try_eq_const_app`; heads, hints, arity, universe comparison and failure-cache conditions remain unchanged.

The fixture defines opaque constants `A : Type`, `B : Type`, regular `F (X : Type) : Type := X`, and `v : F A`. The control is `ok : F A := v`; the candidate is `bad : F B := v`. Baseline ACCEPT/REJECT and fault ACCEPT/ACCEPT establish that the sole changed guard decides the public declaration verdict. Distinct opaque constants have no conversion rule, and the explicit axioms do not assert `A = B` or assume the result.

The NDJSON was hand-authored against the documented 3.1.0 format. Its embedded Lean/exporter metadata is format metadata and does not show that official Lean generated or validated the fixture. Public-path reachability is a source-based causal inference from the sole-source-difference verdict change, not an instrumented branch trace.

All eleven host-observed attempts have complete cleanup and no monitor/accounting faults. The first sandbox attempt was killed before compilation when `/bin/ps` was denied; it is retained. One first focused-test command selected zero tests because of an incomplete exact name; its corrected replay selected one test and is retained alongside it.

The existing faulted suite passed 44 unit tests with zero failures and ignored eight doctests. The regression patch applies cleanly to the exact source, passes one focused test and the 45-test full suite on baseline, and fails under the fault with `test did not panic as expected`. Raw stdout, stderr and resource receipts are under `attempts/`.

## Claim boundary

This is E0 fault-injection evidence about one helper, one revision and one explicit public input. It is not C++ kernel verification, a Lean or Nanoda vulnerability, an exploit, compiled-checker parity, arbitrary congruence coverage, or a production bug report. The local patch is not posting-ready prose and no community message or external repository write was made.
