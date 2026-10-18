# One-endpoint Comparator consumer screen

Evidence class: E0

Selected READY and unstarted on 2026-10-18 within
`F-DISCOVERY-AND-CONFORMANCE`. This is a small investigation of checking-process
integrity, not a mathematical-meaning review or independent kernel-fault study.

## Question and scope

For one formalized endpoint from [openai/math](https://github.com/openai/math),
does the actual Comparator workflow distinguish completed checking of the
requested object by both Lean and Nanoda from omitted checking or mismatched
inputs? Observe its existing behavior first, then identify what an existing LAL
sentinel adds. A configuration that requests only Lean is not itself a false
claim that Nanoda ran. Fresh reproduction cannot establish past execution.

Start with one endpoint, one clean baseline and four local fault scenarios.
Three endpoints through the same workflow would mostly repeat the integration
test; additional endpoints need a later evidence-based selection. Before any
checker outcome, pin the release/toolchain/Comparator versions and actual command,
choose a supported endpoint using source, format and dependency-size inspection,
and record the choice and any exclusions. Prefer a small available dependency
closure; do not inventory or build the entire release. Retain an independently
specified formal target and relevant definitions outside the proof workspace.
Do not replace a selected failure with an easier successful endpoint.

## Small executable investigation

1. Inspect the pinned command, config and success-output path. State exactly
   which consumer asserts success, which checkers are requested, and whether it
   consumes cached results or receipts at all. The source inspection and setup
   belong to this screen; no separate design study or launch-review committee.
2. Run the real endpoint with both checkers requested. Retain the target type,
   dependency/export identities, assumptions, actual invocations and terminal
   outcomes. Bind the reference target before deriving observations from the
   solution. Report compatibility/setup failures separately.
3. Exercise four isolated variants: omit the requested Nanoda invocation;
   substitute a different valid target; change a bound dependency; present a
   success receipt for different inputs or an earlier execution when fresh
   execution is required. Record the exact claim each variant violates. A valid
   changed proof can still be accepted; stale provenance is a different failure.
4. Compare the native consumer's behavior with the existing LAL check. If the
   native workflow has no receipt consumer or no corresponding success claim,
   record that boundary explicitly. Do not invent an upstream defect or build
   a general receipt framework to make the scenario applicable. A small local
   adapter is sufficient to test a useful, explicitly additional LAL check.

Keep requested / invoked / completed distinct from unsupported / failed /
accepted / rejected. Use actual process and artifact evidence, including both
output streams, rather than a flag or aggregate exit code alone. An unchanged
baseline must still pass the added check; detecting every variant by rejecting
everything is not a useful result.

Reuse the checked-object sentinel, real-proof slicer and tested supervisor
(`lib/resource_envelope_supervisor.py`), with the existing isolated execution
path for unfamiliar proof builds. Record per-process time, memory and cleanup
controls before launch. The assumption-reporting pilot covers two Lean routes
and `.olean` metadata, not independent NDJSON checking: inspect the actual
exported-assumption path instead of inheriting an unsupported guarantee.
No host-security or formal-to-informal correspondence claim follows.

## Minimal record and decision

Use one E0 start/finish pair for this fixed screen, raw attempts and one short
result table. Keep exact identities and controls in that record; no separate
manifest hierarchy, new schema, repeated model reviews or per-scenario reranking.
Repair ordinary engineering failures in this item and retain every attempt.
Record available elapsed/token use and explicit unknowns; no invented cost.

Close SIGNAL, NO_SIGNAL or INCONCLUSIVE with a concrete recommendation for the
pinned Comparator/OpenAI-math integration, or an evidence-based no-action
decision. Missing execution is not a successful negative. An informative
positive or negative may justify a separate fresh E1 confirmation; none starts
automatically. Do not expand the sample, build a new checker, train a model,
change production upstream code or contact an external project.

At campaign closure use `scripts/exploration-record check`,
`scripts/exploration-handoff --base <campaign-entry-commit> --write`, then
`--check`, and `git diff --check`; deliver on main. No assurance refresh, full
research replay or routine independent closure review for E0-only records.
Shared tooling changes retain their applicable tests. Selection now launches
nothing; record ACTIVE and the E0 start when this item is actually taken up.

Sources: [Lean validation boundaries](https://lean-lang.org/doc/reference/latest/ValidatingProofs/),
[the external re-check lead](https://github.com/davegoldblatt/openai-zeta-proof-check/blob/main/REPORT.md),
[existing pipeline pilot](../../results/research/pipeline-completeness-pilot-2/report.md),
[assumption-reporting limits](../../results/research/trust-assumption-pipeline-pilot-1/report.md),
[real-proof slices](../../results/research/real-proof-slices-pilot-1/report.md).
These motivate reuse; version-specific behavior is rebound during the screen.
