# Exploration protocol adoption — 2026-09-29

**What did we find?** A small E0 ledger can record a prior question, input/source
identity, raw outcomes and separate confirmation proposals without invoking
research closure. Fifteen focused tests pass, including incomplete-observation
rejection, retained evidence, interrupted starts and CI routing. No scientific
pilot ran and no operational savings have been measured.
**Is it interesting?** Yes, as a concrete cheaper path for hypothesis screening.
The tests establish workflow behavior, not semantic correctness or efficiency
in a real research campaign.
**Does it require more work?** Complete the adoption's full repository validation
and derived-state refresh, recorded under `results/workflow-validation/exploration-protocol-1/`.
Then retain the lane. The separately selected closure-reliability item addresses
stable inputs, resumability and cost accounting before a new semantic campaign.
The memory attribution audit is deferred, not scientifically resolved.

The implementation adds one event schema, one small record/check/proposal command,
one ledger (initially empty) and focused regressions. Existing process supervisors
remain responsible for execution safety. E0-only ledger/raw commits take lightweight
CI; shared changes still take the complete path. Confirmation is a new PLANNED
identity with no launch authority. E0 cannot be relabelled or substituted for a
fresh confirmation result. Existing E1/E2 and historical gates remain unchanged.

No external contribution or experiment follows from this engineering result.
