# Kiota CLI input-open diagnostic improvement

## Plain-language result

**What did we find?** Kiota draft PR12 opens a named input file with
`expect("open input")`. An ordinary missing path therefore invokes Rust's panic
hook and is later collapsed into the generic `ERROR: panic during checking`.
The local patch converts the file-open error directly into Kiota's existing
internal-error verdict, including the requested path and operating-system
reason, without a panic banner.

**Is it interesting?** Yes, modestly. CLI users and automation retain exit code
3 but receive an actionable diagnostic. Proof acceptance, rejection, decline,
stdin handling and successful file parsing are unchanged.

**Does it require more work?** The patch is locally ready for maintainer review.
No second upstream pull request or comment is authorized. Unreadable-file
coverage was intentionally omitted because permission behavior is not portable
under root or privileged CI.

## Exact scope

The portable patch is `kiota-cli-input-error.patch`. It is based on Kiota PR12
head `5c5351a7e2ec74ce3142e32b53aff11b8340448a` and records local commit
`6be42fd28e5dffcf2d2a8cb2a46e008648a1f4c4`.

Production replaces only `File::open(...).expect(...)` with an error mapping to
`TcError::Other("open input `<path>`: <reason>")`. Existing `finish` behavior
therefore emits `ERROR:` and exit 3. The regression uses a repository-relative
path that is asserted absent, invokes the compiled binary, requires exit 3 and
the path-bearing prefix, and rejects both the panic-hook banner and the generic
catch-unwind fallback.

Independent static review accepted the two-file diff with no blocking issues.
It found the test deterministic and non-vacuous, the error classification
preserved, and proof-verdict paths unaffected. The reviewer independently ran
the exact new test (1 passed) and `git diff --check`; it did not independently
run the full suite.

## Validation

Using Rust 1.99.0 with offline locked dependencies:

- `cargo test --offline --locked --test cli_verdicts`: 5 passed;
- `cargo test --offline --locked`: 193 passed, zero failed or ignored;
- `git diff --check`: passed.

The explicit `/workspace/.tools` toolchain has no rustfmt component; none was
installed. No Arena run, security test, resource investigation, upstream write,
PR, comment, merge or push was performed for this improvement.

## Separate lab CI attribution

Lab commit `e56d8b421f62d4447eafa96d16ee7ac9f8eeeb2e` changed only
`docs/EXTERNAL_CONTRIBUTIONS.md` and
`results/research/external-contributions.json`. Its base `cbe4c8a6` passed CI
run 37067149355. Run 37075909966 failed only
`test_child_memory_breach_kills_process_group`: the synthetic child exceeded
the 64 MiB limit and was killed, but the timing-sensitive cleanup observation
reported `cleanup_complete: false`. The supervisor and test bytes were
unchanged. This is unrelated to the ledger publication; the failed run is
preserved and no repair was made here.
