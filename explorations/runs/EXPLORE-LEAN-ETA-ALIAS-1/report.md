# Lean PR15373 preserved-alias eta pilot

What did we find? The approved exact-runner route did not reach the scientific fixture. Docker Desktop started successfully and exposed a Linux/aarch64 daemon, but the one permitted `linux/amd64` `ubuntu:24.04` pull produced no stdout or stderr for 900.10 seconds. The existing supervisor stopped it, reaped it and reported complete cleanup. No base image, official PR15373 toolchain, scientific container or case output was produced.

Is it scientifically interesting? Only as a precise capability boundary. All four semantic cells remain unobserved, so this run says nothing about preserved aliases, partial-constructor eta, `Meta.isDefEq` or `Kernel.isDefEq`. In particular, zero signals here must not be reported as agreement with the frozen false/false and true/true oracle.

Does it require more work? Not within this campaign. The preregistered stop rule forbids switching to a source build or alternate infrastructure after emulator/artifact-route failure. The fixture and independent expected-outcome review remain useful frozen inputs for a separately authorized exact-runner route, but no retry is selected here.

## Retained evidence

The supervised pull receipt contains 871 samples, a 93,093,888-byte maximum sampled host-process-group RSS, a 1.083-second maximum trace gap, one `OBSERVED_TIME_LIMIT` stop, one successful process-group `SIGKILL`, and no monitor, pipe or cleanup errors. Both raw streams are empty and hash to the SHA-256 of an empty file. A post-attempt inspection found no `ubuntu:24.04` image and no scientific container.

An initial wrapper invocation was rejected before launch because the supervisor requires an absolute executable path. It created no attempt directory and performed no pull. The retained attempt corrected only that controller input by using `/usr/local/bin/docker`; the frozen scientific fixture and protocol did not change.

## Claim boundary

This is E0 `INCONCLUSIVE`. It is not evidence for or against the PR, a Lean defect, a regression candidate, kernel/Meta agreement, Docker emulation correctness or exact runner behavior. The cause of the silent registry stall is not identified. No source build, package installation, Docker/security-setting change, upstream message, PR #41 change or non-lab repository write occurred.
