## Contribution

Contribution type:

Manifest path, when applicable:

## Mechanical Evidence

- [ ] Exact source revisions, configurations, corpus identities, and assumptions are recorded.
- [ ] New or changed artifacts are content-addressed and linked to reproduction commands.
- [ ] The success or failure condition is mechanical and does not depend on human or LLM judgment.
- [ ] Raw exceptional outcomes, disagreements, costs, and unresolved states are preserved.
- [ ] Expected semantics do not rely on majority vote.
- [ ] Generated regression candidates carry mechanically established expected-outcome evidence.

## Scoped Claims

- [ ] The change states what it measures and what it does not claim.
- [ ] Injected mutants are not described as discovered bugs.
- [ ] Mutation scores and coverage thresholds remain contextual unless policy explicitly says otherwise.
- [ ] Hard gates remain separate from contextual trend metrics.
- [ ] Public status language matches `results/assurance/current.json`.

## Reproducibility

- [ ] `scripts/validate-contribution --check-catalog`
- [ ] `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- [ ] Relevant milestone assurance command(s)
- [ ] `scripts/artifact-status --require-current`
- [ ] Checker sources are restored and external checkouts are clean.

Commands not run and reason:

## Reviewer Decision

- [ ] Advances the constitutional goal.
- [ ] Evidence supports every changed assurance claim.
- [ ] Artifact invalidation covers changed inputs.
- [ ] Acceptance or rejection is justified by documented standards rather than a preferred outcome.
