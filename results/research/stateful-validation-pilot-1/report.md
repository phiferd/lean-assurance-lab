# Stateful validation pilot 1

The fixed six comparisons preserved their expected relations on official Lean
4.33.0's public `Lean.Kernel.Environment.addDecl` API. All twelve fresh-process
histories matched the independent model for every one of 25 ordered requests:
22 acceptances and three expected rejections, including all twelve targets
accepting. Every complete environment projection matched. The prospective
SUCCESS closure becomes complete only after its required full-suite/refresh
receipt and verified main delivery.

| Comparison | Observed prefixed history | Preserved relation |
| --- | --- | --- |
| Accepted independent definition | A accepts; target accepts | Same closed identity target |
| Accepted conversion prefix | Alias and Reduced accept; target accepts | Same alias-dependent target |
| Rejected malformed definition | `declTypeMismatch`; target accepts | Rejected Bad remains absent |
| Rejected duplicate name | A accepts; `alreadyDeclared`; target accepts | Original A type/body retained |
| Rejected name reuse | `declTypeMismatch`; same-name valid target accepts | Rejection does not reserve name |
| Independent declaration order | B then A then target all accept | Matches A then B then same target |

The [scientific contract](scientific-contract.json) fixes every request AST,
dependency, option and expectation. Each history starts from an empty kernel
environment with trust level zero and checking explicitly enabled. The harness
updates its environment only from `Except.ok`; an ordinary `Except.error`
preserves the immutable caller input. Actual reconstructed requests and complete
sorted name/type/value/safety/universe projections are recorded after every
step. The separate auditor derives bounded typing/conversion expectations and
rejects missing, extra, reordered or altered records. The
[execution manifest](execution-manifest-r4.json), [raw receipts](execution-0001/result.json)
and [read-only replay](evidence-replay.json) bind the exact evidence.

Two generic harness compilation failures occurred before any scientific request:
record-literal syntax and an unavailable `Options.setNat` API. R2 and R3 preserve
both failed attempts and repair only tooling. A late second review then found
that the original generation gate lacked canonical manifest identity checks.
The [incident](generation-control-incident.json) retains the initial protocol
PASS, subsequent FAIL and timing. Both reviewers independently verified that
the actual twelve generated files already matched the exact frozen inputs.
R4 adds strict canonical checks and negative tests, disables regeneration and
[adopts those same bytes](artifact-adoption-r4.json) under a new reviewed gate.
No scientific input was replaced and no scientific execution preceded both R4
launch reviews.

The [accounting](work-accounting.json) records three generic compile attempts
and twelve scientific processes: 15 supervised processes, 518 positive RSS
samples, 17.226 cumulative process seconds, maximum observed RSS 1,340,817,408
bytes and complete cleanup throughout. The scientific batch's observed wall
interval was 24.537 seconds. Manual reading, implementation and review duration
was not instrumented and remains unknown. Counts and time never served as
termination limits. Twenty-three focused audit, custody, repair and closure
regressions pass before the required complete current/historical suite.

Retain the exact harness, independently implemented auditor, twelve history
files and receipts as a normal-priority local regression asset for callers of
the official kernel API. Reuse requires exact source/runtime/options and
scientific/tooling bindings; changed inputs require a new explicit binding.
No supported relation violation was observed, so no external issue, patch or
disclosure follows.

This is one implementation and one functional public API, not independent
checker agreement or a soundness proof. Checker caches and fresh-name state are
per declaration; the study does not stress persistent caches. It makes no claim
about CoreM `addDecl` (which has fallback-axiom behavior), command elaboration,
server sessions, panic recovery, general history invariance or performance.

The whole-project review selects `REAL-PROOF-SLICES-PILOT-1` READY for its
retained-source/reuse, dependency closure and fixed selection preparation.
Its bridge from synthetic cases to real library artifacts offers more new
shared value than expanding this preserved small fragment or starting a new
binder model. Existing corpus provenance limitations and all assurance gates
remain unchanged. The successor is not started in this one-item request.
