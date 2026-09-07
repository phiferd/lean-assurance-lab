# CVC-A7-REPAIR-1 — checked conditional bridge

Outcome: **SUCCESS**, under conditional model `CVC-U1-A7`.

The repaired parser accepted a fresh counted baseline with all nine independent
type pairs and both exact seven-assumption comparator reports. The first proof
attempt then checked the original `EncodingTarget`, `PreservationTarget`,
`AcceptanceTarget` and `BoundaryTarget`. The two positive examples and the zero
and unowned-name rejection boundaries are included in those fixed obligations.

`encoding_preserves` uses `propext` and `Quot.sound`. The other three Lab results
use exactly the reviewed seven assumptions. No `sorryAx`, new axiom, target
change or native-evaluation trust was introduced. The signature and original
meaning are unchanged. See [result](result.json), [proof](run-0002/attempts/03/CVC2Proof.lean)
and [raw axiom reports](run-0002/attempts/03/stdout).

The immediate blockers were engineering defects: universe-decorated names,
wrapped transcript headers, generated style warnings, lookup simplification and
missing decidability instances. The source repair uses existing completeness
lemmas and explicit propositions. New accounting checks also prevent erasing
previously observed work. Forty-four focused checks passed before any new Lean
launch; failed mocked-test setup output remains in `engineering-diagnostics/`.
All old attempts, parsers, contracts, allowlists and historical results remain
unchanged; the earlier baseline failure was not retroactively accepted.

The item used 3 builds (signature, baseline, proof),
1191.641326 active seconds including all engineering work,
and 4.791141 compiler seconds. A7 totals including the
prior failed run are 5 builds and
1247.239069 active seconds, below six builds and
7200 seconds. Including original CVC-3, seven builds were consumed. One remaining
build is unused and this successful run is terminal. No resource cap caused the
stop. Administrative closure and its bounded inert test fixtures are separately
recorded in the [validation record](../../../workflow-refresh/cvc-a7-repair-1-2026-09-07/validation.json).

This proves a structured model connection under the named assumptions. It does
not prove arbitrary-byte decoding, importer behavior, executable validator
refinement, runtime correspondence, or the assumptions themselves. The next
item, `CVC-4-CONDITIONAL`, is READY and unstarted: connect the checked statement
to exact artifact bytes and implementation behavior. The original CVC-4 remains
PLANNED because its original CVC-3 SUCCESS dependency is still unmet. No upstream
action is supported solely by this local proof.
