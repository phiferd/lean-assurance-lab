# Add a let annotation/substitution corner case

This adds one small static `either` test at
`tests/corner-cases/let-value-type-mismatch`:

```text
def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
```

The let value has type `Sort 2`, which disagrees with its `Sort 1` annotation.
Checking that relationship can reject the declaration. Substituting the value
for `u` first produces `def EcosystemCase : Sort 2 := Sort 1`, whose types match.

The [reply to this exact example](https://github.com/leanprover/lean4export/issues/48#issuecomment-5654286873)
supports allowing either outcome as practical checker policy, while leaving a
completely authoritative answer open. The test records that choice without
scoring it as a soundness or completeness failure. It is not a false-theorem
example.

The existing subject-reduction cases concern beta erasure and conversion
transitivity; this case isolates a let annotation removed by substitution.
`constlevels` also contains malformed lets, but combines them with other
unfolding/type defects. The tutorial already supplies a matching positive let,
so no extra accept control is added.

Validation at Arena `fd74e8b84bf4b2a3172b5f6b59ca8679be427ebb`:

```text
python lka.py build-test corner-cases/let-value-type-mismatch
Results: 1 succeeded, 0 failed
```

The static build preserves the existing 601-byte export and records outcome
`either`. No checker was run for this change.
