# Nanoda omitted-thread-count declaration-checking PR draft

Target: `ammkrn/nanoda_lib`

Base: `master` at `4c544ed4099c8227f07d5de77ad1e69fb0740a27`

## Title

Test declaration checking for omitted and zero thread counts

## Body

### Summary

Add regression tests confirming that `ExportFile::check_all_declars` still
checks declarations when the configuration omits `num_threads` or explicitly
sets it to `0`.

### Rationale

Before Serde-based configuration parsing was introduced in `9c3a447`, an
omitted `num_threads` value defaulted to `1`. The field now uses
`#[serde(default)]` on a `usize`, so omission produces `0`. The existing
dispatcher preserves the historical behavior by treating values less than or
equal to `1` as serial.

A refactor that treated only `1` as serial would route the omitted setting to
the parallel path. That path would spawn no workers and return without checking
any declarations.

Explicit `0` is covered separately because `Config` exposes `num_threads` as a
public `usize`, and `check_all_declars` explicitly documents values less than or
equal to `1` as serial. The cases coincide today, but a future custom
deserialization default of `1` could preserve omitted-field behavior while
leaving explicit `0` vulnerable to a dispatch regression.

Both tests reuse the existing invalid `ProjFromProp` fixture, call the public
dispatcher, and expect the fixture's existing `infer_proj prop` failure.

### Testing

- `cargo test num_threads_still_checks_declarations --locked`
- `cargo test --locked`
