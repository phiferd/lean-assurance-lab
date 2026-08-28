# Nanoda Serial Declaration Loop Configuration Witness

Mutant: `nanoda-gen-1dedcb13793f`

The mutation replaces the body of `check_all_declars_serial` at
`src/tc.rs:110` with a no-op. It therefore disables all declaration checking
when Nanoda is configured with `num_threads <= 1`, while having no effect under
the default four-thread configuration.

The original coverage-guided run selected 173 tests but reported survival
because `scripts/run-mutant-input` always used Nanoda's four-thread
`config.json`. The selected source line and the differential runtime were in
different configuration domains.

The runner now accepts `--config` and records the selected config path and
SHA-256. Reusing the independently validated malformed-let case with the
one-thread config gives:

- malformed candidate: baseline `REJECT`, mutant `ACCEPT`;
- matched valid control: baseline `ACCEPT`, mutant `ACCEPT`.

In test terms, declaration validation passes without the mutation and fails
with it. The exact malformed artifact already has official Lean, Kiota, and
Lean4Lean consensus `REJECT` evidence under the Milestone 7 let-value case, so
no duplicate expected-outcome or regression entry is needed.

This is a `MEANINGFUL_SEMANTIC` kill and a durable lesson for future campaigns:
coverage identity must include runtime configuration, and mutations in
configuration-specific branches must be replayed under a reaching config.
