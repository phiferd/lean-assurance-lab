# Lean PR15373 preserved-alias eta pilot retry

What did we find? The retry materially narrowed the predecessor's capability uncertainty but did not produce a semantic observation. An isolated empty Docker config allowed the exact `ubuntu:24.04` `linux/amd64` image to be acquired. The checksum-pinned official archive was downloaded, verified and extracted; a no-mount amd64 probe passed; and the official x86-64 Lean runner was copied into a 4 GiB, no-mount container and invoked. The first invocation failed during fixture elaboration, before any case ran: `Kernel.Exception` lacked the expected string conversion and `meta` was reserved syntax in this runner.

A minimal repaired fixture changes only exception rendering and the two reserved local names. The expressions, raw-shape assertions, kernel-before-Meta order, four labels and expected outcomes are unchanged. The repair could not be replayed: two fresh supervised `docker cp` attempts were stopped by an `EPERM` on the supervisor's `/bin/ps` sampler, and the direct fallback received `EPERM` connecting to `/var/run/docker.sock`. Broader permissions and Docker/security-setting changes were explicitly out of scope, so execution stopped there.

Is it scientifically interesting? As a capability characterization, modestly. The retry establishes that image acquisition, exact artifact verification, amd64 emulation and actual official-runner invocation were feasible; the predecessor's elapsed-only pull cutoff was not an emulator or artifact failure. It does not answer the scientific question. Zero of four cases executed and there are no Meta or kernel Boolean observations.

Does it require more work? Not within this campaign. The repaired fixture and verified runner path are retained, but no automatic retry follows. The exact ephemeral container was last observed stopped after exit code 1; current daemon access prevented final inspection and removal. No permission request, settings change, extra image, source build, push or community communication occurred.

## Claim boundary

This E0 result is `INCONCLUSIVE`. It is not evidence for or against PR15373, preserved aliases, partial-constructor eta, `Meta.isDefEq`, `Kernel.isDefEq`, their agreement, C++ kernel correctness or a Lean regression. The only Lean output was a pre-measurement fixture compatibility failure. The independently frozen false/false and true/true oracle remains entirely unobserved.

## Retained evidence

- `attempts/docker-pull-r2/` records the successful observed public-image pull.
- `attempts/artifact-download/` and `attempts/artifact-extract-r3/` record exact official artifact acquisition and extraction.
- `attempts/amd64-no-mount-probe/` records successful amd64 emulation without a host bind mount.
- `attempts/scientific-run/` records official-runner invocation and the pre-case elaboration errors.
- `prospective-cases-r2.lean` and `fixture-repair-1.json` retain the minimal compatibility repair.
- `attempts/scientific-container-copy-fixture-r2/`, `attempts/scientific-container-copy-fixture-r3/`, `direct-docker-copy-blocker.json` and `capability-blocker.json` record the terminal capability boundary.
