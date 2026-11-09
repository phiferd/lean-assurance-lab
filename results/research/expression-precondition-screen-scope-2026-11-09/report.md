# Prospective screen: typing before semantic comparison

**What did we find?** The retained Lean and Nanoda sources both expose an
unchecked type-inference path used by semantic operations, while their ordinary
declaration paths appear to check expressions before comparing inferred and
declared types. The Lab has not tested the fresh cases below. Source order alone
does not establish that malformed imported expressions can be admitted.

**Is it interesting?** Yes. An ill-typed application whose function ignores its
argument can reduce to a familiar well-typed expression. That gives a small,
falsifiable way to ask whether reduction or definitional equality (the checker's
semantic comparison of expressions) can mask a missing typing precondition at a
checked declaration boundary.

**Does it require more work?** Prepare one E0 screening campaign, bind current
supported checker and exporter identities, generate and inspect the paired raw
imports, then run the fixed matrix. This document scopes that work; it does not
select it in the canonical queue, authorize a launch, report a checker outcome,
or change any declaration-validation catalog decision. The current READY item
remains `LEAN-ETA-MERGED-REPLAY-1`.

## Evidence and distinct question

- In the retained official Lean source,
  [`infer_app`](../../../explorations/runs/EXPLORE-SYMBOLIC-UNIVERSE-1/sources/type_checker.cpp)
  checks the function and argument before comparing the argument's inferred type
  with the function domain in checked mode. Its `infer_only` branch skips the
  argument check. `check` enters checked mode; `is_def_eq` can use inference and
  reduction internally. This is a source-derived reachability question, not a
  demonstrated bypass.
- In the retained Nanoda source,
  [`check_declar` and `infer_app`](../../../explorations/runs/EXPLORE-SYMBOLIC-UNIVERSE-REJECTION-1/sources/tc.rs)
  check the declaration type, infer the value with `Check`, and then compare the
  types. `infer_app` checks an argument only in `Check` mode; `InferOnly` can
  instantiate the function body without that check. The exact pin and current
  source must be verified before using this as a live path claim.
- The frozen [M9 review](../../../docs/research/DECLARATION_VALIDATION_MILESTONE_9_ADVERSARIAL_REVIEW.md)
  keeps expression well-formedness, application argument matching, binder-domain
  sorthood, and value/type matching as distinct provisional premises. It does
  not make implementation agreement semantic authority. The
  [Nanoda cache regression](../nanoda-cache-regression-1/report.md) tested an
  internal malformed-let cache contract, not fresh public imported application
  terms. The [test-effectiveness screen](../../../explorations/runs/EXPLORE-TEST-EFFECTIVENESS-1/summary.md)
  seeded guard omissions; its results are not production defects.

