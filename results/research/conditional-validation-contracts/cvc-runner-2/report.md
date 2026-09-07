# CVC-RUNNER-2 — supervised protocol runner

This item completes the implementation prerequisite for CVC3-U1-PROOF-0001.
It does not prove the Lab contract. No Lean, Lake, signature elaboration,
proof build, checker or research network request ran in this item.
`result.json` records the final checks and costs; `evidence-manifest.json`
binds the implementation, receipts and preserved prerequisite records.

The predecessor's cancellation bug and incomplete accounting were engineering
failures. This repair stays within the successor's existing two-session,
80-process, 400-process-second bound. CVC-RUNNER-1's failed log, orphan,
uninstrumented worker launches, uncertain duration and refusal endpoint remain
unchanged. Unknown predecessor process duration is still unknown.

## Controls and evidence

| Required control | Implementation and adversarial checks |
| --- | --- |
| Fixed contract, runtime, imports, environment and commands | `build_manifest`, `validate_manifest`, `verify_payloads`, entry checkpoint review; changed run ID, command, allowlist/input bindings and runtime refuse before launch. The full pinned runtime and all 37 prepared modules/141 compiled products are hashed read-only. |
| Reserve every attempted launch; finite design and attempt budgets | Append-only reservation precedes staging/fork. UTC and monotonic clocks account for design time, four sessions, 12 invocations and min(300 seconds, remaining session/total). Failed signature attempt 1 stops; failed proof attempts consume numbers and permit counted repair. Absolute deadlines include staging; terminal-time checks also reject post-process audit overruns. |
| Exclusive ownership, crash recovery and no replay | Filesystem lock, durable run/workspace identity, hash-chained WAL before atomic snapshot, prefix validation and reconciliation. Tests reject missing/truncated state, duplicate attempts, number 13, a fifth session, clock rollback and completed replay. |
| Timeout, cancellation and controller death | A separate supervisor watches a parent-loss pipe, enforces the deadline, kills the child's process group and retains raw output/cleanup receipts. Six inert tests cover normal completion, failed start, SIGTERM, descendants, independent leaf expiry and controller SIGKILL. Every fixture process has an independent finite limit. |
| Exact declarations, types and transitive axioms | Generated typechecking examples and fixed `#print axioms` suffix. Parser retains every full list, including empty/multiline lists and comparator names with apostrophes. Missing/duplicate/extra/malformed reports, unlisted axioms and sorry diagnostics refuse. |
| Signature before proofs; no hidden preparation | Exactly one immutable Contract.lean elaboration is invocation 1. Its compiled output set is bound before any proof. Only upstream dependency products are available; the CLI exposes no arbitrary compiler command or dependency compilation. |

One root launch owner reserved each supervised test topology before starting it.
The process count is the fixed test-plan maximum, including forked supervisors
and attempted failed starts. Each fixture conservatively charges its whole wall
time multiplied by that maximum, rather than claiming per-process CPU time.
The legacy dependency-preparation regression ledger contributes its separately
recorded launches and elapsed charges to the same item cap. These figures cover
the new runner fixtures and that instrumented predecessor suite, not ordinary
test-harness/git subprocesses or unrelated existing repository regressions.
The full validation log records those existing tests separately. The first supervised batch is explicitly
adopted into an anti-reset identity/snapshot without altering its original bytes.
A source-binding violation prevents later fixture launches. Exact input hashes
are recorded before each test batch; changes between completed batches are visible.

## Protocol interpretation and trust boundary

A failed start, timeout or interruption always consumes one of the 12 attempt
slots. A normal durable supervisor receipt records measured elapsed time; an
orphan is conservatively charged its full timeout, additionally deducted from
session and total active time. This is stronger than the protocol's permission
to reduce an orphan charge using bounded elapsed evidence. An absent receipt
within the cleanup window prevents overlap; after that window, the reservation
becomes INTERRUPTED with full charge and a persistent cleanup stop.

SUCCESS requires all four exact result declarations and all six axiom reports.
The protocol separately permits NEGATIVE, a counterexample to preservation.
That path checks the exact existential `Accepts a ∧ ¬ Contract a`, with a
counterexample declaration and both comparator reports (three total); it cannot
also require a proof of the contradicted preservation theorem. This interpretation
is explicit in the entry review. It neither weakens SUCCESS nor changes the
immutable contract/assumption allowlist. The expected invalid zeroBoundary
example alone cannot satisfy this counterexample target.

The proof input is a deliberately narrow reviewed Lean subset: one Contract
import, explicit fully qualified theorem headers and ordinary proof bodies.
Strings, quoted identifiers, metaprogramming commands, new axioms, unsafe/native
execution and proof holes are rejected. The textual checks are not a complete
Lean parser or an adversarial source sandbox. The pinned Lean compiler performs
the typecheck. Python, the OS, local filesystem, source review, core/runtime
contents and upstream allowed assumptions remain trusted. Process-group cleanup
covers these reviewed local children; it does not promise containment of hostile
code that deliberately escapes its group.

## Validation

The final suite passed 496 current and 73 frozen historical tests (569 total),
with no skips. Focused coverage comprises 35 pure runner controls, six supervised
process tests and five pure evidence tests. The preserved synthetic terminal-budget
counterexample motivated two of the regressions; no failed evidence was erased.
The authoritative result lists all validation receipts and exact final source hashes.

## Handoff

After passing required checks, commit the runner and exact manifest. A separate
entry review binds that implementation checkpoint, promotes CVC-3 and selects it
without starting it. Use `scripts/run-cvc-u1-proof-successor`; the old endpoint
remains a refusal. Begin a design session before proof work. `preflight` only
checks bound inputs; `attempt` first elaborates the immutable signature as attempt
1 of 12. A signature defect requires an explicit successor, while an ordinary
proof failure is repaired inside the remaining counted proof attempts.

AGENTS.md and both workflow guides now require evidence-preserving diagnosis,
regression, repair and revalidation of solvable engineering failures within the
same item and budget. Accounting faults pause launches for reconciliation;
they do not justify abandoning safe repairs. Real authorization boundaries,
immutable contracts and finite budgets remain controlling.

The broader assurance gate's 15 semantic disagreements remain unresolved.
CVC-4 stays conditional on a usable scientific result, and upstream follow-through
and alternative semantic themes retain their existing dispositions.
