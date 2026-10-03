# Nanoda historical-fault transfer E0 result

**What did we find?** The fixed 90-file compact sample produced two raw verdict
differences between the exact Nanoda revisions: the affected binary accepted
both possibly-Prop projection cases and the fixed binary rejected both with
`infer_proj prop`. All 90 inputs were comparable, all 180 supervised executions
completed, and no parser, adapter, timeout or cleanup boundary occurred. Source
review traces both differences to the fixed revision's separate conservative
possibly-Prop projection policy. They do not demonstrate transfer to the target
projection-structure identity fix in `def_eq_proj`.

**Is it interesting?** Yes, as a guard against a false coverage claim. The two
differences reproduce a profile distinction already characterized by the Lab;
Arena PRs #167 and #171 explicitly permit either outcome. They supply no new
target-fault evidence.

**Does it require more work?** No result-driven confirmation or PR follows.
Retain the two rows as E0 `SIGNAL`, preserve their causal qualification, and
close with no external action.

The [diagnostic review](diagnostic-review.json) binds the exact attempts, source
diff and prior disposition. This E0 screen does not measure defect prevalence,
implementation quality, conformance or correctness.
