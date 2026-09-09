# Research selection and stopping-point review

Effective 2026-09-06 under the owner's instruction to maintain a prioritized
list and finish bounded work before reevaluating; extended 2026-09-08 by the
owner's standing instruction for project-wide reassessment and bounded local
successors. This operating procedure is subordinate to the constitution. Active
execution follows the frontier recorded in RESEARCH_STATUS; a stopping-point
review may replace that frontier through the explicit process below.

## One authority chain and one queue

`docs/RESEARCH_STATUS.md` selects the authorized frontier and links its plan.
`config/research-queue.json` records ranked items within that frontier and
explicitly deferred alternatives across the project. It governs mechanically decidable queue
facts; it cannot activate a frontier by itself. `docs/PROJECT_REVIEW.md` is
generated from the queue and existing assurance inputs. GitHub Issues mirror
claimable work and ownership. Neither Issue order nor a generated report
overrides the repository's frontier or queue.

Use `scripts/validate-research-queue` before selecting work. One writer owns
queue changes. The validator checks unique contiguous ranks, dependencies,
finite budgets, completion records, one active item, the highest-ranked eligible
selection, and agreement with the Active status marker. It does not prove a
priority judgment correct or substitute for exact experiment entry gates.

The owner's standing authorization permits selecting, recording and executing
bounded local successor work that best advances the constitutional goal, even
when its method or research direction differs from the completed plan. At a
logical stopping point, update the explicit successor plan, Active status and
queue together before execution. This is the durable route for changing the
frontier, not a silent prompt override. Local source investigations, regression
construction, implementation and experiments can qualify. Scientific-input
freezes, exact launch controls, finite cumulative budgets, milestone prerequisite
gates and frozen history still apply. External publication, contact and changes
still require authorization for that exact action and target. A task-specific
limit such as one completed item controls when to stop, not whether useful next
work may be selected READY.

## What makes an item executable

Every item names its question/action, target, expected ecosystem value,
supporting evidence, rank rationale, prerequisites, entry gate, finite budget,
completion evidence, stopping condition, and any linked Issue. A vague idea is
`DEFERRED` until it can be made this concrete.

- `READY`: prerequisites and entry gate are satisfied; eligible when execution
  of the selected work is requested or already authorized.
- `ACTIVE`: the selected item is being worked through its stopping condition.
- `PLANNED`: a concrete conditional successor; satisfying dependencies alone
  never starts it. Read the result and record the entry-gate decision first.
- `WAITING`: a specific external dependency blocks progress; record what would
  unblock it. Do not repeatedly poll it in place of executable local work.
- `DEFERRED`: retained alternative with the reason it is not currently eligible.
- `COMPLETE`: the item reached its stop and has a durable closure record with
  outcome `SUCCESS`, `NEGATIVE`, `BOUNDED_UNRESOLVED`, or `SUPERSEDED`, evidence,
  and a concrete recommendation. Completion does not imply scientific success.

Keep at most one research item ACTIVE. Independent reading, source extraction,
or mechanical support can be delegated beneath that item without activating
another research direction. An upstream deadline or correctness emergency can
interrupt it only with the explicit checkpoint described below.

## How to rank

First exclude work outside authorization, with unmet prerequisites, or without
a finite useful stopping point. For the remaining choices, compare:

1. Expected improvement to ecosystem trust or a shared asset: severity,
   relevance to real artifacts, and likely usefulness to others.
2. Information gained: whether the result can settle an ambiguity, avoid wasted
   implementation, unblock other work, or falsify the current approach.
3. Evidence and transfer: strength of the starting evidence and usefulness
   across independent implementations or sources.
4. Cost and feasibility: effort, execution expense, dependency risk, and the
   likelihood of reaching a useful result within the bound.
5. Urgency: a substantive maintainer request, expiring evidence, or a known
   assurance failure can make closure more valuable now.

