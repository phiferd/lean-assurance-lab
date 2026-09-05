# Arena PR #181 maintainer follow-up

## Replacement PR description

This adds two static exports for Lean's strict-positivity check. The rejected
case has the following shape:

```lean
def Ignore (A B : Type) : Type := A

inductive T : Type where
  | mk (f : Ignore Unit T -> T) : T
```

`Ignore Unit T` reduces to `Unit`, but the recursive type `T` still occurs as
an argument to `Ignore`. Lean therefore rejects the declaration as non-positive.
The accepted control replaces `Ignore Unit T` with `Unit`, giving the field
type `(Unit -> T) -> T`.

Both files contain the full exported inductive declaration, including valid
constructor and recursor data. This matters because Arena's related tutorial
example has placeholder recursor data and can be rejected for that independent
reason. These tests isolate the positivity check: the control has outcome
`accept`, and the version with the hidden occurrence has outcome `reject`.

Validation:

```text
python lka.py build-test 'lal-reducible-hidden-positivity-*'
Results: 2 succeeded, 0 failed
```

## Proposed maintainer reply after replacing the PR description

Yes — the original description was AI-assisted, and I should have rewritten it
in plain language before submitting it. Sorry. I replaced it with a direct
explanation of the two declarations and why the second one is rejected.
