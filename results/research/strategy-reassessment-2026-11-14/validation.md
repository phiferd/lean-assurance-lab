# Validation of the research planning revision

The revised queue, plans and generated views agree, and the affected checks
pass after a prose correction and a process-inspection permission repair. Yes,
this is enough to validate the planning update; it establishes no new Lean
behavior. The next research item remains unstarted. Full frozen-host integration
coverage is unavailable because eighteen exact Cargo packages are missing.

## Scope and preservation

Base commit: `e5306b018ddac83478260551b5042108b6d8aa86` on `main`.
All 105 completed queue rows compare equal to the base, including their priorities,
closures and evidence references. The earlier Active narrative is preserved
verbatim under the historical-handoffs heading. The constitution, scientific
inputs, E0 ledger and raw research results are unchanged. No production code,
schema or test implementation changed; the existing count regression exposed
the missing explicit READY-count sentence, which was added to the status prose.

The assurance generator changed only the snapshot's producing-repository
revision. Its measured counts and failing semantic-disagreement gate are
unchanged; downstream snapshot hashes were regenerated through their defined
commands. Artifact freshness is not a claim that the scientific gate passes.

## Commands and observations

| Check | Result |
| --- | --- |
| `scripts/run-unit-tests --require-full-payload` | Preflight exit 2: eighteen exact historical Cargo source packages absent. No full-payload pass is claimed. See retained missing-path log. |
| `scripts/run-unit-tests` | Current suite: 1,678 tests, five errors, three explicit host-integration skips. One error was the missing READY-count prose; four were sandbox denial of `/bin/ps` in supervisor tests. Frozen publication suite: 73 passed. Frozen portfolio suite: 14 passed. Initial failure evidence is retained. |
| Affected test rerun with process-inspection permission | All 74 tests passed after the prose correction. Modules: `test_arena_let_regression_erratum`, `test_metamorphic_supervisor`, `test_research_queue`, `test_research_queue_v2`, `test_research_queue_v3`, `test_research_queue_v4`, `test_project_review_contribution_observations`, `test_external_contributions`, `test_artifact_graph`. No test or gate was weakened. |
| `scripts/check-portable-evidence-replay` | 13 portability tests and one closure-portability test passed. |
| `scripts/exploration-record check --base e5306b018ddac83478260551b5042108b6d8aa86` | PASS: 44 closed E0 trials, no open trial. Two already-recorded lean-action input payloads are unavailable; original ledger identities and retained raw outputs remain valid. No new trial or confirmation observation occurred. |
| `scripts/validate-research-queue --require-ready` | PASS: selected confirmation READY, two READY alternatives in total, integration PLANNED, no ACTIVE item. |
| `scripts/build-external-contributions --write` and `--check` | PASS. Only Nanoda #41/#43 received new dated observations. |
| `scripts/refresh-current-state` | First attempt stopped at project-review generation after snapshot provenance changed, invalidating that strategic evidence binding. Rebinding the current snapshot and retrying completed all fourteen commands. Both attempts are retained. |
| Final `build-project-review --write`, `build-artifact-graph`, then `--check` / `artifact-status --require-current` | PASS after the final prose correction. All 175 current artifact nodes are current; ten historical and four superseded nodes remain distinguished. |
| `git diff --check` | PASS. |

The final 74-test rerun covers every initial error and the changed planning and
generated-view surfaces. The full 1,678-test run was not repeated after these
documentation/permission repairs. This record does not describe that initially
failing invocation as a passing full suite, nor the three skipped host checks
as covered. The planning revision follows the documentation-checkpoint rule in
`docs/RESEARCH_WORKFLOW.md`; future scientific/E2 work retains its full gates.

Exact raw command logs, including failures, are losslessly retained under
[`validation/`](validation/) as `.log.gz` and `.json.gz`; inspect with
`gzip -dc`. The refresh receipts retain their original temporary log paths;
the files themselves are archived alongside this record under `refresh-1-*`
and `refresh-2-*` names. The second bounded independent review found no material
scope flaw and requested the corrected bounded-source wording in the report.

At the accounting checkpoint after local validation, the goal tool reported
224,509 tokens and 1,449 seconds used. It supplied no cache, model, delegate or
billing breakdown, so none is inferred. These are checkpoint observations,
not a final total or an authorization limit.
