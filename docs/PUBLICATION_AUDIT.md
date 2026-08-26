# Publication Readiness Audit

Audit date: 2026-08-25

Audited revision: `3d86039`

Status: **NO-GO pending owner decisions**

## Scope

This audit covers the tracked repository and Git history, GitHub repository
metadata, ignored payload boundaries, public documentation, local links,
credential patterns, executable and binary files, fresh-clone tests, and
third-party provenance relevant to publication.

## Passed Checks

- No private keys, common provider tokens, credential files, authentication
  headers, or suspicious secret assignments were found in tracked content or
  reachable commit history by the repository-local pattern scan.
- The audited revision contains 308 tracked files. Its largest file is the
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

## Publication Blockers

1. **Arena-derived artifact provenance.** The repaired 10 MB projection witness
   is derived from Lean Kernel Arena's `perf/grind-ring-5` export. GitHub exposes
   no detected license for Lean Kernel Arena or CollatzLean. Obtain permission
   or a clear redistribution determination and record attribution before
   publishing that artifact.
2. **Personal-identity disclosure.** Reachable commits contain a personal Gmail
   author address, and historical evidence contains the local macOS username
   in absolute paths. The owner must explicitly accept that disclosure or
   rewrite history and regenerate affected attestations before publication.
3. **GitHub security settings.** After changing visibility, enable private
   vulnerability reporting and protect `main` with the unit-test workflow as a
   required check before inviting contributions.

## Improvements Applied During Audit

- Added `requirements-dev.txt` and a least-privilege GitHub Actions unit-test
  workflow.
- Added the MIT License under `Dan Phifer` and explicit inbound contribution
  terms.
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

Publication can proceed after all three blockers are resolved and the final
checks in this document are rerun against the exact public candidate commit.
