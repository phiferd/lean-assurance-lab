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

## Engineering persistence within an active item

Treat an ordinary engineering failure as work to diagnose and repair within the
active item, not as a scientific negative, completion, or reason to create a
successor. Within the authorized scope and remaining budget, preserve the raw
failure evidence, identify the cause, add the smallest meaningful regression,
repair it, and rerun the affected validation. Do not reset counters, reuse a
completed attempt, weaken a gate, or edit frozen evidence to make the repair
pass.

Freeze scientific inputs and preserve every prior evidence/tooling binding.
Parsers, audit implementations, runner controls and tests may be repaired within
the SAME active item through a new exact tooling revision. A frozen controller
may require a new execution-manifest revision, but that is not a new research
item or a budget reset. Validate old attempts against their original tooling.
Classify an output-format or audit-code defect as a repair pause, not as a
scientific mismatch or automatic terminal result.

Pause launches for accounting, timeout, cleanup or process-control failures;
reconcile conservatively before resuming. One owner binds exact scientific,
source, tooling and test inputs before each batch. Charge actual cumulative
active work; checkpoints do not consume whole time allocations. Preserve all
failed build reservations. Apply these rules prospectively through
`docs/RESEARCH_WORKFLOW.md` and the current bound protocol; historical runs keep
their original rules and are never reopened.

Run focused checks during repairs and the required full suite at logical item
closure, or earlier for a material assurance change. Documentation or tooling
checkpoints do not automatically close or rerank research. Stop only for a real
cap, authority/external blocker, scientific-input change or documented gap with
no feasible authorized repair path. Preserve attempted repairs and explain the
remaining blocker.

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
