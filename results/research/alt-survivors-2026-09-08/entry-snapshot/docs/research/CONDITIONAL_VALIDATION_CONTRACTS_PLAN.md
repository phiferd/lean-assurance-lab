# Conditional validation contracts: bounded feasibility phase

Recorded: 2026-09-06. Frontier: `F-CONDITIONAL-VALIDATION-CONTRACTS`.

This is an explicit successor to the completed corpus-integration phase. The
owner requested this plan and a continuously prioritized work list on
2026-09-06. This records the new direction and its next item; writing the plan
does not execute the research. The first work item is `CVC-1`, a bounded
literature and reuse assessment. Later items are conditional proposals and
become executable only through the stopping-point review below. The original
publication study, catalog dispositions, and historical attestations stay closed.

## Purpose and research question

Improve measured Lean assurance by connecting a precise, conditional semantic
guarantee to actual validation behavior and reusable evidence.

> Which differences between validators preserve the validity of the submitted
> proof and the meaning of its artifact, under an explicit theory, assumptions,
> and interpretation contract?

The phase tests whether a small formal connection can explain an existing
ambiguity more usefully than additional empirical characterization alone.
Formalization is a candidate method, not a new constitutional goal. Successful
reuse, a characterized limitation, or a justified decision to stop can be the
best result. No publication, new defect, or universal Lean specification is a
required outcome.

The previous study's one qualified obligation and fourteen provisional
candidates show a limitation of that particular qualification process. They
do not establish that Lean lacks a specification or that this direction will
succeed. See the immutable
[canonical closure](../../results/research/declaration-validation-publication-study-closure.json).

## The proposed guarantee

Separate theorem derivability, validity of the submitted proof, and fidelity of
the submitted artifact. This phase targets the latter two within a named
fragment. Replacing an invalid submitted proof with another proof of the same
theorem does not satisfy that promise.

A contract must fix the input interpretation independently of a validator,
the target judgment and theory, permitted assumptions and primitives, dependency
environment, supported fragment, and execution conditions. Its intended form is:

```text
validator accepts artifact b  =>  b satisfies the named contract C
```

Soundness restricts successful validation. Acceptance of valid inputs is a
separate completeness obligation over a supported fragment and resource
conditions. Refusal, unsupported input, timeout, and proved invalidity remain
different outcomes. A validator accepting nothing does not demonstrate useful
coverage of the supported fragment.

Different algorithms, internal representations, and reconstruction procedures
are allowed if a proved relation preserves the promised judgment. Different
internal axioms require a justified translation into the chosen target theory;
identical axiom names are neither necessary nor sufficient. Conditional
derivability does not establish consistency of the theory or correctness of the
user's informal mathematical intention.

Treat the contract as a named research model. Selecting assumptions for it does
not approve normative sources, change the existing authority registry, or turn
model-relative examples into universal conformance tests. Any later promotion
uses the repository's declaration-validation adjudication procedure. Keep
formal-model results, implementation observations, source correspondence, and
remaining trust assumptions separately inspectable.

## Ranked work and bounded stages

The canonical ranked records, dependencies, budgets, and current selection are
in [config/research-queue.json](../../config/research-queue.json). The generated
[project review](../PROJECT_REVIEW.md) displays them. The operating procedure is
[Research workflow](../RESEARCH_WORKFLOW.md). This sequence is the initial
hypothesis about value; each completed item triggers a fresh ranking decision.

### CVC-1 — Literature, existing artifacts, and reuse decision

First priority because it can prevent duplicated formalization and change the
choice of fragment before implementation costs are incurred.

- Review existing formal judgments, checker-correctness results, translations,
  and artifact/import boundaries. Compare reusable work with the Lab's actual
  ambiguities. Follow relevant citations as well as repository documentation.
- Start with the sources below; inspect exact theorem statements and relevant
  code, not just abstracts or claims of being verified. Record versions,
  assumptions, proof holes, axiom dependencies where inspectable, input-domain
  restrictions, and the gap to the proposed Lab contract.
- Compare at most three fragments: recursor-type metadata for a restricted
  non-nested inductive family; universe-expression interpretation; and an
  ordinary declaration/import boundary. Recursor metadata is a hypothesis,
  not a preselected winner. Prefer a fragment supported by existing formal work
  and a concrete Lab ambiguity.
