# Cache-selection survivor investigation

Frontier `F-SURVIVOR-CACHE`; bounded item `SURVIVOR-CACHE-1`.
The owner's 2026-09-08 acceptance authorizes the proposed 90-minute investigation
of `nanoda-gen-3365809b3c41` and the accompanying durable project-wide research
selection correction. The entry state is preserved under
`results/research/survivor-cache-1/entry-snapshot/`.

## Question and useful outputs

Explain why the cache-selection predicate change survived 184 historical
covering tests, and establish the smallest attributable behavioral comparison
that the source and available interfaces support. The selected mutation changes
`flag == InferFlag::InferOnly` to `(flag != InferFlag::InferOnly)` in `infer` at
the pinned Nanoda revision `6ae1f0cd962f081f6c423454c5da729d841236a7`.

Source review must distinguish an internal inference-cache state from a state
reachable through normal exported-declaration checking. Every declaration gets
a fresh type-checker cache. A unit regression may exercise `InferOnly` followed
by `Check` on the same expression and type checker, but that result alone cannot
establish export-level reachability, a production-checker defect, a corpus kill,
or equivalence of the mutation over ordinary validation inputs.

Before scientific execution, freeze one exact control/candidate comparison,
source and harness identities, interpretation and expected output signatures.
If an internal unit harness is the supported route, add identical harness bytes
to baseline and mutant source, preserving the selected predicate as their only
scientific difference. Both controls must pass freshly before candidate tests.
Retain a source-grounded reachability analysis and explicit unresolved limits.

Useful closure is a reproducible regression and scoped explanation, supported
indistinguishability analysis, or a bounded unresolved result naming the exact
remaining question. Ordinary implementation failures require same-item repair.
Do not promote the canonical survivor classification without an applicable
admission contract and preservation of every historical binding.

## Reuse, authority and finite execution

Reuse the existing fixed-comparison method, pinned source lock, offline build
payloads and process supervisor. The fresh 2026-09-08 ALT-TRANSFER methods review
already covers fault isolation, controlled comparisons and interpretation limits;
this investigation adopts no new general theory or proof method. Inspect exact
local source and tests before reusing them. No new source authority is approved.

- At most 5,400 cumulative active seconds, including review, engineering,
  delegated support and closure. Preserve paired UTC/monotonic intervals and the
  initial conservative 120-second entry charge; no checkpoint resets a budget.
- At most two offline build reservations of 120 seconds each; failures count.
- At most eight scientific test/checker reservations of 30 seconds each, for at
  most two comparisons fixed before observations. Administrative unit fixtures
  have a separate finite allocation and never become scientific observations.
- No network build access, external writes or contacts, extra mutation identity,
  unbounded synthesis or automatic successor execution.

Root owns launch accounting. Commit the exact tested tooling, source/harness,
runtime inputs, scientific manifest and entry authority before a counted build.
Use isolated source/target directories and `lib/cvc_process.py`; reserve before
launch, retain raw streams and cleanup receipts, charge actual work, and bind
the produced test binaries to their exact source/build records. On accounting,
timeout, cleanup or malformed-output errors, pause dependent launches and
reconcile before continuing. Version any engineering repair within this item,
preserving all failed reservations and original tooling bindings.

## Project-wide reassessment and delivery

The owner's durable-policy correction applies prospectively. At logical closure,
compare useful work across the project's constitutional goals and methods,
including the remaining survivors, existing unresolved evidence, shared assets,
maintenance, upstream follow-through, literature/reuse and local blocker removal.
Record a content-bound strategic review and select the best feasible bounded
local item READY. An ended plan or a blocked transfer input is not a project-wide
blocker. Preserve actual external/semantic gates without manufacturing activity.
Update the authorized frontier, plan, queue and status together; selecting the
next READY item does not start it in this one-item run.

Required checks: focused runner and queue negative regressions; successor queue
integrity and readiness; dedicated evidence/accounting validation; prior transfer
and survivor historical-package validators; declaration-validation catalog and
publication-study historical/full-payload validators; complete current and
historical unit suite through
`scripts/run-unit-tests-with-signal-retry --require-full-payload`; current-state
refresh in dependency order; project-review/artifact freshness; staged diff check.
Preserve original validators and attestations when introducing successor policy.
Commit in-scope work on main and deliver through `scripts/push-main`.
