# Lean eta pilot feasibility — source-only, 2026-09-30

No scientific builds, checker runs, or process launches were performed. No upstream checkout, PR, comment, or canonical lab state was changed. Results below are source analysis and proposed future checks, not confirmed defects.

## Recommendation

Prioritize a four-case **PR15373 alias-preservation pilot**, using the existing E0 lane only if it can consume the exact pinned revision without a new large build. Keep PR15374 as a secondary bounded arity-guard screen. Do not repeat the examples already supplied with the PRs.

Both GitHub PR heads were reverified against the requested pins:

| PR | Current head | Status | Existing request |
| --- | --- | --- | --- |
| [15373](https://github.com/leanprover/lean4/pull/15373) | `015d54649bcaaa0861f355b59761ce308e629fbb` | open draft | author body says “TODO better tests” |
| [15374](https://github.com/leanprover/lean4/pull/15374) | `87b06f446167701524ae9fbe4ae84004d6007e8e` | open draft | author body says “TODO better tests”; code asks `!=` versus `>` |

The author is proposing tests; this is not evidence of a separate maintainer review directive. The fetched inline-review thread lists were empty for both PRs.

## PR15373: alias seam survives the inspected source path

[Kernel source at the pin](https://github.com/leanprover/lean4/blob/015d54649bcaaa0861f355b59761ce308e629fbb/src/kernel/type_checker.cpp#L852) obtains `t_type = infer_type(t)` and `s_type = infer_type(s)`, checks their definitional equality, and enters the partial-constructor branch. That branch starts with `while (is_pi(t_type))`; it only calls `whnf` **after** opening a binder. There is no initial `whnf(t_type)`.

[Elaborator source at the pin](https://github.com/leanprover/lean4/blob/015d54649bcaaa0861f355b59761ce308e629fbb/src/Lean/Meta/ExprDefEq.lean#L178) instead uses `forallTelescopeReducing` on the constructor's inferred type, then applies both terms to all opened variables before comparing projections.

For a local free variable, the kernel's `infer_fvar` returns its stored declaration type unchanged (lines 93–98). Term normalization before `try_eta_struct` normalizes the terms, not the stored type of a free variable. Thus a deliberately preserved alias at the first function-type binder is a source-supported reachable candidate. Definitional equality of the types does not rewrite the saved `t_type` variable.

Small candidate:

```lean
structure Box where
  val : Bool
def FnAlias := Bool → Box
-- Compare f with the unapplied Box.mk, using a local f : FnAlias.
```

`Box` is nonrecursive, has zero parameters and one field, and its constructor is a function. A local `f` has no value to unfold. The alias and `Bool → Box` are definitionally equal. If the initial alias is retained in the kernel local context, the syntactic Pi loop opens zero variables. With an unapplied `Box.mk`, the subsequent constructor-field loop also has zero arguments and reaches `return true` without any projection comparison. This is a suspected unchecked branch in the pinned patch, not a measured acceptance result. The elaborator's reducing telescope opens the Boolean argument and has a real projection comparison to make.

Use a negative semantic witness, not a proof-only or unit-like field: arbitrary `f` is not definitionally equal to `Box.mk`, and specializing `f` to `fun _ => Box.mk false` distinguishes the two at `true`. No theorem stating arbitrary-function equality should be elaborated and trusted as fixture construction.

Smallest future pilot: four semantic cases, each record elaborator and kernel outcomes separately (eight observations, not eight different fixtures).

| Case | Stored local type / compared terms | Intended result |
| --- | --- | --- |
| C1 | explicit `Bool → Box`; arbitrary `f` versus `Box.mk` | reject |
| C2 | preserved `FnAlias`; arbitrary `f` versus `Box.mk` | reject |
| C3 | explicit `Bool → Box`; `fun b => Box.mk b` versus `Box.mk` | accept, eta control |
| C4 | preserved `FnAlias` in fixture context; same eta control | accept |

For C2, supply the closed, binder-containing expression through the existing raw/declaration route so the elaborator cannot pre-normalize the alias or refuse construction before the kernel sees it. Inspect the resulting fixture first: binder domain must remain `.const FnAlias`, term must remain a free/bound variable with no value, and constructor must have zero term arguments. A declaration-level encoding can ask the kernel to check a manually constructed reflexivity proof against the corresponding equality under the binder; it must remain an expected-reject fixture, never accepted as trusted input solely on elaborator success.

**Go:** the fixture preserves that alias shape and source routing; exact pinned checker already exists or is cheaply available within approved scope; bounded duplicate checks do not locate this same negative case. **Stop:** fixture generation canonicalizes the binder type to Pi, uses a lambda or a valued let for the negative term, changes the constructor arity, or requires a new large build. Do not compensate with more aliases or a larger campaign. **After four cases:** equal outcomes close the seam as no signal; a disagreement or unexpected kernel acceptance requires a minimal saved receipt and independent fixture/type validation before any defect claim or communication. A small-build constraint blocker remains a blocker, not permission to run a large build.

## PR15374: smaller incremental value, arity boundary only

Both [Meta `shouldEtaRecursors`](https://github.com/leanprover/lean4/blob/87b06f446167701524ae9fbe4ae84004d6007e8e/src/Lean/Meta/ExprDefEq.lean) and [kernel `should_eta_recursors`](https://github.com/leanprover/lean4/blob/87b06f446167701524ae9fbe4ae84004d6007e8e/src/kernel/type_checker.cpp) use the same guard: reject when application argument count is greater than major index; permit `n ≤ m` for K-like or nonrecursive structure recursors. The comparator must have a different head. Eta expansion first checks the remaining inferred function type after weak-head reduction. Thus `n = m − 1` is a genuine branch enabled by `>` and disabled by `!=`; `n = m` is the intended missing-major case; `n > m` disables this new heuristic. No elaborator/kernel difference is apparent in this guard itself.

The pinned [12520_2 test](https://github.com/leanprover/lean4/blob/87b06f446167701524ae9fbe4ae84004d6007e8e/tests/elab/12520_2.lean) already contains Eq, PUnit, and Prod direct-vs-eta examples. Its `--fails` comments are inherited from old reports, not evidence of current test outcomes. Source-only inspection cannot establish which examples execute successfully.

Secondary pilot, only after the alias screen is closed: a four-case arity matrix on one data-bearing nonrecursive structure recursor, with `m` read from actual recursor metadata. Use (1) `n=m` known eta-positive control, (2) `n=m` arbitrary-function negative control, (3) `n=m−1` arbitrary-function negative control with the extra remaining binder, and (4) `n>m` fully applied negative control. Preserve distinct nonlambda heads for negative comparisons so the ordinary lambda eta path does not mask the changed heuristic. Record Meta and kernel independently. The extra-binder case checks the exact author question without inventing a positive equation that trivially unfolds before the guard.

**Go:** metadata confirms counts, terms remain well typed with distinct nonlambda heads, and existing pinned tests do not cover the missing-minor case. **Stop:** reduction resolves the comparison before this guard, a wrapper unfolds to a lambda, existing tests cover that same boundary, or no exact pinned runner is available without large builds. A uniformly correct matrix is useful regression coverage, not a novel scientific defect or a justification for expanding the campaign.

## Duplicate / novelty boundary

[Issue12520](https://github.com/leanprover/lean4/issues/12520) reports function-eta defeq transitivity failure. Its comments already give the partial-constructor `T.mk` example and the PUnit/Prod examples. The two PR test files reproduce those reported families. They are direct duplicate baselines.

[Renovation14977](https://github.com/leanprover/lean4/issues/14977) explicitly lists both PRs as planned eta fixes. The scientific contribution would be a narrow, source-reachable boundary test distinguishing elaborator from kernel or detecting a regression in the proposed fix. Broad eta novelty is excluded.

Bounded coverage check: fetched pinned `tests/elab/12520_1.lean`, `12520_2.lean`, `etaStruct.lean`, `etaStructIssue.lean`, and `issue2628.lean`. The first two are the PR's own baseline tests; `etaStruct.lean` covers fully applied structure eta and unit-like cases; `etaStructIssue.lean` covers recursive/proof eta agreement; `issue2628.lean` contains function-type aliases in mutual-recursion compilation, not this partial-constructor raw kernel conversion seam. GitHub searches for tests mentioning eta, FunType, partial constructor, and 12520, and issues combining eta/alias or partial constructor, found no exact alias-preserved negative case. Search results use the default indexed branch rather than the pinned branch, so this is **not** an exhaustive absence claim across every test or unindexed draft. Inspect any newly located matching fixture before promoting the pilot.

Only this assessment file was created. No execution evidence is claimed; no canonical queue selection or status changed.
