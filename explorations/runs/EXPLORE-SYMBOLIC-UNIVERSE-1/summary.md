# Six symbolic-universe cases

Lean and Nanoda accepted all six small declarations: twelve completed checks,
with no disagreement, crash or unsupported input. The actual parsed objects
retained the named universe parameters and symbolic expressions. Invalid
declarations were not tested.

This is useful modest coverage beyond the earlier numeric-level corpus, not a
new checker defect or a correctness result. In particular, the dependent-function
cases retain `imax`, the universe operation that returns zero when its right
operand is zero. They exercise its formation and a valid normalization; they do
not establish coverage of every internal comparison branch.

Keep these six cases as a normal-priority local conformance corpus. No upstream
action, confirmation experiment or larger formal model follows from this result.
The separately selected successor checks three invalid universe boundaries with
matched valid controls; it addresses rejection behavior missing from this sample
and remains unstarted.

| Case | Obligation | Lean 4.34.1 | Nanoda `3a24072` |
|---|---|---|---|
| P1 | `Sort u : Sort (succ u)`, declared parameter | ACCEPT | ACCEPT |
| P2 | Same result through a let-bound value | ACCEPT | ACCEPT |
| M1 | `succ(max u v) = max(succ u)(succ v)` | ACCEPT | ACCEPT |
| M2 | `succ(max u v) = succ(max v u)` | ACCEPT | ACCEPT |
| I1 | `Pi (X : Sort u), X : Sort(imax(succ u) u)` | ACCEPT | ACCEPT |
| I2 | Same Pi, replacing `succ u` by `max(succ u) 1` | ACCEPT | ACCEPT |

The source-derived expectations and exact bytes were recorded in the single E0
start before execution. These are hand-encoded standalone NDJSON declarations,
not elaborated source examples. Each file contains one safe definition, no
constants or axioms, and explicit universe parameters. The existing structural
auditor checked references. The actual Lean importer printed raw parsed types
and values before replay in a fresh empty environment with trust level zero.
The post-run analysis matches those prints exactly against the prospectively
recorded cases. Nanoda's source-bound parser inserts raw level constructors;
its selected-declaration output also preserves the symbolic forms. Both
validators received identical input bytes, checked before and after execution.

`max` normalization makes M1/M2's nonidentical level expressions equivalent.
The Pi rule computes I1/I2's inferred `imax` level. I2's redundant maximum can
normalize before a deeper `imax` comparison; no claim of forcing case splitting
is made. The six expected-ACCEPT cases supply no invalid-input detection rate,
independent fault transfer, statistical generalization or whole-kernel guarantee.

One setup attempt failed before scientific checking: Lake tried to reconcile a
dependency URL and was denied write access. Direct Lean invocation with the
retained compiled parser passed. That failed attempt remains intact. No
scientific retry, dependency download, Mathlib build, production checker change,
shared tooling change or full assurance replay was needed.

The twelve Docker-invocation durations total **5.299 seconds**; this includes
launch overhead and is not pure checker time. Ten supervised preparation,
matrix and cleanup attempts total **24.990 seconds**, including the repaired
preflight. These figures exclude model work and unsupervised document editing.
Task-level token/cost totals are unavailable. One bounded source-reading delegate
helped check the prospective expectations; no per-case reviews were added.
Host CLI memory observation does not measure guest checker peak memory.

Final cleanup found only the container's idle sleep process, then stopped it;
its PID is zero and `OOMKilled=false`. Container exit 137 is the intentional
stop of that idle init after checking, not a checker crash. All twelve checker
exits were zero, with empty stderr. The container remained network-disconnected.

The machine result is [result.json](result.json), the exact sample is
[cases.json](cases.json), and identities, controls and scope are in
[protocol.json](protocol.json). Per-check commands, raw streams and durations
are under [observations](observations/); all setup and cleanup attempts are
under [attempts](attempts/). `analyze.py` checks retained evidence without
launching a checker. `generate.py` reproduces the six inputs. `run_matrix.py`
records the exact guest invocations; reproducing execution requires the pinned
Lean/parser/Nanoda installations described in the protocol. Cached native-tool
preparation is retained in the preceding Comparator screen's
`setup_native_r3.sh` and `native-runtime-repair.json`.