- Bound: three sessions of at most 90 active minutes; at most 18 search queries
  and 12 primary sources reviewed in depth, with at most six source-code
  inspections. No builds, checker launches, or toolchain installation.
- Before the first search, create `work-record.json` under the output
  directory below, recording session start/end times and cumulative active
  minutes, every query, each distinct in-depth source, and each code inspection.
  One code inspection is one pinned repository revision and a declared group of
  files addressing one source-to-claim question; changing that question or
  revision consumes another inspection. Count failed queries and inaccessible
  in-depth sources. Resume these counters across handoffs; never reset a bound.
  Stop before the next operation would exceed a count or active-time limit.
- Output: a dated search log, source/version/claim/gap table, candidate
  comparison, and a `REUSE`, `EXTEND`, `BUILD_SMALL`, or `STOP` recommendation
  with a named target, priority, prerequisites, and supporting evidence. Store
  under `results/research/conditional-validation-contracts/cvc-1/`.
- Stop when the decision is supported or the bound is exhausted. Missing access
  or uncertain theorem scope is explicit evidence of a boundary. A bibliography
  alone is not completion, and bounded search does not prove global novelty.

Initial search seeds, checked for relevance on 2026-09-06, are not a completed
survey or approved normative sources:

| Primary source | Question for the reuse assessment |
|---|---|
| [Lean4Lean paper, version 3](https://arxiv.org/abs/2403.14064v3) and [repository](https://github.com/digama0/lean4lean) | Which abstract judgments and verified components can be reused, with what assumptions and version correspondence? |
| [Lean4Lean divergences](https://github.com/digama0/lean4lean/blob/master/divergences.md) | Which deliberate differences already have preservation arguments relevant to the Lab? |
| [MetaRocq](https://github.com/MetaRocq/metarocq) | Which methods for relating syntax, judgments, and verified checking transfer, and which are specific to Rocq? |
| [Lean4Less paper](https://rish987.github.io/files/lean4less.pdf) and [implementation](https://github.com/rish987/Lean4Less) | Does an existing proof translation address the proposed boundary more directly than a new contract implementation? |

### CVC-2 — One interpretation contract and a proof target

Entry: CVC-1 recommends a feasible reuse/extension/build path and the stopping-
point review promotes this item. Pin one fragment and at most two validation
strategies. Fix the meaning of the supplied proof, declarations, metadata,
dependencies, and requested theorem. State required environment invariants,
allowed reconstruction, resource outcomes, and explicit exclusions.

State the required acceptance set, even if finite, and distinguish it from the
larger domain of the soundness theorem. Either prove completeness for a named
fragment or limit the acceptance promise to the exact tested set. One accepted
example cannot establish acceptance coverage for a broader fragment.

Output: one small formal signature/judgment file with exact source mappings,
an explicit acceptance obligation, positive and negative examples, and an
assumption/dependency ledger.
Select a specific preservation theorem or counterexample target and an exact
finite execution protocol before feedback. A signature with no proved result
must remain labeled as a specification proposal. Stop after two 90-minute
sessions if the target cannot be stated without assuming its own conclusion;
record the missing definition or theorem and rerank.

### CVC-3 — Bounded formal preservation result

Entry: a fixed contract, reviewed assumptions, available pinned proof runtime,
and the new phase's explicit execution protocol. Attempt one theorem connecting
the selected strategy to the promised judgment. Include a valid accepted
example, check the exact CVC-2 acceptance obligation, and include a boundary
example; expose transitive assumptions and any `sorry`
or axioms. A proof that assumes the desired checker correctness is not success.

Bound: four 90-minute sessions and at most 12 proof-build attempts, each at most
five active minutes; failed attempts count. No full kernel verification, nested
or mutual-inductive expansion, or additional semantic family. A runtime or
dependency problem consumes the bound and may end in a materialization task.

Stop with a checked scoped theorem, checked counterexample to the proposed
contract, or a bounded unresolved result naming the exact missing lemma,
translation, or assumption. A model proof is not evidence that an executable
validator satisfies it. If suitable work already exists, reproduce and bind it
instead of rebuilding it.

A checked counterexample is a `NEGATIVE` scientific outcome, even when the
investigation completed well. At its stopping-point review, replace the
theorem-dependent CVC-4 proposal with a bounded counterexample investigation or
contribution item if that now has highest value. Do not relabel the negative as
`SUCCESS` to satisfy a dependency. Retain the superseded proposal and reason.

### CVC-4 — Connect the result to real artifacts and validators

Entry: CVC-3 provides a usable result and review still ranks this connection
highest. Map the selected fragment to exact artifact bytes and at most two
implementation lineages. Inspect parser, reconstruction, validation, and
semantic use separately. Identify any shared importer or proof-runtime trust.

Bound: three 90-minute sessions; at most four candidate/control pairs and
16 validator launches, each at most 30 seconds; no broad fuzzing or new mutation
campaign. Bind inputs, expected-outcome hypotheses, versions, and the launch
protocol before runs; preserve and hash actual outputs after execution.

Output: a reproducible explanation of agreement or disagreement, supported by
the formal result and exact implementation mapping. Testing a few instances
does not prove implementation refinement. A remaining adapter gap is a bounded
unresolved result, not a validator defect. Stop when the fixed comparison closes
or its bound is spent, even if more examples look interesting.

### CVC-5 — Shared value and phase decision

Prepare the useful result for reuse: a regression, a bounded conformance case
under the named contract, a formalization contribution, a precise unresolved
implementation question, or an evidence-based recommendation of no external
action. Name the target, priority, prerequisites, and exact supporting evidence.
Drafts must stand alone for the intended maintainer. Submission remains subject
to target-specific owner authorization.

Bound: two 90-minute sessions, using existing evidence and no checker launches.
Assess whether the phase explained a real ambiguity or supplied a reusable
formal connection. Compare the next contract slice with existing survivor
triage, transfer work, upstream closure, and operational blockers. Record a
continue/reuse/redirect/stop decision and a ranked next queue. Do not infer broad
coverage, soundness, or method superiority from this single fragment.

If an earlier item ends negatively or unresolved, perform its closure and
reranking immediately; do not wait for CVC-5 or force the remaining sequence.

## Execution boundaries and constitutional alignment

All stages are ceilings, not targets for consuming time. Their detailed queue
entry and a recorded entry-gate decision control promotion from `PLANNED` to
`READY`. Routine progression within this phase does not need repeated owner
confirmation. A new research theme or expansion beyond these bounds requires
explicit authorization reflected in durable state.

The existing campaign manifest/schema is specific to the closed ecosystem
frontier. CVC-2 must define an explicit successor execution path before CVC-3/4;
old run IDs and manifests cannot be reused. No runner change or experiment is
authorized merely by this planning update. Preserve failed attempts and resume
accounting in that successor.

This phase advances the constitution through inspectable conditional claims,
reproducible artifacts, exposed uncertainty, and a concrete ecosystem
recommendation at every stop. It preserves the authority boundary by treating
assumptions as model choices. It preserves strategy replaceability by reviewing
formalization against tactical alternatives after each bounded result. It
preserves history through new paths and unchanged predecessor attestations.

## Prospective repair-policy amendment — 2026-09-07

The owner authorized the engineering corrections in
[Research workflow](../RESEARCH_WORKFLOW.md#engineering-repairs-and-evidence-versions).
Apply them to CVC-A7-REPAIR-1 and new protocols: preserve scientific inputs and
old attempt bytes, version tooling within the same item, classify parser/audit
implementation errors as repair pauses, and carry actual cumulative active
seconds and every consumed build across controller revisions. A repair cannot
weaken exact type/axiom auditing or permit proof feedback before the baseline.

The original A7 total remains six builds and 7200 active seconds. The completed
run consumed two builds and 55.59774324996397 seconds. Its explicit continuation
therefore permits at most four new builds and 7144.402256750036 additional active
seconds, including runner repair and proof work. Work intervals may be split or
resumed without forfeiting time; each interval is at most 60 minutes. Retain
300-second compiler timeouts and zero dependency/observer/research-network
launches. Count the fresh signature and baseline; normally two proof attempts
remain. No other scientific scope or resource ceiling increases. Old terminal
runs and their historical session-count decisions remain unchanged.

Implementation revisions must bind exact sources/tests and pass affected
regressions before another launch; they do not require item closure or a new
queue selection. Run the full required suite at logical item closure. The
owner-requested documentation checkpoint preceding this continuation needs
queue/status agreement, affected generator/currency checks and diff checks;
it adds no proof or checker evidence and does not rerun the unchanged full suite.

## Conditional implementation successor — 2026-09-07

CVC-A7-REPAIR-1 completed the four original obligations with `SUCCESS` under
`CVC-U1-A7`. Its [stopping review](../../results/research/queue-reviews/2026-09-07-cvc-a7-repair-1.json)
selects **CVC-4-CONDITIONAL**, READY and unstarted. This is an explicit successor
to the original CVC-4 proposal; the original CVC-3 failure and CVC-4 dependency
remain unchanged. No broader milestone or semantic family is activated.

Apply the original CVC-4 artifact/mapping question, at most two implementation
lineages, four fixed candidate/control pairs, and 16 validator launches of at
most 30 seconds. The cumulative allocation is 16200 actual active seconds,
including engineering, in recorded intervals of at most 90 minutes. Before any
launch, commit the exact inputs, versions, expected hypotheses, source/runtime
mapping, tested controls and finite launch matrix. Bind any necessary setup or
fixture budget explicitly; the scientific launch allowance grants no implicit
extra processes. Version tooling repairs within this item while retaining raw
attempts, consumed costs and frozen scientific inputs.

The output must explain a concrete implementation boundary using the checked
conditional model. Finite testing does not establish parser, importer or
executable-validator refinement, or discharge A7. Stop after the fixed comparison
or a real cap/boundary, perform the required closure checks, and rerank. Do not
start this successor during the CVC-A7-REPAIR-1 closure.

## Validation and handoff

At a scientific frontier transition or logical research-item closure, validate
the queue, its focused tests,
the full-payload unit suite (including unchanged historical-transition tests),
the historical publication study, contribution catalog, current derived
artifacts, and final queue/review consistency:

```sh
scripts/validate-research-queue
python3 -m unittest discover -s tests -p 'test_research_queue.py'
scripts/close-declaration-validation-publication-study validate-historical
scripts/validate-publication-study-snapshot --require-full-payload
scripts/run-unit-tests-with-signal-retry --require-full-payload
scripts/validate-contribution --check-catalog
scripts/refresh-current-state
scripts/build-project-review --check
scripts/artifact-status --require-current
```

Each research item adds its own exact proof/evidence checks before execution.
The unit-suite wrapper invokes the unchanged complete suite; on macOS it binds
the narrowly bounded group-signal retry described in `docs/AGENT_WORKFLOW.md`.
It does not change test assertions or historical process receipts. Administrative
fixture allocations remain separate and visible, including exhausted earlier
allocations and any explicit finite repair allocation.
Do not rerun checkers to refresh planning documents. Preserve the broader
assurance gate's unresolved failures. At handoff, record the completed item,
its outcome and evidence, the ranking decision, and the next selected item.

## Frozen-byte adapter boundary handoff — 2026-09-07

CVC-4-CONDITIONAL closed `BOUNDED_UNRESOLVED` after two complete pairs and a
source-characterized ownership-control parser failure. Its
[stopping review](../../results/research/queue-reviews/2026-09-07-cvc-4-conditional.json) makes the immediate no-external-action
and phase decision; it does not promote original CVC-5 or defer required closure.
No repair preserves the selected bytes and pinned observer binaries. Adding a
parameter-level record preserves the structured AST but changes the exact
scientific artifact, so a distinct input-boundary decision must precede it.

Select **CVC-4-ADAPTER-REVIEW**, READY and unstarted, for one existing-evidence
review capped at 3600 actual active seconds. Decide a justified stop or exact
scientific-input successor proposal, including scientific identity, intended
representation change, expected value, reuse alternatives, prerequisites,
finite cap and entry conditions. Generate no byte variant, run no observer,
proof, setup or research-network process, and perform no external action.
Preserve every existing artifact, failure, charge, assumption and withdrawn
recommendation. This narrowly ranked decision stays in the conditional phase;
it activates no new comparison or semantic family. Original CVC-4/CVC-5
requirements remain unchanged. Only CVC-4-CONDITIONAL closes in this work.

## Exact ownership-input successor — 2026-09-08 UTC

The [existing-evidence review](../../results/research/conditional-validation-contracts/cvc-4-adapter-review/assessment.json)
completed SUCCESS and selects **CVC-4-OWNERSHIP-1**, READY and unstarted. Its
[canonical proposal](../../results/research/conditional-validation-contracts/cvc-4-adapter-review/successor-proposal.json)
fixes one new parameter-level record per old ownership stream, immediately before
the final definition: level index 3, name index 3 in the control and 2 in the
candidate. Every old byte, referenced AST, declaration parameter list, model
assumption and pinned observer/runtime identity is retained. Generate the new
streams only after this selected successor starts, never in the completed review.

The successor includes preparation, a minimal reuse of existing supervision,
a durable serialization regression, and one four-cell comparison. Require all
six proposal prelaunch gates, including exact committed inputs, tested tooling,
source/output hypotheses and an entry review. Both fresh controls must accept
before either candidate runs. A parser error cannot count as ownership refusal.
The unowned candidate remains CHECKED_UNSUPPORTED, not a proved invalid proof.

Allow at most 5400 cumulative active seconds including engineering, intervals of
at most 90 minutes, two new streams/one pair/two lineages, and four new observer
reservations of at most 30 seconds. Preserve all twelve old charges and cap the
combined observer reservations at sixteen; never resume a terminal run or reuse
its unused slots. No proof, setup/build or research-network launches. Bind any
required inert administrative fixtures separately. Missing payloads cannot
justify rebuilding or substituting an observer within this item.

Repair ordinary engineering faults within the same successor using exact tooling
revisions and preserved counters. Stop after the finite comparison or a real cap,
scientific-input boundary, authority/payload blocker, or demonstrated gap without
a feasible authorized repair. Do not introduce another pair or automatic further
successor. Retain a local regression plus finite report or bounded unresolved
result, and perform the complete validation/handoff procedure above. Original
CVC-4/CVC-5 dependencies remain unmet. No scientific variant, observer launch or
external research action was performed by this review.

## Ownership comparison closure and conditional phase decision — 2026-09-08

`CVC-4-OWNERSHIP-1` completed SUCCESS: both fixed controls accepted, and both
candidates reached the exact ownership refusal hypotheses after the sole
parameter-record insertion. This supplies a local reproducible serialization
regression; E-UNOWNED remains outside Supported, not semantically disproved.
Four new plus twelve retained reservations exhaust the sixteen-launch combined
ceiling. Original evidence and conditional assumptions remain unchanged.

The [stopping review](../../results/research/queue-reviews/2026-09-08-cvc-4-ownership-1.json)
selects `CVC-5-CONDITIONAL`, READY and unstarted, as a distinct existing-evidence
successor to the shared-value/phase-decision question. Original CVC-4 and CVC-5
remain PLANNED under unmet original dependencies. This is an explicit ranking
decision after the fixed comparison, not an automatic further experiment.

Use at most 3600 actual active seconds, including engineering, in intervals of
at most 60 minutes. Produce one reusable entry point connecting the exact A7
theorem/assumptions, three finite boundaries, raw observations and regression;
state a concrete external-action recommendation or justified no-action result;
compare continue/reuse/redirect/stop options and select a next item or explicit
authority/state blocker. Use existing evidence only: zero new scientific bytes,
observer/proof/setup/build/research-network launches or external actions. Do not
activate a new semantic family or research theme. Apply the same required
closure validation and handoff procedure; do not start it in this closure.

## Conditional reuse closure and paused handoff — 2026-09-08

`CVC-5-CONDITIONAL` completes the shared-value decision with SUCCESS for an
existing-evidence package and REUSE recommendation. The
[entry point](../../results/research/conditional-validation-contracts/cvc-5-conditional/README.md)
connects the exact checked model, assumptions, original failures and finite
observations to the local serialization regression. No new science ran.

Further scientific execution is PAUSED. The selected
`CVC-NEXT-AUTHORIZATION` entry is WAITING and unstarted: owner selection and
durable authorization of a named bounded successor are missing. Consider the
existing survivor-triage alternative first, or retain the pause; substantive
maintainer guidance may instead justify a scoped follow-up. This decision does
not activate that theme, a new contract slice, polling or additional launches.
The existing sixteen observer reservations remain consumed. Original CVC-4 and
CVC-5 remain PLANNED with their unmet original dependencies.

Use the explicit queue-v2 handoff for this non-operational state. Integrity
validation must check the blocker, evidence and status marker; an executable
readiness request must still fail. Preserve the original v1 validator and its
historical source bindings. This representation implements the workflow's
existing pause rule and does not weaken any scientific or eligibility gate.
Run the full closure validation above plus package checks and focused successor
queue tests. Future work needs its own durable authorization and finite entry
conditions. No subsequent research item starts during this closure.
