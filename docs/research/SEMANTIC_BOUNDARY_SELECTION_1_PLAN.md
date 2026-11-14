# Select one consequential semantic-boundary experiment

The completed checked-import confirmation found no unexpected behavior in forty
outcomes on known inputs. No demonstrated consumer need or incremental coverage
justifies more packaging. Upstream recursor and cache reports suggest different
trust boundaries, but we have not established a new reachable mechanism locally.
Yes, a focused source comparison is worth doing if it decides which uncertainty
merits an experiment. Compare the two mechanisms below, recommend at most one
separate experiment, and stop; a supported decision to pursue neither is valid.

Item: `SEMANTIC-BOUNDARY-SELECTION-1`, READY and unstarted as of 2026-11-14.
Frontier: `F-DISCOVERY-AND-CONFORMANCE`. This is a source-only selection item,
not an E0 campaign or authorization to run either proposed experiment.

## Decision and scope

1. **Recursor validation versus execution.** Does validation establish the type
   of the exact reduction rule later executed, including after universe
   instantiation and auxiliary-recursor reconstruction? Trace imported metadata
   through checking, reconstruction/substitution, installation and reduction.
   Identify the checked expression and the consumed expression, with the
   invariant relating them. A representation difference alone is not a defect.
2. **Context-dependent cache reuse.** Can a cached typing or equality judgment
   be reused where its binder environment no longer supports it? Trace the
   stored judgment, key, environment dependencies, lifetime, clearing and reuse.
   A missing key field alone is not a defect if scope or invalidation enforces
   the necessary invariant. Extend to declaration visibility only if that same
   concrete source path makes it relevant.

Use the public reports below to locate candidate implementations and prior
tests, then pin current source revisions and relevant file/blob identities.
Start with one concrete implementation path for each mechanism; inspect further
paths only to establish its reachability or invariant. This is not an ecosystem
inventory or a request to test every checker. Prefer existing local source and
inspection tools. Do not build checkers, generate experimental witnesses, run
checker cells, change production code, or create another framework in this item.

For each mechanism, record the public entry path, the causal path to a possible
wrong judgment, the independent semantic basis for the expected result, a
plausible valid control, and relevant existing coverage. Distinguish a missing
test from a missing validation invariant. Checker agreement, an LLM judgment,
and changed imported metadata are not independent semantic justification.

## Starting sources and exposure

These are primary-source leads observed on 2026-11-14, not new local findings:

- [Arena #350](https://github.com/leanprover/lean-kernel-arena/pull/350), merged
  November 10 at `6c2d82164f1a2b1ac94aee62290fe78a3c3853fb`, adds forged
  recursor-rule/type cases including auxiliary reconstruction and wrong
  arguments. Its acceptance reports concern the author's then-tested profiles.
- [Arena #345](https://github.com/leanprover/lean-kernel-arena/pull/345), merged
  November 9 at `bb886a2769ed4f66c050bc7ac6a897ff8018b0c2`, tests reuse of an
  open-term cache entry under differently typed binders. The author reports no
  Arena checker failing at submission; the affected implementation was proposed
  inference work in `ocaml4lean#7`.
- [Nanoda #84](https://github.com/ammkrn/nanoda_lib/pull/84), merged November 7
  at `0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`, adds imported rule-value
  checking and universe alignment. A repair is evidence to inspect, not proof
  that the entire family is closed.
- [Arena #349](https://github.com/leanprover/lean-kernel-arena/pull/349), merged
  November 10 at `564fe0cc3b5b212fe75e6d56d32723cad4f4a999`, adds Palladium.
  Its described caching, reconstruction and declaration-visibility design may
  supply an alternative path to inspect; integration alone creates no demand
  for another checker matrix or evidence of implementation independence.

Record overlap with published witnesses and the retained local recursor plans
and results. Published witnesses may motivate a distinct hypothesis or later
serve as labeled calibration controls; replaying them is not new discovery.
This informed source comparison is independent of the missing historical audit:
it cannot establish past Lab capability, discharge that audit's dependencies,
or claim fresh holdout custody. Keep the old historical and transfer plans,
missing original evidence, and completed ordinary-import screens unchanged.

## Deliverable and stopping boundary

Produce one concise dated report with the two source-bound dispositions. Select
at most one new mechanism based on reachability, consequence, independent
expectation, coverage gap and feasible execution—not on apparent sophistication
or number of implementations. Identify the particular invariant that blocks a
rejected candidate in the inspected pinned paths; do not claim global safety or
impossibility from a bounded audit.

If one candidate qualifies, specify the precise question, target revisions,
smallest discriminating experiment, valid control, expected-result basis,
relevant prior exposure and remaining launch prerequisites. Record its separate
plan and queue selection through the existing workflow, then stop before launch.
If neither qualifies, explain why and make the project-wide successor decision
without manufacturing another nearby expected-rejection screen or planning loop.
Ordinary source-access or tooling failures require feasible repair within this
item; unavailable required evidence/capability must name the missing edge and
what would unblock it.

End the report with a short research-value paragraph: what uncertainty was
resolved, what decision changes, whether a reusable artifact has an identifiable
consumer, and whether further work on this topic would add material information.
The immediate use is deciding whether to spend execution effort on one specific
semantic question; do not invent package demand to justify the work.

Use the existing source-only closure checks and project-wide handoff. No new
schema or approval gate is required. An eventual E0 campaign retains its
prospective registration, evidence controls and lightweight handoff protocol;
selection here supplies no runtime or confirmatory evidence. External writes,
frozen-history edits and assurance-milestone advances remain out of scope.
