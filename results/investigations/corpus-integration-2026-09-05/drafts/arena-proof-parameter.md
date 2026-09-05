# Arena PR #182 maintainer follow-up

## Replacement PR description

This adds two static exports for an inductive type with parameters `(P : Prop)`
and `(p q : P)`. They represent the following two constructor results:

```lean
-- accepted control
mk : T P p q

-- corner case
mk : T P q p
```

The official Lean checker accepts `T P p q` and rejects `T P q p`. Kiota
accepts both because `p` and `q` are proofs of the same proposition and its
comparison uses proof irrelevance. The control therefore has outcome `accept`,
while the swapped case has outcome `either`; Arena can record both checker
behaviors without scoring either one as a failure.

Both files contain the full exported inductive declaration, with recursor data
matching the corresponding constructor result. They are placed in
`tests/corner-cases/` as `proof-param-ok` and `proof-param-swap`, following the
layout used by PR #176. Arena's existing `nested-nonuniform-param` test concerns
a value parameter in a nested occurrence; these tests isolate proof parameters
in an ordinary constructor result.

Validation:

```text
python lka.py build-test 'corner-cases/proof-param-*'
Results: 2 succeeded, 0 failed
```

## Maintainer reply posted

Fixed: I moved the pair to `tests/corner-cases/` as `proof-param-ok` and
`proof-param-swap`, following PR #176, and updated the descriptions and file
references. Both tests build successfully.
