# Investigation And Upstream Action SOP

## Purpose

This procedure turns assurance findings into improvements to Lean kernels,
validators, and shared test corpora. Evidence collection is not complete until
the project records a clear recommendation. Recommendation and execution are
separate: external actions always require explicit human authorization.
Every mature recommendation names a concrete action and target.

## Required Finding States

Every active or completed investigation must use one of these dispositions:

- `UNDER_INVESTIGATION`: decisive evidence or expected semantics is missing.
- `ACTION_RECOMMENDED`: evidence supports one or more concrete next actions.
- `ACTION_TAKEN`: the authorized action has a durable issue, pull request, or
  disclosure reference.
- `DEFERRED`: a concrete recommendation exists, but a documented prerequisite
  or human decision prevents execution.
- `NO_EXTERNAL_ACTION`: evidence shows that external action would duplicate
  existing coverage, cannot improve an identified target, or is otherwise
  unwarranted. The rationale and any local action remain explicit.

`Discuss`, `keep watching`, and `recorded for future work` are not sufficient
recommendations unless they name a decision owner, prerequisite, and the action
that follows when the prerequisite is met.

## Evidence Readiness

Before recommending an external issue or pull request, record:

1. The exact artifact and a positive or matched control.
2. Raw and normalized outcomes from unmodified implementations.
3. Expected-outcome evidence, or an explicit unresolved-semantics status.
4. Exact revisions, configuration, and reproduction commands.
5. Current-upstream reproduction for every implementation being contacted.
6. A duplicate search using the exact behavior, test name, and relevant source
   terminology.
7. A security assessment deciding between a public report and responsible
   disclosure.

A recommendation may be recorded before all prerequisites pass, but it must say
which checks remain and cannot claim `ACTION_READY` implicitly.

## Action Decision Rules

| Finding | Default recommendation |
| --- | --- |
| Expected `REJECT`, implementation accepts | Validate current upstream, then file an implementation issue. Treat as high priority because acceptance may expand trusted behavior. Propose a shared `reject` test when coverage is absent. |
| Expected `ACCEPT`, implementation rejects | Validate current upstream, then file an implementation issue. Propose a shared `accept` test only when equivalent coverage is absent. |
| Expected semantics unresolved | Continue reference/specification investigation or request maintainer adjudication. Do not assign fault by implementation count. |
| Shared corpus lacks an established boundary | Propose a corpus issue or pull request containing the minimized case, control, and expected-outcome evidence. |
| Shared corpus already covers the exact boundary | Do not propose duplicate corpus coverage. Report implementations that fail the existing test when current-upstream reproduction persists. |
| Root cause and focused fix are validated | Recommend an implementation pull request, normally linked to the issue unless project norms favor a direct PR. Include a regression test. |
| Security-sensitive behavior may enable false proof acceptance or another concrete exploit | Stop public technical disclosure and recommend the affected project's private security channel. |
| No persistent gap or duplicate existing report | Record `NO_EXTERNAL_ACTION` with the reproduction or duplicate reference. |

The mutation that exposed a boundary is evidence about test sensitivity, not an
automatic patch. Never recommend applying a mutant as the fix without separate
root-cause analysis and validation.

## Recommendation Record

Action recommendations conform to
`schemas/investigation-action-recommendations.schema.json`. Each recommendation
must include:

- action type and exact target;
- priority and rationale;
- prerequisites and evidence references;
- whether it is an external action;
- human authorization status;
- execution status and, after execution, the durable external reference.

External recommendations remain clear while authorization is pending. Use
`REVIEW_REQUIRED`, not a vague or empty recommendation.

## External-Facing Draft Standard

An issue or pull request description must stand on its own for a maintainer who
has not read this repository, an agent conversation, or the underlying research
ledger. Before requesting authorization to submit or revise it, read the exact
proposed text without those sources and verify that it answers:

1. What concrete declaration, input, or behavior is being added or reported?
2. What is the smallest difference between the compared cases?
3. What outcome is expected, and why is that outcome appropriate for the
   target project?
4. What value does the contribution add beyond existing tests or reports?
5. How can the maintainer reproduce the result?

Define `candidate`, `control`, implementation names, and project-specific terms
when they are needed. Do not rely on unexplained Lab phrases such as “bound
evidence,” “shared expression,” “complete recursor,” “profile
characterization,” or “the reviewed pair.” Translate the relevant evidence
into source-level examples or ordinary language first. Put hashes, internal
artifact paths, frozen-frontier details, and broader scientific qualifications
in a separate local evidence section unless the maintainer needs them to assess
the contribution.

Check the target repository's current layout, naming conventions, contribution
guide, and the project's own previously accepted contributions before choosing
paths or test names. Record the precedent used. Keep names short enough for the
target's user interface. A local draft may contain internal notes, but it must
place the exact external-facing body in a clearly delimited section that passes
the stand-alone reading test above.

AI-assisted prose requires the same author review as code: remove conversational
context, internal shorthand, inflated claims, and wording the contributor could
not explain directly. A successful schema check, build, or duplicate search
does not establish that prose is clear; the final stand-alone reading is a
required review step.

## Human Authorization Gate

An LLM, automation, or contributor may investigate, recommend, search for
duplicates, validate current upstream, and prepare a draft without external
publication. It may create an issue, comment, pull request, email, or security
report only after a human explicitly approves that action and target.

Authorization for one target does not authorize another. Approval to file an
implementation issue does not authorize an Arena pull request, and approval to
prepare a draft does not authorize submission.

## Completion And Follow-Through

An investigation is operationally complete when:

1. its evidence and recommendation records are current;
2. every recommended external action is `ACTION_TAKEN`, `DEFERRED` with a
   concrete reason, or explicitly declined by a human;
3. issue and pull request URLs are linked back into the project;
4. upstream adjudication or fixes trigger local expected-outcome, regression,
   and assurance updates;
5. the research frontier advances without losing unresolved follow-through.

The project should prioritize reporting an action-ready high-impact finding
over generating another metric or adjacent matrix.
