# Raw let checking and zeta reduction

`SEMANTIC-LET-CONTRACT-1`, 2026-09-13. Result: a focused documentation question is
useful; the universal serialized-input policy remains unresolved. Reuse the
existing example and source distinctions. Do not start a new proof or witness
search, promote the catalog, or assign an Arena outcome on this packet alone.

The frozen claim is `EXPR.LET.VALUE_TYPE_MATCH`: the inferred type of a local
let value is definitionally equal to its annotation, for let expressions reached
while checking a primary ordinary declaration after annotation/value
well-formedness. The modeled target is checked ordinary declaration addition
at Lean v4.33.0 `d8b18978322de05a8f3dba51ef03cf5461676c17`. Parsing, reconstruction,
elaboration, unchecked insertion and the 4.29.1 producer are distinct scopes.
The exact identity and prior qualification decisions remain unchanged.

## What the sources establish

| Source and exact locus | Useful statement | Boundary |
| --- | --- | --- |
| Reference manual `02d0d61`, `Manual/Types.lean`, 25–60, 93–94 | Core terms are related to types by typing rules; zeta substitutes let-bound values; conversion changes an already assigned type along definitional equality. | This is explanatory type-system prose, not an algorithm for rejecting all arbitrary serialized expressions. Prior conversion-source approval remains DEFER. |
| Lean v4.33.0 `src/kernel/type_checker.h`, 125–143 | `infer` promises a correct inferred type conditional on a type-correct input; `check` checks the expression. `whnf` is documented as returning weak-head normal form. | The short `whnf` comment does not itself state an admissible-input or environment contract. Do not transfer `infer`'s comment to another API as if it were explicit documentation there. |
| Same revision `type_checker.cpp`, 200–222, 504–506 | Checking-mode `infer_let` checks annotation sorthood and value compatibility before extending its context. The reduction branch substitutes body/value directly. | These are separate code paths and implementation evidence. They do not impose a universal temporal ordering on every conforming reducer/checker. |
| Lean4Lean `ecb3b666`, `Verify/Typing/Expr.lean`, `TrExprS.letE`; `Verify/TypeChecker/WHNF.lean`, `whnfCore'.WF` and `whnf'.WF` | The raw-expression translation relation has a value-typing premise for a let. The reduction specification assumes a translation relation. | Erasing syntax into an abstract representation does not supply the relation's missing premise. These are scoped formal definitions; no theorem dependency or exact-target normativity is newly established. |
| Exporter/importer pin `f297dfe`, `format_ndjson.md`, introduction and `Expr.letE` | Version 3.1.0 serializes the let annotation, value, body and dependency flag. It describes some exported data as redundant. | It does not identify the let annotation as disposable validation data or state a malformed-let acceptance policy. The recursor redundancy paragraph cannot silently be generalized to lets. |
| Reference manual `02d0d61`, `Manual/ValidatingProofs.lean`, “Gold Standard” | Serialized-format validation, replay and statement comparison are separately described. | That high-level account does not specify whether a checker validates the supplied raw let or only a transformed term. |

Full source receipts, exact hashes and claim ranges are in
[source assessment](source-assessment.json). The independent reviews are
[prior authority](prior-authority-review.md) and [formal boundary](formal-boundary-review.md).
The only approved documentation source remains scoped to theorem-Prop; it does
not authorize a let claim. The old M8 e551 witness and the later 21ef pair have
different identities and observer evidence.

## Minimal existing example

This is a human decoding of unchanged NDJSON, not newly elaborated source:

```text
candidate: def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
control:   def EcosystemCase : Sort 1 := let u : Sort 1 := Sort 0; u
```

Both 601-byte files have a safe definition with opaque hints, no universe
parameters, `nondep:false`, and body `bvar 0`. In the candidate the annotated
value `Sort 1` has type `Sort 2`, not the annotation `Sort 1`. Pure substitution
removes the let and yields `Sort 1`, whose type matches the enclosing declaration's
`Sort 2`. The control substitutes `Sort 0` and has enclosing type `Sort 1`.
This is a source/structure analysis, not a new execution or mechanized proof.

The body uses `u`; this is not a dead-binding example. The pair changes both
the let value reference and the enclosing declaration type. Its metadata does
not establish that Lean's elaborator emitted the malformed candidate. Existing
pinned reject/accept observations remain observer evidence. No new checker
outcome is claimed.

## Assumptions and open alternatives

For a typing judgment, fix an already checked environment, well-formed local
context, in-scope universe parameters and ordinary safe declaration boundary.
For `let x : A := v; b`, a value-typing premise such as `Γ ⊢ v : A` is distinct
from the syntactic substitution `b[v/x]`. In the cited Lean4Lean relation that
premise is explicit. A reduction specification conditional on this relation
cannot validate a malformed input merely because its output has a type.
The formal contract also assumes well-formed environment/context/state and
recursive methods, and constrains successful returns without promising
termination. Nearby admitted definitions and custom bridge assumptions remain
explicit in the formal review; source proof bodies are not a completed proof audit.
Conversely, a reducer that operates on already checked terms need not repeat
validation at every reduction step. Neither fact alone chooses an exported-input
acceptance policy or proves an exact Lean v4.33.0 conformance theorem.

Three possible interface contracts require an explicit choice: validate the
supplied raw declaration; validate a permitted transformed declaration and
state what correspondence is promised; or require prevalidated inputs and
state that malformed inputs are outside the interface's guarantee. The format
and API prose inspected here do not settle that choice for all independent
checkers. A missing policy does not positively authorize both outcomes.

## Recommendation

Prepare one normal-priority documentation question for
`leanprover/lean4export`, targeting `format_ndjson.md` with a possible cross-link
to the reference manual's validation/type-system chapters. The
[unsubmitted question](maintainer-question.md) asks for the validation boundary
and the exact pair's intended treatment; it does not report a checker bug or
claim unsoundness. Before submission, review current documentation and duplicate
issues, confirm the correct maintainer venue, and obtain exact target-specific
owner authorization. The present seven-request audit was pinned-source work,
not a live duplicate-issue preflight.

A precise answer could support a separately gated source qualification and
Arena packaging review. If maintainers instead scope the format to structure
or prevalidated inputs, document that boundary and avoid a strict cross-checker
outcome. The completed Nanoda internal cache test remains useful either way.
Select `HSBM-PILOT-1` next, READY and unstarted: the finite discovery pilot can
produce new shared regression candidates without repeating this unanswered
question or blocking independent work on external feedback.
