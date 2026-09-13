# Clarify validation of let annotations in NDJSON input

Local documentation-question draft for `leanprover/lean4export`; not authorized
and not submitted. Suggested target: `format_ndjson.md`, with a reference-manual
cross-link if that is the better home. This is a contract question, not a defect
or unsoundness report. A current documentation/duplicate check and exact owner
approval are required before sending it.

The [3.1.0 format description](https://github.com/leanprover/lean4export/blob/f297dfe2a8557e8674fe892bb49dffe4bfadc0e9/format_ndjson.md)
includes a let's `type`, `value`, `body` and `nondep` fields. Could it also state
whether a full external checker is expected to validate the supplied raw let's
annotation/value typing, or may first eliminate the let and validate only the
result? If malformed inputs are outside the contract, could that precondition
be explicit?

Here is a human decoding of an unchanged small NDJSON pair, not an
elaboration or test result:

```text
candidate: def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
control:   def EcosystemCase : Sort 1 := let u : Sort 1 := Sort 0; u
```

The candidate annotates `Sort 1` with `Sort 1`, although its type is `Sort 2`.
Substitution erases that annotation and yields `Sort 1 : Sort 2`, matching the
enclosing declaration. The body uses the variable; the control changes both
the value and enclosing declaration type. Both files are 601 bytes, have no
universe parameters, and use a safe definition with opaque hints and a
`nondep:false` let. Exact files and hashes are in the Lab's accompanying
clarification packet and source lock.

In [Lean v4.33.0](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.cpp#L200-L222),
checking a let verifies the annotation and value before extending the local
context, while its [reducer](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.cpp#L504-L506)
performs substitution. The [inference interface](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.h#L125-L143)
also distinguishes inference on type-correct input from checking. We are trying
to document the input guarantee, not require reducers to recheck already
validated terms or prescribe a particular checking algorithm.

For a structurally valid stream in an already checked environment, should the
candidate above be refused as a raw declaration, be permissible only under an
explicit transformation contract, or be outside the checker's promised input
domain? Is there an existing statement of that policy we should cite? A short
note separating structural decoding, supplied-expression validation, and
reduction on prevalidated terms would help independent checker and shared-corpus
authors use consistent expected-outcome language.