Record a short comparative rationale, including why the first eligible item
outranks the next alternative. Use ordinal ranks rather than a weighted score
that pretends these uncertain judgments are exact. Prefer the smaller decisive
item when value is otherwise similar. Account for accumulated deferral so
maintenance cannot be forgotten, but age alone is not proof of value.

### Contribution paths and planning horizon

Owner-directed reassessment, 2026-09-09: maintain a portfolio spanning standard
Arena corpus improvements, individual checker implementation/test hardening,
and implementation-independent Lean obligation clarification. Methods such as
mutation, historical-boundary mining and formalization serve those outputs.
Completion of the next survivor is not itself the preferred project objective.

At closure compare concrete candidates across these three paths, retaining
multiple READY alternatives where entry conditions permit and explicit
PLANNED follow-ups with dependencies and result-dependent promotion gates.
Describe what both a positive and negative finding would lead to. Do not force
equal category quotas, fabricate work, or make all branches depend on one
speculative investigation. The canonical queue checks ranks, dependencies,
budgets and selection; the strategic review records why the comparison is useful.

Before expensive investigation, name the potential external artifact and its
beneficiary. Current implementation correctness excludes a current-defect claim;
it does not exclude a preventive regression. An internal contract can justify
a checker unit test without establishing external reachability. A defensible
test contribution needs an independently stated invariant, concrete coverage or
test-effectiveness gap, plausible failure, focused assertion and maintenance
value. Reuse existing fixtures when appropriate. Distinguish source prediction,
executed regression, submitted contribution and maintainer adoption.

Use current upstream evidence to remove stale waiting conditions. A failed CLI
credential preflight is not a global read-access blocker when a connected
read-only API can supply the needed evidence. Preserve failed receipts and
exact-action approval for external writes. Prefer concise contributions tied
to maintainers' stated needs; combine related clarification questions.

## Finish, then reassess

Choose the first eligible READY item and set it ACTIVE with the start date,
owner, input identities, execution authority, and remaining budget in its work
record. Keep the commitment until its success, negative-result, unresolved,
or budget stop. Record new ideas as candidates; novelty alone does not displace
an active item. Checkpoints for breaks or context handoff resume the same item.

Ordinary implementation or test failures stay inside the active item while
its scope and budget permit repair. Use the versioned repair procedure below;
complete the item only at its scientific result, real cumulative cap, authority
or external blocker, scientific-input transition, or a documented implementation
gap for which no feasible authorized repair remains.

At every stop:

1. Preserve outputs, negative results, failed attempts, elapsed effort, and the
   exact completion/stop evidence. Run the item's required checks.
2. Record the result and a recommendation with action, target, priority,
   prerequisites, and evidence. A completed literature task must recommend a
   reuse/extension/build/stop decision; a reading list is insufficient.
3. Use the LLM to compare the best opportunities across the whole project,
   judging them against the constitution rather than asking only whether the
   current plan's next milestone is ready. Cover competing methods/frontiers,
   unresolved evidence and shared regression value, maintenance and substantive
   upstream needs, and literature/reuse currency. Reassess waiting follow-through
   and deferred work, with concrete evidence and a reason when a category offers
   no useful candidate. Promote a PLANNED item only if its entry gate is met and
   it still merits the cost. Create a bounded local successor when a better
   direction is available under the standing owner authorization.
4. Update the ranked queue and Active status together. Append a dated decision
   under `results/research/queue-reviews/` with the stopped item/outcome, before
   and after ordering, evidence paths, selected next item, and reasons. The
   current schema-v3 queue also binds a project-wide strategic review with the
   compared candidates, exact supporting evidence, category coverage, concrete
   blockers and selected-item agreement. Preserve earlier decisions; never
   overwrite the result to justify a preferred rank.
5. Validate the queue and regenerate its review through the existing refresh
   path. Mirror the bounded task to GitHub only within existing authorization.

