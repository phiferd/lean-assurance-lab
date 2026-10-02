# Reporting input brief: PR15373 declaration admission

This is an internal drafting input, not a disclosure report and not approved for posting.

The demonstrated primitive is narrow: the exact official PR15373 head artifact accepted one closed invalid theorem through checked trust-level-zero `Kernel.Environment.addDeclCore` when the binder domain was stored as the reducible constant `FnAlias`. The syntactically explicit `Bool → Box` negative control rejected in a separate fresh process.

The strongest currently supported title is:

> PR #15373 head accepts an invalid theorem when a reducible function alias reaches partial-constructor eta checking

Do not call released Lean affected, claim that the PR introduced the runtime behavior, assign severity, describe an exploit, or say `False` was derived. Source inspection shows that the relevant loop exists only at the PR head among the three inspected revisions, but runtime causation awaits the exact-parent control.

A future report should explain:

1. Expected behavior: both arbitrary-function theorem declarations must reject because an arbitrary `f : Bool → Box` is not definitionally equal to `Box.mk`.
2. Actual observation: PR head accepted only the declaration whose binder type remained `FnAlias`; the explicit control rejected.
3. Root-cause hypothesis: after type equality succeeds, the new C++ path opens arguments only while the saved `t_type` is syntactically a `Pi`. A reducible alias leaves zero opened binders and therefore zero constructor arguments to compare before the function returns true.
4. Scope: one unmerged draft-PR head, one alias/control pair, no release or current-master runtime test.
5. Requested maintainer action after confirmation: normalize the saved type before deciding whether it is a `Pi`, add the alias negative as a kernel regression, and retain the positive partial-constructor eta cases.

Required attachments after E1 are a portable fixture, head and parent commands, raw observed output limited to the four cells, exact runner identities and the independent Daybreak Blue review. Internal supervisor receipts, workspace paths, queue records and project planning documents are not distributable report material.
