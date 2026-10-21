Arena discovers and copies the proposed test correctly. On the retained Lean and Nanoda profiles, both checkers reject the definition with its used universe parameter omitted, and both accept the unchanged valid control: four usable observations. This is a useful small shared regression candidate, with no unexpected validator behavior (E0 NO_SIGNAL). It establishes neither a current checker defect nor general correctness.

The local patch adds only `tests/other/undeclared-universe-parameter.ndjson` and its rejection YAML to Arena revision `8bbe253405b7e6a0b741381ecdf3eae0293d61ba`. Current Arena uses `master` and organizes synthetic cases under `tests/other`; the older proposed root spelling was adjusted accordingly. No upstream file, branch, PR or issue was modified.

Recommend this one testcase for `leanprover/lean-kernel-arena`, at normal priority, after current-profile compatibility, applicable contribution gates, fresh duplicate preflight and exact-target submission approval. The next separate local item checks Arena's configured Nanoda revision; it is READY but unstarted. No further case family, model or automatic confirmation follows.

The fresh source preflight retained 266 tracked paths, 182 text sources, zero open PRs, and 16 committed NDJSON exports containing 277 declaration occurrences. The static ownership walk found no omitted used parameter and no unresolved references. This is snapshot-specific source evidence; generated tutorial exports, external libraries and unpublished work are outside it. The minimal two-file patch and source archive are retained here.

| Input | Lean 4.34.1 | Nanoda 3a240721 |
| --- | --- | --- |
| Omitted parameter | Reject, named undefined-universe diagnostic | Reject, `all_uparams_defined` assertion at `tc.rs:554` |
| Unchanged valid control | Accept, one declaration, empty environment/trust 0 | Accept, one declaration |

The raw Lean importer prints the intended name, type, value and parameter list. Nanoda's exit 101 is attributed to the intended semantic guard, not inferred from a generic nonzero status. Current Arena's wrapper coarsely maps failures to rejection; its configuration pins newer Nanoda `e0d76f5ec30bba244023466875b4845a57fd3ea5`. That configured build, four-thread/stdin settings and stack-size patch were not exercised here. Lean's version matches the current configuration; its Arena wrapper itself was not run. The data discovery used the exact current `lka.py`, schema and static-file branch, without a Lean/tutorial build.

All four engineering failures remain: a default-branch preflight assumed `main`, the metadata loader needed Python 3.12+ rather than host 3.10, staging then lacked its output, and the first runner incorrectly launched two checker calls before staging. Those missing-file calls are excluded from semantic results. Repair used Python 3.13 in a temporary venv and a new task-local runner revision that checks successful discovery and all staged input/configuration hashes before any launch. Frozen scientific bytes and the original tooling/attempts remain unchanged. No engineering failure remains unresolved.

Actual work: six checker launches (four scientific cells plus two missing-file failures); final checker invocation time 1.624 seconds. Fourteen supervised preparation/runtime/validation/cleanup commands total 21.019 seconds, including setup and failed attempts; these overlapping measurements must not be added. The task container was stopped. No checker build, mutation or Mathlib run occurred. Aggregate model token and monetary cost are unavailable. See `attempts/`, `observations/`, `observations-r2/`, runtime identity and `audit.py`; command counts are observations, not stopping rules.

The candidate is indexed through the existing external-contribution ledger during delivery. This remains an E0 local integration candidate; no E1/E2 contribution-readiness or upstream adoption claim is supplied.
