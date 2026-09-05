# Arena PR #182 maintainer follow-up

## Replacement PR description

This adds two static exports for an inductive type with parameters `(P : Prop)
(p q : P)`. They differ only in the constructor result:

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

Both files contain the full exported inductive declaration, including its
constructor and recursor data. They are placed in `tests/corner-cases/` as
`proof-param-ok` and `proof-param-swap`, following the layout used by PR #176.

Validation:

```text
python lka.py build-test 'corner-cases/proof-param-*'
Results: 2 succeeded, 0 failed
```

## Proposed maintainer reply after the branch update

Fixed — I moved the pair to `tests/corner-cases/` as `proof-param-ok` and
`proof-param-swap`, following PR #176, and updated the file references. Both
tests build successfully.
