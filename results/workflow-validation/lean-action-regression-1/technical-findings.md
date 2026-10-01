# Internal Lean-action technical findings

Local bounded closure COMPLETE at attempts/0006/result.json, validating scientific source commit a1b7a41c750f2711b733790d7b7d0a0ec9b8931a. The fresh E1 controls remain26/26 expected outcomes with52 raw SHA/byte bindings, complete cleanup and no supervision faults. Strict --require-full-payload validation passes1674 current,73 frozen historical and9 portfolio tests, zero skipped. Independent prospective/postrun/E2 and successor-integration reviews accepted the bounded claims. Ordered refresh and all five final checks pass; the downstream retry reused successful stages00–04 without repeating science or the strict suite. The old E1 report/validation are preserved intermediate artifacts; this closure companion resolves their ACTIVE/gate-pending descriptions. The canonical item is COMPLETE; ETA alias preparation is READY and unstarted.

This document is internal technical evidence, not a community comment or submission draft. Older AI-authored drafts remain historical only, visibly NOT FOR POSTING. Current ledger/status supersede earlier comment-approval language. No upstream post, PR, publication or privileged security operation occurred.

## PR192: cleanup makes the existing no-build assertion ineffective

Pinned head209c085c3370c2fbae9e8bdfc87955f0c49a1082; base96e06131c0e9943c780388fd166f55d1e2fa0433. The existing functional test .github/functional_tests/nanoda_bundled/action.yml lines47–56 checks absence of _lean4export/_nanoda_lib after the action. scripts/run_nanoda.sh lines14–28 removes both in an EXIT trap. The successful synthetic fallback control exits0, reports nanoda-status=SUCCESS, records two source clones plus Cargo build, and leaves both directories absent. Thus directory absence cannot establish that no source build happened.

Local test-only pr192.patch retains the clean full-action acceptance test, replaces the directory assertion with a separate direct script invocation, observes resolved bundled exporter/checker calls outside cleanup paths, and refuses source clone/build operations. Sixteen fresh supervised install/action/oracle controls include bundled acceptance, neither-tool fail-fast, permitted successful fallback rejected by oracle after cleanup, missing-exporter fallback rejected, missing-checker fail-fast, and missing-checker marker rejection. Existing coverage inspection includes27 functional-test/workflow paths; it contains the directory assertion, not invocation observation. Patch applies exactly and helper retains executable100755.

Limits: stand-in tools only. The direct script controls do not prove the preceding composite action avoided fallback, execute the proposed YAML workflow, or establish real checker axiom-policy parity. The direct placement avoids elan setup/PATH updates bypassing earlier wrappers; actual GitHub Actions/Lean4.35.0-rc2 workflow execution remains unperformed.

## PR191: existing-policy guard checks a different filename

Pinned head686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345; basea4136f495d9015a29f345a3bab72e133af011079. scripts/run_lake_check.sh lines153–156 checks /etc/apparmor.d/bwrap, while lines158–171 writes/loads /etc/apparmor.d/lean-action-bwrap. Under a failed sandbox probe and assumed trusted-executable precondition, a destination-only existing file does not trigger the guard.

Local pr191.patch checks both conventional and destination filenames and names the existing file in refusal diagnostics. Ten fresh projected controls compare original/fixed branches for absent, conventional-only, destination-only, both-present and healthy-probe/destination-present states. Original destination-only exits0 and the model writer/loader replace destination bytes; fixed exits2 before either operation and preserves bytes. Absent setup and successful-probe no-op remain unchanged. Existing28-path functional-test/workflow inventory exercises AppArmor CI success, not destination-only refusal. Patch applies exactly.

Limits: /etc paths remapped into fixture directories, privileged commands intercepted, trusted executable assumed. No actual host overwrite, exploitability, general idempotency, AppArmor/sysctl/setuid or kernel-soundness conclusion follows.

## Policy and remaining capability boundary

Source config equality checks show both Nanoda paths permit the three standard axioms plus Lean.trustCompiler and optional sorryAx, with unpermitted_axiom_hard_error:false. A zero exit therefore is not by itself an unexpected custom-axiom acceptance result. Actual clean/standard/sorry/custom/native-decide checker conformance remains INCONCLUSIVE: required Lean4.35.0-rc2 is absent. No large build/toolchain acquisition was attempted. PR190 already covers clean-versus-sorry paranoid and unsupported-toolchain behavior; no additional patch candidate was justified from the bounded dispatch checks.

Public community guidelines prohibit LLM-written GitHub/Zulip comments: https://leanprover-community.github.io/community_guidelines.html . The target https://github.com/leanprover/lean-action/blob/main/CONTRIBUTING.md links to https://github.com/leanprover/lean4/blob/master/CONTRIBUTING.md PR Submission, requiring AI assistance disclosure and manual checking and stating solely AI-authored PRs are unwelcome. Patches are AI-authored local proposals for human understanding and substantive manual review; agent review is not human review. No automatic sharing recommendation, ready-to-post prose or external authorization follows, and origin must not be disguised.

Final read-only preflight: all PR190/191/192 OPEN, unmerged at pinned heads, no discussion/reviews/inline threads. Relevant source/test inventory unchanged at those immutable heads; this does not claim exhaustive absence of unrelated closed-issue coverage. Metadata and timestamp retained in final-upstream-preflight.json.

## Evidence and reproducibility

- Scientific plan/manifest/patches/harness/raw26 controls: results/research/lean-action-regression-preparation-1/; raw attempts/0001, source freeze872221b.
- Safe custody replay: scripts/check-portable-evidence-replay; successor test tests/test_evidence_replay_portability_lean_action.py, no original-host command execution.
- Strict suite: stages/03-full-suite/0003/command.log and receipt; terminal closure: attempts/0006/result.json.
- Fresh experiment replay would require a new prospective lab attempt and unchanged supervisor; do not rerun recorded absolute commands as instructions or execute PR191 privileged operations.

Avoidable mechanics costs are retained explicitly: unregistered receipt family caused first strict current-suite failure; editing a shared test that was a frozen older execution input caused the second. Early scripts/check-portable-evidence-replay plus the targeted frozen resource input test and changed-path binding audit would have caught these before long runs. Two scope-dependency preflights failed before stages. A later refresh failure was one missing ignored53KB historical baseline; restored from original exact attested SHA, no measurement rerun. Final downstream retry reused the successful strict suite. These integration repairs do not strengthen the scientific findings or weaken gates.
