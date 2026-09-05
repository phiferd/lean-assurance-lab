# Arena PR #181 maintainer follow-up

## Replacement PR description

This adds two static exports for Lean's strict-positivity check. The rejected
case has the following shape:

```lean
def Ignore (A B : Type) : Type := A

inductive T : Type where
  | mk (f : Ignore Unit T -> T) : T
```

`Ignore` takes a second type argument but does not use it, so `Ignore Unit T`
reduces to `Unit`. For positivity checking, however, Lean conservatively counts
the syntactic occurrence of `T` in the domain of the arrow instead of unfolding
`Ignore` to erase that argument. It therefore rejects the declaration as
non-positive.

The accepted control replaces `Ignore Unit T` with `Unit`, giving the field
type `(Unit -> T) -> T`.

Both files contain the full exported inductive declaration, with constructor
and recursor data matching each version. Arena's related tutorial example has
placeholder recursor data and can be rejected for that independent reason.
These tests isolate the positivity check: the control has outcome `accept`, and
the version with the phantom `T` argument has outcome `reject`.

Validation:

```text
python lka.py build-test 'lal-reducible-hidden-positivity-*'
Results: 2 succeeded, 0 failed
```

## Maintainer reply posted

I replaced the description with a source-level explanation of the two
declarations and why the second one is rejected.