Reprioritize an unfinished item only for explicit owner redirection, invalidated
inputs/assumptions, exhausted bounds, a material blocker, or urgent credible
correctness evidence/maintainer deadline. Record the interruption, preserved
checkpoint, consumed budget, and reason before switching. Do not silently reset
budgets or extend scope. A bounded unresolved result cannot satisfy a downstream
dependency that needs success; revise or replace that task explicitly.

Maintain a useful executable frontier by selecting the highest-value feasible
authorized READY item at handoff. A completed plan, a blocked planned milestone,
or a change of local direction alone does not justify PAUSED or another request
for authorization. Before concluding there is no work, assess whether a bounded
local investigation, regression, implementation, maintenance action or
blocker-removal task would advance the constitutional goal. Prefer work with a
decisive shared output over successive planning-only items. If no valuable local
task is feasible, preserve the evidence and identify the actual external input,
target-specific authorization, technical capability, scientific gate, exhausted
bound or lack of a useful bounded question. State what would unblock it. Do not
invent a nominal task or run an endless planning loop. The validator refuses to
present an empty/blocked queue as operationally ready. Selecting a successor
does not execute it; stop after one item when the request specifies that bound.

The explicit schema-v2/v3 handoff represents this case as `PAUSED`, with the
highest-ranked WAITING/DEFERRED decision selected, no READY/ACTIVE items, a
nonempty reason, exact required decision and existing evidence references.
`Queue handoff: PAUSED.` must appear in Active status. Integrity validation
reports PAUSED with no executable item; `scripts/validate-research-queue
--require-ready` fails. Schema v1 retains its original requirement for eligible
work and remains the bound interface for historical scientific tooling. A
paused handoff is a durable blocker, not authorization for an agent to execute
the selected waiting entry. Version 2 retains its exact original validation
rules through `lib/research_queue_v2.py`; new project-wide review requirements
are implemented only in the explicit `lib/research_queue_v3.py` successor.

For schema v3, `strategic_review` binds a dated JSON review by path and SHA-256.
It records `PROJECT_WIDE` scope, `ENTRY` or `CLOSURE`, the completed item at
closure, the selected successor, and the digest of the current queue excluding
that review reference. It binds the constitution, this workflow, the current
plan and each candidate's cited evidence. The review assesses all five
categories: `METHODS_AND_FRONTIERS`, `UNRESOLVED_AND_SHARED_ASSETS`,
`MAINTENANCE_AND_UPSTREAM`, `LITERATURE_AND_REUSE` and
`LOCAL_BLOCKER_REMOVAL`. An empty candidate list for a category requires a
concrete written explanation; it never requires inventing a candidate. Compare
at least two actual unfinished queue alternatives and include every READY or
ACTIVE item as FEASIBLE. Other retained entries may be represented as BLOCKED
or DEFERRED, or excluded with a reason in the relevant category assessment.
Candidate dispositions must agree with queue status. A PAUSED selection and any
assessed local blocker-removal candidates need exact blocker evidence; no
FEASIBLE candidate may remain. ENTRY applies only while the selected item is
ACTIVE; a READY or PAUSED handoff requires CLOSURE and its completed-item
reference. A CLOSURE review leaves the next item unstarted.
The checks enforce scope recording, finite queue items, evidence freshness and
selection consistency. They cannot prove the LLM's research judgment correct,
prove a natural-language blocker genuine, or confer semantic authority.

Deliver the completed item on `main` using `scripts/push-main`, as required by
`AGENTS.md`. A push to a task branch is not completed repository delivery.

## Engineering repairs and evidence versions

Owner-authorized correction, 2026-09-07. This policy applies prospectively to
new execution protocols and the selected CVC-A7 repair. Completed protocols,
failed attempts, frozen manifests and historical decisions retain their bytes
and original interpretation.

