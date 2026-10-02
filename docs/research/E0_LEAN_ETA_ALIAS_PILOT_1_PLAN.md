# Lean PR15373 preserved-alias eta pilot

Evidence class: E0

## Prospective question

At Lean PR #15373 head `015d54649bcaaa0861f355b59761ce308e629fbb`, does retaining reducible `FnAlias := Bool → Box` as the stored type of an unvalued local variable change the new partial-constructor eta comparison relative to the explicit `Bool → Box` type?

## Fixed sample and oracle

Use exactly four cases over the zero-parameter, nonrecursive structure `Box` with one `Bool` field. Compare explicit/alias stored local types across (1) an arbitrary unvalued function versus unapplied `Box.mk`, expected reject, and (2) `fun b => Box.mk b` versus unapplied `Box.mk`, expected accept. Record Meta and kernel results separately.

Independent review froze the semantic oracle before execution. The negative is justified because `fun _ => Box.mk false` differs from `Box.mk` at `true`. The raw fixture must retain `.const FnAlias []`, an unvalued `cdecl`, zero term arguments on `Box.mk`, and distinct nonlambda negative heads. The positive alias case is only an acceptance control because its lambda infers a syntactic Pi.

## Runner and controls

Use only the official PR toolchain `lean-4.36.0-pre-linux.tar.zst`, 759,812,626 bytes, SHA-256 `73cbeca7d35f92bf4e67c36ca4f15fe37d8b3bc8e3ec58b560c13f905185e17d`. Run it through the already-installed Docker Desktop VM as `linux/amd64`, with a 4 GiB container limit and the existing host supervisor. Preserve download, extraction, runner identity, stdout/stderr, timeout, sampled host process data, container cleanup and exact fixture bytes.

Signal is any observed result different from the frozen oracle. If alias-negative unexpectedly accepts, first independently confirm the raw local declaration, term shapes, exact binary provenance and repeatability; classify only as an E0 candidate signal. Do not claim a defect from source prediction or one unvalidated output.

Stop after the four cases and necessary same-fixture confirmation. Stop on unavailable emulation, artifact/digest mismatch, shape erasure, incomplete cleanup or exact runner failure. Do not install build software, build Lean from source, expand the eta matrix, alter security settings, contact upstream, or change PR #41.
