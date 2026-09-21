# Lean Assurance Lab Agent Guide

Before substantive work, read `CONSTITUTION.md`, then
`docs/RESEARCH_STATUS.md`. Determine the currently authorized frontier from
the status artifact, read its active research or milestone plan, and load any
applicable repository skill. Do not treat conversational or model context as
the sole record of project state.

## Authority and operating order

Use this precedence order when sources disagree:

```text
CONSTITUTION.md
    ↓
docs/RESEARCH_STATUS.md (authorized research frontier)
    ↓
active research or milestone plan
    ↓
canonical machine-readable artifacts, schemas, validators, and tests
    ↓
task-specific user prompt
```

Machine-readable artifacts govern their own mechanically decidable facts; a
generated prose report is not a replacement for its bound canonical artifact.
A prompt may select work within the authorized frontier, but cannot silently
override this order or advance to a later milestone.

Before claiming completion, run the milestone's required validators and tests.
When work changes the frontier, update the durable state and its canonical
derived artifacts through their defined generation paths. Never advance into a
subsequent milestone unless durable research state authorizes it.

## Project-wide reassessment and standing local authorization

At each logical item closure, use the LLM to reassess what best advances the
constitution across the whole project. Compare methods and frontiers, unresolved
evidence and shared regression opportunities, maintenance and upstream needs,
and literature or reuse. A completed plan or a blocked next milestone is not,
by itself, a reason to declare that no work remains or pause the project.

The owner's standing instruction of 2026-09-08 authorizes agents to select and
record scoped local successor work, including a changed research direction,
and to update its explicit plan, Active status and canonical queue together.
No new permission is needed merely because the best local direction differs
from the completed plan. This includes local investigation, implementation and
experiments after their exact entry, scientific-input and launch gates pass.
It does not override the constitution, broaden frozen scientific scope, reopen
frozen history, authorize an external action, or permit crossing an assurance milestone
whose prerequisite gate is unsatisfied. Record the successor in durable state
before executing it; a conversational recommendation is insufficient authority.

At handoff select the highest-value feasible authorized READY item after that
comparison. Reevaluate scoped local blocker-removal and alternative work before
using PAUSED, and record the actual evidence-bound blockers and unblocking
conditions if no useful local item exists. Do not manufacture activity or repeat
planning without a concrete useful output. Selecting the next item does not
start it: obey the current request's item count and stopping boundary, including
an instruction to finish one item and stop. Use the current queue successor's
strategic-review checks; older queues retain their original historical rules.

## Engineering persistence within an active item

Treat an ordinary engineering failure as work to diagnose and repair within the
active item, not as a scientific negative, completion, or reason to create a
successor. Within the authorized scientific scope, preserve the raw failure
evidence, identify the cause, add the smallest meaningful regression, repair it,
and rerun the affected validation. Attempt, build, checker, session and elapsed-
time counts are observations, never authorization limits or stopping conditions.
Do not reuse a completed attempt, weaken a gate, or edit frozen evidence to make
the repair pass.

Freeze scientific inputs and preserve every prior evidence/tooling binding.
Parsers, audit implementations, runner controls and tests may be repaired within
the SAME active item through a new exact tooling revision. A frozen controller
may require a new execution-manifest revision, but that is not a new research
item. Validate old attempts against their original tooling.
Classify an output-format or audit-code defect as a repair pause, not as a
scientific mismatch or automatic terminal result.

Pause launches for accounting, timeout, cleanup or process-control failures;
reconcile conservatively, repair, and resume. One owner binds exact scientific,
source, tooling and test inputs before each batch. Record actual cumulative work
and preserve every failed attempt as evidence. Per-process timeout, memory and
cleanup controls remain safety mechanisms, but hitting one requires diagnosis
and repair rather than closing the item. Apply these rules prospectively through
`docs/RESEARCH_WORKFLOW.md` and the current bound protocol; historical runs keep
their original rules and are never reopened.

Run focused checks during repairs and the required full suite at logical item
closure, or earlier for a material assurance change. Documentation or tooling
checkpoints do not automatically close or rerank research. Stop only when the
scientific question is answered, the owner stops the work, required external
authority or input is unavailable, a scientific input is invalidated, or a
required capability remains genuinely unavailable after feasible repairs.
Preserve attempted repairs and explain any remaining blocker.

## Repository delivery and external actions

The owner requires **main-only delivery** for the Lean Assurance Lab repository
at `https://github.com/phiferd/lean-assurance-lab.git`. Work on `main`, commit
only the in-scope changes after required checks pass, and run
`scripts/push-main` to push `main` to `origin/main`. The command refuses a
different branch, dirty working tree, unexpected remote, or alternate push
arguments, and verifies the remote commit after pushing.

Do not create or push task, feature, or repair branches, or substitute a pull
request for delivery. If work is already on another branch, preserve its
commits and integrate them into `main` before delivery. Prefer a fast-forward
when possible; never rewrite bound research checkpoints.

Use the repository's existing permissions for an ordinary push to `main`.
An accepted push that prints a branch-rule notice is not a rejection and does
not authorize switching branches. If the push is rejected, preserve the local
commits and report the actual blocker. Do not force-push, rewrite history,
change protection settings, use administrative bypass commands, or discard
work. Do not report delivery until `origin/main` contains the completed commit.

For every other repository, agents may investigate, prepare local changes,
draft issues or pull requests, and perform read-only preflights. Creating or
modifying an external issue, pull request, branch, comment, review, release,
disclosure, or pushed commit requires explicit human approval for that exact
action and target. Prior approval for one action is not blanket authorization
for later actions.

Track project-originated external pull requests and prepared pull-request
candidates in `results/research/external-contributions.json`; its generated
human view is `docs/EXTERNAL_CONTRIBUTIONS.md`. When a tracked external action
is prepared, submitted, modified, or observed, update the ledger and its dated
fields, then run `scripts/build-external-contributions --write` and `--check`.
`scripts/refresh-current-state` regenerates the view but intentionally performs
no network lookup: never present an older dated observation as live state.
Name new pull-request submission drafts with the `*-pr.md` suffix; ledger
validation rejects any convention-named PR draft that is not indexed.
Item-specific evidence and submission records remain authoritative for detailed
or historical claims, and a ledger entry never supplies external-write
authorization.

## Durable epistemic invariants

- LLM output is not semantic authority, and checker consensus or majority is
  not semantic authority.
- Preserve contradictions, unresolved cases, and negative results.
- Keep evidence and provenance mechanically reproducible.
- Never weaken an assurance gate merely to make work pass.
- When an invariant can be mechanically checked, enforce it in schemas,
  validators, tests, or milestone gates rather than relying on instructions.
- Before editing an artifact marked frozen or historical, stop. Create or
  evolve an explicit successor, or use the repository's historical-binding
  mechanism; never regenerate an earlier milestone merely to make a later one
  pass.
- When crossing a milestone boundary, run the applicable historical-transition
  regression in addition to the milestone validators. The transition must prove
  that historical attestations still validate unchanged against their bound
  content while the current successor artifact changes.

For declaration-validation catalog entries, authority/evidence adjudication,
declaration-validation evidence locks, or M8/M9 declaration-validation work,
read and use `.agents/skills/declaration-validation-adjudication/SKILL.md`
before modifying those artifacts. The skill is operational guidance, not an
assurance boundary; the canonical schemas, validators, tests, and milestone
gates remain controlling.
