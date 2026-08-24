# Lean Assurance Lab Constitution

## Purpose

This project exists to improve trust in Lean as an ecosystem.

Its work is to provide mechanically reproducible visibility into the current
quality of Lean validation, conformance, and kernel-adjacent assurance. It
should help the community understand what is known, what is untested, what is
ambiguous, and what has changed.

The central goal is:

```text
Continuously improve and explain the measured assurance state of the Lean
validation ecosystem.
```

Every project objective, milestone, experiment, and contribution should be
judged by whether it advances that goal.

## What This Project Is

This project is an assurance project for the Lean ecosystem.

It measures the behavior of validators, kernels, corpora, and related tools
through mechanical artifacts. It records evidence in forms that can be
inspected, reproduced, challenged, and improved by others.

It is also a corpus-improvement project. When the system finds a validation gap,
the preferred outcome is a durable regression test, a clearer specification of
expected behavior, or a better explanation of an unresolved disagreement.

It is a visibility project. A useful result is not only a stronger corpus or a
better validator, but a clearer public account of the current assurance state:
which claims hold, which claims have expired, and which areas remain weak or
uncertain.

It is a community-aligned project. It should make participation easier for
validator authors, Lean users, researchers, and maintainers while keeping the
project's standards of evidence clear.

## What This Project Is Not

This project is not a claim that Lean is correct.

It does not prove the Lean kernel correct, and it must not present measured
testing strength as mathematical certainty. Its claims are always scoped to
specific artifacts, versions, configurations, assumptions, and models.

This project is not a hunt for a single vulnerability.

Finding a serious Lean issue would be important, but the project succeeds by
building lasting assurance infrastructure, improving shared tests, and exposing
the current state of validation quality.

This project is not tied to one technique.

Mutation testing, differential validation, coverage, witness generation,
minimization, fuzzing, formal methods, and manual review may all be useful. No
single method is constitutional. Strategies may change when better evidence,
tools, validators, or community needs emerge.

This project is not an implementation scoreboard.

Independent validators are valuable because they give the ecosystem more ways
to observe semantic behavior. Results should be used to improve shared
assurance, not to reduce validator work to rankings divorced from context.

This project is not governed by conversational memory.

Important conclusions must live in durable artifacts, not in an LLM transcript,
a person's recollection, or an informal explanation.

## Tenets

### Mechanical Evidence First

Authoritative claims must be grounded in executable or inspectable artifacts.
Humans and LLMs may propose, explain, and prioritize work, but they do not
replace mechanical evidence.

### Scoped Claims

Every assurance claim must say what it applies to. Revisions, configurations,
corpora, validators, semantic assumptions, and test models are part of the
claim. When those inputs change, the affected claim expires.

### Visibility Over Comfort

The project should make uncertainty visible. Unknowns, disagreements,
unclassified survivors, weak subsystems, flaky behavior, and failed
reproductions are valuable facts. They should be preserved rather than hidden.

### Improve Shared Assets

The preferred output of a discovered gap is an improvement to the shared Lean
validation ecosystem: a regression test, a clearer conformance case, a better
validator check, or a documented unresolved issue.

### Generalization Matters

Evidence is stronger when it transfers across independent implementations or
independent sources of validation. The project should prefer results that
improve shared semantic assurance over results that only exploit one
implementation's local details.

### No Single Metric Is the Goal

Metrics are instruments, not the mission. Mutation score, coverage, corpus
size, witness count, and execution cost are useful only when interpreted in
context. Optimizing a metric at the expense of ecosystem assurance violates
this constitution.

### Reproducibility Is a Feature

A fresh process should be able to inspect the repository and determine the
current assurance state, the evidence behind it, and the work still unresolved.
Reproduction is part of the product, not an optional afterthought.

### Community Participation With Standards

The project should welcome contributions from the Lean community and adjacent
research communities. Contributions may propose new validators, tests, mutation
models, generators, reports, or analyses, but accepted work must preserve the
project's standards for scoped, durable, mechanically grounded evidence.

### Strategy Is Replaceable

Tactics and architecture may evolve. If a different method better advances the
constitutional goal, the project should adopt it. A method earns its place by
improving trust, quality, visibility, or reproducibility.

### Exceptional States Deserve Attention

Validator disagreements, unexplained behavior changes, ambiguous expected
semantics, and irreproducible results are not noise. They are high-value signals
that should be recorded, investigated, and resolved or explicitly left open.

## Alignment Test

A proposed objective is aligned when it can answer yes to these questions:

1. Does it improve trust, quality, or visibility for the Lean ecosystem?
2. Will its conclusions be represented by durable, reproducible artifacts?
3. Are its claims scoped to exact inputs and assumptions?
4. Does it preserve uncertainty rather than hiding or overstating it?
5. Can community members inspect, challenge, or build on the result?

If the answer to any question is no, the objective should be revised or
rejected.

## Constitutional Goal

The project should continuously move Lean validation toward a state where the
community can see, reproduce, and improve the evidence behind ecosystem trust.

The work is never finally complete. At any point, the project should be able to
publish the best current assurance snapshot, explain its limits, and continue
from there when Lean, validators, corpora, tools, or assumptions change.
