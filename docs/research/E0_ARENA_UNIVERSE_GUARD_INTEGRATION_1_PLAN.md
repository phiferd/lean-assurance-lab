# Integrate one missing-universe-parameter rejection case

Evidence class: E0

Selected READY and unstarted on 2026-10-21 after the source-only corpus reuse
assessment. That assessment identified one useful snapshot-specific gap:
rejecting a definition whose type/value uses a universe parameter omitted
from its declaration's parameter list. Existing duplicate-parameter and
constant-instantiation-arity cases test different conditions.

Prepare one minimal local Arena data-only patch: a standalone
`tests/undeclared-universe-parameter.ndjson` and its YAML metadata with expected
rejection. Reuse the retained `P1-invalid` scientific content and the unchanged
P1 valid control. Recheck current target duplication before preparing a new
contribution; bind the selected target revision, candidate/control bytes,
metadata/schema expectations and compatible cached checker identities before
one E0 start. This is integration of a known case, not a fresh fault holdout.

Use the existing Arena file-test convention and retained raw-input runners.
Validate the metadata/discovery path and locally reproduce the expected reject
and accept on official Lean and Nanoda: two inputs, four initial calls. Require
the actual undeclared-parameter diagnostic/guard, not just a nonzero exit.
Preserve all attempts and repair ordinary tooling/compatibility failures
without changing the intended omission. No Mathlib or whole tutorial build,
new checker, formal model, mutation benchmark or additional test family.

Deliver the minimal patch and exact local evidence, or a concrete duplicate/
compatibility no-go. Track any prepared contribution candidate through the
existing external-contribution ledger and builder; do not create a new
tracking mechanism. No posting, PR, issue, branch push or maintainer contact
is authorized. Any submission requires human approval for its exact target.

Use the existing lightweight E0 start/finish, ledger/diff/handoff checks and
applicable existing ledger/schema validation. No full assurance regeneration
or routine independent closure review solely for this pilot. Finish this one
item, select its successor and stop before starting it.
