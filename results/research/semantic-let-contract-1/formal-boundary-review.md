# Retained Lean4Lean let boundary review

Item: `SEMANTIC-LET-CONTRACT-1`. Source revision:
`ecb3b6661c14f8147be1069b126c629114baf4a8`.
The local retained checkout at
`external/lean-kernel-arena/_build/checkers/lean4lean/src` reports that exact
HEAD. All line references below were read with `git show REV:PATH`, not inferred
from mutable checkout bytes. This is a source review, with no build, proof,
checker or network launch and no new authority decision.

## Direct definitions and statement boundaries

1. **Translation already carries the let compatibility condition.**
   `Lean4Lean/Verify/Typing/Expr.lean:74-106` defines `TrExprS` and `TrExpr`.
   In the `TrExprS.letE` constructor (96-100), the first premise is
   `env.HasType Us.length Δ.toCtx val' ty'`. The remaining premises translate
   the annotation, value and body; the body translation uses the extended
   `(none, .vlet ty' val') :: Δ` context. The result translates the raw let to
   `body'`, with no let constructor or annotation retained in that result.
   This is a relation with semantic premises, not a total syntactic erasure
   function applicable to every raw expression. `TrExpr` (105-106) additionally
   permits a translated result related by `env.IsDefEqU`.

2. **Structural predicates do not supply that typing premise.**
   In the same file, `Closed` (9-17) constrains de Bruijn indices and excludes
   expression metavariables; its let clause requires closed annotation/value
   and a body closed beneath one binder. `FVarsIn` (31-43) restricts free
   variables and excludes expression/level metavariables, traversing all
   three let components. Neither predicate asserts the value has the declared
   annotation type. `VLocalDecl.WF` (47-49) separately requires
   `env.HasType U Γ value type` for a `.vlet`; `VLCtx.WF` (56-61) combines
   those declaration obligations with context and variable-dependency checks.

3. **The let inference statement distinguishes checking and infer-only use.**
   `Lean4Lean/Verify/TypeChecker/InferType.lean:379-386` states `inferLet.WF`
   with `hr : e.FVarsIn (· ∈ c.vlctx.fvars)` and
   `hinf : inferOnly = true → ∃ e', c.TrExprS e e'`.
   Thus infer-only use assumes translation of the input; its let premise
   already supplies annotation/value compatibility. The checked branch in
   the source derivation (346-359) checks the annotation, obtains a sort,
   checks the value, applies definitional equality, and follows an exception
   path on false. The infer-only branch (360-362) instead extracts the let
   premises from `hinf`. The broader `inferType'.WF` statement repeats this
   mode-sensitive input condition at 413-416. These are observations of
   definitions and statements, not a fresh verification of their proof terms.

4. **The WHNF statement does not cover arbitrary raw lets.**
   `Lean4Lean/Verify/TypeChecker/WHNF.lean:29-31` states `whnfCore'.WF` with
   `he : c.TrExprS e e'`. Its result condition is
   `c.FVarsBelow e e₁ ∧ c.TrExpr e₁ e'`. The let branch (122-124) destructures
   that pre-existing `TrExprS.letE` witness and uses the body's `inst_let`
   translation before the recursive WHNF call. `whnf'.WF` at 132-133 has the
   same input translation premise. Consequently these stated contracts do
   not establish behavior or permission for reduction of a raw malformed let
   lacking the translation premise.

5. **Environment, state and recursive-method assumptions remain explicit.**
   `Lean4Lean/Verify/TypeChecker/Basic.lean:190-205` makes `VContext` carry
   a semantic environment, primitives, an environment translation and a
   well-formed translated local context. `VState.WF` (245-254) includes cache,
   context, equality-manager and name-reservation conditions. `M.WF`
   (278-280) constrains successful `.ok` returns from a well-formed starting
   state; it does not assert success or termination. `Methods.WF` (314-323)
   supplies corresponding recursive-method contracts, and `RecM.WF` (325-326)
   quantifies over methods satisfying those contracts. This review does not
   audit their complete imported dependency or axiom closure.

## Qualification and proposed wording

The cited WHNF file contains explicit `sorry` bodies for
`reduceRecursor.WF` (6-8) and `reduceProj.WF` (25-27). The inference file contains
one for `inferProj.WF` (388-391), and the translation file defines `TrProj`
using `sorry` at 67. The directly discussed let and WHNF statements have
source proof bodies, but that fact supplies no complete proof-audit claim.
No theorem was compiled, rechecked or accepted as normative authority here.

Recommended qualified statement: “At the retained Lean4Lean revision, the
formal translation relation for a let requires the translated value to have
the translated annotation type. The source's WHNF preservation statement
assumes this translation relation and a well-formed context/state. Erasure in
that model therefore does not, by itself, justify accepting arbitrary raw lets
before those conditions are established.”

Recommended remaining question: “For the intended serialized-input contract,
where must these admissibility conditions be established: at import/checking,
before invoking reduction, or by a documented alternative acceptance contract?”
The retained source characterizes a model/API boundary; it does not decide a
universal exported-input policy, settle the frozen Lab denotation, or support
an Arena `reject`/`either` outcome by itself.

The four primary files to preserve are `Verify/Typing/Expr.lean`,
`Verify/TypeChecker/InferType.lean`, `Verify/TypeChecker/WHNF.lean`, and
`Verify/TypeChecker/Basic.lean`, all beneath `Lean4Lean/` at the revision above.
`Verify/Expr.lean` contains syntactic helper lemmas; it is not the location of
the `TrExprS` let clause.

Accounting: this delegated review overlaps the root item's continuous active
interval and must not be added to it a second time. The root work record starts
at `2026-09-13T13:13:05.637413+00:00` / monotonic `83940.16999425`;
the review's observed checkpoint is `2026-09-13T13:17:51.218423+00:00` /
monotonic `84225.733556791`, an enclosing interval of `285.563562541` seconds
through that checkpoint. The delegation start itself was not separately
clocked; final writing/closure remains charged through the root's later end.
