# Proposed title

test: cover constructor owner-index validation

# Proposed body

Add a paired integration regression for constructor metadata whose owner exists
but whose `cidx` does not select that constructor from the owner's ordered
`ctors` list.

The positive fixture declares `LALNest.node` at index `0` and accepts. The
negative fixture is byte-identical except for `cidx: 1`; it requires
`TcError::Reject` with the exact message:

```text
constructor `LALNest.node` is not `LALNest`'s own constructor at index 1
```

The exact assertion is intentional: the existing `orphan-ctor` test covers the
earlier missing-owner branch using a generic rejection assertion, while this
pair protects the distinct owner-present list/index predicate and prevents an
unrelated later rejection from satisfying the test.

This is a preventive, test-only change. It does not report a current Kiota bug
or establish a universal Lean metadata rule. The pair exercises the
out-of-range form of the predicate; it does not add a separate in-range
wrong-constructor case.

Validation on Kiota `9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`:

- `cargo test --offline --locked --test exports ctor_owner_index -- --nocapture`:
  2 passed, 70 filtered out.
- `cargo test --offline --locked -- --nocapture`: 83 unit and 72 integration
  tests passed (155 total); zero failures or ignored tests.

The two fixtures reuse existing export bytes unchanged. No production source,
dependency, checker, proof, mutation, or generated export was changed.
