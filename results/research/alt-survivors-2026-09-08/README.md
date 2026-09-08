# Reuse one let-expression regression for a pending mutant

`ALT-SURVIVORS` selects **`nanoda-gen-9face4e6a6f7`** for a fixed follow-up
proposal. The output is a planning result, not a new checker observation.
All seven pending survivors retain their original classification and remain
outside the canonical modeled population.

The selected mutation changes Nanoda's let-expression guard from
`flag == Check` to `!(flag == Check)`. The already investigated mutant
`nanoda-gen-21ef4d1d32a1` changes the same occurrence to `(flag != Check)`.
`InferFlag` derives equality in the pinned source. This relationship makes the
existing regression a strong reuse candidate, but does not supply an execution
receipt for the separately identified pending mutant.

## The fixed question and inputs

Does the existing let mismatch/control pair distinguish the exact selected
mutant from pinned Nanoda revision
`6ae1f0cd962f081f6c423454c5da729d841236a7`?

Both [candidate](../../../corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson)
and [control](../../../corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson)
are existing 601-byte artifacts. The candidate annotates a let value with
`Sort 1`, but supplies `Sort 1`, whose type is `Sort 2`. Its outer declaration
expects the substituted body's actual type, `Sort 2`. The control supplies
`Sort 0` with annotation and outer declaration type `Sort 1`. Preserve both
files exactly, including their corresponding outer-type difference.

The [prior result](../../investigations/ecosystem-closure-2026-09-05/triage/nanoda-gen-21ef4d1d32a1/result.json)
records accepted controls and rejected candidates for baseline Nanoda and
official Lean; the old `21ef` mutant accepted both. These observations remain
historical and apply to their original binaries. The selected `9face` mutant
has not been observed on this pair. Its old covering schedule matched baseline
on all 17 scheduled tests, with no difference. That result proves neither
equivalence nor adequacy of the broader corpus.

## Why this candidate

The [inventory](inventory.json) projects all seven pending identities from the
bound entry assurance snapshot and their exact mutation/comparison records.
It ranks the selected let guard first because there is already a small,
admitted regression for the same predicate inversion. The cache guard pair
needs a concrete checked/unchecked cache history. The universe boundary needs
a reachable simplified input. The free-variable guard needs an importer and
representation argument. The two thread guards concern dispatch and, for
one, a separate zero-thread configuration question. None is classified by
these planning judgments.

The intended value is one reproducible association between an existing
regression and a distinct unresolved mutation identity. It is not another
semantic boundary, a new defect, an independent transfer study, or a reason
to add a duplicate corpus file. The [reuse assessment](reuse-assessment.json)
uses the Lab's existing source-directed differential method. No new research
method or literature novelty claim is introduced.

## Proposed execution, awaiting authorization

The [execution proposal](execution-proposal.json) fixes one pair and four
primary cells: baseline control, selected-mutant control, baseline candidate,
selected-mutant candidate. Both fresh controls must accept before either
candidate. Expected candidate behavior is the baseline's let-value typecheck
refusal and selected-mutant acceptance. Source mapping, a verified single
mutation, the fixed pair, matching raw failure signatures and successful
controls are needed for attribution; a nonzero exit code alone is insufficient.

Proposed ceilings are 5400 cumulative active seconds including engineering,
two offline build reservations of at most 120 seconds, and eight checker
reservations of at most 30 seconds. Four extra cells permit counted repair
replays of the same inputs. No new export-stream variant, proof, network
request or external research action is proposed. Exactly one selected mutant
source is materialized after authorization; a repair rebuild preserves it.

The selected mutant's old binary was not retained with an attributable identity.
The original runner restored and rebuilt a shared baseline executable. A future
item must make an isolated source copy, apply the one existing mutation spec,
bind the installed toolchain and offline dependencies, reserve the build, and
bind its resulting binary before checking. It must never substitute the `21ef`
binary or modify the historical checkout. The [source lock](source-lock.json)
includes exact portable copies of the baseline Rust source and Cargo files;
the Rust source-tree digest matches the original scheduled comparison.
These unmodified copies from `ammkrn/nanoda_lib` retain its
[Apache-2.0 license](evidence/nanoda-LICENSE).

The proposal reuses tested process supervision but needs a small dedicated
runner tied to the new item. Historical ecosystem entry points remain closed
and are not launch-ready substitutes. The manifest's seven gates cover owner
authorization, committed input/configuration identities, source/build
provenance, tested tooling, product binding, cumulative accounting/cleanup and
controls before candidates. Per-input configurations use the existing file
input adapter; no checker configuration was generated here.

Successful execution could support associating the existing regression with
the selected identity through the canonical append-only classification and
admission procedure. A failed hypothesis or real blocker preserves raw evidence
and an unresolved result. Neither failure to find a difference nor source
similarity alone authorizes a classification change.

## Recommendation and handoff

Recommend the bounded **`SURVIVOR-LET-REUSE-1`** execution item next, subject to
separate owner authorization of this exact proposal and its prelaunch gates.
It is selected WAITING and unstarted; the queue is PAUSED after planning closure.
No external action is recommended: this proposal supplies no new upstream
behavior or distinct corpus contribution. Historical official observations are
reused without a new official run, current-master claim or normative promotion.

The owner supplied the missing `CVC-NEXT-AUTHORIZATION` decision by explicitly
approving this planning item. The unexecuted administrative placeholder is
preserved in the [entry queue](entry-snapshot/config/research-queue.json) and
[entry decision](entry-decision.json), not counted as another completed research
item. Earlier CVC failures, assumptions, sixteen observer reservations and
original unmet dependencies remain unchanged.

The [canonical result](result.json), [work record](work-record.json),
[evidence manifest](evidence-manifest.json), and
[closure validation](../../workflow-refresh/alt-survivors-2026-09-08/validation.json)
retain the exact scope, costs and verification. The proposal can be checked
without launching a checker:

```sh
scripts/validate-survivor-proposal
```

This command validates a non-executable proposal. It does not authorize or run
the proposed experiment.
