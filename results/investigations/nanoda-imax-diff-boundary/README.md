# Nanoda IMax Diff Boundary Equivalence

Mutant: `nanoda-gen-ca8565ff512e`

The mutation changes `diff >= 0` to `diff > 0` in the equal-`IMax` fast path
at `src/level.rs:188`.

Reusing the prior equal-`imax` definitional-equality control did not distinguish
the builds: both baseline and mutant Nanoda accepted it. The source-derived
candidate instead declares an inductive whose constructor field sort and
inductive codomain are both `succ (imax u v)`. `check_ctor` directly tests that
the field universe is less than or equal to the codomain universe. Both builds
also accepted this 46-record artifact.

## Source Analysis

The changed fast path is an optimization, not the only implementation of equal
`IMax` comparison. After `leq` simplifies both levels, an outer `IMax` has a
canonical second operand handled by one of the following later arms:

- a universe parameter invokes `leq_imax_by_cases`, substituting zero and a
  successor for that parameter and requiring the comparison in both cases;
- a `Max` or nested `IMax` is decomposed by the two general `is_any_max` arms.

For identical left and right levels at `diff = 0`, those fallbacks establish the
same true result as the original fast path. The mutation changes only the route
used to reach that result.

Nanoda already has a focused `leq_test_imax_imax` unit test whose first assertion
is `leq(imax(a, b), imax(a, b))`. Running that test against the mutant passed.
This directly exercises the equality boundary after the fast path's guard has
been made false.

## Evidence

- `reproduction.json`: prior equal-`IMax` control, accepted by both builds.
- `equal-imax-reproduction.json`: source-derived inductive candidate, accepted
  by both builds.
- `equivalence-analysis.json`: hash-bound classification and focused-test
  result.

The checker source was restored to `diff >= 0`, rebuilt in release mode, and
verified clean after the focused test.

## Status

The mutant is `EQUIVALENT`. No regression candidate should be added because
removing the fast path does not change Nanoda's final answer.
