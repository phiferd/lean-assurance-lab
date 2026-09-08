# Cache survivor export-reachability boundary

`SURVIVOR-CACHE-EXPORT-1` closes `BOUNDED_UNRESOLVED` at an ordinary-carrier
and exact-pointer boundary. No build, checker, proof, network request,
scientific export pair, or external action ran.

The internal predecessor remains a real same-checker distinction: after a weak
inference caches a malformed let, the baseline `Check` recomputes and rejects
while the mutation can reuse the weak entry. The K-recursor route is also real:
`reduce_rec` calls `to_ctor_when_k`, which weakly infers the major before its
WHNF reduction.

## Why the ordinary export construction stops

The minimal desired shape needs a carrier `q : K(E)` and a target such as
`f q E`. Comparing the carrier's inferred type with `f`'s first binder would
reduce `K(E)` and weakly infer `E`; checking the second argument would then
visit `E` strongly.

Nanoda's ordinary entry order prevents that carrier from being supplied
self-containedly. A direct recursor application strongly checks every argument,
including the major, before binder equality can reduce it. An earlier carrier
declaration has its header checked with `Check` in a fresh checker before any
later declaration can use it. A local carrier's binder annotation is checked
first for the same reason. Cross-declaration cache warming cannot help because
each declaration gets a fresh `TcCache`.

There is a second exact-sharing constraint. A constant type is copied through
level substitution into the current checker DAG. An `E` reconstructed inside
the carrier type is not automatically the same pointer as an `E` repeated in
the target's export DAG. Thus unchecked carrier injection or target-only
checking would both change the scientific question and still require an
additional pointer-sharing construction.

This is not a proof that every possible export or every compound validator gap
is unreachable. It is a source- and parser-bound limit for the identified
ordinary K-recursor-major route. The canonical survivor remains
`SURVIVED_WITHOUT_WITNESS`, and this result supports no external defect report
or corpus admission.

The next recommended local question is the pending universe survivor
`nanoda-gen-e9648d8c028d`: determine whether the changed `diff == 0` / right
`Zero` branch is reachable after level simplification before spending checker
reservations.
