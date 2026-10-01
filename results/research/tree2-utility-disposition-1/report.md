# Concrete downstream utility assessment

We did not demonstrate a concrete upstream use of the published Tree2 lemmas.
The actual preserved completeness branch already has general proofs of the
occurrence, substitution and restoration facts that seemed the most plausible
reusable contribution. Its remaining hypotheses are not discharged by our
specialized equations. No upstream dependency or missing-lemma status changed.

This is a useful negative assessment of target fit, not a new positivity result.
The published work remains valid specialized proof engineering; neither the
standard strict-positivity classification nor successful all-depth compilation
establishes downstream usefulness. The prior recommendation that this was enough
for a maintainer usefulness discussion was premature.

Stop this Tree2 expansion and reposition it as a checked worked example until
an independently identified consumer needs its exact interface. Do not start
another grammar, fold, consumer demonstration or reduction framework to rescue
the result. No upstream outreach is warranted. The later owner authorization covers this
truthful lab disposition, not an external contribution or new research.

## Scope and identities

This source-only assessment was preregistered in `plan.json`. At its entry the lab was at
10bcbf1d2d7c87ea603d6cca083bbcc7cc80dc4c; its worktree and all prior sources and
frozen reports were unchanged during the source assessment. At assessment entry
the sole ACTIVE queue entry was E0-TREE2-COMPUTATION-PILOT-1, with zero READY
entries. The subsequent authorized disposition closes that campaign with a
NEGATIVE usefulness outcome and restores the existing alias source-preparation
item READY and unstarted; no successor work executes in this disposition. No compiler was launched, no Lean theorem
was added, and no new build/cache or axiom claim is made.

Pinned upstream: 10fe085e21773ff0b62a6aacf6db29fccf849bae. Current master observed
through GitHub API on 2026-10-01:
a31e829790101f7c523e79b6b5ede03834b9e9f6. The root and all three modules of
`ConLeche/Complete` are byte-identical between the pinned and current snapshots.
File hashes and relevant commit API responses are retained here. Full read-only
snapshots remain in the local utility-assessment directory. Exact source links
below and `source-evidence.json` identify the inspected upstream files.

## Established target, not just comments

On pinned/current master, `ConLeche/Complete.lean:8-24` describes parked results
and forbids outside consumers. `OfficialNested.lean:320` defines positivity
acceptance, while `PosDerivComplete.lean:435` and `:618` prove success from a
native `PosDR` derivation. The comments at `OfficialNested.lean:25-31,61-66`
describe intended hypotheses, not an implemented acceptance-to-derivation
theorem. No admitted proof hole is present in these three main modules.

History led to an actual, more informative target. Current `DESIGN.md:92108`
names half(A)'s branch; `:95148-95149` explicitly records the maintainer's
decision to keep it parked. Read-only remote refs and the tag API establish that
both `agent/uinds-COMPLETE3` and `complete3-parked` point to
e7f50cd7ff68f4e444a083d7bcec8ebccbfd8a0f. This is a historical upstream WIP
target, not evidence that the maintainer currently wants new completeness work.

That preserved source has the real theorem
`ConLeche/Verify/Inductives/PosCompleteSide.lean:361`,
`nestedBlockPositivity_of_official_accepts`. Its conclusion is
`OkOr (fun _ => True) (nestedBlockPositivity ops env ctx ctorss)`, meaning
success **or decline**, not unconditional successful execution. Its premises
at `:365-382` include official positivity and typing verdicts, stream/context/
environment/fresh-name facts, `WhnfSim`, `InferSim`, `U4Typed`, `TypingContract`,
`LevelSim`, frame-constructor freshness, declaration checks, holes, and
`KeysLetProjFree`. `DESIGN.md:91433-91469` catalogs which premises were derived
and which remain named contracts or restrictions. These are actual theorem
dependencies; they are not `sorry` holes that a specialized example fills.

## Before/after dependency assessment

