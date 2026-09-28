# Source and reuse decision — 2026-09-27

Select one supported public API, `Lean.Kernel.Environment.addDecl`, at official
Lean 4.33.0, commit `d8b18978322de05a8f3dba51ef03cf5461676c17`.
The directly fetched tag receipt identifies that commit. Downloaded AddDecl.lean
and Environment.lean are byte-identical to this installed toolchain's sources.
The existing complete runtime inventory from the trust-assumption pilot is
reused by content binding and verified against the actual installation before
launch. This claims exact installed bytes, not a reproducible binary build.

`AddDecl.lean:23` exposes the checked API as a public definition returning
`Except Exception Environment`. The frozen options explicitly disable
`debug.skipKernelTC`; no unchecked insertion API is used. Environment.lean
documents non-destructive updates, unique names, the public constructor boundary
and the primitive `addDeclCore`. Each history starts from `mkEmptyEnvironment 0`
and extracts its kernel environment; imports used to compile the harness do not
become declarations in this separate empty environment.

`environment.cpp:180–190` checks safe definitions before producing a new
environment. `:287–295` returns through `catch_kernel_exceptions`; ordinary
kernel errors are explicit values. The adapter retains the input environment on
`.error`, never catches a panic and never retries a terminating process.
`type_checker.cpp:46` and `:1194–1214` show a fresh checker-owned state per
declaration, including name generation and caches. This API permits an
environment-history comparison, not a persistent cache stress experiment.
Declarations use explicit disjoint names except the preregistered duplicate
and rejected-name-reuse histories. The independent auditor verifies full
dependency order and all environment projections, including the existing
definition's type/body after duplicate rejection.

The CoreM `Lean.addDecl` wrapper is excluded. Its `AddDecl.lean:187–220` error
path deliberately tries to insert fallback axioms and rethrows; this is a
different contract, not rollback. No second wrapper is counted as implementation
independence. The plan permits at most two APIs; the live queue now uses the same
wording, with six comparisons unchanged.

Focused primary-source/reuse refresh used official Lean tag/source URLs and the
[Hypothesis stateful testing documentation](https://hypothesis.readthedocs.io/en/latest/stateful.html)
on 2026-09-27. The decision question was whether an existing state-machine
framework or retained project machinery should be reused. Hypothesis supports
model/state comparison but generated rule sequences and shrinking are not
needed for this fixed six-history pilot. Reuse its model-comparison discipline,
the project's positive-RSS supervisor, exact committed-byte gates and closure
automation. Build only the missing deterministic public-API harness and an
independent, negative-capable session auditor. No broad literature exhaustion,
global novelty or theorem claim follows.

Primary sources: [Environment API](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/Lean/Environment.lean),
[public wrapper](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/Lean/AddDecl.lean),
[kernel insertion](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/environment.cpp),
[checker state](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.cpp).

Preparation observations: first sandboxed `/bin/ps` preflight was denied with
EPERM; the same required preflight passed using the ordinary escalation path
(positive 14192 KiB sample). First sandboxed curl could not resolve the host;
the exact read-only downloads then succeeded with escalation. Neither attempt
launched a checker or constructed scientific fixtures. These are setup evidence,
not scientific failures; future supervised launches need the same host access.
