# Draft: make the native-literal hash test non-vacuous

Target: `ammkrn/nanoda_lib` at `4c544ed4099c8227f07d5de77ad1e69fb0740a27`
Proposed action: pull request
Submission status: **not authorized and not submitted**

This is an evidence-linked successor to the content-bound [original
draft](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/action-recommendations/drafts/nanoda-literal-hash-test-nonvacuity.md).
It does not authorize or submit an upstream action.

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

- [test-effectiveness assessment](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/test-effectiveness-assessment.json)
  records the source-level finding and scope.
- [assertion-only reproduction receipt](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/execution/baseline-nonvacuity-receipt.json):
  expected failure at the first String `Some` check.
- [focused repaired-test receipt](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/execution/repaired-focused-receipt.json):
  pass.
- [full locked-suite receipt](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/execution/repaired-full-suite-receipt.json):
  `cargo test --offline --locked` passed 38 library tests with zero failures;
  8 doc tests were ignored.
- [final test-only patch](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/patches/final-test-repair.patch).
- [result record](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/result.json)
  and [human-readable report](https://github.com/phiferd/lean-assurance-lab/blob/773f2cac989e54fcb846bc87e3789985a1fd0e7e/results/research/nanoda-test-nonvacuity-1/report.md).

## Before submission

Recheck current upstream and open pull requests for an equivalent repair, rebase
the patch if the base has advanced, rerun the focused and full locked suites,
and obtain explicit human approval for this exact pull request and target.
