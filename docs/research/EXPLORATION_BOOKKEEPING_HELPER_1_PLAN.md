# E0 bookkeeping helper

What did we find? Six closed screens needed schema corrections and a count correction despite retained receipts. Is it interesting? Yes, a small deterministic helper can reduce mechanical transcription without replacing scientific judgment. Does it require more work? Implement drafts and fail-closed receipt accounting in the existing exploration-record CLI; no new receipt system or launch.

Owner-approved local maintenance, separate from the closed source-only triage.
Generate unappended start/finish drafts from the current event schema, selected campaign and existing ledger. Preserve explicit unresolved fields for researcher question, controls, interpretation, outcome and decision. Reuse append validation; drafts grant no execution authority. Derive supported counts from retained receipt layouts, deduplicating repeated result/cell exports and rejecting conflicting identities or unsupported/ambiguous counts. Reproduce 40 final cells, 48 launches, three prelaunch failures and eight retained construction cells in the six-trial campaign. Do not infer construction merely from subtraction: identify final attempt receipts against the finish count and keep earlier receipts separate. Frozen evidence remains unchanged. Add meaningful regression tests, run affected exploration/queue tests and applicable portable replay and full unit-suite checks. Shared tooling changes require the full validation path; E0 handoff alone is insufficient. Keep all work local, no publication.

## CLI use

`scripts/exploration-record draft start EXPLORE-EXAMPLE-1` prints a wrapper
containing an `event` object and its `unresolved_fields`. It reads the selected
READY/ACTIVE E0 campaign and schema. A selected maintenance item without an E0
plan is deliberately refused. The lab source revision and plan inputs are
initial suggestions; add every actual source, dirty patch, input and tool identity.
Scientific question, sample, controls, command and planned count remain null.

For an OPEN trial, `scripts/exploration-record draft finish EXPLORE-EXAMPLE-1`
keeps outcome, interpretation and completeness unresolved. Optionally supply
`--raw-output <retained-file>` repeatedly and `--final-result <result-json>`
to populate supported completed cells and receipt-cost counts. The final result
must be included in raw output. Source-only observations with no supported
process receipts keep counts unresolved for manual review.

Save the wrapper's `event` object, fill all null fields, review identity/scope,
and use the unchanged `scripts/exploration-record append event.json`. Appending
still enforces campaign authorization, schema, lifecycle, input hashes and
NO_SIGNAL completeness. No draft is executable authority or an appended event.

`scripts/exploration-record counts --campaign <closed-campaign> --final-result
<result-json>` (repeat once per trial) prints supported final/launch/prelaunch
counts without writing evidence. Explicit final selection is required because
an earlier construction attempt can contain the same number of cells. All finish
raw references are inspected for retained launches; receipt copies share one
raw-stream identity, and conflicting copies or missing/tampered streams fail.
Prelaunch error exports deduplicate by retained attempt directory. Other error
layouts fail closed. Nonfinal cells are retained work, not automatically waste.
The helper does not derive verdicts or estimate money/time savings.
