# INTERNAL HISTORICAL DRAFT — NOT FOR POSTING

AI-authored text below is retained only as historical local work. It is not submission material or a proposed community comment. This notice supersedes earlier references to user approval for posting these drafts. Technical evidence and patches are local material for human understanding and independent manual review.

Public community guidelines prohibit LLM-written GitHub/Zulip comments: https://leanprover-community.github.io/community_guidelines.html . The target CONTRIBUTING guide links to Lean4 PR submission rules, requiring AI assistance disclosure and manual checking and stating solely AI-authored PRs are unwelcome: https://github.com/leanprover/lean-action/blob/main/CONTRIBUTING.md ; https://github.com/leanprover/lean4/blob/master/CONTRIBUTING.md . No automatic patch sharing, comment, appeal, reposting, publication or external action is authorized.

---

Could the existing-policy guard also check the file it writes? At head `686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345`, [lines153–156 check `/etc/apparmor.d/bwrap`](https://github.com/leanprover/lean-action/blob/686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345/scripts/run_lake_check.sh#L153-L156), while [lines158–171 write/load `/etc/apparmor.d/lean-action-bwrap`](https://github.com/leanprover/lean-action/blob/686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345/scripts/run_lake_check.sh#L158-L171). If the initial sandbox probe fails and only the destination file exists, the current guard permits the write.

I prepared a small patch checking both filenames and naming the existing file in the refusal diagnostic. Fresh fixture tests compare the original and patched AppArmor branch: the patch exits2 before writer/loader calls and preserves destination bytes; absent-file setup and the successful-probe no-op remain unchanged.

This is projected shell behavior under an assumed trusted-executable precondition. Policy paths were remapped into fixtures and privileged commands were intercepted; no `/etc` write, sudo, AppArmor load, sysctl or setuid operation ran. It is not a demonstrated host overwrite, exploitability or general idempotency claim. The patch is available if useful for this PR.
