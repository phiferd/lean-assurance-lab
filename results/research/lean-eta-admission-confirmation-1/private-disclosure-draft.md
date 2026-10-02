# Checked declaration admission accepts an invalid theorem through a reducible function alias

Private maintainer disclosure draft. Do not send without explicit human approval.

## Summary

At exact Lean PR #15373 head `015d54649bcaaa0861f355b59761ce308e629fbb`, `Lean.Environment.addDeclCore` with `doCheck := true` accepted and stored an invalid theorem at trust level zero when the function domain was represented by a reducible alias. The same build rejected the syntactically explicit-domain control, and exact parent `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` rejected both forms with `declTypeMismatch`.

The supplied value proves `∀ f, f = f`; the declared type requires `∀ f, f = Box.mk`. Checked admission must reject both declarations.

## Exact evidence

| Revision | Domain representation | Result |
| --- | --- | --- |
| PR head `015d54649bcaaa0861f355b59761ce308e629fbb` | reducible `FnAlias` | accepted |
| PR head `015d54649bcaaa0861f355b59761ce308e629fbb` | explicit `Bool → Box` | rejected: `declTypeMismatch` |
| Parent `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` | reducible `FnAlias` | rejected: `declTypeMismatch` |
| Parent `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` | explicit `Bool → Box` | rejected: `declTypeMismatch` |

Each cell ran in a fresh process against a separately built exact revision. The fixture verified trust level zero, closed expressions without metavariables, checked insertion, and exact stored type/value after acceptance. It used no `sorry`, added axiom, unchecked insertion, or `skipKernelTC`.

The complete preserved observations and hashes are in `result.json` and `report.md`. A compact proposed regression is in `proposed-regression.lean`.

## Source-supported hypothesis

The head changes `type_checker::try_eta_struct_core` to support partial-constructor eta comparison. It infers `t_type`, verifies equal types, and then opens arguments with `while (is_pi(t_type))`. When `t_type` is syntactically the reducible constant `FnAlias`, the first `is_pi` test is false even though weak-head normalization exposes a function type. No arguments are opened, `Box.mk` remains unapplied, and a later field-comparison loop can perform zero comparisons before returning true. The explicit domain exposes the binder and reaches the mismatch.

This matches the source difference and alias/explicit control, but remains a hypothesis until a candidate fix is tested.

## Impact boundary

The demonstrated primitive is admission and storage of one closed invalid theorem through the raw checked declaration API at the tested PR head. This work did not test a released Lean version or current `master`; derive `False`; establish an ordinary source, package, artifact, or remote route; assess severity; or validate a fix.

## Suggested repair and validation

Before syntactically inspecting `t_type` for `Pi`, normalize it to weak-head normal form. Also consider requiring the applied constructor to reach the expected parameter-plus-field arity before field comparison. These are candidate directions, not validated fixes.

A fix should be tested against the alias negative, the explicit negative, existing valid partial-constructor eta cases, and reducible aliases exposing multiple binders. The proposed standalone regression has not itself been executed and should be adapted to the repository's preferred kernel-test location and message convention.

