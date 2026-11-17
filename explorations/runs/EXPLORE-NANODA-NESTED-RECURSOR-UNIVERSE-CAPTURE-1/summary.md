# Nanoda nested-recursor universe-capture screen

## Plain-language result

**What did we find?** Nanoda accepted the valid nested-recursor control and
rejected the candidate before it could become an admitted declaration. The
candidate deliberately leaves an undeclared universe in one recursive rule;
Nanoda reached its semantic type checker and failed the declaration's
definitional-equality comparison. The two final planned observations are
complete. This tested one constructed nested inductive against one exact Nanoda
revision; it did not test other recursor shapes, checkers, or revisions.

**Is it interesting?** No as a new defect signal, but yes as a useful boundary
result. The source-derived concern was concrete: reconstruction could align the
candidate's fresh universe while later substitution would leave it in a
recursive reduct. In this exact case, however, Nanoda's ordinary declaration
check rejects the malformed rule. Agreement with the independent Lean typing
check is not a general correctness claim; it only closes this proposed route.

**Does it require more work?** No confirmation or defect work follows from this
result. In particular, it should not be promoted to E1, packaged as a new
regression product, or reported upstream. The next queue item is a separate
project choice, not a continuation justified by this negative screen.

## Exact observation

The final revision-3 pair retained a genuinely nested `LALNest` declaration
whose owning recursor declared only universe `v`. The control rule used `v`; the
candidate rule used fresh, undeclared `u`; the observer declared no universes.
The pair differed only in the main recursor rule-root pointer. Official Lean
accepted an explicit level-1 control reduct and rejected the candidate reduct
because its level-1 motive could not serve as a motive into `Sort u`.

Nanoda commit `0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929` produced:

- control: exit 0, `ACCEPT`;
- candidate: exit 101 at `src/tc.rs:988`, where
  `assertion failed: self.def_eq(u, v)`, classified as semantic `REJECT`;
- E0 outcome: `NO_SIGNAL`, with zero signals and both planned runs complete.

The accepted control and rejected candidate were run with the same retained
binary, configuration, supervisor limits, and input transport. No supervision,
timeout, cleanup, or accounting fault remained.

## Preserved repairs and limits

The first fixture revision stopped both cases in Nanoda's parser because it
contained structurally duplicate dormant expression rows. Revision 2
canonicalized 22 duplicate expressions per input to their existing DAG
pointers, then exposed a second shared generator defect: a shifted source
universe parameter still pointed to the old name index. Revision 3 repaired
that exact `Level.param` reference, mechanically proved that declaration
universe parameters were established before use, and preserved the intended
one-pointer control/candidate difference. All six Nanoda launches, both failed
fixture revisions, preparation failures, independent-check revisions, build
attempts, raw logs, and receipts are retained.

This was a two-case exploratory screen, not a fault-rate measurement. Nanoda
was not instrumented to print its internal reduct; the reduct typing evidence
is a separate official-Lean check. The result does not establish general
soundness, a proof of `False`, or behavior in another checker.

## Research-value questions

1. **Did this add new semantic information?** Yes, narrowly: the proposed
   nested-recursor universe-capture route is blocked by Nanoda's declaration
   definitional-equality check in this exact source-derived case.
2. **Did it reveal a previously unknown defect?** No. The candidate was not
   admitted, so the screen produced no defect signal. The two repaired issues
   were local fixture-generation defects and are preserved as failed attempts.
3. **Does the result justify confirmation, packaging, or upstream action?** No.
   It supplies neither a confirmatory discrepancy nor demonstrated incremental
   consumer value.
4. **What should happen next?** Close this campaign as `NO_SIGNAL`, perform the
   one required project-wide successor selection, and leave that separate item
   unstarted.
