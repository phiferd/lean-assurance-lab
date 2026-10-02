# Independent expected-outcome review

**PASS for freezing semantic expectations; fixture invariants remain unverified until an exact runner observes the raw fixtures.** This review is reasoning support, not semantic authority or execution evidence.

| Case | Meta expectation | Kernel correctness expectation |
| --- | --- | --- |
| Arbitrary `f : Bool → Box` versus `Box.mk` | reject | reject |
| Arbitrary `f : FnAlias` versus `Box.mk` | reject | reject |
| `fun b => Box.mk b` versus `Box.mk`, explicit context | accept | accept |
| Same eta expression with alias retained in the context | accept | accept |

The negative oracle is justified independently of the proposed implementation: instantiate the arbitrary function with `fun _ => Box.mk false`; at `true`, its field differs from `Box.mk true`. Function and structure eta do not identify every arbitrary function with the constructor.

The pinned source creates a prediction distinct from that correctness oracle. Meta opens the constructor's reducing telescope and must compare `(f b).val` with `b`. The kernel's partial-constructor loop initially tests syntactic `is_pi(t_type)`; a preserved alias could skip binder opening and leave zero constructor arguments to check. Alias-negative acceptance is therefore a plausible signal, not an outcome to assume.

Required interpretation checks:

- Inspect the stored local type as exactly `.const FnAlias []`, with unvalued `f`, no metavariable assignment or let value, and zero term arguments on `Box.mk`.
- Preserve distinct nonlambda negative heads through comparison entry and record orientation.
- Record Meta and kernel independently; elaborator rejection must not prevent construction of the kernel fixture.
- Treat the positive alias case only as an accepted routing control. Because its lambda infers a syntactic Pi, it need not traverse the same alias-sensitive branch.
- Do not use successful elaboration of a negative equality as its validity oracle.

The pinned `tests/elab/12520_1.lean` is a positive partial-constructor eta test over `True`; it does not duplicate the preserved-alias arbitrary-function negative boundary.
