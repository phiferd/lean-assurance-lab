# Automated Campaigns

`scripts/run-campaign` supervises one already-generated mutation batch. It is
an execution mechanism, not a witness generator and not an external-action
mechanism. It records its state in `results/campaigns/<campaign-id>.json` and
can be resumed after interruption.

Start a bounded campaign after generating a batch:

```sh
scripts/run-campaign nanoda-reduction-0001 --batch-id nanoda-reduction-0001
```

Resume it after an interruption:

```sh
scripts/run-campaign nanoda-reduction-0001 --batch-id nanoda-reduction-0001 --resume
```

Use `--through execution` when an assurance snapshot should be generated in a
separate review commit. `--phase-timeout SECONDS` bounds a whole phase; zero
is the default and means that the supervisor does not impose an additional
deadline.

The campaign binds the selected mutant identities, checker source digest,
mutation-model digest, and coverage-manifest digest. Mutable build and
execution evidence does not invalidate a resume. A changed selection does:
create a new campaign instead of silently mixing evidence.

`scripts/validate-mutation-batch --resume` now persists every completed build
result. `scripts/run-mutation-batch --resume` already persists every completed
mutant execution. A machine can therefore perform build validation, scheduled
execution, and assurance refresh unattended. Human review remains required for
witness design, semantic classification, and every external publication.
