# Exact PR15373 head admits an invalid alias-domain theorem

**What did we find?** The exact PR #15373 head accepted one invalid theorem
through Lean's checked, trust-zero declaration-admission path. The exact parent
revision rejected the same theorem, and both revisions rejected the matched
version whose function type was written explicitly instead of through a
reducible alias.

**Is it interesting?** Yes. This is a reproducible kernel declaration-admission
regression at the tested PR head, not merely a disagreement between external
checkers. The accepted declaration was closed, used no `sorry`, metavariables,
added axioms or unchecked insertion, and the stored theorem type and value were
the submitted invalid expressions.

**Does it require more work?** Yes. Maintainers should receive a private,
reviewable reproducer and proposed regression test. A candidate fix should be
validated separately. No upstream message or patch submission is authorized by
this result.

## Result

Both declarations claim that every `f` of a function type equals the structure
constructor `Box.mk`, while the supplied value proves only `f = f`. Both are
therefore expected to reject.

| Revision | Stored function domain | Observed |
| --- | --- | --- |
| PR head `015d5464` | reducible constant `FnAlias` | `ACCEPT` |
| PR head `015d5464` | explicit `Bool → Box` | `REJECT` (`declTypeMismatch`) |
| Parent `2c2bdd96` | reducible constant `FnAlias` | `REJECT` (`declTypeMismatch`) |
| Parent `2c2bdd96` | explicit `Bool → Box` | `REJECT` (`declTypeMismatch`) |

This is the preregistered
`CONFIRMED_PR_HEAD_ADMISSION_REGRESSION` outcome. All four fresh processes used
trust level zero and explicit checked `Lean.Environment.addDeclCore` with
`doCheck := true`. All completed with clean supervision and no accounting or
monitoring fault.

## Source explanation

The head adds a partial-constructor eta path in `try_eta_struct_core`. After
establishing that the two terms have definitionally equal types, it opens
arguments only while the saved `t_type` is syntactically a `Pi`. When that type
is the reducible constant `FnAlias`, the loop opens no binders. The subsequent
constructor-argument loop then has no field arguments to compare and the
function can return true. The explicit function type enters the loop and
rejects, as does the exact parent which lacks this new path.

That source explanation is a bounded root-cause hypothesis. A later fix
validation should normalize `t_type` before the `Pi` decision, preserve valid
partial-constructor eta cases, and prove that this alias negative rejects.

## Evidence and scope

The canonical result is [result.json](result.json). The immutable launch inputs
are [launch-manifest.json](launch-manifest.json), the exact source identities are
[source-manifest.json](source-manifest.json), and the independent final launch
review is [daybreak-final-review-edb92569.md](daybreak-final-review-edb92569.md).
Raw output and process receipts are retained under the four named attempt
directories.

The runtime claim is limited to exact head
`015d54649bcaaa0861f355b59761ce308e629fbb` and exact parent
`2c2bdd9630a7a6c51d7620d5efefcdba104f38f3`, built by the same recorded method.
No released version or current `master` was runtime-tested. We did not derive
`False`, develop an exploit, assess public reachability or severity, or contact
upstream.
