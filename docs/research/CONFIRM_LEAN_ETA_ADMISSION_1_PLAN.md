# Confirm PR15373 checked declaration admission

**What did we find?** E0 observed that the exact official PR15373 Linux artifact accepted one closed invalid theorem through checked `Kernel.Environment.addDeclCore` when its function domain remained the reducible constant `FnAlias`; a separately launched explicit `Bool → Box` control rejected. **Is it interesting?** Yes: this is a direct declaration-admission signal at one unmerged PR artifact. **Does it require more work?** Yes. Confirmation must independently review the oracle and fixture, repeat the exact head observations, and execute the same pair against the exact parent revision before making a PR-causation or report-ready claim.

Evidence class: E1. This is a bounded confirmation plan, not an E2 assurance result, disclosure report, current-release claim or authorization for upstream communication.

## Question and fixed scope

At Lean PR #15373 head `015d54649bcaaa0861f355b59761ce308e629fbb`, does checked trust-level-zero declaration admission reproducibly accept the closed theorem

```text
forall f : FnAlias, f = Box.mk
```

with supplied value `fun f : FnAlias => Eq.refl f`, while rejecting the identical declaration with `FnAlias` replaced syntactically by `Bool → Box`? Does the exact parent revision `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` reject both cells?

The sample is exactly four fresh-process cells: alias and explicit negatives at the PR head, followed by the same alias and explicit negatives at the exact parent. Every process uses trust level zero and checked `addDeclCore` with default `doCheck := true`. Inspect and retain raw declaration types and values before admission. Require closed expressions, no metavariables, no `sorry`, no added axioms, no unchecked insertion and no `skipKernelTC`.

Do not derive `False`, construct a broader exploit, add aliases or structures, expand across releases or current `master`, contact upstream, or test a public target. A later fix validation is a separate phase after a confirmed result and a frozen proposed patch.

## Evidence and source identities

- E0 result: `explorations/runs/EXPLORE-LEAN-ETA-ADMISSION-1/result.json`.
- E0 fixture and raw outputs remain discovery evidence only; confirmation executes fresh processes and writes fresh receipts.
- PR head official archive: 759,812,626 bytes, SHA-256 `73cbeca7d35f92bf4e67c36ca4f15fe37d8b3bc8e3ec58b560c13f905185e17d`.
- PR head source revision: `015d54649bcaaa0861f355b59761ce308e629fbb`.
- Exact parent source revision: `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3`.
- Read-only upstream state and source hashes: `results/research/lean-eta-admission-confirmation-1/source-history-preflight.json`.

The parent executable must be built from the exact parent revision or acquired from an official artifact whose content identity is independently verified. Do not substitute a release, current `master`, the PR base SHA or another CI artifact. Freeze the complete parent source inventory, build command, compiler/tool identities, produced executable and relevant shared-library hashes before a scientific cell.

## Entry and launch gates

1. A Daybreak Blue reviewer independently reads this plan, the exact head and parent source, the proposed fresh fixture and the E0 raw outputs. The reviewer must assess the semantic oracle, raw-expression invariants, source-path explanation, expected four-cell matrix, supervision and reporting limits. No other model substitutes for this gate without a new owner decision.
2. Freeze a fresh confirmation fixture and expected-result record after that review. Repairs require another Daybreak Blue review before launch.
3. Acquire or build the exact parent runner and verify both head and parent runtime revision identities. Record all archive/source/build inputs and output hashes.
4. Commit the plan, independent review, fixture, expected matrix, runner identities, supervisor and launch manifest before executing a scientific cell. Validate an immutable input snapshot under the completed snapshot/reuse closure controls.
5. Use the existing process supervisor with per-process memory, output, trace-gap and cleanup controls. Preserve every launch, including build and fixture failures. Pause on monitoring, accounting or cleanup faults; repair within this item without changing the four-cell question.

Daybreak Blue is not exposed as a subagent model in the current cloud workspace as of 2026-10-02. The item therefore remains `PLANNED`; no confirmation cell or parent build may start here.

## Outcome rules

- `CONFIRMED_PR_HEAD_ADMISSION_REGRESSION`: head accepts only the alias negative, parent rejects both negatives, all identities and fixture invariants pass.
- `CONFIRMED_HEAD_ONLY_WITH_CAUSATION_UNRESOLVED`: head accepts only the alias negative, but a valid parent observation is unavailable or the parent also accepts it. Report the exact boundary without calling the PR causal.
- `NOT_REPRODUCED`: both valid head cells reject under the frozen fixture and verified runner.
- `INVALID`: explicit negative accepts, alias shape is lost, any trust/checking invariant fails, or the fixed sample changes.
- `BLOCKED`: required Daybreak Blue review, exact parent runner, immutable launch inputs or safe supervision remains unavailable after feasible preparation.

## Reporting gate

A maintainer-ready package requires a confirmed bounded outcome, exact source references, a clean portable reproducer, explicit affected-version limits, a tested negative control and a proposed regression test. Exactly one Daybreak Blue drafting agent must prepare the disclosure draft; the main owner then checks every claim against the retained source and execution records. Do not include author-machine paths, internal queue language or unneeded raw receipts. Do not assign CVSS, claim released versions, exploitability or a derivation of `False` without separate evidence.

Any upstream comment, private message, issue, advisory or pull request still requires explicit human approval for its exact text and target.
