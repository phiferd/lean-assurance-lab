# Nanoda literal hash test non-vacuity repair

`NANODA-TEST-NONVACUITY-1` completed with `SUCCESS` at Nanoda
`4c544ed4099c8227f07d5de77ad1e69fb0740a27`.

The existing `hash_test0` generated 10,000 String pairs and 10,000 Nat pairs,
but its helper disabled both native-literal extensions before constructing the
export. Both quick constructors therefore returned `None`. Hashing and comparing
the `Option` values passed without creating or inspecting any native literal.

An assertion-only patch reproduced the defect: the focused test failed on its
first String `Some` requirement. The final test-only patch first asserts the
intentional disabled behavior, then clones the configuration, enables both
extensions before building a fresh export/DAG, requires successful construction,
matches `Expr::StringLit` and `Expr::NatLit`, checks their stored payloads, and
retains repeated-value hash and interned-pointer equality.

The repaired focused test passed. The exact same patch also passed the complete
locked upstream suite: 38 library tests passed with no failures; eight doc tests
were ignored. A stable-rustfmt probe rewrote unrelated files because it could
not honor the project's unstable settings. Those bytes were rejected and the
final patch was rebuilt in a clean detached checkout; the failure receipt is
preserved.

This is a test-effectiveness result, not evidence of a checker correctness or
Lean semantic defect. The recommended next external action is the prepared
test-only pull request after a current duplicate/rebase preflight, renewed tests
and explicit target-specific human approval. Nothing was submitted.

At project closure, `ARENA-LET-REGRESSION-1` is the highest-ranked remaining
READY item and is selected unstarted. It reuses an exact existing mismatch pair
for potential shared corpus value, subject to duplicate and expected-outcome
qualification.