| Possible existing contribution | Actual upstream status before this assessment | After inspecting our lemmas |
| --- | --- | --- |
| Occurrence conversion between native and official representations | Parked `PosComplete.lean:332` `SRel.occ_of` and `:386` `SRel.of_occ` already prove both directions for the upstream relation | Unchanged. `Domain.encode_occ`, `native_occ` and `official_occ` classify only our independent grammar, fixed member and placeholders. They do not remove a missing upstream occurrence lemma. |
| Substitution compatibility | Parked `PosComplete.lean:606` `SRel.instantiate1` already proves relational compatibility for arbitrary related terms and substitutions; current master `UniformOcc.lean:38` also has general constant-occurrence preservation under fresh-variable instantiation | Unchanged. `Domain.raw_instantiate` is a specialized nondependent parameter substitution equation. |
| Restoration after abstraction | Parked `PosCompleteInit.lean:369` `rb_abs` already restores arbitrary `Good` input under `HolesOk`; `:411` `nestOcc_abs` transports occurrence to holes | Unchanged. `Domain.canonicalize` and `key_map` establish fixed syntactic equations, not the branch's stack-relative `SRel`/read-back interface. |
| Successful lowering output uniqueness | Our `Tree2EliminationDeterminism.lowering_success_unique` is genuinely generic over the main-branch elimination context | No demonstrated demand. The parked theorem already consumes `OfficialPosAcceptsAt ... st`, binding the precise final state; `PosCompleteElim.lean:870` transports invariants from that same elimination result. Removing an unused fuel ambiguity is not one of its open obligations. |
| Reduction/typing simulation | `WhnfSim` at `PosComplete.lean:201` quantifies over every frame stack, active list, depth and `SRel`-related pair; `InferSim` and typing contracts likewise cover the branch's input relation | Unchanged. Our fixed-environment Core equations concern independently enumerated fields and grammar terms. They cannot establish those universal contracts. Restricting the branch to only those terms would change its claim, not discharge the existing premise. |
| Freshness and residual keys restriction | `PosCompleteSide.lean:374-378` requires frame freshness from arbitrary `StepInv`/`ContKeyOk` inputs; `:381` requires `KeysLetProjFree` | Unchanged. Our explicit List tower has distinct keys and excludes let/projection syntax. This proves a worked subfamily, not these general premises. |

The duplicate coverage is not merely a similar comment: the parked source
contains complete proof bodies for the first three rows. We inspected their
statements and use sites but did **not** independently rebuild the historical
branch. Its old kernel/derivation APIs differ from the pinned cache, so an
unmotivated branch rebuild or mass port would add work without demonstrating
usefulness. No minimal checked application was attempted because we identified
no unresolved existing obligation that an existing lemma could satisfy.
There is another interface mismatch: parked `OfficialPosAcceptsAt` at
`OfficialNested.lean:362-366` checks every fresh-local base above its threshold;
the pinned acceptance predicate used by our published package checks a fixed
base. Moving the package to that branch would require additional work even
before the universal simulation premises could be considered.

A bounded independent source review by `/root/review_bridge` agreed with the
negative assessment and identified no contrary concrete application. Its exact
scope was source interpretation and target fit; it performed no compilation or
edits. The review is retained in `independent-review.md`.

## Concrete boundary and recommendation

`PosCompleteKeys.lean:28-44` already characterizes a substantive boundary:
the walk's key-parameter check excludes member occurrences under projections;
the branch records an official-accepted projection example and a separate let/
normalization mismatch in the simulation hypothesis. Our grammar excludes both
shapes. Additional examples within that grammar cannot settle those issues.
Those historical claims were source-inspected here, not freshly executed or
promoted to confirmed defects.

The honest result is **no demonstrated downstream use**. Preserve the existing
checked example, retire the expansion rationale, and only resume if a human or
independent source identifies a needed existing obligation with a compatible
interface. No scientific theorem failed, but the usefulness hypothesis did not
survive this bounded assessment. No external access or implementation blocker
prevents that conclusion.

## Exact upstream sources

- [Current main completeness root](https://github.com/leanprover/con-leche/blob/a31e829790101f7c523e79b6b5ede03834b9e9f6/ConLeche/Complete.lean#L8).
- [Preserved actual target and its premises](https://github.com/leanprover/con-leche/blob/e7f50cd7ff68f4e444a083d7bcec8ebccbfd8a0f/ConLeche/Verify/Inductives/PosCompleteSide.lean#L361).
- [Existing occurrence and substitution relation](https://github.com/leanprover/con-leche/blob/e7f50cd7ff68f4e444a083d7bcec8ebccbfd8a0f/ConLeche/Verify/Inductives/PosComplete.lean#L332).
- [Existing abstraction restoration](https://github.com/leanprover/con-leche/blob/e7f50cd7ff68f4e444a083d7bcec8ebccbfd8a0f/ConLeche/Verify/Inductives/PosCompleteInit.lean#L369).
- [Keys restriction and recorded boundary](https://github.com/leanprover/con-leche/blob/e7f50cd7ff68f4e444a083d7bcec8ebccbfd8a0f/ConLeche/Verify/Inductives/PosCompleteKeys.lean#L28).

This disposition changes planning and current explanatory prose only. It does
not rewrite historical E0 outcomes, reviews, proofs or closure evidence.
