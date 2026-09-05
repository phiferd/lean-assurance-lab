# Arena PR #181 current description

This adds one static export for Lean's strict-positivity check. The declaration
has the following shape:

```lean
def Ignore (A B : Type) : Type := A

inductive T : Type where
  | mk (f : Ignore Unit T -> T) : T
```

`Ignore` takes a second type argument but does not use it, so `Ignore Unit T`
reduces to `Unit`. A checker that inspects the unreduced constructor field may
reject the syntactic occurrence of `T` in the domain of the arrow. A checker
that first weak-head-normalizes the field type may instead see `(Unit -> T) ->
T` and accept it. The test therefore has outcome `either`.

The file contains the full exported inductive declaration, with matching
constructor and recursor data. Arena's related tutorial example has
placeholder recursor data and can be rejected for that independent reason.
This test therefore isolates the positivity behavior with an otherwise complete
export.

The test is placed at `tests/corner-cases/positivity-whnf`.

Validation:

```text
python lka.py build-test corner-cases/positivity-whnf
Results: 1 succeeded, 0 failed
```
