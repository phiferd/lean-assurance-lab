# Imported-expression typing before comparison screen

**What did we find?** A source review leaves one small unchecked-inference
reachability question at ordinary checked declaration admission. No new checker
case has run. The earlier Nat-based sketch depends on declarations absent from
the retained empty-environment replay, so this campaign uses closed sort terms
to preserve the same ignored-argument typing fault without adding an import or
axiom.

**Is it interesting?** Yes. Beta reduction can erase an ill-typed argument
before a semantic comparison. A checked declaration must still establish the
argument's typing precondition. A fixed paired screen can reveal an unexpected
acceptance or characterize the reachable check order in two implementations.

**Does it require more work?** Bind and audit six raw inputs and the exact Lean,
Nanoda, importer, configuration and runner bytes; append one E0 start before
checker observations; then execute exactly the twelve paired cells. The screen
does not begin E1 confirmation or an external action.

Evidence class: E0
Campaign: `E0-EXPRESSION-PRECONDITION-SCREEN-1`.
Trial: `EXPLORE-EXPRESSION-PRECONDITION-1`.
Frontier: `F-DISCOVERY-AND-CONFORMANCE`.

## Fixed question and sample

Do official Lean and Nanoda reject a closed ordinary definition when an
application argument has the wrong type, even though the applied lambda ignores
that argument and its result reduces to an otherwise valid expression? Place
the application in exactly three positions: definition value (V), declared type
(T), and the domain of a Pi in the declared type (B). Each negative changes one
argument node from its matched valid control. The six expression trees and
expected outcomes are:

```text
P = Sort 0                 P : Sort 1
U = Sort 1                 U : Sort 2
Fv = (fun (_ : U) => P)    Fv : U -> U
Ft = (fun (_ : U) => U)    Ft : U -> Sort 2

V-control   : U               := Fv P       ACCEPT
V-negative  : U               := Fv U       REJECT
T-control   : Ft P            := P          ACCEPT
T-negative  : Ft U            := P          REJECT
B-control   : (x : Ft P) -> U  := fun x : U => P   ACCEPT
B-negative  : (x : Ft U) -> U  := fun x : U => P   REJECT
```

Each negative attempts to pass `U : Sort 2` to a lambda requiring an argument
of type `U`. Each control passes `P : U`. Beta reduction discards either
argument, returning `P` from `Fv` or `U` from `Ft`; that reduction alone cannot
justify typing the application. The sample has no named constants, axioms,
recursors, metavariables, free variables or universe parameters. It tests
application typing, not the earlier symbolic-universe-level cases.

The [dated scope review](../../results/research/expression-precondition-screen-scope-2026-11-09/report.md)
motivates this sample. Its Nat names are replaced *before* trial start solely
because the preserved one-declaration empty-environment replay contains no
Nat declarations. This change does not broaden the three placements or twelve
planned cells. Do not treat the predecessor sketch as a scientific observation
or silently replace any of these six trees after start.

## Entry, input and launch gates

1. The selected campaign must be ACTIVE in the canonical queue, Active status
   and this plan together. Review the pinned Lean, Nanoda and lean4export source
   paths and local/upstream overlap. Retain exact supported runtime, parser,
   source, configuration and supervisor identities. The retained Lean 4.34.1 /
   Nanoda `3a240721` isolated container is the proposed reuse target only if
   its bytes, process controls and stopped-container state verify. Do not move
   to a different revision or build as an unrecorded fallback.
2. Use the existing raw 3.1.0 encoder and structural decoder, extended only in
   a task-local generator for `lam` and `app`. Generate six one-definition files
   and matching Nanoda configs. A read-only independent audit must verify the
   exact expression trees, one-node control/negative change, empty environment,
   parser support and expected type argument *before* any checker call. Bind
   SHA-256 of every scientific input and task-local runner. The official raw
   importer must print the actual parsed structures before replay; Nanoda's
   parser preservation may be supported by bound source and input identity.
3. Append a valid E0 start event to `explorations/ledger.jsonl` before any
   checker launch. Its source revisions, versions, commands, inputs, fixed
   sample, controls and signal criteria must match the audited files. Retain
   every failed setup, parser, audit and launch attempt. Commit a prelaunch
   checkpoint if required by the runner's immutable-input gate.
4. Run each of the twelve cells in a fresh supervised process. Use the existing
   resource-envelope supervisor with a per-process deadline, memory observation
   and cleanup; stop new launches on accounting or cleanup failure and repair
   feasible engineering faults within this campaign. Verify source/runtime,
   input and command identities at launch. The checker must report an attributed
   ordinary definition result, not merely exit zero or nonzero.

## Classification and closure

An expected result is three valid controls ACCEPT and three negatives REJECT
on each checker. A source-attributed checker assertion may count as a rejection
while preserving its panic transport. Parser refusal, wrong parsed shape,
unrelated crash, timeout, missing accounting or missing declaration identity is
not a rejection. Record the first attributable failing stage; a final rejection
alone does not show that the final comparison was reached.

Close SIGNAL only for an unexpected checked-definition acceptance of a negative
with intact bad application, a passing paired control, a sound independent
typing argument and complete supervision. This is a candidate, not a confirmed
defect. A later E1 experiment requires separate selection, independent input
and expectation review, fresh execution and its own confirmation gates. Close
NO_SIGNAL only with all twelve attributable expected cells. Otherwise close
INCONCLUSIVE with the exact missing observation or capability boundary.

Retain one E0 start/finish pair, raw outputs and attempts, a concise result and
one project-wide campaign handoff. Run the exploration ledger and diff checks,
then `scripts/exploration-handoff --base <pre-campaign-commit> --write` and
`--check`; commit on `main` and deliver through `scripts/push-main`. No full
assurance refresh is required solely for ordinary E0 closure. Shared tooling
changes retain their normal tests and gates. Stop after selecting, but before
starting, the separate successor.

No mutant, checker source change, Nat import, recursor witness, eta replay,
new case family, version sweep, Mathlib build, conformance/correctness claim or
external write is in scope. Process limits are safety controls, not attempt
budgets or scientific stopping conditions.
