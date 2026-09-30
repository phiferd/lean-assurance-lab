# 2. Python/testing: preserve rejection-with-formatting-panic as a small fixture

Local task draft for owner review; unpublished and unassigned.

**Question:** Can a small retained fixture keep semantic rejection, diagnostic failure and supervisor failure distinguishable in reports?

**Prerequisites:** Python/unittest, reading JSON and captured stderr. Repository files only; no compiled Lean, importer or large corpus. This is fixture/reporting work, not a request to repair Lean4Lean.

**Starting evidence:** `explorations/runs/EXPLORE-SEMANTIC-INVALID-TARGET-1/attempt-0001/invalid-first-lean4lean/{supervisor.json,process.stderr}`, its valid baseline, `lib/pipeline_completeness.py:process_classification` and the source-only triage summary. The captured invalid target exits 1, includes an extension-access panic and ends with a declaration type mismatch/raw-printer fallback. Exact original source/binary correspondence remains unestablished.

**Expected artifact:** A focused regression fixture/test showing (a) the retained valid baseline ACCEPT, (b) the retained malformed target REJECT with diagnostic-panic text preserved, and (c) a synthetic supervisor timeout or monitor error classified separately as INFRASTRUCTURE_FAILURE. Use the existing process classifier and raw evidence; no verdict-by-text parser or new receipt system. If the current report path drops the raw diagnostic distinction, describe the exact field/path before proposing the smallest repair. Do not call exit 1 alone semantic proof or change the scientific outcome.

**Go:** Existing retained bytes and supported receipt fields suffice; reference or copy with provenance and keep original bytes unchanged. **Stop:** A checker rerun, new build, source/binary causal claim or unrelated parser redesign would be required; record that boundary. A test that merely repeats the classifier's branches without the real fixture is insufficient.

**Completion:** The fixture plus control test passes and preserves the diagnostic limitation, or a precise reporting boundary is documented. Run affected tests; shared code changes require the applicable full checks. No upstream defect claim or communication follows.
