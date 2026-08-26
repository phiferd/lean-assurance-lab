# Publication Readiness Audit

Audit date: 2026-08-26

Audited base revision: `1fc23bb`

Status: **GO, with publication-day controls pending**

## Scope

This audit covers the tracked repository and Git history, GitHub repository
metadata, ignored payload boundaries, public documentation, local links,
credential patterns, executable and binary files, fresh-clone tests, and
third-party provenance relevant to publication.

## Passed Checks

- No private keys, common provider tokens, credential files, authentication
  headers, or suspicious secret assignments were found in tracked content or
  reachable commit history by the repository-local pattern scan.
- The publication candidate contains 314 tracked files. Its largest file is the
  10,184,927-byte repaired projection witness, below GitHub's 100 MB per-file
  limit.
- No unexpected binary or executable payloads were found.
- No unsafe `shell=True`, unsafe YAML loading, `pickle`, `eval`, or `exec`
  use was found.
- All local Markdown links resolve.
- Public status language preserves the current failing assurance gate,
  unresolved checker disagreements, bounded claims, and explicit non-claims.
- Contribution forms and responsible-disclosure guidance are present.
- A no-external-checkout clone runs the unit suite after the publication-audit
  repair; the materialized-validator compatibility test is explicitly skipped
  at that boundary.

## Resolved Publication Blocker

The repaired 10 MB projection witness is derived from Lean Kernel Arena's
`perf/grind-ring-5` export. Arena collaborator Joachim Breitner clarified that
Arena tests record their source provenance and are generally under the Apache
License, Version 2.0, in
[leanprover/lean-kernel-arena#162](https://github.com/leanprover/lean-kernel-arena/issues/162#issuecomment-5421173941).

The repository now uses the same Apache-2.0 license. [NOTICE](../NOTICE) traces
the source revisions and prominently records the modifications to the repaired
projection witness and the two Milestone 6 derivatives. No pre-publication
provenance blocker remains.

## Publication-Day Controls

Immediately after changing visibility, enable private vulnerability reporting
and protect `main` with the unit-test workflow as a required check before
inviting contributions.

## Owner Decisions

- Existing commit-author email and historical local-path disclosures are
  accepted; repository history will not be rewritten. Future commits in the
  local checkout use the authenticated GitHub noreply address.
- The complete repository uses the Apache License, Version 2.0. Identified
  third-party derivations and modifications are recorded in `NOTICE`.
- CollatzLean is referenced only by links; its content is not redistributed by
  this repository.

## Improvements Applied During Audit

- Added `requirements-dev.txt` and a least-privilege GitHub Actions unit-test
  workflow.
- Replaced the initial MIT license with Apache-2.0, aligned inbound contribution
  terms, and added a third-party provenance and modification notice.
- Made the materialized-checker compatibility test skip cleanly when a clone
  does not contain the ignored Arena checkout.
- Added `SECURITY.md` with coordinated-disclosure instructions.
- Added clone-safe setup and test instructions to `README.md`.

## Non-Blocking Limitations

- The 9.5 GB materialized corpus and complete coverage payload remain ignored.
  Their tracked manifests verify local materializations, but durable remote
  payload storage is still an open project task.
- The full validator and coverage workflows require pinned external tools and
  are intentionally not run in lightweight pull-request CI.
- The local scan is not a substitute for GitHub secret scanning. Enable secret
  scanning and push protection when repository visibility and account features
  permit it.

## Final Verification

- All 58 local unit tests pass.
- Portable coverage verification passes with 197 tests and 3,451 canonical
  covered locations.
- Milestone 8 passes all 24 checks; Milestone 9 passes all 26 checks, including
  the Apache license and derived-artifact notice check.
- The artifact graph reports 91 current, 7 historical, and 4 superseded nodes,
  with all current claims valid.
- The current assurance gate still fails solely for the two unresolved semantic
  checker disagreements. Publication readiness does not suppress that result.

Publication can proceed. Apply the publication-day controls in the same
visibility-change session.
