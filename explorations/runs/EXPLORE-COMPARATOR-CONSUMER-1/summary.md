# One-endpoint Comparator screen — 19 October 2026

The clean `OAI.WitnessedChoice.main` endpoint passed both actual checking paths.
The additional LAL check passed that baseline and rejected all four controlled
checking, identity and freshness failures. This is useful integration evidence:
a consumer's success message needs to be tied to the independently requested
object and executable. Retain the small adapter for LAL's Comparator receipts;
no upstream defect report, automatic confirmation or larger proof replay follows.

Evidence class: **E0, SIGNAL** — one bounded integration signal, not four bugs.
Four real Comparator executions and one offline receipt control completed.

| Scenario | Native consumer and observed checking | Additional LAL check |
| --- | --- | --- |
| Clean baseline | Success; pinned Nanoda completed with exit 0; Lean replay accepted | PASS |
| Requested Nanoda omitted | Success, including “nanoda kernel accepts”; the configured no-op ran, real Nanoda did not; Lean accepted | FAIL: missing pinned checker invocation/completion |
| Valid target substituted | Success; both checkers accepted `Nat.add_comm`, as the altered config requested | FAIL: original target/config and exact artifact identities differ |
| Supporting proof changed | Success; both checkers accepted the same main statement after a harmless `id` wrapper changed a direct supporting proof | FAIL: bound source dependency and export identities differ |
| Old success used for a fresh request | No native execution: Comparator has no receipt-consumption interface. The baseline's historical success record was presented to the local check | FAIL: fresh execution identity differs |

These are controlled violations of the outside request. Comparator trusts its
configuration and configured external executable; following a changed config or
a successful configured program is within that native contract. No published
false assurance claim or past run was reproduced. The stale-control JSON retains
historical invocation facts; its explicit `native_run` field says that no fresh
native run occurred.

The baseline checked export contains 40,520 declared constant names and exactly
`Classical.choice`, `Quot.sound` and `propext` as declared axioms. Its type is
`OAI.WitnessedChoice.BGS.MainStatement`. The changed-proof export has the same
count, type and axioms, with a different hash. The streaming inventories found
no unresolved actual constant/projection dependencies. The full export includes
extra requested built-ins and permitted axioms; it is a bound checking
environment, not a claim of a minimal theorem-only dependency closure. The
trusted challenge's `sorry` placeholder was never the submitted solution proof.

Exact source selection, exclusions and revisions are in [selection.json](selection.json).
The independent request and successful baseline identities were retained outside
the proof workspace before fault launches. The final profile used official Lean
4.34.1, Comparator `d03acab`, exporter `076e8e5`, Nanoda `3a24072`, and real
Landrun 0.1.17, under a non-root user with networking disconnected. Comparator's
only tracked source adaptation was its toolchain patch from 4.34.0 to 4.34.1.
The minimal workspace preserved the 27 published OAI modules, trusted challenge,
Mathlib pin and `autoImplicit=false`; unused release dependencies were omitted.
See [native runtime repair](native-runtime-repair.json) and the retained recipes.
The old True-fixture sentinel could not be used unchanged: its exact-identity
contract was applied through a small local adapter, while the existing slicer
helpers and process supervisor were reused. No shared framework or schema changed.

Setup failures and interrupted attempts are retained in `attempts/` and
[setup-incidents.txt](setup-incidents.txt). The incomplete emulated build supplied
no verdict; the native attempt reused completed compilation cache and checked
freshly. Both task containers are stopped with PID 0 and no OOM event. Their
local caches remain in the final control state and need identity checks before
reuse. Raw exports/logs are losslessly compressed; [packed-evidence.json](packed-evidence.json)
records original paths, sizes and hashes. Source snapshots with whitespace were
also compressed without altering their bytes. Runtime archives and compiled
caches remain local ignored payloads, reacquirable only by their pinned identities.

Observed cost: 158 supervised commands across preparation, inspection, execution
and retention; 5,702.645 summed child seconds (overlapping), over a 5,584.508-second
observed wall span. The four completed Comparator runs took 450.43, 168.41,
51.16 and 219.13 seconds. These are not comparable standalone performance trials.
Aggregate parent/delegate token use and guest checker memory peaks are unavailable;
no dollar or efficiency estimate is made.

For LAL's next Comparator receipt integration, the normal-priority action is to
bind the original config, source/export identities, pinned checker executable
and actual completed run. It requires a trusted reference request and observer
outside the proof-producing workspace. The retained adapter demonstrates this
bounded contract; no general receipt service is selected. E0 observations supply
no kernel-correctness, informal-meaning or independent-holdout claim.

The separate next item is a [six-case symbolic-universe screen](../../../docs/research/E0_SYMBOLIC_UNIVERSE_SCREEN_1_PLAN.md),
selected READY and unstarted. It targets a controlled rule-coverage gap in the
closed-numeric term pilot using tiny standalone declarations, rather than another
large external proof build. Independent transfer keeps its existing supplied-input
gate; semantic-fidelity work stays deferred.

To inspect compressed streams, use `gzip -dc <path>.log.gz`. From the repository
root, `python3 explorations/runs/EXPLORE-COMPARATOR-CONSUMER-1/check_observations.py`
rechecks the retained identity matrix without launching kernels. The streaming
inventory script also accepts `.ndjson.gz`. Fresh scientific reproduction needs
the pinned tools/sources, the retained setup/control recipes and new executions;
this readback is not fresh confirmation.
