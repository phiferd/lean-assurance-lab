# Recursor trust: a bounded historical check — October 24, 2026

**What did we find?** The Lab already mutated imported Nanoda recursor flags
and types, compared reconstructed metadata, and transferred those inputs to
other checkers. The reviewed records do not demonstrate detection of the later
field-count or declaration-placement faults. This is a provisional diagnosis
from selected records, not a complete historical coverage audit; no checker ran.
**Is it interesting?** Yes. The gap appears to be incomplete follow-through from
individual validation checks to every path by which imported information becomes
trusted, rather than an absence of metadata testing or cross-checker work.
**Does it require more work?** Freeze the full pre-disclosure asset inventory and
measure its coverage in the planned historical campaign. Separately test a new,
explicitly informed defensive strategy for validating metadata and declaration
relationships.
The already selected merged-Lean replay remains the next, separate queue item.

## Evidence examined

These are historical observations at their recorded targets, not claims about
current checker behavior. Links identify the controlling reports and receipts.

| Record | Method and observed scope | What it does not establish |
| --- | --- | --- |
| Aug. 27 [restored recursor flag](../../investigations/nanoda-restored-recursor/README.md) and [source trace](../../investigations/nanoda-restored-recursor/SEARCH_NOTES.md) | Changed exported `k` from false to true; baseline rejected, a checker mutant skipping `aux_data_ck` accepted, and both accepted the control. The trace names count/name/flag comparisons and separate type/rule checks. | No later declaration consumed the changed flag in the recorded seed. A killed checker mutant is not a demonstrated defect in the baseline. |
| Aug. 28 [restored recursor type](../../investigations/nanoda-restored-recursor-type/README.md) | Changed only the auxiliary recursor's type pointer, 49 to 68; baseline rejected and a mutant skipping reconstructed-type comparison accepted. Cross-checking retained Kiota acceptance. | No enumeration of alternative import/install paths, and no field-count or placement mutation in this case. |
| Aug. 28 [restored constructor](../../investigations/nanoda-restored-ctor/witness-analysis.json) | Changed exported constructor index `cidx`, 0 to 1, against a corresponding check mutant; valid control passed. | This tests one relationship on the checked path, not completeness of validation across paths. |
| Sept. 13 [semantic import contract](../semantic-import-contract-1/report.md) | Reviewed four one-scalar pairs (`k`, recursor type, constructor index, `numIndices`) and compared supplied, reconstructed, retained and consumed information. Recognized policy differences and unresolved universal obligations. | The report explicitly notes incomplete baseline source/binary identity in three older Nanoda receipts. These cannot be promoted to fully identified execution evidence without resolving that gap. |
| Sept. 14 [Nanoda nested regression](../nanoda-nested-regression-1/report.md) and [design](../nanoda-nested-regression-1/regression-design.json) | Source-only design for reserved `_nested` namespace traversal and in-memory type substitutions at pinned Nanoda `4c544ed4`. | No imported metadata mutation or Nanoda launch; the word “nested” does not establish coverage of these faults. |
| Sept. [Kiota trust-boundary analysis](../recursor-type-trust-boundary-1/report.md) and [repair](../kiota-recursor-type-repair-1/report.md) | Traced retained serialized recursor types into constant inference; designed reconstruction, comparison/replacement, complete-block staging and rollback. | A Kiota repair does not establish the analogous Nanoda invariant, although earlier cross-checker experiments did contribute to this line of work. |
| Sept. 22 [repair closure decision](../queue-reviews/2026-09-22-kiota-recursor-type-repair-1-closure.json) | Compared assumption-reporting and stateful-validation successors; selected transitive assumption reporting. | The recorded candidate comparison contains no analogous cross-checker recursor trust audit. This is evidence of an omitted follow-through option, not a complete causal account of why two bugs were missed. |
| Oct. 3 [historical-fault transfer plan](../../../docs/research/E0_HISTORICAL_FAULT_TRANSFER_SCREEN_1_PLAN.md) | Fixed 90-file corpus against affected/fixed Lean nested-unused-parameter and Nanoda projection-identity versions; generated candidates were outside scope. | Fixed-corpus transfer is not a general exported-metadata or declaration-placement generator. |

## Revised diagnosis

The evidence contradicts “the Lab did not mutate imported recursor metadata”
and “the Lab never transferred a trust-boundary finding.” Both happened. It
supports the narrower hypothesis that experiments centered on selected checks
and retained cases, without demonstrated coverage of all routes from imported
recursor information to trusted reduction or inference. The repair closure's
successor comparison is a concrete place where analogous obligations could have
been considered and were not recorded as a candidate.

The common obligation is: information used to justify typing or reduction must
be validated against trusted structure, or replaced by safely reconstructed
information, before use on every reachable installation path. Merely parsing a
serialized field does not imply that accepting a change to it is unsound. A
checker may safely ignore or reconstruct redundant fields. Conversely, rejection
on the normal path says nothing about an alternative path that bypasses it.

The October 23 repairs define known historical regression targets, as documented by the
[dated upstream observations](upstream/verified-metadata.json). This note does
not replay either published reproduction input. Excluding their bytes cannot undo exposure
to their mechanisms: a generator designed now is informed development, even if
it derives cases from general invariants and uses unrelated seeds. Only an
unchanged pre-disclosure detector can support a prior-capability claim; even
then, retrospective detection is not proof that the Lab would have selected or
run it at the time.

## Change in direction

The [successor plan](../../../docs/research/RECURSOR_TRUST_BOUNDARY_PLAN_2026_10_24.md)
requires a compact source inventory, mutations at the public import boundary,
and an explicit cross-checker disposition after a consequential finding. It
separates historical capability, informed retrospective development, and future
transfer. It adds no assurance framework, changes no frozen result, and starts
no experiment. The Arena universe confirmation remains deferred.

This documentation checkpoint used one bounded read-only delegate for historical
extraction. No scientific build, checker execution, input generation or external
write occurred. Aggregate model-token usage is unavailable; no cost estimate is
inferred. The full asset inventory and exact pre-repair/repaired execution profiles
remain unbound.
