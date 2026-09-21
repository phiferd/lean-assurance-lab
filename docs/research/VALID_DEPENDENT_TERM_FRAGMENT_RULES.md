# Valid dependent-term fragment rules

This note is the readable view of the canonical contract in
`results/research/valid-dependent-term-pilot-1/design.json`. The JSON artifact
governs mechanically decidable details.

The syntax is `Sort n`, de Bruijn bound variables, Pi, lambda, application and
let. Contexts are innermost-first, and each stored context entry is relative to
its tail. Looking up entry `i` therefore shifts it by `i + 1`.

`Sort n` has type `Sort (n + 1)`. A Pi whose domain has sort level `u` and
whose body has sort level `v` has sort level `0` when `v = 0`, and otherwise
`max u v`. This is the closed-numeric result of Lean's `imax`; no `imax` level
expression is admitted to the corpus.

A lambda is assigned the Pi type formed from its checked domain and inferred
body type. Application first beta-zeta weak-head normalizes the function type
to a Pi, checks the argument type by beta-zeta conversion, and substitutes the
argument into the codomain. Let checks that its annotation is sort-valued and
that the value has the annotated type before substituting the value into the
body type.

Definitional equality in this pilot is deliberately narrower than Lean's: two
terms are equal only when their strong beta-zeta normal forms are the same
de Bruijn expression. Eta, proof irrelevance, delta, iota, recursors, constants,
inductives, quotients, literals, metavariables and free variables are excluded.
The generator must stay inside this subset; the auditor fails closed on any
other constructor or on resource exhaustion.

Every case carries a full derivation tree. A separate auditor reimplements
parsing, shifting, substitution, normalization, inference, category checks and
derivation replay. It must not import those semantic helpers from the generator.
The exported checked-object bridge separately reconstructs the NDJSON graph and
requires exact agreement with the generated value and type before a target
checker may observe the artifact.
