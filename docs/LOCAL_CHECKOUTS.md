# Identify the checkout before a handoff

A task clone and a contributor's usual checkout can have different local
branches and commits. Record the absolute checkout path and commit when
handing off a result; a branch name alone does not locate the work.

Run these read-only commands in the checkout being reported:

```sh
git rev-parse --show-toplevel
git rev-parse --path-format=absolute --git-common-dir
git branch --show-current
git rev-parse HEAD
git status --short
git worktree list
git remote get-url origin
```

Independent clones have separate Git common directories. Linked worktrees
share a common directory, and `git worktree list` identifies them. A missing
local branch in one clone does not establish that the branch is absent from
another clone. Check a bundle's contents with `git bundle list-heads` before
treating it as a fallback: a proof-source bundle may belong to a different
repository from the lab integration.

Git conflicts and tool authorization failures occur at different stages.
A tool may deny a command before Git runs; inspect the rejection to establish
whether execution began. A Git conflict is reported by Git after execution.
Neither outcome grants permission to change credentials or protection rules.

For lab delivery, follow [the repository workflow](AGENT_WORKFLOW.md#repository-delivery)
and its `scripts/push-main` checks after the required review and authorization.
