# Exploration before confirmation

Effective prospectively, owner-directed 2026-09-29.

**What did we find?** Hypothesis screening needs a cheaper completion path than
an assurance claim. Earlier studies retain their original evidence classes and
closure requirements; none is retroactively downgraded.
**Is it interesting?** Yes. This separates learning whether a question merits
investment from establishing a reproducible scientific conclusion. Operational
savings remain unmeasured until real pilots use this lane.
**Does it require more work?** Use the E0 lane for authorized screening and
measure its cost. Promote valuable observations into separate E1 experiments.
Repair shared closure machinery separately; this protocol does not claim to fix it.

## Evidence classes

| Class | Purpose | Permitted conclusion and validation |
| --- | --- | --- |
| E0 exploration | Screen an idea using a small declared sample | Candidate signal, no signal observed, or inconclusive; minimal identity and raw output, focused checks only |
| E1 confirmation | Test a hypothesis under a frozen protocol | Bounded result; independent input/expected-result review, fresh controlled execution, exact provenance and applicable confirmation checks |
| E2 assurance or external claim | Integrate a result into shared regressions, assurance state or an external contribution | Existing independent review, replay, full closure and applicable milestone gates; exact external authorization still required |

E1 does not automatically become E2. Its plan must declare the evidence needed
for its bounded claim before launch. This first implementation changes E0 only:
it does not silently waive any existing E1/E2 or milestone requirement. Evidence
class is selected before observation, never lowered because a result is negative.
E0 metadata and a clearly labelled summary may be public; E0 cannot substantiate
conformance, correctness, safety, performance bounds or a confirmed defect.

## Four invariants, one inexpensive record

1. **Identity:** source revisions, patches if dirty, command/tool/model versions,
   input files or a retained generation recipe and seed. Preserve generated and
   revised inputs with the raw output. A mutable path alone is not an identity.
2. **Question:** state the screening question and sample before running. Define
   what observable behavior would count as a signal and the necessary controls.
3. **Observation:** preserve raw stdout/stderr, exit/timeout/cleanup outcomes,
   actual commands and input identities for every attempt, including debugging.
4. **Classification:** records are always E0. Missing or failed measurements
   cannot be reported as a successful negative screen.

Use one small start event and one finish event in
`explorations/ledger.jsonl`, plus the raw files they reference. The start is
written before launches but need not be committed first. Git provides retained
history; no second immutable-manifest system, recursive receipt graph, separate
report or per-trial independent model review is required. Do not rewrite closed
rows or their evidence. Corrections are a new linked exploration identified in
its question/limitations, preserving the original and explaining the correction.

Iterative fixture construction and debugging are allowed. Log each revision and
command in raw output; don't quietly change the sample or replace failures with
successful cases. A changed screening question/sample gets a new start. Ordinary
engineering failures remain visible; repair feasible faults within the screen.
If the screen remains uninformative, use INCONCLUSIVE with its cause and a
continue/stop decision, never NO_SIGNAL. No claim that the mechanism is absent
follows from an inconclusive screen. Sample sizes bound scientific scope, not
permission to discard engineering failures or change frozen confirmation inputs.

Keep per-process timeout, memory and cleanup controls using an existing tested
supervisor. Pause launches on accounting or cleanup failure. E0 does not permit
unsafe unsupervised execution, external writes or changes to frozen evidence.
The record command does not run processes or prove natural-language observations.

## Authorization and ordinary closure

The queue selects an exploratory **campaign**, with an E0 plan containing the
literal line `Evidence class: E0`, its allowed questions/targets and reusable
supervisor. One ACTIVE campaign owns its trials. Campaign selection follows the
existing durable queue process; individual trials do not rerank the whole
project. Appending a start requires that selected ACTIVE campaign and its E0
plan. Writing a manifest is not permission to exceed its scope.

For an ordinary E0-only pilot, run `scripts/exploration-record check`, inspect
its observation/decision, and `git diff --check`; commit the start, finish and
raw evidence together, then use `scripts/push-main`. One commit is normal; two
are acceptable when an initial checkpoint is useful. This is a delivery target,
not a reason to hide failures or fabricate completion.

**An ordinary E0 NO_SIGNAL result requires no closure replay, independent final
review, generated assurance refresh, artifact hash graph, historical
reconstruction, or separate closure-retry receipt.** The same lightweight path
handles SIGNAL and INCONCLUSIVE; promotion is a separate decision. No full suite
is triggered solely by adding E0 records. Shared runner/tooling modifications
still require affected regressions and the existing material-change/full-suite
rules. Never use E0 to relabel a production fix as an untested experiment.

