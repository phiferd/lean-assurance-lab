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
