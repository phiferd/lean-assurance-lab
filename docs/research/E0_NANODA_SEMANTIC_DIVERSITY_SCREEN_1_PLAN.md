# Screen for fresh Nanoda semantic-mutation diversity

Status: READY and unstarted after closure-reliability completion.

Evidence class: E0

**What did we find?** Prior mutation batches spread tests across semantic
subsystems, but the repository has not asked whether the current pinned source,
coverage map, mutation catalog and append-only registry still contain a small
fresh diversity-balanced sample. This plan records that question; it does not
answer it.
**Is it interesting?** Potentially. A cheap inventory screen can show whether a
new confirmation campaign has concrete source targets before paying for mutant
builds and checker runs. Source candidates alone are not defects or behavioral
evidence.
**Does it require more work?** Run the single E0 inventory trial below. If it
finds the preregistered signal, prepare a separate confirmation proposal; do not
build mutants or reuse the E0 output as confirmation.

## Fixed campaign scope

Run one read-only trial against pinned Nanoda
`6ae1f0cd962f081f6c423454c5da729d841236a7`, the repository's current mutation
catalog, retained coverage map, baseline timing data and append-only mutation
registry. Before executing, append the E0 start record with exact hashes for
those inputs, `scripts/generate-mutations`, the Rust mutator and its toolchain.

Invoke the existing generator without `--write` or `--register`, selecting at
most six candidates with `semantic-diversity-v1`. Preserve stdout, stderr, exit,
elapsed time and cleanup status under the exploration run directory. The signal
criterion is a complete six-candidate selection spanning at least three modeled
semantic subsystems and three source functions, with every identity absent from
the retained controlled/generated mutation set. A complete valid selection that
does not meet that criterion is `NO_SIGNAL`; missing inputs, tool failure,
accounting failure or incomplete selection is `INCONCLUSIVE` after feasible
same-trial repair.

The only permitted observation is the generated candidate inventory and its
mechanical diversity/identity counts. Do not apply a patch, compile a mutant,
launch a checker, alter the canonical mutation registry/batches, refresh coverage,
contact upstream or make a conformance/correctness claim. Use the E0 ledger and
lightweight checks in `docs/EXPLORATORY_EXPERIMENT_PROTOCOL.md`. A signal may
justify a new `CONFIRM-*` proposal with fresh execution and independent gates;
it does not promote this campaign's bytes.

## Why this precedes the memory audit

This trial reuses an existing deterministic selection path and can cheaply
decide whether fresh semantic confirmation has concrete targets. The deferred
short-process memory audit remains valuable and fully scoped, but it interprets
an older finite result and cannot produce a new semantic test target. Reassess
the audit at this one-trial campaign handoff.
