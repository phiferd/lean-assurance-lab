The experiment closed INCONCLUSIVE with zero execution retries. Afterwards,
selection checkpoint CI run 36640893431 failed: five historical tests require a
READY successor while the entry checkpoint was ACTIVE; the status also omitted
the exact READY-count sentence expected by one test. The completion handoff
naturally leaves a READY successor and restores that sentence. No test or gate
was changed. The attached excerpt preserves those failures; the full log remains
at https://github.com/phiferd/lean-assurance-lab/actions/runs/36640893431.
This is one administrative correction after the initial operations snapshot,
not an experimental retry or evidence that the entry-CI limitation is repaired.
The next campaign is already selected E0, so its start/results/handoff can be
recorded in one commit without pushing a transient ACTIVE checkpoint.

The first focused invocation omitted the repository's v4 queue compatibility
bootstrap, producing five schema errors. Retrying with that existing import
passed all 11 affected tests. Both logs are retained; no source repair was
needed. This is one validation-invocation retry, separate from zero scientific
retries. model-usage-delivery.json is a later cumulative snapshot of the SAME
root turn, superseding (not adding to) model-usage.json. It still excludes the
subsequent commit/push, remote CI polling and final response.
