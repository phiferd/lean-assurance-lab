# Zero-thread declaration-checking regression

Frontier `F-SURVIVOR-THREAD-CONFIG-REGRESSION`; bounded item
`SURVIVOR-THREAD-CONFIG-REGRESSION-1`. This successor may start only after
`SURVIVOR-THREAD-CONFIG-REACHABILITY-1` closes and a project-wide review selects
it.

## Question and useful result

Turn the source-proved public `num_threads = 0` check-elision distinction for
`nanoda-gen-93b21593b0d8` into a reproducible fixed regression without creating
new export bytes. Reuse the exact admitted 21ef invalid candidate and matching
control, freeze zero-thread configuration bytes, pinned baseline and mutant
source/runtime identities, expected candidate/control outcomes and strict raw
receipts before launch. A useful result is a controlled baseline/mutant
difference, a falsification of the source-derived expectation, or a bounded
engineering failure that preserves all attempts.

The item does not attempt to close `nanoda-gen-2bdfe18a9ec2`; its one-thread
stack, spawn and panic boundary remains separate.

## Finite gate and stop

Before any build or checker launch, implement and inert-test a narrow runner,
bind the existing 601-byte candidate and control, exact zero-thread configs,
mutation identity, pinned source, toolchain and expected outcomes, and commit
the execution checkpoint. Reuse an existing exact binary only if its identity
is fully bound; otherwise permit at most two offline builds, 180 seconds each.
Then run controls before candidates with at most four checker launches, 30
seconds each. Total active work is at most 7,200 seconds across two sessions.
Run zero network, Lean proof, new-export-byte, mutation-identity or external
action launches. Stop on the first control mismatch, identity/accounting fault,
unreconciled process failure, completed fixed pair or cumulative cap.
