# Binder model pilot protocol, draft R1

## Question and interpretation

Compare the two selected public structural expression APIs with a separately
implemented capture-avoiding named-variable model on exactly 10,000 operation
vectors. A valid vector is **well scoped in its declared finite external
context**. No term in this protocol is claimed to be well typed by Lean. The
APIs transform expression syntax without a type-checking environment, so a
typing judgment would answer a different question.

The common expression grammar is `bvar`, `sort 0`, binary application, default
lambda with a domain and body, and let with a type, value, and body. Binder
names are semantically ignored by the de Bruijn observers. Lambda domains and
let types/values have the current binding depth; bodies have one extra binder.
No Pi, metavariable, free-variable ID, constant, projection, literal, metadata,
universe parameter, reduction or type-checking operation is in scope.

## Context and operation semantics

External contexts are ordered nearest first. `C = [c0,c1,...]` means loose
index zero denotes `c0`. Under a binder its name is prepended. A name in the
body resolves to the nearest matching binder before an external name. Thus
shadowing is explicit. `sort 0` has no variables.

* `LIFT(e,s,d)`: insert `d` fresh names into `C` at position `s`, leaving the
  named expression unchanged. Its de Bruijn translation is compared with
  `liftLooseBVars e s d` and Kiota `shift(e,d,s)`. Both `s=0`, interior `s`,
  and `s=|C|`, plus `d=0,1,2`, occur. New names cannot collide with existing
  context or binder names.
* `SUBST(e,a)`: `e` is scoped in `[c0]++D`, and `a` in `D`. Replace free `c0`
  in the named expression with `a`; alpha-rename every binder that would
  capture a free name of `a`. The result is scoped in `D`. Compare it with
  each API's `instantiate1`.
* `LIFT_COMPOSE(e,s1,d1,s2,d2)`: lift once from `C` to `C1`, then from `C1`
  to `C2`; record and compare both intermediate and final results. The
  second cutoff is relative to `C1`.
* `SUBST_COMPOSE(e,a,b)`: `e` is scoped in `[c0,c1]++D`, `a` in `[c1]++D`,
  and `b` in `D`. Substitute `c0` with `a` and then `c1` with `b`; record and
  compare both results. The second operation also reaches any `c1` inserted
  by the first. Its context is the once-reduced `[c1]++D`.

The named implementation will compute free names, rename binders only when
needed, and compare alpha-equivalence separately from literal binder names.
The expectation auditor will have no import from the named model or vector
producer. It will independently check named-to-index translation, syntax and
context scope, operation results using direct de Bruijn rules, and alpha
normalization. Its direct de Bruijn calculation is a cross-check of the finite
expectations, not an independent proof of either API's semantics.

## Exact deterministic enumeration

Scientific vector ordinals are `0..9999`. The top-level operation is
`floor(i/2500)` in the order `LIFT`, `SUBST`, `LIFT_COMPOSE`,
`SUBST_COMPOSE`. Within each operation, `floor((i%2500)/500)` selects one
of five syntax families and `i%500` is the variant. There are exactly 500
variants of each family in each operation stratum. A SplitMix64 stream is
seeded by the fixed 64-bit seed `0xB17D3A9E5C204F61` XOR the ordinal. All
random draws are unsigned 64-bit modulo the specified bound; no language
library random implementation is part of the input contract.

Every initial context is `[c0,...,c(n-1)]`, where `n=3+(next()%4)` (3..6).
The final context after a composition can reach length ten. The source's
first variable `c0` occurs in each family, making first substitution
nonvacuous. Family 0 is an open application; family 1 has two nested lambdas;
family 2 has an application whose lambda domain uses an external variable;
family 3 has a let whose type, value and body expose different binder depths;
family 4 nests a lambda, let and application. The exact five constructors,
including variable selection and optional wrappers, are frozen in the
scientific generator source before input construction. All generated source
trees have at most 20 nodes and maximum binder depth three; external indices
are at most five before lifts. A failed size or scope check is an engineering
pause, not permission to replace an ordinal.

For each first lift, `s` is a draw modulo `|C|+1`; `d` is a draw modulo 3.
For the second lift, the same formulas apply to `C1`. This yields a fully
specified context transformation even when a lift is a no-op. The replacement
`a` and `b` grammar is a variable, application, lambda or let over their
respective allowed contexts, with at most seven nodes. At least the even
variants of families 1–4 use an enclosing binder named `c1`, and every fourth
such variant uses free `c1` in `a`; these are mandatory capture-collision
cases. The exact replacement choice is frozen in generator source. Terms may
repeat; vector IDs and complete operation records may not. Generated vectors
must retain invalid/unsupported dispositions rather than resampling, though
the frozen grammar is designed to make every ordinal valid.

Each vector records source and argument named syntax, input and output
contexts, input de Bruijn syntax, operation parameters, model-expected
intermediate and final de Bruijn syntax, and all independently audited checks.
There are 15,000 expected output comparisons per observer: one for each single
operation vector and two for each composition vector.

All vector and observer decoders require exact record keys and JSON integer
types for indices, cutoffs, increments and ordinals. Negative values,
out-of-range indices, booleans in integer slots, malformed constructors,
unknown operation tags and excess fields fail closed. The corpus auditor
mechanically counts each operation/family stratum, mandatory capture
collisions, all cutoff/increment boundaries, lambda domains, and let
type/value/body occurrences; a claimed stratum without its actual witness is
an audit failure.

## Scientific and execution freezes

Before constructing any of the 10,000 scientific inputs, commit the complete
protocol, exact generator and named model, independent auditor, focused
negative regressions, source snapshot and source/reuse review, and a scientific
manifest naming their hashes, the seed, grammar, counts and intended checks.
The exact execution manifest also binds official Lean 4.33.0 runtime/source,
Kiota `2d2a9fa` source and built adapter, observer adapter bytes, Python,
process supervisor, `/bin/ps`, resource limits, process environment and batch
partition. The independent reviewer checks those freezes before construction.
Kiota's adapter invokes `clear_subst_memos` before every vector so shift and
single-instantiation memo results do not cross vector boundaries. It retains
the source implementation's interner within each batch process, since the
interner preserves structural identity and is not a semantic cache. Each
observer batch runs in a fresh process, and the exact fixed batch partition
is bound before launch.

After construction, audit every vector without an observer. Preserve the
portable NDJSON and its hash in a separate committed artifact lock. An
actual-host positive RSS preflight precedes every scientific launch batch.
Observer processes have finite per-process time and RSS ceilings, group cleanup
and raw stdout/stderr custody. A timeout, RSS/monitor failure, cleanup failure,
malformed output or accounting mismatch pauses further launches for diagnosis
and repair under a new exact tooling/execution revision. No attempt limit or
elapsed-time limit closes the item. Each previous attempt remains bound to
its original bytes. The independent result auditor reconstructs every
observer output and compares the full 15,000-case expectation set, rejecting
missing, extra, duplicated or malformed lines.

Focused negative controls must reject wrong named-to-index translation,
capture of an open replacement, failure to lower higher context indices,
wrong lift cutoff, wrong lambda-domain or let type/value depth, altered
expectation, omitted vector, duplicated vector and extra vector. No observer
success code alone can satisfy a semantic comparison.

Agreement warrants only the exact fragment, generated vectors, runtime and
APIs. A difference requires local minimization and a target-specific
recommendation. No external action is authorized.
