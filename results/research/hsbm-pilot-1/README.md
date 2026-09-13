# HSBM-PILOT-1 — fixed six-commit pilot

**NEGATIVE:** the preregistered threshold of two fresh, nonduplicate actionable
commits was not met. One useful Nat dispatcher test recommendation partly reuses
known `Nat.land` evidence and is conservatively excluded from fresh yield.
This result neither rejects history review in general nor compares its efficiency
with another method.

The population is all 36 reachable non-merge commits in exclusive
`713c245191f7afbc4e996f853ca3131b9b11ec27..4c544ed4099c8227f07d5de77ad1e69fb0740a27`.
Four in-range calibration commits are excluded; `4db8bcc` precedes the lower
bound. The 32 eligible IDs, lexical signal matches, scores, diff sizes, four
family-stratified selections and two seed-20260909 controls were frozen at
`fe61bdf` before semantic inspection. Each selected commit's first ten ancestry
path descendants were frozen at the same time. Large changes have more chances
to match lexical signals; neither signal families nor churn prove semantic risk
or test coverage.

| Selection | Source finding | Contribution decision |
| --- | --- | --- |
| `2747659` signal | Version migration has replacement inline tests; eager mode still lacks a fixed distinguishing pair | Reuse existing tests and queued cache assessment |
| `54f24a8` signal | Six native operations have helper tests but no active expression-dispatch test matrix; other boundaries are obsolete or unresolved | One preventive reuse recommendation, with prior `Nat.land` overlap |
| `73cc1b2` signal | Deleted pretty-print fixture already failed its parent's version gate; output assertion was weak | No fresh regression candidate |
| `1283899` signal | imax repair adds focused assertions; Arena `nat-rec-rules` directly covers recursor self-comparison | Reuse existing regressions |
| `0bc3631` control | Projection repair gains a named-panic test in its first descendant | Already covered |
| `2097cc6` control | Checked conversions are inlined without a changed source-level boundary | No new candidate |

The [ledger](ledger.json) records all six commits and ten boundary assessments.
Independent [review A](review-a.json), [review B](review-b.json),
[control review](review-controls.json), and [selection audit](selection-review.json)
separate input/state changes, inferred reach, assertion strength, executable
wiring, test timing and current continuity. The complete Nanoda tree has 38
statically active test attributes; this is not a new execution result.

Current source was fetched for Nanoda and Arena (Arena `512ee87`). The retained
Arena inventory includes all 231 tracked paths and 76 static test specifications.
No generated tutorial or dynamic coverage was run. The prior Nat.land source
sensitivity experiment is explicitly reused; neither broad Init acceptance nor
absence of operation-name matches alone establishes missing runtime coverage.

Seven source/setup charges include one failed DNS attempt and six successful
smart-HTTP requests (GET and POST both charged). There were **zero** research
builds, checker runs, proofs, mutants, new serialized export inputs or external
research writes. Repository Python validation is administrative. The immutable
[entry work record](work-record.json) records ACTIVE at entry; the separate
[work closure](work-closure.json) records completion and the cumulative clock.
Failure and repair notes are retained in [engineering notes](engineering-notes.json).

Next: **NANODA-NAT-DISPATCH-REGRESSION-1**, READY and unstarted. Prepare one small
six-operation dispatcher test with real literal payload assertions and a disabled
control. Reuse `Nat.land` as a known control. The [closure plan](closure-plan.md)
records its 90-minute scope, finite build/test caps and exact prelaunch gates.
No upstream submission or new research launch is part of this handoff.

Reproduce the frozen selection entirely offline:

```sh
scripts/validate-hsbm-pilot-closure --reproduce-selection
```

The retained Git bundle supplies all source objects. The validator checks the
committed freeze, selected IDs and limits, evidence hashes, request accounting,
paired clock and unstarted successor. It does not certify source interpretation
as Lean semantic authority. Closure verification is recorded under
`results/workflow-refresh/hsbm-pilot-1/`.