At campaign handoff, summarize all started pilots (including OPEN and
INCONCLUSIVE), cost and recommendations once; perform one strategic selection
and its applicable queue/view checks. That administrative update is not E2
promotion and does not require scientific replay for each pilot.
Use `scripts/exploration-handoff --base <pre-campaign-commit> --write`, then
`--check`. This validates the ledger, queue and strategic selection and updates
only `results/research/project-review.json` and `docs/PROJECT_REVIEW.md` through
their existing builder. It reads retained assurance observations but does not
replay or reattest them. It creates no extra log/receipt tree. Do not call the
general `refresh-current-state` pipeline for this handoff: E0 completion and
successor selection do not change assurance evidence. Retain raw attempts once;
no additional narrative or closure receipt is required for each retry.

## Outcomes and promotion

- **NO_SIGNAL:** completed the stated sample with the relevant observations
  available and no candidate signal. Report only “no signal observed here.”
- **SIGNAL:** one or more observations justify consideration of confirmation;
  report limitations and incomplete coverage explicitly.
- **INCONCLUSIVE:** insufficient observation, invalid inputs, unavailable
  capability, unresolved engineering failure or owner stop; explain the cause.

An acceptance count does not answer a resource question if required resource
measurements are missing. For example, the old resource pilot's zero RSS samples
would make an E0 sampled-memory question INCONCLUSIVE, even with 24 accepts.
Do not claim that short duration caused the missing samples without evidence.

Promotion appends a link to a **new** `CONFIRM-*` identity, hypothesis and reason.
The `proposal` command renders an E1 PLANNED proposal, never an executable or
completed result. It must enter the normal queue with a separate plan and pass
its entry, oracle and launch gates. E0 raw output cannot fill E1 result fields.
Freeze expectations before fresh confirmation observations; independently review
expected behavior. Reuse discovery cases honestly as reproduction cases; a fresh
process does not make a known case an independent holdout. Claim generalization
only with separately justified fresh cases. Valuable negative findings may also
be proposed for confirmation; promotion is based on information value, not only
on finding a discrepancy.

Keep every start in the ledger to expose the denominator. `check` reports OPEN,
NO_SIGNAL, SIGNAL, INCONCLUSIVE and proposal counts; a proposal is not a confirmed
discrepancy. Record observed token/time cost or explicit unknowns. Do not estimate
dollars from cached and uncached token totals without applicable billing data.
Prefer deterministic tools for bookkeeping. Model selection is an execution
choice, not semantic authority; expensive reasoning belongs at interpretation
and confirmation boundaries, with no repeated model review of routine receipts.

## Command interface

`scripts/exploration-record append event.json` validates and appends a start,
finish or promote event, adding the timestamp. The event envelope is:

```json
{"schema_version": 1, "evidence_class": "E0", "event": "start",
 "id": "EXPLORE-EXAMPLE-1", "data": {"campaign": "SELECTED-CAMPAIGN-ID"}}
```

This envelope is illustrative, not runnable: fill `data` with the fields in
[`exploration-event.schema.json`](../schemas/exploration-event.schema.json).
The tests contain complete synthetic start/finish/promotion examples; they are
not scientific results and never enter the live ledger. Input and raw-output
references name retained repository-relative files. Full SHA-1 source revisions
are required; dirty source changes require a retained patch.

The append command records SHA-256 identities for every start input while its
bytes are available. OPEN trials still require those inputs. For a closed trial,
ledger validation can use the recorded identity when a local build/coverage
payload is absent; if present, its bytes must match. This validates the record,
not the ability to reproduce the run: missing payloads must be reacquired and
verified before reproduction. Raw output and source patches must always remain
available. The first historical E0 start is bound through
`explorations/legacy-input-identities.json` to its already retained identity file;
neither its ledger rows nor its original evidence is rewritten.

`scripts/exploration-record check --base <prior-commit>` verifies schema,
lifecycle, paths and the append-only prefix relative to a review base (HEAD by
default). The check also rejects changes to previously recorded inputs and raw evidence.
Keep new raw files under `explorations/runs/<id>/`. CI uses the lightweight
check for ledger/raw-only changes, or the handoff command when a completed E0
campaign also updates its queue, current planning documents, new plans/review
records and the two project-planning views. Existing research-plan edits,
shared tooling, schema, workflow, assurance or unknown changes take the full CI
path. The handoff check validates closed trials and a consistent unstarted
successor; changing a queue file alone cannot select the E0 shortcut.
`scripts/exploration-record proposal CONFIRM-EXAMPLE-1` renders the separate
proposal after its promotion event is recorded. The command never launches,
changes the queue, refreshes assurance or grants external-write authorization.
