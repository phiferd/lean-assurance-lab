# Independent post-result review

Verdict: **CONDITIONAL**. The retained evidence supports a valid, bounded disagreement between `Kernel.isDefEq` and `Meta.isDefEq` on the pinned artifact. It does not yet establish that PR15373 introduced a production checking regression or declaration-acceptance defect.

## Fixture validity and non-circularity

`prospective-cases-r2.lean` constructs correctly scoped raw expressions and supplies an unvalued local with `withLocalDeclD`. The negative terms contain no metavariables, loose bound variables, valued lets or constructor arguments. Assertions preserve:

- the exact stored alias expression `.const ``FnAlias []` for the alias case;
- an unvalued local declaration;
- a free-variable, non-lambda negative left side;
- an unapplied constant `Box.mk` with zero term arguments;
- distinct negative heads; and
- kernel observation before the Meta call.

The false negative oracle is semantic and implementation-independent: an arbitrary `f : Bool → Box` cannot be definitionally equal to `Box.mk`; for example, `fun _ => Box.mk false` differs at `true`. The positive alias case remains only a routing control because its compared lambda itself infers a syntactic Pi.

The compatibility repair is immaterial to those properties. It replaces unsupported rendering of `Kernel.Exception` with a literal error marker and renames reserved local identifiers. Expressions, assertions, comparison orientation, case order and expectations are unchanged.

## Kernel API contract and source path

The bundled `src/lean/Lean/Environment.lean` documents `Kernel.isDefEq` as the kernel definitional-equality predicate, mainly for debugging, and states that the kernel type checker does not support metavariables. It does not document a requirement that local declaration types be supplied in weak-head normal form, nor does it describe the predicate as permissive or approximate. The fixture satisfies the explicit no-metavariables restriction.

At pinned source revision `015d54649bcaaa0861f355b59761ce308e629fbb`, `infer_fvar` returns the local declaration's stored type unchanged. `try_eta_struct_core` first verifies inferred-type definitional equality, but its partial-constructor expansion loops only while the saved `t_type` is syntactically Pi. With stored `FnAlias`, it opens zero binders; with unapplied `Box.mk`, it then has zero constructor arguments to compare and returns true. This source path explains the exact observed alias-negative result.

The complete generated C++ foreign-function wrapper/header was not locally available, so that narrow caller-contract layer remains unaudited. Nothing in the bundled Lean API documentation supplies a pre-WHNF or permissiveness exception that would explain the result as documented behavior.

## Environment and configuration

Both observations use the same `Environment` and `LocalContext` from the same `MetaM` execution. The kernel call runs first, so Meta assignments or caches cannot influence it. The compared negative expressions contain no metavariables, making Meta assignment policy irrelevant to the raw terms. Kernel and Meta intentionally implement different conversion procedures, so disagreement alone is not a defect proof; the independent semantic oracle is what makes kernel `true` suspicious.

## Artifact and result binding

The official archive is retained at 759,812,626 bytes with SHA-256 `73cbeca7d35f92bf4e67c36ca4f15fe37d8b3bc8e3ec58b560c13f905185e17d`. The extracted `libleanshared.so` contains githash `015d54649bcaaa0861f355b59761ce308e629fbb` and hashes to `060d3748f8792f02b0943695d1e83d5253ac343f3371bd3c56617b5308d1a289`. The bundled `ExprDefEq.lean` hashes identically to the pinned checkout copy: `93e22fdd01f808a9ea82e8c4060466f03a2243f682fb7344b92f2726d95c0709`.

The repaired fixture hashes to `f3a586214ab3bc003d93315d32a27d0296418e4f1cc23b6ad89f98b592ca53b6`. The scientific stdout hashes to `c603b1bf957b1d983db5700345704f2b966dcfde77abbdb5aef3c147126d0252`; its receipt exited zero with empty stderr, no monitor errors and complete supervisor cleanup.

The completed run did not print revision, in-container fixture hash or in-container shared-library hash, and it did not call `Kernel.check` on each operand. Host-side bindings are strong but do not replace those direct confirmation observations.

## Attribution boundary

The exact parent revision is `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3`. No ready local binary for that revision was found. The sparse source checkout lacks required parent blobs; a read-only Git inspection unexpectedly attempted a promisor fetch, failed DNS and obtained nothing. Stable installed releases would not establish this PR's before/after effect.

Therefore the supported statement is:

> The exact pinned PR artifact exhibits a bounded `Kernel.isDefEq=true` / `Meta.isDefEq=false` result for the preserved-alias arbitrary-function fixture, while the explicit negative and both constructor controls match the frozen oracle.

Unsupported statements include “PR15373 introduced this behavior,” “the production kernel accepts an invalid declaration,” “this is exploitable,” or “current Lean main is affected.”

No runtime, Docker action, build, download, edit outside this retained review, publication, push or upstream communication occurred during the independent review.
