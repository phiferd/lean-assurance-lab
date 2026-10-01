# Independent source utility review

Reviewer: `/root/review_bridge`, bounded source-only review, 2026-10-01.

Confirmed the negative utility assessment: no concrete application found that
discharges a remaining universal parked-completeness premise.

- General occurrence correspondence is already proved by `SRel.occ_of`/
  `of_occ` (`PosComplete.lean:332,386`); substitution by
  `SRel.instantiate1:606`; abstraction restoration by `rb_abs` and
  `nestOcc_abs` (`PosCompleteInit.lean:369,411`). Our grammar equations
  specialize these mechanisms to a restricted schema.
- `domain_conversion` proves typing for one encoded domain family. It does
  not supply `WhnfSim` (`PosComplete.lean:201`), universal `InferSim`/
  `U4Typed` (`PosCompleteRun.lean:874,891`), oracle `TypingContract`/
  `LevelSim` (`PosCompleteSide.lean:47,58`), or general `FrameFresh`
  (`PosCompleteSteps.lean:460`).
- The assembly explicitly retains those premises at
  `PosCompleteSide.lean:365-388`. `KeysLetProjFree` is a deliberate
  restriction, not derivable from acceptance (`PosCompleteKeys.lean:28-44`).
- Lowering uniqueness has no missing-output identification job:
  `OfficialPosAcceptsAt` already fixes `st` (`OfficialNested.lean:362`).
  Parked acceptance quantifies over every fresh-local base; our published
  package uses pinned fixed-base acceptance.

`DESIGN.md:91433-91469` confirms these are remaining named obligations.
Recommend stop expansion and reposition the existing results as restricted
model case studies, not demonstrated progress discharging the parked universal
theorem. No edits, compilation, or external actions performed by the reviewer.