Freeze the scientific question: input meaning, target declarations, permitted
assumptions, expected outcomes, selected runtime/dependency identities and total
resource ceilings. Version the engineering implementation: output parsers,
auditing code, runner controls, proof implementation and tests. A tooling defect
is not a scientific mismatch or a reason to close the active research item.
A parser or audit failure pauses new launches for diagnosis; only an actual
change to a fixed scientific input or a demonstrated semantic mismatch invokes
the corresponding scientific boundary.

Before resuming after a repair, retain the raw failure, add the smallest useful
regression and record a new exact tooling revision with its source/test hashes,
validation evidence and reason. Every attempt binds the scientific manifest,
tooling revision, exact source and generated compiler input before launch.
Validate old attempts with their original bound tooling, not the latest parser.
If a frozen controller cannot represent the repair, use a new controller or
manifest revision under the SAME active research item; carry all consumed
counters and time. A controller revision is not a new research item, a free
attempt, or permission to reinterpret earlier evidence. Never reopen a terminal
historical run; a separately identified continuation can inherit its costs.

Charge actual cumulative active work, including implementation, diagnosis and
proof work, using paired UTC/monotonic interval records. Breaks and checkpoints
may subdivide the allowance without forfeiting unused time or resetting costs.
For protocols adopting this policy, queue `max_sessions × session_minutes`
specifies the cumulative time allocation; recorded work intervals do not consume
whole allocations. The new protocol must enforce its explicit remaining-second
ceiling and per-process timeout. Closed protocols retain their original session
rules. Every actual build reservation still counts, including failures, setup,
baselines and interrupted launches. Unknown costs stay unknown or receive the
recorded conservative charge; they never become zero.

Keep one launch owner. Pause and reconcile accounting, timeout, process-control
or cleanup faults before any further launch. Tooling repair must preserve the
acceptance predicate and reject missing, extra or malformed semantic evidence;
changing an expected result, weakening a gate, or expanding an assumption list
is not an engineering repair.

Use focused regressions and affected validators at implementation checkpoints.
Run the required complete current/historical suite at logical research-item
closure, or earlier when a material change invalidates prior assurance. A
routine tooling repair, documentation commit or bookkeeping checkpoint does not
by itself trigger a full closure, reranking or full-suite replay. Documentation
checkpoints require queue/status agreement, affected generation checks and diff
checks. Preserve exact validation inputs and logs; reuse an unchanged input
manifest rather than duplicating it for every command.

## Literature is a first-class task

Perform a bounded literature and existing-tool search before a new theory,
method, representation, proof technique, or substantial tool is adopted, and
when a result appears to duplicate existing work. At each stopping-point
review, record whether the relevant search remains current. After 30 days of
active research without a relevant refresh, explicitly rank a small update
search against the other work. Time alone does not trigger an unattended job.

Search primary papers, formal developments, official documentation, and source
repositories. Follow citations and compare theorem statements, supported
fragments, versions, assumptions, proof dependencies, and implementation
boundaries. Record query/date/source/version/relevance and inclusion/exclusion
reasons. Preserve enough exact source identity for another person to challenge
the conclusion; bind any source used by a formal claim through its evidence path.

Every search has a decision question, finite time/source budget, and terminal
recommendation: reuse, extend, build only the missing part, or stop. Capture
inaccessible sources and uncertainty. Search exhaustion is not global novelty;
a current repository is not proof that all its stated theorems are complete.

## GitHub Issues and external follow-through

An Issue should identify the queue ID and frontier, question, evidence,
deliverables, dependencies, budget, stopping criteria, and owner. Contributors
claim bounded work there; repository records establish results and priorities.
Closing an Issue requires the repository closure evidence, and an Issue does
not automatically become next because it is new, old, assigned, or popular.

Keep pending upstream decisions linked to Waiting records with an unblocking
condition and a bounded next status check. At review boundaries, prioritize
substantive feedback by value and urgency. A read-only status check can be a
finite maintenance item; a watcher or recurring automation is a separate
operational request. External issues, comments, PRs, and other messages still
need target-specific owner authorization. Local work and drafts can proceed
without publishing a tracking Issue first.
