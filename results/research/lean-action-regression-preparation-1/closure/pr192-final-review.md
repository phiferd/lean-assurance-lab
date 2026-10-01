# INTERNAL HISTORICAL DRAFT — NOT FOR POSTING

AI-authored text below is retained only as historical local work. It is not submission material or a proposed community comment. This notice supersedes earlier references to user approval for posting these drafts. Technical evidence and patches are local material for human understanding and independent manual review.

Public community guidelines prohibit LLM-written GitHub/Zulip comments: https://leanprover-community.github.io/community_guidelines.html . The target CONTRIBUTING guide links to Lean4 PR submission rules, requiring AI assistance disclosure and manual checking and stating solely AI-authored PRs are unwelcome: https://github.com/leanprover/lean-action/blob/main/CONTRIBUTING.md ; https://github.com/leanprover/lean4/blob/master/CONTRIBUTING.md . No automatic patch sharing, comment, appeal, reposting, publication or external action is authorized.

---

Could the no-source-build test observe tool invocations instead of post-run directories? At head `209c085c3370c2fbae9e8bdfc87955f0c49a1082`, [the test checks directory absence](https://github.com/leanprover/lean-action/blob/209c085c3370c2fbae9e8bdfc87955f0c49a1082/.github/functional_tests/nanoda_bundled/action.yml#L47-L56), but [the EXIT trap removes both directories](https://github.com/leanprover/lean-action/blob/209c085c3370c2fbae9e8bdfc87955f0c49a1082/scripts/run_nanoda.sh#L14-L28). A successful source fallback therefore satisfies this assertion.

I prepared a test-only patch that retains the clean full-action test, then instruments a direct `run_nanoda.sh` invocation after setup. It records calls to the resolved bundled exporter/checker outside the cleanup paths and refuses source clone/build commands. Fresh synthetic controls accept bundled dispatch and reject both successful fallback after cleanup and a missing bundled-checker invocation. The direct placement avoids the composite action's elan/PATH update bypassing the wrappers.

These are shell-route controls with stand-in tools. They do not establish that the preceding full action avoided fallback, execute the YAML workflow, or test actual bundled/source checker acceptance or axiom-policy parity. I have not run the proposed workflow with Lean4.35.0-rc2. The patch is available if useful for this PR.
