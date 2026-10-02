# PR15373 alias pilot capability decision — 2026-10-02

## Prospective question and scope

At Lean PR #15373 head `015d54649bcaaa0861f355b59761ce308e629fbb`, does a reducible function-type alias retained as the stored type of an unvalued local variable change the new partial-constructor eta result? The bounded matrix is exactly four cases: explicit/alias stored type crossed with an arbitrary-function negative and constructor-eta positive. Meta and kernel observations are separate.

Success for a future E0 launch means all four exact cases execute on that pinned runner with raw output retained and fixture assertions confirming the alias/local/constructor shape. A candidate signal is any result differing from the independently frozen expectations: both negatives reject and both positives accept. Stop on shape erasure, duplicate coverage, inability to run the exact pin, or a request to broaden beyond these four cases.

## Live source and duplicate preflight

- PR #15373 remains an open draft at the exact pin. Its body still asks for better tests.
- Its only added test, `tests/elab/12520_1.lean`, exercises positive partial-constructor eta for `True → T`; it does not store a reducible function alias on an arbitrary unvalued function.
- The PR has no review threads. Bounded GitHub searches for `FnAlias`, partial-constructor aliases, and the `Bool → Box` shape found no exact duplicate.
- Issue #12520 and renovation #14977 cover the broad eta family, so no broad novelty claim is available.
- Independent expected-outcome review passed the four semantic expectations but requires raw fixture inspection before interpreting any run.

## Exact-runner inventory

The PR CI publishes only `lean-4.36.0-pre-linux.tar.zst`, 759,812,626 bytes, with release digest `sha256:73cbeca7d35f92bf4e67c36ca4f15fe37d8b3bc8e3ec58b560c13f905185e17d`. There is no macOS artifact. The CI artifact is 758,996,810 bytes. The Mac is arm64 and has released Lean toolchains through 4.33.1, but not the PR toolchain.

Native prerequisites currently present: Apple clang, GNU make, Rust 1.98, 380 GiB free disk. CMake and Ninja are absent. A native exact-source build therefore requires at least a new CMake installation and a separately recorded build plan; the owner's willingness to wait for a healthy build removes elapsed time as a reason to reject it, but does not silently authorize software installation.

Docker Desktop is already installed (1.5 GiB), but its daemon is stopped. The smallest exact-runner route is therefore prospective only: start the existing Docker Desktop VM, download the official 759.8 MB PR toolchain, and run it in a bounded `linux/amd64` container. This introduces virtualization/platform-emulation work and a large download, so it must be reported and explicitly approved before use. If that route is declined, the alternative is approval to install CMake and perform an isolated native build at the pinned source.

Proposed bounded resource plan if approved: reserve 4 GiB of workspace for the verified archive and expansion; use one existing Docker Desktop VM and at most one small Linux base-image pull if none is cached; run one four-case Lean process under the lab's existing process supervisor with an explicit timeout, memory observation and cleanup; preserve stdout/stderr and exact identities; then stop. Do not build Lean from source, install packages, broaden the matrix, or contact upstream on this route. If `linux/amd64` emulation is unavailable or the exact archive fails to execute, retain the failure and stop rather than changing platform infrastructure.

No checker was launched, no toolchain artifact downloaded, no software installed, and no Docker daemon started in this preparation step.

## Fixture and interpretation controls

`prospective-cases.lean` constructs the alias as the raw expression `.const FnAlias []`, creates each context entry as an unvalued `cdecl`, and keeps `Box.mk` at zero term arguments. The negative heads are a free variable and a constructor constant, both non-lambdas. Kernel observation is taken before Meta observation in each fresh local context. The positive alias case is only an acceptance/control route: its compared lambda infers a syntactic Pi and does not prove that the alias-sensitive kernel branch was exercised.

An unexpected alias-negative acceptance would be an E0 candidate signal only. It would require fresh independent fixture/type validation before any defect claim, confirmation, or upstream communication.
