# Validation receipt

## Base/head identity

```text
base 86060d51a69e91445bbae6b6b1366c12e05e67f0
head a3e17bf3d0f30a66384967929fba0d5c33d1e765
```

## Regression effectiveness on unchanged PR 38 base

The two new end-to-end regression tests were applied without the production
changes to a detached worktree at the exact base. Command:

```sh
docker run --rm \
  -v /tmp/nanoda17-basecheck:/work \
  -v /etc/ssl/certs:/etc/ssl/certs:ro \
  -w /work rust:1.90-bookworm \
  /bin/bash -c 'cargo test pp_declars_ -- --nocapture'
```

Result: expected failure, `0 passed; 2 failed`. The valid-name selection test
reported `«b c»`, `A.«b c»`, and `A.«b.c»` missing. The alias test reported
that invalid `A.b c` was accepted. This demonstrates both relevant assertions
detect the pre-patch behavior.

## Final patch validation

Command at exact head:

```sh
docker run --rm \
  -v /workspace/nanoda17:/work \
  -v /etc/ssl/certs:/etc/ssl/certs:ro \
  -w /work rust:1.90-bookworm \
  /bin/bash -c 'cargo test --all-targets'
```

Result:

```text
lib: 60 passed; 0 failed; 0 ignored
bin: 0 passed; 0 failed
```

`git diff --check` also passed, and the Nanoda worktree was clean after commit.
The container was needed because the host environment exposed neither `cargo`
nor `rustc`. The first container attempt required mounting the host CA bundle
for crates.io; this changed no credentials or network configuration.

## Lab repository checks

At LAL base `c43d3558464aa67cdeeb281a513fce22dac6d980`:

- `scripts/validate-research-queue`: passed; the queue is valid and PAUSED
  with no executable item.
- `python3 -m unittest tests.test_arena_let_regression_erratum`: six tests
  passed, including the canonical READY-count check. The earlier transient
  mismatch is absent after the reserved campaign's independently authored
  closure.
- `python scripts/exploration-record check --base c43d3558...`: passed.
- `python scripts/exploration-record lane --base c43d3558...`: selected
  `lane=full`.
- `python scripts/check-portable-evidence-replay
  --require-foreign-checkout`: passed, covering 20 families and 635 receipts.
- `python scripts/run-unit-tests`: the current partition ran 1,676 tests but
  did not pass in this host environment: one test could not find `rustc`, and
  three process-group cleanup tests observed descendants after termination.
  The historical partition subsequently passed 73 tests with one documented
  missing-payload skip, followed by 14 additional historical tests passing.

The four current-partition failures do not read the additive report directory
and are recorded rather than repaired here. Exact pushed-commit GitHub Actions,
which provisions Python 3.10 and runs the same full lane, is the publication
gate.
