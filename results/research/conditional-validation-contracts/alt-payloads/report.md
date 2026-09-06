# ALT-PAYLOADS: exact offline dependency repair proposal

2026-09-06 · **SUCCESS for the diagnostic proposal** ·
`STATIC_DEPENDENCY_REPAIR_PROPOSAL_UNEXECUTED`

Prepare the CVC-U1 upstream dependency bundle from the existing local donors,
then implement its separate proof runner. The static closure contains **37
modules: 12 Lean4Lean and 25 Batteries**. No build, Lean/Lake invocation,
download, toolchain installation, Lab elaboration or checker launch ran.
This result establishes a concrete preparation path; compilation and the
conditional preservation theorem remain untested.

The canonical [proposal](proposal.json) fixes paths, pins, command arguments,
finite budgets, failure accounting, entry gates and acceptance checks. The
[source closure](source-closure.json) fixes every selected source identity,
import edge and dependency-first order. Its read-only
[inspector](inspect-source-closure.py) reproduces the local donor checks.

## What the diagnosis changes

The older CVC-2 import regex did not handle `meta`/`public meta` imports. Following
those edges adds `Batteries.CodeAction.Deprecated`, `Batteries.Lean.Position`,
`Batteries.Lean.Syntax` and `Batteries.Tactic.Lint.Basic` to its 33-module list.
The successor retains that negative finding; the prior inventory is unchanged.
The final proposal budgets all 37 source compilations, including modules that
already have donor outputs, to avoid mixing provenance from old builds.

All twelve selected Lean4Lean source files match the retained target-tree blobs
at `8223d223ed98661882e95d9d6a7126df7097cd76`. The available checkout remains
`ecb3b6661c14f8147be1069b126c629114baf4a8`; it is not a full checkout of the target.
The proposed bundle is explicitly that target-byte subset. Batteries comes
from its exact local `76e1c118b0700b4ceafe99532e887d6431625e1a` checkout.

The donor Lake configuration additionally requires Lean4Export, while the
target manifest requires only Batteries. The proposal uses one merged source
root and the installed absolute Lean 4.33.0-rc2 binary in dependency order.
It invokes no Lake resolver, network acquisition or native compiler. Static
source inspection supports this command shape; actual compatibility remains
a charged preparation question.

## Concrete next item

Select **CVC-PREP-1**, a bounded implementation and preparation item. It first
implements the narrow preparation controller and inert tests, verifies/copies
only the selected sources into `external/cvc-u1-dependencies-0001/src`, and binds
the full installed runtime `bin`/`lib` contents and loader/platform boundary.
It commits the controller, passing tests and exact source/runtime execution
manifest before the first compiler invocation.

The controller's proposed interface is
`scripts/prepare-cvc-u1-dependencies --manifest config/cvc-u1-dependencies-0001.json`.
That interface does not exist yet. Its per-module command is fixed as an argv:

```text
<bound absolute lean binary> -o <repository>/external/cvc-u1-dependencies-0001/build/lib/lean/<module-path>.olean <module-path>.lean
```

The working directory is the isolated `src`; both `Lean4Lean/` and `Batteries/`
are beneath it. The exact environment, including isolated output and bound core
roots in `LEAN_PATH`, is in the proposal. Preserve every emitted module companion,
including private/server and IR files, alongside hashes of logs and outputs.
The source files themselves are unchanged.

CVC-PREP-1 has two 90-minute sessions, at most 37 compiler invocations, at most
300 seconds per invocation and 6,600 cumulative compilation seconds. All caps
apply together. Its inert controller tests have a separate 80-launch, five-second
per-process, 400-process-second ceiling within the same active-time budget.
Reservations precede launch; failed starts and interruptions count. Stop on the
first failed module, unexpected dependency/native-compilation need, identity
mismatch or exhausted bound. No failed module gets a free retry.

The separate **CVC-RUNNER-1** proposal remains PLANNED. It allows two 90-minute
sessions and only inert process fixtures (80 launches, five seconds each,
400 process seconds total). Reuse the existing campaign's locking, gated spawn,
termination and copy patterns, but retain its closed-frontier authorization.
A new runner must enforce the fixed CVC-3 signature/proof sequence, immutable
inputs, session/attempt budgets, axiom audit, crash-safe resume and result checks.
Fixture tests validate control logic; they do not establish theorem truth.

CVC-3 remains PLANNED. Its first Lab signature elaboration is counted attempt 1;
at most eleven proof invocations remain afterward. Dependency preparation,
runner implementation and later proof effort retain separate ledgers and an
aggregate phase-cost account. No signature repair or axiom-policy change is
included in this proposal.

## Stopping-point decision and limits

CVC-PREP-1 ranks first because local pinned sources support a finite repair of
the known dependency gap. CVC-3 lacks that bundle and its tested runner. Arena
follow-through remains blocked on the recorded CLI authentication failure;
there is no new upstream disposition or urgency evidence. Survivor and transfer
alternatives remain outside this phase. Same-day CVC-1 literature/reuse evidence
is still relevant; this proposal adds no semantic family or formal method.

The runtime binary and version header are bound, but a complete runtime and
loader manifest is explicitly required before any preparation launch. Static
import closure does not prove elaboration success, actual axiom closure or
executable-validator refinement. A missing donor or compilation failure must
produce a bounded unresolved successor record, not an implicit download,
source repair, larger budget or broadened claim.

No external issue or publication is warranted by this operational result. The
recommendation targets local reproducibility. Close and deliver ALT-PAYLOADS,
select CVC-PREP-1 READY, and stop without starting it. Exact gate commands and
outcomes are recorded in
[validation.json](../../../workflow-refresh/alt-payloads-2026-09-06/validation.json).
