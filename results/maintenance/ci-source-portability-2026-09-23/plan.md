# CI source portability repair — 2026-09-23

Status: LOCAL VALIDATION COMPLETE; awaiting GitHub CI on the pushed repair.

Repair the existing unit-test entry point's assumptions about ignored Kiota
source materialization and a particular macOS Cargo registry/toolchain. This is
routine tooling maintenance under RESEARCH_WORKFLOW.md, not a new scientific
item or milestone. TRUST-ASSUMPTION-PIPELINE-PILOT-1 remains READY and unstarted.

Failed CI: https://github.com/phiferd/lean-assurance-lab/actions/runs/35854272482
at dacfcc76bf8d1521cd1f0f6e7f3977d770c83e8e. Preserve failed-ci.log. The live
suite reported seven failures and five errors; historical suites passed. Local
full-payload results had hidden the clean-checkout portability issue.

Implement an offline, exact source-only test bootstrap from the committed Kiota
archive, reusing existing archive and tree verification. Never overwrite a
mismatched existing source tree, alter frozen bindings, or build/run a checker.
Keep host-specific frozen integration checks explicit: absent native payloads
must be visible, and --require-full-payload must remain strict. Add portable
regressions for preparation and host verification logic, and a clean-checkout
regression that demonstrates the original failure and repaired path.

Delegates independently diagnose source custody and host-dependent tests, then
own disjoint portable helper/test files. The parent owns the unit entry point,
workflow integration, evidence, validation, review and delivery.

Validate focused failures and new regressions, run the complete suite from a
clean checkout with no ignored external source (native host resources remain
available on this Mac), verify absent host payloads on GitHub Linux CI, run the complete
local full-payload current/historical suite, and preserve immutable predecessor
checks. Push the repair to main through scripts/push-main and confirm GitHub CI
passes on the delivered commit. Any engineering failure is repaired within this
maintenance task; no assurance or payload gate is weakened to obtain a pass.
