# Arena let-policy follow-up

`ARENA-LET-POLICY-FOLLOWUP-1` produces one candidate-only `either` package and a
[local PR draft](../../action-recommendations/drafts/arena-let-value-type-mismatch-pr.md).
Recommend submitting the two-file change to `leanprover/lean-kernel-arena`
after fresh target/source/duplicate preflight and exact owner approval.
No external submission or checker execution occurred.

## Why this case adds value

The exact existing 601-byte export represents:

```text
def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
```

The annotation and value disagree: `Sort 1` has type `Sort 2`. Substituting for
the bound variable erases that annotation and yields a declaration with matching
types. The bound variable is used. This is an acceptance-policy characterization,
not a false theorem or a universal soundness claim.

The refreshed [reply to lean4export #48](https://github.com/leanprover/lean4export/issues/48#issuecomment-5654286873)
still gives practical latitude on this exact example and explicitly lacks a
completely authoritative answer. This supplies positive support for the proposed
`either` label under the Lab's portfolio rule, while preserving the frozen
catalog/authority state. It does not require all checkers to reproduce the
reference kernel's behavior or approve the package on Arena's behalf.

Current Arena source is `fd74e8b84bf4b2a3172b5f6b59ca8679be427ebb`, retrieved
on 2026-09-14 and bound in the complete 234-file source archive. The independent
[overlap review](independent-overlap-review.json) inventories 76 YAML descriptions,
15 static exports, 50 test Lean source files and 100 tutorial declaration macros.
It inspects the declared generated/external routes without executing them.
This is a complete declared source inventory, not a global claim about all
runtime-generated exports or semantic equivalence.

The `subject-reduction-redex`/reduct pair concerns beta erasure and conversion
transitivity through `Acc`. Let performance cases have matching annotations.
`constlevels` does contain malformed lets, including an annotation/value type
mismatch, but combines them with separate unfolding and type defects inside a
larger theorem type. It does not isolate this annotation/substitution choice.
The tutorial's `letType` already has the matching control shape, so an extra
accept test would add little. The historical candidate/control pair changes
both the let value and the enclosing declaration type; no one-field control
claim is made.

Arena retains accepted/rejected status for `either` tests and displays the
choice while excluding both outcomes from soundness/completeness scores.
Declines and errors remain separately visible. The contribution is a compact
shared input and explicit policy explanation, not a test that forces one answer
or promises that every implementation already accepts/rejects in a given way.

The bounded pull-request search returned 21 related bodies, none describing
this exact isolated case. Returned states, timestamps and comment counts were
null; no complete issue/comment inventory or live disposition is claimed.
The #48 comments refresh returned the same one reply with omitted timestamps.
All four charged read-only requests and their receipts are preserved.

## Package and validation

The package contains only `tests/corner-cases/let-value-type-mismatch.yaml` and
its static `.ndjson`. The YAML describes the mismatch and substitution result,
links the exact reply and sets `outcome: either`. The NDJSON is byte-identical
to the retained candidate; no new scientific export or variant was generated.

The first static reservation passed `lka.py build-test` with one success and
zero failures in under one second. It copied exactly 601 bytes/13 lines and
recorded the expected case name and `either` outcome. Dependencies from the
existing local Arena environment meet the current runner's declared versions;
no setup download was needed. The source archive is not a Git checkout, so
build statistics lack a Git revision; exact source identity comes from the
committed archive and manifest instead. The build validates static packaging,
not Lean semantics or checker behavior.

The [execution manifest](execution-manifest.json), [raw receipt](static-build-01/supervisor.json),
[build result](static-build-01/result.json), patch and original bytes remain
bound. Lab full current/historical validation and final cumulative accounting
are recorded separately in `validation.json` and `delivery-accounting.json`.

## Handoff

Select `NANODA-NESTED-REGRESSION-1` READY and unstarted under its original
90-minute/eight-request/source-only scope. The prepared Arena draft is a concrete
submission candidate; publication awaits the owner's exact approval and fresh
preflight. Existing Nanoda capacity holds remain dated and unchanged. The theorem
companion still lacks a distinct refusal risk, cache work lacks its outcome
witness, and historical assurance/transfer gates remain unmet. No second
research item starts in this request.
