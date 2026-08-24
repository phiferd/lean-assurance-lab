# Contributing

LeanVerifier welcomes contributions that improve the measured assurance state
of the Lean ecosystem. `CONSTITUTION.md` governs acceptance. A contribution is
reviewed by whether it adds scoped, durable, mechanically reproducible evidence,
not by whether it produces a favorable metric or confirms an expected result.

## Start Here

1. Read `CONSTITUTION.md`, `docs/PUBLIC_STATUS.md`, and the relevant design
   section in `docs/DESIGN.md`.
2. Open the matching issue form for substantial work so assumptions and expected
   evidence are visible before expensive execution.
3. Pin every source revision, configuration, corpus input, and random seed.
4. Preserve raw exceptional outcomes and unresolved states.
5. Run the repository tests and current assurance commands before submitting.

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
disclosure status. Deliberately injected mutants are fault models, not discovered
bugs. If semantics are unresolved, report a disagreement rather than assigning
fault by vote. Do not post sensitive vulnerability details publicly before
coordinating responsible disclosure with affected maintainers.

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

Use the structured forms for validator disagreements, proposed regressions,
mutation operators, stale artifacts or reproduction failures, and assurance
report issues. General feature work should begin with the closest form and state
the intended mechanical completion condition.
