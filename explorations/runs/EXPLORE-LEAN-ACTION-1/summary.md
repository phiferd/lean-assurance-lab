# Local lean-action E0 findings

What did we find? Thirteen controlled shell cells completed. PR192 emits identical axiom configurations on its bundled and source routes with both sorry toggle values, and preserves exporter/checker failure exit codes. Its functional test cannot detect a successful source fallback by looking for directories after the action cleans them up. PR191's existing-policy guard checks a different pathname from the one it writes. Actual bundled versus source checker acceptance remains INCONCLUSIVE: exact Lean 4.35.0-rc2 is unavailable locally. No real checker, source build or privileged setup ran.

Is it interesting? Yes, as a small contribution opportunity in test quality and setup safety. The directory assertion has a concrete controlled counterexample; the AppArmor pathname mismatch is source evidence only. No invalid-proof acceptance, checker conformance, security exploitation or kernel soundness claim follows.

Does it require more work? Prepare fresh E1 regression controls for PR192's no-source-build oracle and PR191's existing-output-file refusal; review exact expectations independently, then run only safe intercepted controls. Real axiom comparison needs an existing exact supported runner and freshly frozen binary/source/configuration identities. No external communication or publication is authorized. PR15373 preparation remains deferred and unstarted.

## Exact scope and evidence

Observed 2026-10-01 around 00:15–00:24 UTC via GitHub connector: PR190/191/192 OPEN/unmerged; conversation comments empty. Reviews not reverified. Revisions are in `source/identities.json`: base96e06131, PR190a4136f49, PR191686ffeb3 (stacked on190), PR192209c085c. Full source snapshots are retained. Cloned current lean-action main was f061402b; analysis concerns the pinned PRs, not an asserted current-main defect. Isolated lab starts at6be539c; original and prior task-2 checkouts were preserved.

`attempts-r3/<cell>/command.json`, `receipt.json`, `stdout`, `stderr`, `github-output` and `calls.jsonl` retain every controlled child. All13 have complete cleanup, no monitor/pipe/accounting fault and no timeout. There were14 actual shell child launches including the sandbox-monitor-failed R2 child. Initial runner construction failed before child launch; original script, prelaunch directory and transparent reconstructed failure description are retained. No broad suite or assurance refresh was performed.

| Controls | Observed exit and output |
| --- | --- |
| bundled/source × sorry false/true | all0, nanoda-status=SUCCESS; configs identical pairwise |
| exporter failure |7, nanoda-status=FAILURE; checker not invoked |
| checker failure |9, nanoda-status=FAILURE |
| one bundled binary missing |0 via mocked source fallback; clones/build commands recorded |
| PR190 actual-host OS represented as Darwin |1, explicit Linux requirement |
| unsupported Lake top-level help with exit0 |1, explicit unsupported-toolchain error |
| failed sandbox probe |2, nothing checked/setup diagnostic; checker not invoked |
| late bwrap failure after successful probe |2, setup diagnostic |
| checker/build rejection |1, rejection/build-failure diagnostic |
| check success |0, lake-check-status=SUCCESS |

All successful Nanoda rows are mock command-routing observations. Mock export payloads are deliberately not Lean proof objects. `Foo` is selected in all7 PR192 cells from a lowercase package name with defaultTargets=["Foo"]. Base already exported one package-derived module, so multiple libraries are a scope clarification rather than a newly demonstrated regression.

## Policy limits

Base and PR192 share propext, Classical.choice, Quot.sound, Lean.trustCompiler, optional sorryAx, and unpermitted_axiom_hard_error:false. The mock checker captures config before cleanup. Source equality plus pairwise captured config equality does not establish that different checker versions implement the same policy. The source path still tracks Nanoda's mutable debug branch; the bundled path uses compiler-matched binaries. Every real future run must identify the binary/source behind each route.

Do not treat a zero exit on a reachable custom axiom or sorry as an unexpected acceptance without consulting that exact checker's documented warning/hard-error behavior. The base hard-error flag is false. This screen did not adjudicate that behavior. Prospective fixture matrix: clean theorem; individually reachable standard permitted axioms; reachable sorry with both toggle settings; reachable custom proposition axiom used to prove that proposition; native_decide with exact reported Lean.trustCompiler dependency. Record selected module, exported dependency/axiom inventory, config, status and diagnostics separately. No allow-sorry migration to paranoid is promised; PR192 explicitly warns that none exists.

PR190 already contains clean-versus-sorry paranoid and unsupported-toolchain functional tests; no duplicate clean/sorry PR190 contribution is proposed. The local controls add source-bound exit/setup distinctions only. PR191 privileged branches, root-owner/symlink trust checks and real Linux behavior remain unexecuted.

## Contribution candidates (private and unsubmitted)

1. PR192, normal priority: replace post-cleanup directory absence with a durable branch/build observation. Source trap unconditionally removes _lean4export and _nanoda_lib. The forced source-false control records both clones and both build commands, returns SUCCESS and leaves both directories absent, which satisfies the existing assertion. A proposed replacement must pass bundled-path control and fail successful-fallback control. This is an E0 test-oracle signal, not a checker defect. A minimal design is an explicit route output or intercepted forbidden clone/build commands; decide after fresh E1 expected-result review.
2. PR191, normal priority: guard the actual output policy path /etc/apparmor.d/lean-action-bwrap before writing, optionally both conventional policy names. Existing source checks /etc/apparmor.d/bwrap then executes sudo tee /etc/apparmor.d/lean-action-bwrap. This contradicts the intended refusal to overwrite existing policy at the destination. Confirm with safely mocked filesystem/privileged operations under a new E1 protocol; do not mutate host security settings. No exploitability claim follows.
3. PR192, deferred capability-dependent: real axiom-policy parity table using exact supported toolchain and pinned fallback. Stop rather than install/build the missing stack. Existing macOS toolchains range through4.33.1; `toolchain-inventory.txt` records them. No real case in this table was run.

Two commits before ordinary closure are bookkeeping history, not scientific assurance. The original runner TypeError and workspace /bin/ps restriction remain preserved; the successful actual-host retry did not change source, question or mock sample. Token/cost totals are unknown; no monetary estimate. Thirteen completed controls took approximately9 seconds in the host call; exact child timings are in receipts.
