# Valid dependent-term pilot 1 result

Status: **SUCCESS**

The pilot produced its complete fixed positive suite: 50 distinct closed terms,
with ten each in the Pi, lambda, application, let and mixed categories. Every
case carries a full derivation under the frozen checker-neutral rules. The
separate auditor replayed all derivations, recomputed typing, substitution,
beta-zeta normalization, category predicates and metrics, and passed the exact
corpus before observer execution.

The source module was compiled once and exported as 50 independent
one-declaration format-3.1.0 artifacts. The checked-object bridge reconstructed
every expression DAG and matched the generated term and normalized expected
type. The committed execution manifest then ran exactly 100 cells: every case
under official Lean 4.33.0 and Nanoda `6ae1f0c`.

| Observer | ACCEPT | Other outcomes |
| --- | ---: | ---: |
| official Lean 4.33.0 | 50 | 0 |
| Nanoda `6ae1f0c` | 50 | 0 |
| **Total** | **100** | **0** |

No conformance difference was observed in any category. This is a bounded
positive result for the exact corpus and profiles; checker agreement is not
semantic authority and makes no correctness claim outside the fragment.

Two preparation failures were preserved as engineering evidence rather than
scientific outcomes. Attempt 1 stopped before launch because the sandbox blocked
the supervisor's `/bin/ps` memory audit. Attempt 2 built and independently
audited all cases, then exposed a checked-object parser defect: ordinary Lean
definitions use the documented `{"regular": n}` reducibility-hint form. A
focused regression and a new tooling revision repaired that parser without
changing the design, seeds, terms or selection rule. Attempt 3 prepared the
unchanged corpus successfully; no target checker observed a case until its
corpus and 100-cell manifests were committed.

Retain the generator, independent auditor, corpus, exporter bridge and guarded
runner as a local positive-conformance asset. They are suitable for exact
regression replay when supported checkers change. No external contribution is
recommended from this all-accept result alone; upstream packaging would require
a concrete consumer, fresh duplicate and maintenance review, and separate human
authorization.

Canonical evidence is in [result.json](result.json), with the exact corpus in
`corpus/valid-dependent-term-pilot-1/` and raw matrix receipts in
`checker-run-0001/`.
