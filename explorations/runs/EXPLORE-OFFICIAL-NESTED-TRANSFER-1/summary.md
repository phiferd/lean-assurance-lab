# Official Lean historical-fault transfer E0 result

**What did we find?** The fixed 90-file compact sample produced no verdict
difference between the exact official Lean 4.29 and 4.33 binaries. All 90 inputs
were comparable, all 180 supervised executions completed, and no parser,
adapter, timeout, cleanup or other compatibility boundary occurred.

**Is it interesting?** No. This sample did not detect the historical
nested-unused-parameter fault. That is a bounded corpus blind spot, not evidence
that the fault was absent or that either binary is generally correct.

**Does it require more work?** No result-driven follow-up is warranted. The
screen used the complete preregistered sample and the known fault-specific
Collatz witnesses were deliberately excluded.

This is E0 screening evidence over exact retained binaries. It does not measure
defect prevalence, implementation quality, conformance or correctness.
