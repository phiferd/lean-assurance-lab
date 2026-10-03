# Kiota PR12 recursor CLI contract follow-up

## Plain-language result

**What did we find?** Kiota draft PR12 at `5c5351a7e2ec74ce3142e32b53aff11b8340448a`
incorporates PR11's exact `774ce05792deda309ef96e9781d6cfe0b0b496a5` commit through
merge commit `ada249b`, then refines its error mapping so a bad supplied recursor
type remains a proof rejection rather than becoming an internal error. The
recursor tests exercise the parser API, while the existing CLI-verdict tests
exercise unrelated inputs. A local one-test patch closes that integration seam:
the original malformed `LALNest.rec_1` fixture must exit with status 1 and emit
the reconstruction-specific `REJECT` diagnostic.

**Is it interesting?** Yes, modestly. The test protects the observable contract
between the imported reconstruction and PR12's new accept/reject/decline/error
CLI. It adds no new semantic claim and does not characterize Arena resource use.

**Does it require more work?** The patch is ready for maintainer review, but no
upstream write is authorized here. It should be considered as a small addition
to PR12; no separate framework or resource investigation follows.

## Current upstream observation

Observed read-only on 2026-10-02:

- upstream `main`: `9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`;
- PR11 head: `774ce05792deda309ef96e9781d6cfe0b0b496a5`, open, no review,
  issue, or inline comments and no reported checks;
- draft PR12 head: `5c5351a7e2ec74ce3142e32b53aff11b8340448a`, open, no review,
  issue, or inline comments;
- PR12's ordinary CI checks reported success. Its three Arena regression jobs
  reported failure; this follow-up does not reinterpret or investigate those
  already documented resource/availability results.

## Local patch

The portable patch is
`results/research/kiota-pr12-cli-contract-2026-10-02/kiota-pr12-recursor-cli-contract.patch`.
It records full upstream base `5c5351a7e2ec74ce3142e32b53aff11b8340448a`
and local patch commit `f0375647ebac180c27898b5df7b8116ec7c7ca5d`.

The sole change adds `malformed_recursor_type_is_a_proof_rejection` to
`tests/cli_verdicts.rs`. It runs the existing
`recursor-type-reconstruction.reject.ndjson` through the compiled CLI and
checks both exit status 1 and the exact `REJECT: recursor \`LALNest.rec_1\` type
does not match reconstructed type` diagnostic.

This expectation matches the current PR12 binary directly: running that fixture
as a file produces the same diagnostic and exits 1. The assertion is stable at
the intended integration boundary because `src/parser.rs` deliberately maps a
`TcError::Reject` from recursor comparison to that declaration-specific text,
while `src/main.rs` deliberately maps every `Reject` to the `REJECT:` prefix and
exit 1. PR12 separately preserves `Decline` and `Other` during reconstruction,
so an accidental classification regression would change the observable prefix
or exit code and fail this test.

The test is not vacuous: it launches `CARGO_BIN_EXE_kiota`, writes the complete
existing malformed export to stdin, waits for the child, and inspects both its
real process status and captured stderr. Nearby coverage already proves a JSON
parse error is exit 3/`ERROR`, a diagnostic cutoff is exit 2/`DECLINE`, a valid
export is exit 0, and an unrelated bad definition is exit 1/`REJECT`. The 15
focused recursor tests separately prove exact parser rejection, valid controls,
ordinary/mutual/nested acceptance, universe handling, reconstructed storage,
K recomputation, and transactional rollback. This addition therefore covers
only the previously missing composition of those two tested layers.

## Validation

Using Rust 1.99.0 with the repository lockfile and offline dependencies:

- `cargo test --offline --locked --test cli_verdicts`: 5 passed;
- `cargo test --offline --locked --test exports recursor_type_reconstruction`:
  15 passed, 70 filtered out;
- `cargo test --offline --locked`: 193 passed total (101 library, 2 streaming
  CLI, 5 CLI-verdict, and 85 export tests), with zero failures or ignored tests;
- `git diff --check`: passed.

The explicit `/workspace/.tools` Rust toolchain was checked directly: neither a
`rustfmt`/`cargo-fmt` binary nor an installed rustfmt component is present, so
`cargo fmt -- --check` could not run. No component was installed. The patch is
one conventionally formatted Rust test and its diff was inspected directly. No
Arena run, network write, PR update, comment, issue, merge, or push was
performed.
