# Consider the reducible-hidden-positivity companion pair

Submitted as [Arena PR #181](https://github.com/leanprover/lean-kernel-arena/pull/181) after explicit owner approval.

The pair now materializes successfully against Arena `abc55357aee17c59dfdbf39c8a2e19739e23dd10`: the control has outcome `accept`; the candidate is a proposed `reject`. The two `build-test` package invocations completed within their fixed bounds, with zero checker launches, downloads, or external writes.

The control field is `Unit -> I`. The candidate changes the shared domain to `LALConstType Unit I`, where `LALConstType A B := A`, through the constructor and complete recursor metadata. Bound prior evidence records candidate rejection with accepted controls and a controlled Nanoda positivity mutation that accepts the candidate. Those observations support a focused corpus proposal; they do not establish universal Lean semantics or an implementation defect.

The current Arena tutorial source was retrieved at the exact pinned revision and retained with its response binding. A latest-upstream preflight at `8ae1d84e335d2381b2bfcc0dbde7fc3da8e96062` found only a Sokobanoda revision bump since the integration baseline and no exact duplicate. This is integration and duplicate-review evidence, not authority for the `reject` contract.
