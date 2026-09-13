# test(tc): cover native Nat operation dispatch

The existing arithmetic tests call the BigUint helpers directly. This patch adds two tests of `TypeChecker::try_reduce_nat`, checking that each cached operation name reaches the intended arithmetic and produces a real natural-number literal.

The fixed cases cover gcd, bitwise AND/OR/XOR, and left/right shifts. A second test first checks `Nat.land 10 12 = 8`, then disables the extension while retaining the same real operands and requires no reduction. The fixture enables literals before creating its DAGs, binds all six cached names explicitly, and uses the existing empty export unchanged.

Only `src/tests.rs` and the new `src/tests/nat_dispatch.rs` change. This is preventive coverage of an internal API; it does not claim a current defect or a public import-path guarantee.

Validation at `4c544ed4099c8227f07d5de77ad1e69fb0740a27` with Rust 1.98.0:

- `cargo test --offline --locked nat_dispatch -- --nocapture`: 2 passed.
- `cargo test --offline --locked -- --nocapture`: 40 library tests passed; 8 existing documentation examples remain ignored.

Local preparation only. Patch: `results/research/nanoda-nat-dispatch-regression-1/patches/nat-dispatch.patch`. Before submission to `ammkrn/nanoda_lib`, refresh source and duplicates, rerun focused/full tests after any rebase, and obtain approval for that exact pull request. Hold for maintainer capacity while #32 and #33 await acknowledgment.
