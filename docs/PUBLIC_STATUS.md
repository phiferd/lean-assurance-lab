# Lean Assurance Lab: Public Status

This page is generated from `results/assurance/current.json` by
`scripts/render-public-status`.

New to Lean, proof kernels, or mutation testing? Start with
[Why Test a Proof Kernel?](INTRODUCTION.md).

Snapshot SHA-256: `24a1c963e456068803eae1d77cf53e278bb145acea3bcd93c486472df5549efd`

## Current Gate: FAIL

The current assurance gate has 4 passing hard checks and
1 failing hard check. Failure reason: `semantic_checker_disagreements`.

The failure is intentional and informative: official Lean rejects two
universe-ownership artifacts that Kiota accepts. Their expected outcome is
mechanically established as `REJECT`, but the independent checker disagreement
remains unresolved. The project does not use implementation counts or majority
vote to erase that state.

## Measured State

- Validators: 3 pinned implementation families.
- Corpus: 197 materialized tests,
  9506646641 content-addressed bytes.
- Modeled semantic mutants: 29 evaluated,
  9 killed by the existing corpus,
  1 additional source mutant killed by a
  generated witness, and 19 surviving without a
  witness.
- Witness synthesis: 1 of
  2 bounded searches found a witness.
- Rotating held-out evaluation: score 0.5 to
  1.0 across 2 one-mutant folds;
  classification `MIXED_WITH_POSITIVE_GAIN`.
- Unresolved disagreements: 2 semantic
  and 1 parse-behavior case.
- Recorded execution: 859
  checker runs and 11322.03
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
