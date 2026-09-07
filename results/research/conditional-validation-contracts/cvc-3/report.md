# CVC-3: comparator assumption boundary

Outcome: **BOUNDED_UNRESOLVED**. No checked Lab theorem or counterexample.

The fixed run `CVC3-U1-PROOF-0001` elaborated the unchanged CVC-2 signature
successfully as attempt 1. Attempt 2 tried the named-to-positional encoding
bridge, comparator preservation, both required acceptance cases and both
boundaries. It failed: the lookup induction needs a Boolean equality fact for
unequal encoded names, and the concrete acceptance/support goals need definition
unfolding before decidability synthesis. The source and compiler diagnostics
remain unchanged under `run-0001/attempts/02/`.

That same invocation printed the required transitive assumptions of both
imported comparators. Each report includes two axioms absent from the frozen
allowlist:

- `Lean.Level.instLawfulBEqLevel`: lawfulness of the Boolean equality on levels;
  the pinned source identifies the implementation as C++.
- `Lean.Level.isExplicitSubsumedAux_eq`: equality between the partial explicit
  subsumption helper and its total copy.

The complete reports also contain `propext`, `Classical.choice`, `Quot.sound`,
`Lean.Level.normalize_eq`, and `Std.TreeMap.all_eq_all_toList`. Those five are
within the existing conditional policy. Neither imported comparator report
contains `sorryAx`. The failed Lab declarations do contain elaborator-generated
`sorryAx` in their diagnostic reports and establish no proof result.

Both comparators are mandatory audit targets in proof and counterexample modes.
Repairing the Lab proof cannot change their fixed transitive dependencies. The
run therefore stopped at an immutable assumption boundary, before any further
feedback. The allowlist, signature, comparator inputs, runner, and predecessor
results remain unchanged. This is neither a mathematical counterexample nor
evidence of an executable validator defect. The source annotations explain
what was assumed; they do not discharge the assumptions.

The one design/diagnosis session consumed **199.947382292 seconds**. The two
compilation attempts consumed **2.357550584 seconds**, with complete reservations,
terminal receipts, raw streams and cleanup receipts. Ten attempt slots remain
unspent in the terminal run and cannot be recycled. There were zero observer
launches, dependency compilations, downloads or research network requests.
Recorded aggregate preparation/runner/proof active time is 7174.931631292 seconds;
preparation/proof compilation time is 52.112492251 seconds. Prior failed runner
fixture duration remains unknown. Required unchanged regression fixtures and
administrative closure costs are recorded separately in the validation record.

Select **CVC-AXIOMS-1** next: inspect the exact source statements, dependency
paths, trust assumptions and feasible discharge or alternative reuse, then
recommend a justified explicit successor or stopping this path. Bound that
review to two 60-minute sessions and six already-pinned files, with zero builds,
fixtures, checkers, network requests, source approvals or external messages.
The current fragment's reuse assessment remains relevant, but the new compiled
dependency evidence requires this targeted review before further proof effort.
No external action is recommended on the current evidence. CVC-4 and CVC-5 stay
conditional PLANNED; no successful-theorem prerequisite has been met.

Canonical records: [result](result.json), [diagnostic](stop-diagnostic.json),
[work record](work-record.json), [evidence manifest](evidence-manifest.json), and
[stopping-point review](../../queue-reviews/2026-09-06-cvc-3.json).
Required validation receipts live in
`results/workflow-refresh/cvc-3-2026-09-06/validation.json`.
