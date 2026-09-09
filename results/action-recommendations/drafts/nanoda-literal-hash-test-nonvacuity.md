# Draft: make the native-literal hash test non-vacuous

Target: `ammkrn/nanoda_lib` at `4c544ed4099c8227f07d5de77ad1e69fb0740a27`  
Proposed action: pull request  
Submission status: **not authorized and not submitted**

## Proposed title

`test: make native literal hash assertions non-vacuous`

## Proposed body

`hash_test0` currently uses the default test configuration, which disables both
native-literal extensions. The quick Nat and String constructors therefore
return `None`, so the loop's equality and hash assertions compare absent values
rather than literal expressions.

This test-only patch makes the disabled behavior explicit, then enables both
extensions before constructing a fresh export/DAG. It requires successful
literal construction, checks the `StringLit` and `NatLit` variants and stored
payloads, and retains the repeated-value hash and interning assertions.

Validation on the exact base revision:

- assertion-only reproduction: expected failure at the first String `Some` check;
- focused `hash_test0`: pass;
- full `cargo test --offline --locked`: 38 library tests passed, 0 failed; 8 doc tests ignored.

## Before submission

Recheck current upstream and open pull requests for an equivalent repair, rebase
the patch if the base has advanced, rerun the focused and full locked suites,
and obtain explicit human approval for this exact pull request and target.
