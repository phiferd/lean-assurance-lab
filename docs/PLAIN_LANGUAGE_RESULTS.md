# Plain-language research results

This standard applies to new human-facing research reports, status summaries,
handoffs, and final responses. Lead with the answer a project owner needs;
put reproducibility detail after it.

## Required opening

Use three short prompts, with direct answers:

1. **What did we find?** Say what happened, to how many cases, and what was not
   observed. If the work is unfinished, say what is known *so far*.
2. **Is it interesting?** Say whether the result found a new problem, confirmed
   a useful behavior, produced a reusable tool or test, ruled out an idea, or
   remained inconclusive. Give the reason in ordinary words. Do not call every
   successful run a discovery.
3. **Does it require more work?** State the action and why, or say "No follow-up
   is warranted from this result." Separate local work, an upstream proposal,
   and the next independent queue item. Name a blocker and what would remove it
   when an answer is still pending.

After this opening, include the exact versions, controls, evidence, limits,
failures, and machine-readable references needed for reproduction. The opening
must agree with those artifacts. A plain explanation never licenses a broader
claim than the evidence supports.

Use familiar words first. Explain a necessary term once; avoid unexplained
acronyms, internal item IDs, outcome codes, and phrases such as "bound profile,"
"matrix cell," or "closure receipt" in the opening. If a result is negative or
ordinary, say so. If only some cases ran, separate those results from cases
that were too large, unsupported, or unavailable. Never turn a test pass into
a proof of correctness.

## Example from the real-proof-slices pilot

**What did we find?** We selected twelve declarations from three existing Lean
libraries. Nine produced test cases within the size limit, and both Lean and
Nanoda accepted all nine. The other three were too large to run.

**Is it interesting?** We found no checker disagreement. The useful result is
a repeatable way to extract smaller test cases from large libraries. These
observations do not show that either checker is correct in general.

**Does it require more work?** No issue or upstream contribution follows from
these cases. Keep the extraction tool and nine accepted cases as local checks.
The next binder-model study asks a separate question; it was not triggered by
a failure in this pilot.

The [original technical report](../results/research/real-proof-slices-pilot-1/report.md)
and its bound evidence remain the source for exact claims.

## Review before delivery

Read the opening without the technical sections. A reader should be able to
repeat the finding, why it matters, and the next action without decoding an
artifact name or status code. Then check each sentence against the canonical
result and limits. Revise the prose if either check fails.

This is a prospective writing rule. Do not edit frozen or historically bound
reports merely to add the new opening; use a dated reader companion instead.
