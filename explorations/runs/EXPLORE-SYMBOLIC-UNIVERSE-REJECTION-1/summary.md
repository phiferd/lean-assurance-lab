# Three universe rejection boundaries

Lean and Nanoda each accepted the three valid controls and rejected all three
invalid declarations: twelve expected outcomes, with no disagreement. The
invalid cases omitted a used universe parameter, lowered a declared sort level,
or replaced the dependent-function universe operation `imax` with `max`.
Nanoda's three rejections used explicit assertion panics, which remain visible
in the results rather than being described as clean exit-code rejections.

This is useful modest coverage of nearby invalid inputs, complementing the
earlier all-positive screen. It found no checker defect. It does not measure a
general fault-detection rate, all universe identities, or kernel correctness.

Retain the three small invalid variants with their existing controls as a
normal-priority local corpus. No production change, upstream action or automatic
confirmation follows. The separately selected, unstarted successor assesses
whether the accumulated cases add useful coverage beyond existing Nanoda/Arena
tests before proposing more cases or a contribution.

| Case | Expected | Lean 4.34.1 | Nanoda `3a24072` |
|---|---|---|---|
| P1 | ACCEPT | ACCEPT | ACCEPT |
| Pbad: omit the used parameter `u` | REJECT | Undefined-universe error | Parameter-guard assertion |
| M1 | ACCEPT | ACCEPT | ACCEPT |
| Mbad: lower the declared maximum level | REJECT | Declaration-type mismatch | Type-equality assertion |
| I1 | ACCEPT | ACCEPT | ACCEPT |
| Ibad: substitute `max` for `imax` | REJECT | Declaration-type mismatch | Type-equality assertion |

The P1/M1/I1 control files are byte-identical to the preceding screen. Each
invalid twin changes exactly one NDJSON record. For Pbad, every use of `u`
remains while its declaration parameter list is empty. For Mbad, `Sort(max u v)`
is incorrectly assigned type `Sort(max u v)` instead of
`Sort(succ(max u v))`; at `u=v=0` the levels differ by one. For Ibad, the Pi
`forall (X : Sort u), X` infers `Sort(imax(succ u) u)`; at `u=0` that level is
zero, while `max(succ u) u` is one. These are prospective source-derived
arguments, not labels inferred from checker agreement. The zero substitutions
explain invalidity; no extra instantiated cases were run.

The six exact files, expected outcomes and tool identities were recorded in
one E0 start before checker observation. The unchanged raw Lean adapter printed
the parsed parameter list, type and value before fresh empty-environment
kernel replay at trust level zero. All six prints match the recorded cases
exactly, including the rejected declarations. Nanoda's current parser source
hash matches its pinned raw-constructor implementation; the expected errors
occur in its checking code, not its parser. Both validators consumed the same
files, whose guest hashes were verified before and after checking.

Lean's invalid calls exited 1 with the intended undefined-parameter or
declaration-type-mismatch diagnostic. Nanoda exited 101 at `tc.rs:554` for
`all_uparams_defined`, and `tc.rs:955` for `assert_def_eq`. These are its
source-attributed rejection mechanisms. An unrelated panic or generic nonzero
exit would not have qualified. There were three expected assertion exits, zero
unexpected crashes, zero unsupported inputs and zero scientific retries. No
runtime branch-coverage or independent-fault holdout claim is made.

The initial preparation attempt found Docker's daemon stopped. Starting Docker
Desktop restored the existing cached profile; both attempts are retained.
No toolchain build, dependency download, Mathlib build, new general harness,
shared tooling change, formal model or full assurance replay was needed.
Cleanup found only the idle container init, then stopped it: PID zero,
`OOMKilled=false`, network map empty. Its intentional idle-init stop exited
137 after all checker processes had finished; this is separate from their
recorded exits.

The twelve recorded Docker checker invocations total **10.053 seconds**,
including launch overhead and a cold first Lean call. Six supervised
preparation/matrix/cleanup attempts total **15.219 seconds**, with one repaired
preparation failure. These are process durations, excluding model work and
document editing. Task-level token/cost totals are unavailable. No delegate or
model call ran in the execution/analysis loops. Host CLI supervision does not
measure guest checker peak memory.

The canonical result is [result.json](result.json). Exact cases and arguments
are in [cases.json](cases.json), and source/binary identities, controls and
prospective rejection classification are in [protocol.json](protocol.json).
All twelve command records, raw streams and elapsed times are under
[observations](observations/); preparation and cleanup attempts remain under
[attempts](attempts/). `analyze.py` rechecks the retained evidence without
launching validators. `generate.py` recreates the exact three controls and
single-record invalid variants; `run_matrix.py` retains the execution recipe.
The raw replay adapter, official source excerpts and cached-profile build
provenance are reused unchanged from `EXPLORE-SYMBOLIC-UNIVERSE-1`.
