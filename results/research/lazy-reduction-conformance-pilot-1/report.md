# Lazy reduction conformance pilot 1

The exact six conversion cases were accepted by both reduction profiles:
**12/12 ACCEPT, with all six KAM demand requirements satisfied.** The four
separate capability cells also matched: both controls accepted and both
candidates rejected at the exact reconstructed recursor-type comparison.
The [scientific result](result.json), [raw matrix](science-0001/result.json),
[independent object audit](artifact-audit.json) and [replay](evidence-replay.json)
bind the claims. Repository closure additionally requires the final validation
and refresh [receipt](final-closure/result.json).

| Frozen case | Substitution | KAM mode 3 | Observed KAM beta / let |
| --- | --- | --- | --- |
| beta | ACCEPT | ACCEPT | 1 / 0 |
| zeta | ACCEPT | ACCEPT | 0 / 2 |
| beta-under-let | ACCEPT | ACCEPT | 1 / 2 |
| let-under-beta | ACCEPT | ACCEPT | 1 / 2 |
| shadowed-binder | ACCEPT | ACCEPT | 2 / 0 |
| repeated-bound-variable | ACCEPT | ACCEPT | 1 / 0 |

All substitution machine beta/let counters were zero. Every scientific cell
reported one loaded and checked declaration, zero failures/unchecked declarations,
zero native operations, zero machine delta/iota/projection and zero fusion
rechecks. The counter requirement was frozen as a lower bound before execution;
the additional let count is retained, not retroactively made an exact expectation.
The independently checked declared types require beta/zeta head conversion to
the value's inferred type. These are closed numeric-universe Pi/lambda/app/let
terms with no constants or inductives. The producer directly encodes the audited
AST and identifies itself honestly; no Lean compiler/exporter process generated
these six files. They were generated once after committed contract/tooling/review
and committed with the exact twelve-cell manifest before observation.

The observer is lazylean v0.3.0 at
`68c66fa18c1afe029512b90ecfe0b162c0dcd8fb`, built on Darwin arm64 with the
independently reviewed [portability patch](portability-r1.patch). The patch
guards allocator/huge-page hints and an unavailable x86 profiling counter; it
changes no checking or reduction code. Both profiles use fresh processes,
one worker and the same explicit clean environment; `--engine subst` and
`--engine kam` with experimental `LL_KAM_MODE=3` are the only profile difference.
The build binds compiler, SDK interfaces, preprocessor closure, static GMP and
binary bytes. Host system C++/libSystem runtime comes from the recorded macOS;
this is host-scoped reproducibility, not a fully hermetic runtime.

The first host RSS preflight was denied before a child launch. An authorized
host retry retained the safety gate. The first controlled build compiled but
failed to link because resolving `clang++` to `clang` changed driver semantics
and omitted C++ runtime linkage. [R2](build-repair-r2.json) preserves the exact
failure and driver-name regression and succeeds with unchanged source/scientific
inputs. All 28 supervised processes (10 dependency scans, two builds and 16
checker cells) had positive RSS and complete cleanup. Development/classifier
review repairs, a metadata-only dry-link failure and its unretained diagnostic
limitation remain recorded; no attempt count was used as a stop condition.
Full [accounting](work-accounting.json) retains measured costs and unknown manual
time. Twenty-two focused tests pass, including negative graph/typing/output
controls and raw-evidence replay. The complete current/historical suite and
current-state refresh are separately required by the final receipt.

Retain this adapter, six demand-qualified regressions, independent auditor,
contracts and raw receipts locally at normal priority. The two profiles share
one implementation and source lineage; agreement supplies no independent
semantic authority, universal conformance or soundness result. Repeated bound
variables do not establish memoization benefit or separately forced uses.
No checker defect, benchmark or external action follows from this result.
Changed observer, source, runtime or scientific inputs require fresh exact
binding in an explicit successor.

The project-wide closure comparison selects `STATEFUL-VALIDATION-PILOT-1`
READY and unstarted. Its six fresh-versus-prefixed public-request comparisons
offer a distinct next conformance question. Public API, session/recovery and
dependency contracts must be established inside that item before its scientific
gates. Retained proof slicing, binder modeling and build/resource matrices remain
planned alternatives; held upstream follow-up and historical assurance limits
are unchanged. No successor work was executed here.
