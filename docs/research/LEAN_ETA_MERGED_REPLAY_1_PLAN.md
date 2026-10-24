# Replay the original Lean admission witness after merge

**What did we find?** Lean merged the partial-constructor repair after the Lab's
report, but the Lab has not replayed its original invalid declaration on that
merged revision. **Is it interesting?** Yes: this is an open verification gap
for a demonstrated incorrect acceptance. **Does it require more work?** Run the
preserved witness and controls once under a separately bound replay protocol.

Evidence class: E1. Selected READY for preparation on 2026-10-24; unstarted.
This is known-case repair verification, not discovery, an independent holdout,
or a new assurance milestone.

## Fixed question and scope

Does checked, trust-zero declaration admission reject the original alias-domain
invalid theorem on merge commit `7632b2cf35e51ec5d92d9cdd86296a8481dcb01e`,
while rejecting its explicit-domain negative control and preserving valid
partial-constructor eta behavior? The final PR head is
`e5aed18a894735d1e20bd96048a308eae3dc1840`; it is not the merge commit.

Reuse the unchanged raw alias/explicit pair from
`results/research/lean-eta-admission-confirmation-1/` and its reviewed semantic
expectations. Select only the two existing valid constructor controls from
`explorations/runs/EXPLORE-LEAN-ETA-ALIAS-RETRY-1/` before launch. Preserve their
API-level scope; do not call a definitional-equality check declaration admission.
Bind the exact four cases and each expected observation in a fresh protocol.
No new alias family, broader version sweep, False derivation or exploit work.

## Entry and launch gates

1. Verify the preserved fixture/review hashes and bind the exact merged source,
   build recipe or exact official artifact, toolchain and runtime/library hashes.
   A matched source build is allowed if no exact official artifact is available;
   no substitution of moving main or a release. Reuse existing tooling/cache
   only after identity checks. Do not rebuild historical head/parent controls
   merely to repeat their already recorded result.
2. Record the narrow source change and reuse the passed original oracle review.
   Independently review any changed semantic fixture, expectation or adapter
   before launch; no review may change the frozen historical experiment.
3. Commit fresh immutable inputs and a separate manifest. Keep raw alias shape,
   closed expressions, no extra axioms/sorry/metavariables, explicit doCheck=true,
   trust level zero and stored-declaration verification on unexpected acceptance.
   Classify exact kernel exceptions; crashes or failed builds are not rejections.
4. Use the retained supervised runner with timeout, memory and cleanup controls.
   Preserve all failed attempts. Repair ordinary engineering failures within this
   item with a new tooling revision; counters do not terminate the work.

Deliver raw fresh observations, exact source/runtime identity, a bounded
confirmed/not-confirmed/inconclusive repair result and a dated reader companion
to the original report. Update contribution tracking without rewriting the old
result. Run affected tooling tests and applicable E1 current/historical closure
checks once at logical closure; introduce no framework or unrelated assurance
change. A merge or upstream CI pass alone cannot satisfy this question.

Finish this item, reassess the queued historical recursor audit and stop before
starting its successor. No upstream message, issue, PR or other external change
is authorized. The original experiment's model-specific review conditions
remain attached to that historical experiment; this successor reuses its passed
oracle evidence and does not reopen it.
