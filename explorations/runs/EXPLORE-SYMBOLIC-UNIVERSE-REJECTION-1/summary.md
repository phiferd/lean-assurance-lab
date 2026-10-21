Both checkers accepted all three valid controls and rejected all three invalid
variants: six accepts and six expected rejections in twelve fresh calls. The
fixed E0 screen closes **NO_SIGNAL**. No unexpected acceptance, parser failure,
unsupported input, diagnostic crash or timeout was observed.

Yes, this is modestly useful: it adds three concrete rejection boundaries to
the earlier positive-only symbolic-universe sample. Agreement on these tiny
cases does not establish soundness, a fault-detection rate or behavior outside
the two pinned profiles.

Retain the exact three invalid/valid pairs as a normal-priority local boundary
corpus. No checker fix, confirmation experiment or external action follows from
this result. No further experiment starts here. The campaign handoff assesses
the existing queue separately; it must not invent a follow-on experiment.

| Input | Expected | Official Lean 4.34.1 | Nanoda `3a240721` |
| --- | --- | --- | --- |
| P1 valid: declared universe parameter | Accept | Accept | Accept |
| P1 invalid: used parameter omitted | Reject | Undefined universe parameter | Expected checker assertion at `tc.rs:554` |
| M1 valid: successor/max sort level | Accept | Accept | Accept |
| M1 invalid: sort level lowered | Reject | Declaration type mismatch | Expected checker assertion at `tc.rs:955` |
| I1 valid: Pi universe uses imax | Accept | Accept | Accept |
| I1 invalid: imax replaced by max | Reject | Declaration type mismatch | Expected checker assertion at `tc.rs:955` |

Nanoda implements these rejections with Rust assertion panics. All three
diagnostics match the prospectively reviewed semantic check and source line;
they are recorded as `EXPECTED_CHECKER_ASSERTION_PANIC`, not hidden or treated
as unrelated diagnostic crashes. A nonzero exit alone was not used as a verdict.
Lean's raw parsed output exactly matches each frozen declaration, including
the empty universe-parameter list and both altered sort expressions. Nanoda
preservation is supported by its exact parser source and byte-identical input,
not by a runtime AST dump: it checks before pretty-printing.

The controls are unchanged predecessor bytes. Each invalid input changes one
JSON row. The [input review](input-review.md), [protocol](protocol.json) and
[cases](cases.json) were bound in the prospective E0 start before the matrix.
The unchanged importer, encoder conventions, structural auditor, cached parser,
official Lean and Nanoda binaries, and resource supervisor were reused. The
analysis checks the exact twelve raw outputs, original input bindings,
before/after runtime and input hashes, and complete supervisor receipts.
No production checker or shared tooling was changed.

The twelve checker invocations took 5.285233 aggregate host-observed seconds.
Ten supervised setup, matrix and cleanup operations took 19.081053 receipt
seconds, including the ten-second container stop. All completed without a
monitor error, timeout or unresolved cleanup. The guest process listing had
no remaining checker process before stopping; the reused container was returned
to stopped state, non-OOM, with exit 137 from stopping its `sleep infinity`.
That container exit is not a scientific checker result. No scientific retry,
large build or full assurance replay ran. Host CLI memory observations do not
measure guest checker peak memory. Task-level token and monetary cost are
unavailable.

An initial broad container-configuration read was denied because it could
expose environment secrets. A narrower approved command/mount inspection
resolved reuse eligibility without reading environment variables. Two local
queue preflight failures exposed a missing ignored historical fixture in the
isolated checkout and a stale READY table row; copying the already retained
fixture and updating the ACTIVE row resolved them before the ledger start.
Neither failure launched a scientific checker.

Raw output and upstream sources retain their original whitespace. The local
`.gitattributes` exempts only four copied source files and the `PARAMS ` raw
output from formatting checks; it changes no evidence bytes or semantic checks.
