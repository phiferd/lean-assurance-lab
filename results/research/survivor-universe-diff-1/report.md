# Universe diff-zero reachability result

`SURVIVOR-UNIVERSE-DIFF-1` closes `SUCCESS`: pinned Nanoda can reach the
mutated right-`Zero` guard at `diff == 0` from an ordinary exported theorem.
No build, checker, proof, network request, scientific byte generation or
external action ran.

The existing non-Prop theorem uses `ExprSort(Level::Zero)` as its type. Nanoda
infers that expression as `ExprSort(Succ Zero)` and applies the theorem-only
proposition gate, which calls `is_zero(Succ Zero)`. After simplification,
`leq_core` starts at `(Succ Zero, Zero, 0)`.

The original guard `diff < 0` does not match there, so the successor arm recurs
to `(Zero, Zero, -1)` and the original right-`Zero` guard returns `false`. The
mutant guard `diff <= 0` returns `false` immediately. The branch selection is
different, but the local Boolean and source-predicted theorem outcome are the
same. The historical 163-test comparison's zero differences are consistent
with this trace; they are not semantic authority or an equivalence proof.

The predecessor question is therefore answered, but a global classification is
not. Residual simplified `Max` states, nested `IMax` case rewrites and the full
public-caller invariant remain to be closed. The canonical survivor registry is
unchanged, no external action is supported, and
`SURVIVOR-UNIVERSE-EQUIVALENCE-1` is selected READY and unstarted to prove the
remaining invariant or preserve its exact boundary.
