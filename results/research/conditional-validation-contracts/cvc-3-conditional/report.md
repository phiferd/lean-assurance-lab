# CVC-3-CONDITIONAL: fixed baseline audit failure

Recorded 2026-09-07. Outcome: **BOUNDED_UNRESOLVED**.
Scientific status: **NO_CHECKED_LAB_RESULT**. Model: `CVC-U1-A7`.

The unchanged signature compiled as counted attempt 1. The exact fixed baseline
compiled as attempt 2 with exit code 0, verified process cleanup and no timeout.
Its frozen transcript audit failed with `malformed full axiom list`, making the
run terminal before any Lab proof feedback. This is a local engineering failure,
not a counterexample to the contract or evidence that A7 is false.

The [result](result.json), [diagnostic](stop-diagnostic.json),
[raw baseline output](run-0001/attempts/02/stdout), and
[append-only ledger](run-0001/execution/events.jsonl) retain the distinction
between compiler success and audited baseline failure. No Lab proof implementation,
observer, dependency build or research network request ran in this item.

## Failure and repair boundary

The baseline's `pp.universes`/`pp.all` options print axiom declarations such as
`Classical.choice.{u}` and `Std.TreeMap.all_eq_all_toList.{u, v}`. The fixed audit
accepts only undecorated names and splits every comma, including the comma inside
the universe argument list. The first observed audit error follows directly.
Two further independent incompatibilities are visible in the same immutable
transcript: the two TreeMap type headers wrap their universe parameters across
a newline, and generated typed definitions produce nine source-positioned
linter warnings before the type reports.

The [offline diagnostic reproduction](parser-diagnostic.json) found the seven fixed declaration names in
both comparator reports and equal whitespace-normalized bodies for all nine
actual/expected type pairs. That diagnostic extraction does not replace the
frozen audit or retroactively accept the baseline. No semantic mismatch is
demonstrated by this failure, and no assumption is discharged.

The raw transcript reproduces the frozen audit failure without another compiler
launch. The new closure validator also replays that failure to justify the
supervisor `COMPLETE` / runner terminal `FAILED` distinction. Pure regressions
preserve the observed parser rejection and test evidence tampering.

Editing the current audit, baseline, manifest or source expectations would
change an immutable input bound to checkpoint
`40cac6066856a25c8ff5d66691a75b743673ec4a`. The runner is already terminal.
An identical retry cannot fix this deterministic failure, and proof edits cannot
satisfy the mandatory baseline gate. These are concrete restrictions on repair
within this run. The feasible path is an explicit successor with new bindings;
no old input, receipt, output, counter or historical attestation is changed.

## Accounting and recommendation

One session consumed 55.59774324996397 research seconds. The two compiler
reservations consumed 2.71219816734083 seconds in total. Exact machine values
are in the result and ledger. Four slots remain unspent and cannot be reused
inside this terminal run. Required closure checks and inert fixture costs are
recorded separately in the [validation record](../../../workflow-refresh/cvc-3-conditional-2026-09-07/validation.json).
Predecessor costs retain their scope; prior unknown fixture duration stays
unknown. Compiled signature products are local full-payload evidence; the small
baseline product is retained with its raw exception-path receipt.

Select **CVC-A7-REPAIR-1**, READY and unstarted, to repair transcript handling
through an explicit successor and finish the original bounded bridge if its
new baseline passes. Preserve the exact semantic signature, independently
written types, seven-assumption envelope and original four Lab obligations.
A narrow grammar must validate universe decorations and wrapped headers without
accepting changed types, missing/extra/duplicate reports or unknown diagnostics.
The successor may suppress only the two identified lint checks in its own fixed
baseline source; it must retain a strict diagnostic policy and counted audit.

Local repair comes first. Before new Lean feedback, commit the exact successor
controller, manifest, baseline and gate review with pure regression evidence.
At most four newly bound 300-second build reservations are available: fresh
signature, baseline, then normally two proof attempts. Baseline retries consume
these slots. Combined A7 builds remain at most six; including original CVC-3,
at most eight. Carry consumed research time: at most 3600 additional
active seconds in the one remaining session of at most 60 minutes, including
repair work. Both the original six-build and two-session A7 ceilings remain
unchanged; unused time in the closed first session is not recovered.
No dependency, observer or research network launch is authorized. This preserves
the total experiment allowance while changing the immutable execution path.

This repair outranks changing comparator strategy because it is a deterministic,
locally reproduced prerequisite for the existing question. Recent literature
and assumption reviews remain applicable. Arena access remains last-known
blocked without fresh feedback; survivor/transfer themes remain deferred.
Original CVC-4/CVC-5 remain PLANNED with unmet prerequisites. No external
research issue, message, normative-source approval or contribution is warranted
by this local parser failure. The [queue review](../../queue-reviews/2026-09-07-cvc-3-conditional.json)
records the comparison and next selection; the successor has not begun.
