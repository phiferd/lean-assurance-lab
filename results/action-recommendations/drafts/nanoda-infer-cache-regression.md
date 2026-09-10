# Draft pull request: protect checked inference from unchecked cache entries

Target: `ammkrn/nanoda_lib` at base revision
`4c544ed4099c8227f07d5de77ad1e69fb0740a27`.

Status: not authorized and not submitted. Before any submission, check current
upstream source and existing issues/pull requests, rebase the test-only patch if
needed, rerun the focused and full locked suites, and obtain explicit approval
for the exact pull request.

## Proposed title

`test(tc): protect checked inference from unchecked cache entries`

## Proposed body

This adds two focused unit tests for the inference-cache validation boundary.

- A well-typed let is inferred with `InferOnly`, then checked on the same
  expression pointer and type-checker. The test verifies successful results are
  retained in the separate unchecked and checked maps.
- A malformed let is rejected by a fresh `Check`, succeeds with `InferOnly`, and
  is still rejected by `Check` after the unchecked result has warmed the cache.

The patch is preventive: it protects the current split-map policy and does not
claim that ordinary exported declarations can reach the internal malformed-let
sequence. It changes only `src/tests.rs` and a new `src/tests/tc.rs`; production
code, dependencies and export fixtures are unchanged.

Validation at the bound base revision:

- `cargo test --offline --locked infer_cache -- --nocapture`: 2 passed, 0 failed
- `cargo test --offline --locked`: 40 library tests passed, 0 failed; 8 doc tests ignored

Local evidence and the exact patch are retained under
`results/research/nanoda-cache-regression-1/` in Lean Assurance Lab.
