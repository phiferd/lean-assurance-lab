# One fixed survivor-triage proposal

Recorded: 2026-09-08. Frontier: `F-SURVIVOR-TRIAGE-PROPOSAL`.

The owner explicitly accepted the proposal to execute `ALT-SURVIVORS`, one
bounded planning item with no checker execution. The authorization and exact
entry-state copies are retained in
`results/research/alt-survivors-2026-09-08/work-record.json` and
`results/research/alt-survivors-2026-09-08/entry-snapshot/`.
This is an explicit planning successor to the completed conditional-contract
phase. It does not reopen that phase, its runs or its consumed budgets.

## Question and completion

Which one of the seven canonically pending survivors has the strongest
existing-evidence case for a small, attributable investigation using the Lab's
existing methods and assets?

Complete `ALT-SURVIVORS` with one exact mutation identity and source revision,
a reproducible inventory and comparative rationale, a scoped reuse assessment,
and a finite execution-manifest proposal. Bind available source, patch,
historical observations and proposed reused inputs by content. State the
question, hypotheses, controls, attribution conditions, input/runtime/tooling
prerequisites, accounting and cleanup requirements, exact output and stop
conditions. Identify missing inputs honestly. The proposal must be reviewable
without generating candidate bytes or launching the proposed experiment.

Success means a mechanically checked proposal ready for a target-specific
execution decision; it does not mean a witness, semantic classification or
defect has been demonstrated. If the evidence cannot support an executable
path, retain a bounded unresolved result naming the concrete missing gate.

## Scope and budget

- One planning allocation of at most 5400 actual cumulative active seconds,
  including delegated support, engineering and closure validation, recorded
  with paired UTC and monotonic intervals. Concurrent support is included in
  the owner's elapsed interval; no allowance resets at checkpoints.
- Read existing local artifacts and pinned sources; compare all seven pending
  mutants and select exactly one. Reuse existing methods where applicable.
  New methods require a separately bounded literature assessment before use.
- Zero checker, proof, setup/build or research-network launches; zero generated
  scientific byte variants; zero external research actions. Repository delivery
  and the required administrative tests are separate from research launches.
- Bind a separate finite inert-fixture allocation before closure tests. Use the
  existing fixture accounting and process controls; preserve every failure and
  reconcile before further launches. No allowance to modify scientific caps.
- Do not change survivor classifications, mutation-score denominators, catalog
  dispositions, normative authority, old evidence or completed run ledgers.

## State transition and next decision

The owner supplied the missing decision recorded by `CVC-NEXT-AUTHORIZATION`.
Archive that unexecuted administrative placeholder in the exact entry queue;
retire it from the current queue without representing a second completed
research item. Promote only `ALT-SURVIVORS` to ACTIVE. All actual predecessor
research records and unmet original dependencies remain preserved.

At closure, record the result and recommendation, compare serious alternatives,
and select the named proposed execution item without starting it. Execution
requires separate owner authorization and all exact prelaunch gates. If no
READY item remains, use the existing schema-v2 PAUSED handoff, with that WAITING
decision and its concrete blocker. Do not invent further planning work to fill
the queue. Complete at most this one research item, deliver it, then stop.

## Required validation and delivery

Validate the proposal's exact bindings, fixed selection and finite gates with
a local no-launch validator and focused negative tests where warranted. Run:

```sh
scripts/validate-research-queue
python3 -m unittest discover -s tests -p 'test_research_queue*.py'
scripts/close-declaration-validation-publication-study validate-historical
scripts/validate-publication-study-snapshot --require-full-payload
scripts/run-unit-tests-with-signal-retry --require-full-payload
scripts/validate-contribution --check-catalog
scripts/validate-cvc5-package
scripts/refresh-current-state
scripts/build-project-review --check
scripts/artifact-status --require-current
git diff --check
```

The complete suite includes unchanged historical transition regressions. Add a
focused transition check showing that the predecessor queue remains valid in
its bound entry snapshot while the current queue changes. Never modify frozen
history to make a transition pass. Keep raw check receipts and exact tested
inputs. Preserve unresolved broader assurance failures. Commit in-scope changes
on `main` and deliver with `scripts/push-main`; no successor runs at delivery.

## Planning closure — 2026-09-08

`ALT-SURVIVORS` completes SUCCESS for the fixed existing-regression proposal.
The canonical [result](../../results/research/alt-survivors-2026-09-08/result.json)
and [stopping review](../../results/research/queue-reviews/2026-09-08-alt-survivors.json)
select `SURVIVOR-LET-REUSE-1` WAITING, with PAUSED execution. Its exact proposal
requires separate owner authorization, a minimal tested successor, a counted
isolated build and all prelaunch gates. No execution is authorized by this
closure; no second planning or research item begins. Retain all old source,
observation, classification, denominator and accounting bytes.
