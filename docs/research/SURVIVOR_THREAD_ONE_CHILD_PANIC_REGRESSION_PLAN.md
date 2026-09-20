# One-thread child-panic operational regression

Item `SURVIVOR-THREAD-ONE-CHILD-PANIC-REGRESSION-1` is a separately selected,
unstarted successor to `SURVIVOR-THREAD-ONE-DETERMINISM-1`. It may execute only
after its own fresh entry record, immutable input/build manifest and prelaunch
validator are committed. It does not reopen the historical `SURVIVED` record.

## Question

At pinned Nanoda `6ae1f0cd962f081f6c423454c5da729d841236a7`, does the exact
`REL_GT_TO_GE` mutation `nanoda-gen-2bdfe18a9ec2` change the observed failure
propagation of one existing invalid 601-byte export under public
`num_threads=1`? The original selects serial checking; the mutant selects one
scoped worker.

The only intended claim is an operational diagnostic distinction for these
inputs, builds and configuration. It is not a semantic acceptance, soundness,
current-upstream or general thread-safety claim.

## Frozen candidate shape

The successor must bind existing bytes only:

- the matching-let control
  `corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson`;
- the invalid-let candidate
  `corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson`;
- separately authored but immutable baseline and mutant configuration bytes
  that differ from the prior zero-thread candidate only at
  `num_threads: 1`;
- source trees differing only at the exact `> 1` to `>= 1` mutation.

The fixed four cells are control/baseline, control/mutant,
candidate/baseline and candidate/mutant. The controls must accept. The candidate
baseline must retain the direct type-equality assertion predicate; the candidate
mutant must retain the literal joined-worker panic predicate. Equal nonzero exit
codes alone do not satisfy the distinction.

## Entry and prelaunch gates

Before any build or process:

1. bind exact source, cargo, toolchain, input, configuration and binary paths
   by hash;
2. independently validate the one-field mutation and configuration relation;
3. bind a four-cell manifest with 30-second process timeouts, 2 GiB sampled RSS
   ceiling, raw stdout/stderr receipts and process-group cleanup; and
4. require both matching-control cells to complete with one successful ordinary
   one-worker creation before interpreting either candidate result.

A spawn failure, timeout, monitor fault, missing receipt or incomplete cleanup
is infrastructure failure. It never counts as the expected child-panic result.

## Finite bound

At most one 60-minute session, four source/setup inspections, two offline builds
of at most 600 seconds, four checker processes of at most 30 seconds and 2 GiB
sampled RSS per process. No network, proof search, production checker edit, new
export byte, new mutation identity, external action or assurance-milestone
advance. Preserve every reservation and raw receipt.

Close SUCCESS only with the full four-cell matrix and exact raw predicates; close
BOUNDED_UNRESOLVED with an evidence-bound process/control failure or if the
source-derived diagnostic relation cannot be reproduced under the fixed controls.
At closure select but do not start a successor.
