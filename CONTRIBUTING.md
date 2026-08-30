# Contributing to Lean Assurance Lab

Lean Assurance Lab welcomes contributions that improve the measured assurance
state of the Lean ecosystem. `CONSTITUTION.md` governs acceptance. A
contribution is reviewed by whether it adds scoped, durable evidence that is
mechanically reproducible, not by whether it produces a favorable metric or
confirms an expected result.

## Contribution License

By submitting a contribution, you agree that it may be distributed under the
repository's [Apache License, Version 2.0](LICENSE).

## Start Here

1. If the domain is new to you, begin with the
   [Introduction](docs/INTRODUCTION.md).
2. Read the [Constitution](CONSTITUTION.md),
   [Investigation and Upstream Action SOP](docs/INVESTIGATION_SOP.md),
   [Public Status](docs/PUBLIC_STATUS.md), and the relevant section of the
   [Design](docs/DESIGN.md).
3. Open the matching issue form for substantial work so assumptions and expected
   evidence are visible before expensive execution.
4. Pin every source revision, configuration, corpus input, and random seed.
5. Preserve raw exceptional outcomes and unresolved states.
6. Run the repository tests and current assurance commands before submitting.

The normal validation commands are:

```sh
scripts/validate-contribution --check-catalog
python3 -m unittest discover -s tests -p 'test_*.py' -v
scripts/current-assurance-snapshot
scripts/artifact-status --require-current
```

The current assurance gate may legitimately be `FAIL`. A contribution must not
rewrite policy, suppress evidence, or relabel an unresolved state merely to make
the gate pass.

## Research Planning And Issue Coordination

[`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md) decides which research
questions are Active. GitHub Issues split those questions into independently
executable units and coordinate ownership. For substantial work, assignment or
an explicit claim on the Issue is the coordination mechanism.

An Issue is not project truth. Closing an Issue does not establish a result
until the required evidence and conclusion are represented in repository
artifacts. The pull request and its mechanical evidence are the reviewable
result; accepted repository artifacts are the durable conclusion.

A contributor may propose work outside the current frontier, including through
an explicit contribution path below. The proposal does not silently become
Active merely because an Issue exists. Research priority changes belong in
`docs/RESEARCH_STATUS.md` and must retain a bounded, falsifiable completion
condition.

## Contribution Manifest

Evidence-producing contributions should include a JSON manifest conforming to
`schemas/contribution-manifest.schema.json`. Validate it with:

```sh
scripts/validate-contribution path/to/contribution.json
```

Every manifest records:

- contribution type, title, and summary;
- exact revisions, configurations, assumptions, and explicit non-claims;
- content-addressed artifacts and their roles;
- reproduction commands, content-addressed results, and mechanical conditions;
- unresolved states that remain after the work;
- type-specific metadata defined by `config/contribution-types.json`.

Artifact and result paths must be repository-relative and cannot traverse
outside the checkout. Required type-specific metadata must have non-empty
values; a present key with no information does not satisfy the contract.

Commands and artifacts are evidence; prose is interpretation. A successful test
requires executable normalized outcomes or another explicit mechanical
condition. Human or LLM judgment cannot substitute for that condition.

## Contribution Paths

### Validators

Provide the validator identity, implementation family, pinned source revision,
build and run commands, export compatibility profile, and independence
statement. Include a reproducible build, binary identity, positive-control run,
normalized outcome adapter, and explicit decline behavior. Compatibility limits
must remain visible.

### Corpus Tests

Provide the test identity, export format, targeted subsystem, expected outcome,
expected-outcome evidence, and positive control. A candidate is not ready merely
because one checker differs. Expected behavior must be mechanically established
without majority voting, and unresolved checker disagreement stays attached.

### Mutation Operators

Provide the operator and family identifiers, target language, semantic
rationale, structured discovery rule, exclusion rule, and isolated build
validation. Deterministic identities, unsupported sites, duplicates,
non-semantic candidates, and build failures must be reported separately.

### Witness Generators

Provide supported subsystems, deterministic seed policy, direct success
predicate, attempt budget, and minimization policy. Record every attempted
candidate and normalized outcome pair. Budget exhaustion is `UNRESOLVED`, not
evidence that a mutant is equivalent.

### Reports

Provide a report identifier, schema, content-bound input inventory, aggregation
rules, uncertainty fields, reproduction command, and stale-input gate. Separate
hard gates from trend metrics. Include costs, incompatible cases, unresolved
states, and the exact scope of every conclusion.

### Bug Investigations

Provide exact affected versions, a content-addressed reproducer, raw and
normalized unmodified-validator outcomes, expected-semantics status, and
disclosure status. Every mature investigation must also provide a concrete
action recommendation, recommendation disposition, and human-authorization
status under `docs/INVESTIGATION_SOP.md`. Deliberately injected mutants are
fault models, not discovered bugs. If semantics are unresolved, recommend the
specific investigation or adjudication needed rather than assigning fault by
vote. Do not post sensitive vulnerability details publicly before coordinating
responsible disclosure with affected maintainers. Issues, pull requests,
comments, and disclosures require explicit human authorization for each target;
the recommendation itself must remain clear while authorization is pending.

### Documentation

Identify the audience, document paths, claims changed, and evidence links. Check
commands against current interfaces. Assurance language must match the current
snapshot and retain limitations, non-claims, and unresolved states.

## Review Standard

Reviewers apply the pull request checklist and the per-type checks in
`config/contribution-types.json`. A contribution is acceptable when:

1. it advances trust, quality, or visibility for the Lean ecosystem;
2. its claims are scoped to exact versions, configurations, and assumptions;
3. its evidence is executable or inspectable and content-addressed;
4. changed inputs invalidate dependent claims through the artifact graph;
5. unknowns, disagreements, failures, and costs remain visible;
6. expected semantics do not come from majority vote;
7. generated tests carry expected-outcome evidence before promotion;
8. tests cover the behavioral and invalidation contracts affected by the change.

These standards make acceptance or rejection traceable to the constitution and
mechanical evidence rather than personal preference.

A contribution may be rejected when any of these conditions is missing. A
negative, neutral, incompatible, or unresolved result is welcome when the
evidence is sound and the claim is honest.

## Pull Requests

Keep changes scoped and retain unrelated local evidence. Include the contribution
manifest when the change creates assurance evidence. Complete
`.github/pull_request_template.md`, run the listed verification commands, and
explain any command that could not be run. Do not regenerate expensive evidence
solely to change timestamps.

## Issue Selection

Use the contributor-task form for bounded, claimable project work beneath an
Active frontier item or an explicit contribution path in this guide. Use the
incoming-finding forms for validator disagreements, proposed regressions,
mutation operators, stale artifacts or reproduction failures, and assurance
report issues. Every substantial task must state its starting evidence, resource
profile, durable repository outputs, allowed outcomes, non-claims, and
mechanical completion condition before expensive execution begins.
