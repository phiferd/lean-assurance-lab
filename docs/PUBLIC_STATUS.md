# Lean Assurance Lab: Public Status

This page is generated from `results/assurance/current.json` by
`scripts/render-public-status`.

New to Lean, proof kernels, or mutation testing? Start with
[Why Test a Proof Kernel?](INTRODUCTION.md).

Snapshot SHA-256: `0698008297f756bd8754784034856df8cbddfbb4367e8af2de92f8aca5a3e419`

## Current Gate: FAIL

The current assurance gate has 4 passing hard checks and
1 failing hard check. Failure reason: `semantic_checker_disagreements`.

The failure is intentional and informative: the unresolved semantic cases now
include two
universe-ownership artifacts that Kiota accepts against official
Lean's expected rejection, plus a nested-inductive metadata artifact that
official Lean and Lean4Lean accept while current Nanoda rejects, plus a
definition self-reference that official Lean and Lean4Lean reject while Kiota
accepts. The project does not use implementation counts or majority vote to
erase those states.

## Measured State

- Validators: 3 pinned implementation families.
- Corpus: 197 materialized tests,
  9506646641 content-addressed bytes.
- Canonical modeled semantic population: 67 evaluated,
  51 killed by the existing corpus,
  3 additional source mutants killed by a
  generated witness, and 0 surviving without a
  witness.
- Mechanically executed survivors awaiting semantic/witness triage:
  9. They are not included in the
  canonical modeled population or its mutation-score denominator.
- Reference-aligned mutants: 5 excluded
  from mutation-score denominators because the mutant matches established
  expected behavior while baseline does not.
- Witness synthesis: 4 of
  6 bounded searches found a witness.
- Rotating held-out evaluation: score 0.5 to
  1.0 across 2 one-mutant folds;
  classification `MIXED_WITH_POSITIVE_GAIN`.
- Unresolved disagreements: 15 semantic
  and 1 parse-behavior case.
- Recorded execution: 979
  checker runs and 6922.33
  checker-seconds across the non-overlapping components listed in the snapshot.

## What This Means

These measurements apply only to the exact revisions, configurations, corpora,
mutation models, and policies bound by the snapshot. They do not prove Lean is
correct or that the corpus is sufficient. The validator mutations are
deliberately injected fault models, not bugs discovered in the unmodified
validators. Mutation scores and coverage are contextual trend metrics, not hard
quality gates.

## Participate

`CONTRIBUTING.md` defines seven contribution paths, required metadata,
mechanical evidence standards, review criteria, and issue forms. Neutral,
negative, incompatible, and unresolved results are useful when reproducible and
honestly scoped.
