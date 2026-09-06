# Research selection and stopping-point review

Effective 2026-09-06 under the owner's instruction to maintain a prioritized
list and finish bounded work before reevaluating. This operating procedure is
subordinate to the constitution and the Active frontier in RESEARCH_STATUS.

## One authority chain and one queue

`docs/RESEARCH_STATUS.md` selects the authorized frontier and links its plan.
`config/research-queue.json` records ranked items within that frontier and
explicitly deferred alternatives. It governs mechanically decidable queue
facts; it cannot activate a frontier by itself. `docs/PROJECT_REVIEW.md` is
generated from the queue and existing assurance inputs. GitHub Issues mirror
claimable work and ownership. Neither Issue order nor a generated report
overrides the repository's frontier or queue.

Use `scripts/validate-research-queue` before selecting work. One writer owns
queue changes. The validator checks unique contiguous ranks, dependencies,
finite budgets, completion records, one active item, the highest-ranked eligible
selection, and agreement with the Active status marker. It does not prove a
priority judgment correct or authorize an experiment.

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

## Finish, then reassess

Choose the first eligible READY item and set it ACTIVE with the start date,
owner, input identities, execution authority, and remaining budget in its work
record. Keep the commitment until its success, negative-result, unresolved,
or budget stop. Record new ideas as candidates; novelty alone does not displace
an active item. Checkpoints for breaks or context handoff resume the same item.

At every stop:

1. Preserve outputs, negative results, failed attempts, elapsed effort, and the
   exact completion/stop evidence. Run the item's required checks.
2. Record the result and a recommendation with action, target, priority,
   prerequisites, and evidence. A completed literature task must recommend a
   reuse/extension/build/stop decision; a reading list is insufficient.
3. Reassess dependencies and all serious alternatives, including waiting
   follow-through, deferred work, and literature needs. Promote a PLANNED item
   only if its entry gate is met and it still merits the cost.
4. Update the ranked queue and Active status together. Append a dated decision
   under `results/research/queue-reviews/` with the stopped item/outcome, before
   and after ordering, evidence paths, selected next item, and reasons. Preserve
   earlier decisions; never overwrite the result to justify a preferred rank.
5. Validate the queue and regenerate its review through the existing refresh
   path. Mirror the bounded task to GitHub only within existing authorization.

Reprioritize an unfinished item only for explicit owner redirection, invalidated
inputs/assumptions, exhausted bounds, a material blocker, or urgent credible
correctness evidence/maintainer deadline. Record the interruption, preserved
checkpoint, consumed budget, and reason before switching. Do not silently reset
budgets or extend scope. A bounded unresolved result cannot satisfy a downstream
dependency that needs success; revise or replace that task explicitly.

Maintain at least one eligible next item at handoff. If the queue would become
empty, close the current item and add a small decision/reuse investigation
inside the authorized scope, with its own bound and useful output. This is not
permission for an endless planning loop: if no valuable authorized local task
exists, record the authorization or external-state blocker and the exact next
decision needed. Pause execution instead of inventing activity. The validator
will refuse to present an empty/blocked queue as operationally ready.

Deliver the completed item on `main` using `scripts/push-main`, as required by
`AGENTS.md`. A push to a task branch is not completed repository delivery.

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
