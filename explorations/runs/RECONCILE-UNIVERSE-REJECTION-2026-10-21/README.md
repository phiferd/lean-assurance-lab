# Concurrent completion reconciliation

The published rejection screen at `1c5ae22492bc3e7345c027372094d09a6a649103`
already completed the requested three-pair item. Its canonical result is six
accepts and six expected rejections. A local run, prepared from stale
`061ffa69` state before fetching, independently repeated the same selected item
and also obtained six accepts and six expected rejections. It is a duplicate
reproduction, not an independent holdout or confirmation.

The first local push was rejected because `main` had advanced. Preserve both
commits without rewriting history: local commit
`03e56c5a5618a840ecc05fbe2a05ffdc72fe136c` and the published `1c5ae224` are
merge parents. The published canonical ledger, scientific artifacts, planning
and successor selection are adopted unchanged. The local run reused the same
trial ID and paths, so its duplicate ledger rows must not be appended to the
canonical ledger or mixed with the published run's measurements.

`local-03e56c5a.tar.gz` retains the complete local run plus its local ledger and
planning proposal at their original paths under a `local-03e56c5a/` prefix.
All 87 archived files were compared byte-for-byte against the preserved local
commit. Archive SHA-256: `d34218b8b6d76235cdedff5a3e5ae9e434fe5cacd903a23cad002276c7d35744`.
The local start/finish references bind that local commit's namespace, not the
published artifact files occupying similarly named paths. Inspect or reproduce
it from that exact commit/archive; do not run its analyzer against the merged
canonical directory. No prior experiment's bytes or results were regenerated.

The archived local run took twelve checker calls (10.053 seconds total) and
six supervised preparation/matrix/cleanup attempts (15.219 seconds total),
including one repaired stopped-daemon failure. Those costs are additional to
the published run, not substituted for its accounting. Task-level token/cost
accounting is unavailable. The raw evidence and local source-only reuse proposal
remain archived; the proposal is not activated by this reconciliation.

No successor work starts. The published queue retains
`TRANSFER-HOLDOUT-INTAKE-1` WAITING and its explicit blocked handoff. Its missing
independent input/custody package and separate intake authorization remain the
unblocking requirements. No external contribution or new scientific trial is
created by this repair.
