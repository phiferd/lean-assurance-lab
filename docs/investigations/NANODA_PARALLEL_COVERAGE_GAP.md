# Nanoda Parallel Coverage Gap

## Finding

The mutation-surface audit reported six semantically eligible candidates with
no covering tests. Five were in `strong_reduce`, an explicitly dead,
debug/introspection entry point. The sixth removed `check_declar` from
`check_all_declars_par`.

The missing parallel-path coverage was caused by a configuration mismatch:
coverage was collected with `num_threads: 1`, while mutation execution uses the
Arena checker configuration with `num_threads: 4`. Serial coverage therefore
could not select any input for a mutation that only affects the parallel worker.

## Reproduction

The deterministic `SKIP_VALIDATION` mutant `nanoda-gen-4c6d80f39770` changes
the worker call to an unreachable validation call. On the exact
`tutorial/012_nonPropThm` artifact, baseline Nanoda rejects and the mutant
accepts. The standard scheduler's new full-corpus fallback independently kills
the same mutant on `tutorial/052_indNeg` after 10 executions.

## Process Change

Modeled candidates are no longer discarded merely because line coverage
selects zero tests. The generator prices them as full-corpus runs and the
scheduler selects every baseline input. This is conservative: missing coverage
can increase execution cost, but it cannot silently create an input-free
survivor.

`strong_reduce` is now excluded from the modeled semantic function policy. This
is based on its explicit `#[allow(dead_code)]` annotation and source comment,
not on whether the current corpus happened to cover it.

The historical audit and batch manifests remain unchanged. The machine-readable
resolution is `results/investigations/nanoda-uncovered-mutation-sites.json`.
