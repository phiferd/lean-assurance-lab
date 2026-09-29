# Short-process memory accounting audit 1

Status: READY and unstarted. This is a scoped follow-up selected after
`RESOURCE-ENVELOPE-PILOT-1`. It audits the meaning and provenance of the
existing short-process memory observations. It does not authorize checker
builds, observer launches, changes to the frozen resource inputs, or a rerun of
the fixed matrix.

At entry, create
[`results/research/resource-envelope-short-process-memory-audit-1/work-record.json`](../../results/research/resource-envelope-short-process-memory-audit-1/work-record.json)
with the exact frozen receipt and source bindings before any audit work begins.

## Plain-language purpose

**What did we find?** The resource pilot's twelve Nanoda cases and six Nanoda
empty-input baselines all completed in roughly four milliseconds. The
supervisor targeted a ten-millisecond sample cadence; all eighteen runs have
zero sampled RSS points and no sampled group peak. Their receipts do preserve
an operating-system `wait4` child-accounting high-water value. The absence of
samples is an observed limitation of these short runs, not proof that the
configured cadence alone caused it.

**Is it interesting?** Yes. The data expose a real distinction between sampled
process-group memory and the high-water value returned when a child exits. A
reader needs to know exactly what the latter can support before treating it as
a resource result.

**Does it require more work?** Yes. Audit the exact eighteen Nanoda receipts,
their direct executable identity, the supervisor's `wait4` and unit handling,
and the recorded Darwin platform against primary operating-system
documentation. Report a scoped use or limitation for the preserved
high-water values, and specify the host metadata needed in future runs. Keep
the original result unchanged and retain its null sampled group peaks.

## Question and fixed scope

For the twelve scientific and six baseline Nanoda receipts in the reviewed
resource result, what does `wait4(pid, 0)`'s `ru_maxrss` value represent on the
recorded Darwin 24.6.0 arm64 host, and can those values be described as a
target-process lifetime high-water, an OS child-accounting high-water, or a
process-group peak?

The audit covers exactly those eighteen receipts, the frozen R2 execution
manifest, the reviewed scientific result, `lib/resource_envelope_supervisor.py`,
`lib/resource_envelope_observe.py`, and the exact Nanoda executable/source
bindings already retained by the resource item. Reuse the prior
[`independent-measurement-rss-attribution-correction-r1.json`](../../results/research/resource-envelope-pilot-1/independent-measurement-rss-attribution-correction-r1.json)
as a prior review, not as proof about an exact kernel build: it inspected
Apple-published XNU `main` and explicitly preserved that source-version limit.
Primary reuse references are Apple's [`wait4(2)` manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/wait4.2.html),
the pinned runtime's [Python 3.10 `os.wait4` documentation](https://docs.python.org/3.10/library/os.html#os.wait4),
and the source links already recorded in the correction. The Apple manual
describes resource usage for the terminated process and its children; it does
not make that result a simultaneous process-group peak.

The report must preserve these distinctions:

- `maximum_sampled_group_rss_bytes` is `null` for all eighteen Nanoda runs;
- each receipt's `child_peak_rss_bytes` is the normalized `wait4` value with
  its raw value and unit retained;
- an OS child-accounting high-water is not a simultaneous process-group peak;
- the historical runtime binding records `Darwin`, release `24.6.0`, and
  `arm64`, but does not contain the full kernel build string; a present-day
  host readout cannot retroactively supply that missing historical identity.

Do not alter, regenerate, or relabel the frozen result, manifests, receipts,
raw streams, or earlier review. Do not claim sampled memory where no sample
exists. Do not infer a general memory bound, an implementation ranking, or a
measurement result for other hosts or runtimes.

## Preparation and review gates

1. Create and commit this successor's work record with the exact hashes for the
   reviewed result, all eighteen selected receipts, R2 manifest, prior
   attribution correction, supervisor, observer auditor, and pinned Nanoda
   executable/source binding. Preserve the distinction between result bytes
   and derived interpretation.
2. Independently check each receipt's cell or baseline label, direct `argv`,
   process identity, exit status, elapsed time, sample count, sampled peak,
   raw `ru_maxrss`, unit, and normalized high-water against the frozen result
   and custody hashes. Keep an explicit row for every one of the eighteen
   runs.
3. Read primary Apple documentation for `wait4` and any exact-version source
   available from the recorded host binding. Compare the result with the
   existing correction's XNU-main source inspection. If exact historical
   kernel correspondence cannot be established from committed evidence,
   record that boundary and do not substitute a current `uname` value.
4. Decide which wording the evidence supports for these exact values. If
   descendant-accounting behavior or target attribution remains uncertain,
   retain the conservative `OS child-accounting high-water` label and state
   the missing evidence. Give the minimum host metadata to record in a future
   resource run, including the full kernel build identity and raw/unit fields.
5. This item authorizes no process launches, including synthetic subprocesses;
   use only read-only receipt, source, and documentation checks. A future
   process-control experiment would require a separately selected item and
   its own exact input and launch gates. No external action is authorized.

## Completion

Complete when a reproducible eighteen-row receipt audit supports either a
precisely scoped metric interpretation or a named historical attribution
boundary, and the report gives a concrete future metadata/method rule. Preserve
the prior result's zero-sample observations and all historical bindings. This
item may recommend that the current high-water values remain descriptive
OS-accounting data while future studies bind an exact kernel build. It cannot
retroactively improve the sampled process-group measurements.
