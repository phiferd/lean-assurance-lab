# CVC-4-CONDITIONAL — exact artifact and implementation comparison

**BOUNDED_UNRESOLVED** at a characterized frozen-byte/importer boundary.

| Input | Model status | Official Lean 4.33.0 | Nanoda 6ae1f0c |
| --- | --- | --- | --- |
| E-CONTROL | CHECKED_REQUIRED_ACCEPTANCE | ACCEPT | ACCEPT |
| E-POS | CHECKED_REQUIRED_ACCEPTANCE | REFUSED_TYPE_COMPARISON | ACCEPT |
| E-ZERO-CONTROL | MODEL_VALID_BY_DEFINITION | ACCEPT | ACCEPT |
| E-ZERO | CHECKED_MODEL_INVALID | REFUSED_TYPE_COMPARISON | REFUSED_TYPE_COMPARISON |
| E-OWNED-CONTROL | MODEL_VALID_BY_DEFINITION | ACCEPT | PARSER_ERROR |
| E-UNOWNED | CHECKED_UNSUPPORTED | NOT_RUN | NOT_RUN |

The pinned official observer refuses E-POS, one of the exact required acceptances of CVC-U1-A7; Nanoda accepts it. Both accept the right-successor and zero controls and refuse the zero-invalid candidate. The ownership comparison is unresolved: the official control accepts, but Nanoda fails in its parser before checking the control; neither ownership candidate was launched.

For every named natural-number assignment, `imax u (v+1) = max u (v+1)`. The checked bridge proves the supplied sort body meets the named model under A7. Refusal by the official observer therefore limits that observer’s acceptance relative to this model; it supplies no invalid accepted proof or universal defect claim.

The exact source mapping separates parsing, reconstruction, validation and semantic use. Both parsers retain `imax`; Nanoda’s comparator simplifies right-successor `imax` to `max` and right-zero `imax` to zero. The official path reaches C++ `is_equivalent`, but its internal implementation bytes were unavailable locally. The installed Lean-level normalizer contains the rewrite and cannot substitute for that missing C++/binary connection.

A7 remains explicit. The proof uses the official Lean runtime and imported Lean4Lean results; it is not an independent validation of the official observer. Nanoda and official use distinct parser lineages. Their source-to-binary correspondence and arbitrary-byte import/refinement remain unproved.

E-POS and E-CONTROL retain their original byte hashes. Four new Lab-authored NDJSON streams instantiate the zero and ownership boundaries plus controls. New metadata describes format compatibility, not exporter-produced proof provenance. No frozen catalog, authority assignment or prior disagreement was changed.

The first execution paused after two charged launches: the official control passed, while Nanoda reported typecheck success with an unexpected pretty-printer error. Source inspection found that default `print_axioms=true` requests printing without a destination. An explicit same-item tooling revision sets only that diagnostic flag false and runs fresh counted controls. Original configs, tests, raw logs and the failed output hypothesis remain unchanged; no earlier result is retroactively accepted.

The revised execution then paused at its tenth launch. Nanoda panicked at `parser.rs:506` while importing the ownership control: the stream declares unused `v` but has no `Level::Param(v)` record. The parser unconditionally requires such a record for each declared parameter. The unowned candidate has the same missing-record prerequisite by source inspection, but was not executed. This parser error is not an ownership refusal or a model counterexample.

Diagnosis found no repair that preserves the selected bytes and observer binaries. Adding a parameter record would retain the structured AST meaning but change the exact scientific artifact submitted for this comparison. A wrapper would likewise change observed bytes; a parser rebuild would change the pinned observer and exceed the zero-build allowance. Changing output classification would weaken the acceptance control. The source prerequisite is now covered by a pure regression. Original failures remain unchanged. A separately reviewed scientific-input transition is needed before any byte variant can be executed.

The item used 12 of 16 allowed validator launches (2 retained first-run launches plus 10 revised launches), 0.386228 process seconds and 2830.644582 active seconds including engineering, below the 16200-second cap. Every launch had a 30-second limit. Two pairs completed; nine revised hypotheses matched, one control hit a parser error and two cells were not launched. Four launch slots remain unused. No setup build or research-network request ran. Required administrative closure fixtures are recorded separately.

Next: **CVC-4-ADAPTER-REVIEW**, selected READY and unstarted for one existing-evidence input-boundary proposal or stop decision. CVC-5 is not promoted. Existing imax defect recommendations remain withdrawn; the partial result and adapter diagnostic stay local. No new scientific inputs, successor execution or external submission start here.

Reproduce the evidence checks with `scripts/validate-cvc4-evidence --require-full-payload`; omit that option to inspect retained evidence without ignored observer binaries. The stopped run cannot be resumed through the launch command. See [result](result.json), [source mapping](mapping/mapping.json), [fixed cases](cases.json), [adapter diagnosis](adapter-boundary.json), [original ledger](run-0001/events.jsonl), [revised ledger](run-0002/events.jsonl) and [closure validation](../../../workflow-refresh/cvc-4-conditional-2026-09-07/validation.json).