Read-only source refresh on 2026-11-09 found the same relevant order at Lean
`d5cd01659b2442bf6cde4dca16a642710a1f39b8`
([`infer_app` and `check`](https://github.com/leanprover/lean4/blob/d5cd01659b2442bf6cde4dca16a642710a1f39b8/src/kernel/type_checker.cpp))
and Nanoda `0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`
([`check_declar`, `infer_app`, and `infer_pi`](https://github.com/ammkrn/nanoda_lib/blob/0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929/src/tc.rs)).
These are source observations, not executable/runtime bindings or an exhaustive
audit of every caller. A launch still needs exact supported source, exporter,
binary and configuration identities.

This screen tests ordinary imported definition checking. It does not replay the
Lean partial-constructor eta witness or either Nanoda recursor report, mutate a
checker, use a recursor, or evaluate a previous published witness. Its possible
new signal is an unexpected *checked declaration acceptance* on an input whose
typing error is independently justified. A direct `is_def_eq` API result on an
ill-typed operand is not such a signal.

## Fixed candidate construction

Use only core `Nat` and two closed function expressions, shown here as readable
Lean notation for raw expression trees:

```lean
typeFn  := fun _ : Nat => Nat
valueFn := fun _ : Nat => Nat.zero
goodArg := Nat.zero
badArg  := Nat          -- has type Type, while both functions require Nat
```

The `badArg` application is invalid even when beta reduction discards that
argument. It is the sole intended fault in each negative. For each row, build a
fresh raw export or checked-addition input from a supported valid producer case,
then replace exactly one argument node. Preserve identical surrounding
declarations, universe arguments, order and checker configuration between each
negative and its control.

| Pair | Valid control | Negative candidate | Intended boundary |
| --- | --- | --- | --- |
| V — value | `v : Nat := valueFn goodArg` | `v : Nat := valueFn badArg` | Validate the value application before its inferred type is compared with `Nat`. |
| T — declared type | `t : typeFn goodArg := Nat.zero` | `t : typeFn badArg := Nat.zero` | Validate the reducible declared-type application before comparing it with the value type. |
| B — binder domain | `b : (x : typeFn goodArg) → Nat := fun x : Nat => Nat.zero` | `b : (x : typeFn badArg) → Nat := fun x : Nat => Nat.zero` | Validate the binder-domain application before reduction makes the function types appear equal. |

### Paper review of the exact six expression trees

Here `N = Const(Nat, [])`, `Z = Const(Nat.zero, [])`,
`Lₜ = Lambda(_: N, N)`, and `Lᵥ = Lambda(_: N, Z)`. The binders in both
lambdas are unused. All six candidates are closed and use no universe
parameters, metavariables, recursors, axioms, or new constants.

| Input | Declared type tree | Value tree |
| --- | --- | --- |
| V control | `N` | `App(Lᵥ, Z)` |
| V negative | `N` | `App(Lᵥ, N)` |
| T control | `App(Lₜ, Z)` | `Z` |
| T negative | `App(Lₜ, N)` | `Z` |
| B control | `Pi(x: App(Lₜ, Z), N)` | `Lambda(x: N, Z)` |
| B negative | `Pi(x: App(Lₜ, N), N)` | `Lambda(x: N, Z)` |

`Z` has type `N`, whereas `N` has a universe sort as its type. Thus each
negative fails the one application-domain comparison `type(argument) =?= N`;
the matching control passes it. Reduction erases the argument:
`App(Lₜ, _)` reduces to `N`, and `App(Lᵥ, _)` to `Z`. This explains why a
comparison of reduced expressions alone would be insufficient. It does not
prove that any checker omits the required application check.

For V, checked value inference should reject before the final declaration
value/type comparison. For T, checked declared-type inference should reject
before its sort check and before value/type comparison. For B, checked Pi-domain
inference should reject before it extends the binder context. The retained Lean
and Nanoda call orders support these expected paths, but actual stage attribution
requires fresh raw observations. The AST review is **not** a raw-export or
checker result.

A bounded local text search found no earlier use of either exact closed lambda
recipe in retained `.lean` or `.md` sources. Arena's
[`perf/discarded-argument`](https://github.com/leanprover/lean-kernel-arena/blob/master/tests/perf/discarded-argument.lean)
and [`perf/discarded-argument-match`](https://github.com/leanprover/lean-kernel-arena/blob/master/tests/perf/discarded-argument-match.lean)
cases are adjacent conversion-performance work with well-typed arguments and
`debug.skipKernelTC`; they do not test this checked invalid-import boundary.
This is a bounded duplicate review, not a complete upstream search. A fresh
source and test duplicate check at the selected revisions remains a launch gate.

The notation is a construction recipe, not a claim that these exact strings are
accepted by an exporter. Freeze the actual parsed expression trees and raw bytes
before any target checker call. If a producer normalizes away the application,
construct the raw expression with the existing export encoder and verify the
target parsed shape; otherwise classify that pair ineligible before execution.
Do not replace an ineligible pair with a new one inside the same campaign.

Use official Lean's trust-zero checked admission and Nanoda's checked ordinary
definition import as the two independently implemented observers. Six inputs
times two checkers make twelve planned cells. Each valid control must be
accepted and retain the intended application shape. Each negative should be
rejected for its typing fault. A parser rejection, unsupported expression,
wrong parsed shape, unrelated panic, timeout, or missing declaration receipt is
not a semantic verdict. Record the first attributable failing stage; do not
infer reachability of a later comparison merely because the final verdict is
rejection.

## Prospective gates and result rule

Evidence class: E0. This is a screening design, not confirmation.

1. Before queue selection, refresh source/reuse against the exact supported
   Lean and Nanoda revisions. Search the existing Lab cases and upstream tests
   for the same ignored-argument application and placement; record duplicates
   and drop a duplicate pair prospectively rather than presenting it as novel.
   Recheck the declaration entrypoint, inference flags, reduction and equality
   call sites at those revisions. Use the existing encoder and supervised runner;
   no new harness is justified by this scope.
2. Select this as a bounded campaign only through `docs/RESEARCH_STATUS.md`,
   `config/research-queue.json`, an explicit E0 plan and strategic review in
   their required generation/validation path. Record each trial's question,
   source identities, input identities, sample, expected controls and signal
   criteria in `explorations/ledger.jsonl` **before** checker execution. Retain
   every construction/debugging attempt and the frozen raw inputs.
3. Run each cell in a fresh supervised process with exact source, binary,
   exporter/encoder, input, command, exit, timeout and cleanup receipts. Check
   the actual declaration result and stage-specific diagnostic. No source edit,
   mutant, historical replay, extra case family, broader version sweep, or
   external action belongs to this screen.
4. Close `SIGNAL` only if a negative is accepted by a checked declaration path,
   its paired control passes, the parsed bad application survives, and an
   independent typing argument rules it out. Propose a separate E1 confirmation
   with fresh execution and independent input/expectation review before any
   defect or conformance claim. Close `NO_SIGNAL` only if all eligible fixed
   cells yield attributable expected observations; otherwise use `INCONCLUSIVE`
   and explain the missing evidence. Preserve disagreement and all failures.

One completed twelve-cell matrix, or a precise prelaunch representability or
capability boundary, answers this bounded screen. Actual setup/repair effort
is observed, not an authorization cap. The screen never supplies a soundness
rate, universal typing guarantee, independent holdout, or new normative catalog
authority. The separate historical recursor audit and merged-Lean replay keep
their own priorities and evidence.
