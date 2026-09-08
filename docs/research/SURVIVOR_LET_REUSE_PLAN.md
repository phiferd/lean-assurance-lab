# Fixed let-regression reuse execution

Frontier `F-SURVIVOR-LET-REUSE`; sole authorized item `SURVIVOR-LET-REUSE-1`.
The owner's 2026-09-08 execution decision is recorded in
`results/research/survivor-let-reuse-1/entry-decision.json`. It activates the exact
`results/research/alt-survivors-2026-09-08/execution-proposal.json` as a successor;
that planning artifact remains immutable and retains its historical approval state.

## Fixed question and bounds

Does the already admitted 601-byte let mismatch/control pair distinguish exact
`nanoda-gen-9face4e6a6f7` from the pinned Nanoda baseline? Execute only the four
proposal cells: baseline control, mutant control, baseline candidate, mutant
candidate. Both controls must freshly accept before either candidate. No new
export bytes, mutation identity, proof, network request or external research
action is authorized. The only source patch is the bound 9face predicate.

All proposal limits apply: 5400 cumulative active seconds including engineering
and closure; two offline build reservations of at most 120 seconds; eight checker
reservations of at most 30 seconds; one fixed pair, zero scientific variants.
Track paired UTC/monotonic clocks from the new work record; use the greater
elapsed duration plus the conservative 120-second pre-record charge. Parallel
work consumes the same wall-clock interval, not a fresh allocation.

## Launch and repair protocol

G1-G7 in the proposal are mandatory. Root is the only launch owner. Before a
counted offline build, commit exact source/configuration, local dependency and
toolchain identities, the dedicated runner, manifest and passing negative tests.
Bind the pinned README required by include_str from the same upstream revision
as a non-scientific build payload; the 22 pinned source/Cargo files retain exact
bytes except for the single specified predicate replacement. Isolate source,
Cargo home/vendor and target outputs; no historical checkout is edited.

Use `lib/cvc_process.py` and the bounded macOS signal adapter. Persist a hashed
reservation before each process, preserve raw outputs, and bind exact supervisor
receipts and resulting mutant binary to the reserved build and source inputs.
Exact clean success output is required for acceptance. The expected refusal is
specific to the baseline candidate and the source-bound infer_let/assert_def_eq
path; exit code or generic panic alone is insufficient. Other outcomes remain
separate. Evidence is a finite implementation comparison, not semantic authority.

Engineering/output/audit faults pause dependent launches for feasible same-item
repair, exact new tooling revision and focused regression checks. Preserve every
attempt, failure, bound input and cumulative cost. No old attempt is reused or
budget reset. Timeout, cleanup, cancellation or accounting failures require
conservative reconciliation before resuming. Stop at a real cap, missing payload,
authority/science change or diagnosed gap without a feasible authorized repair.

## Completion and delivery

Close after the fixed attributable result and local recommendation, or an
explicit bounded unresolved result. Fresh successful comparison supports reuse
association; canonical mutation promotion requires a compatible append-only
admission route with historical-transition checks. If the historical admission
route cannot accept another identity without altering frozen evidence, preserve
classification and record the concrete successor need. Do not create a duplicate
corpus artifact or upstream report to force admission.

At closure run the dedicated validator, focused runner and queue tests, the
required complete current/historical full-payload unit suite through
`scripts/run-unit-tests-with-signal-retry --require-full-payload`, publication
historical and full-payload snapshot validators, contribution/catalog checks,
prior CVC package and survivor-proposal validators. Keep finite administrative
process-fixture allocations separate from scientific launch limits. Preserve
raw failing checks and repair within the same active budget.

Update queue/status, result and stopping-point review; run
`scripts/refresh-current-state`, project review and current artifact checks.
Commit in-scope work on main and deliver with `scripts/push-main`, verifying the
remote commit. Select one concrete next item without starting it; further item
execution needs its own entry gate/owner authority. Preserve all historical CVC
results, sixteen observer charges, failed/unknown costs, old admission evidence,
upstream Waiting triggers and original CVC-4/CVC-5 dependencies.
