# OPS-UPSTREAM-1: Arena disposition check

Recorded 2026-09-06. Outcome: **BOUNDED_UNRESOLVED**.

The required `scripts/github-cli-preflight leanprover/lean-kernel-arena`
failed with GitHub CLI authentication unavailable. The repository's
`docs/AGENT_WORKFLOW.md` requires stopping upstream access at that failure.
No disposition or duplicate-inventory GET request ran. Current Arena status
and changes since the prior record are **unknown**, not “no change.”

The exact output is retained in [preflight.log](preflight.log); session,
input-commit bindings, and unused budget are in [work-record.json](work-record.json).
The canonical [status packet](status-packet.json) preserves the last known
external-action record from 2026-09-05T21:56:24Z:

| Target | Last recorded disposition | Current check |
|---|---|---|
| Arena PR #181 | Submitted; single `corner-cases/positivity-whnf`, outcome `either` | Not retrieved |
| Arena PR #182 | Submitted; `proof-param-ok` / `proof-param-swap` corner-case pair | Not retrieved |
| Arena duplicate inventory | No exact pair matches at `8ae1d84` | Not retrieved |
| Kiota clarification | Owner-deferred pending Arena feedback | Deferral preserved |

These are dated local records. This item supplies no new upstream observation,
semantic adjudication, or reason to contact maintainers. The locally recorded
historical evidence, PR heads and comments, and Kiota decision remain preserved
unchanged.

Repair CLI access with `gh auth login -h github.com --web`. After confirmed
repair, rank a fresh bounded Arena check at a stopping-point review; substantive
maintainer feedback supplied by the owner is another review trigger. A new
check requires successful CLI preflight and its own queue item and finite
budget. This completed item must not be resumed or repeatedly polled. No
watcher, external message, or browser fallback was created.

Select **ALT-PAYLOADS** next: its existing READY proposal can address the
recorded Lean4Lean/Batteries dependency gap locally. CVC-3 remains PLANNED
pending compiled dependencies and a tested protocol-specific runner. The
current CVC-1 literature assessment remains applicable to the same fragment.
The next item has not started.

The session consumed zero post-preflight GETs, builds, research checker
launches, or external messages. The CLI preflight's own authentication and
repository-access probes are separate from the six-request allowance.
Validate this packet offline with `python3
results/research/ops-upstream-1/validate-evidence.py`. Required repository
checks and their logs are recorded in
`results/workflow-refresh/ops-upstream-1-2026-09-06/validation.json`.
