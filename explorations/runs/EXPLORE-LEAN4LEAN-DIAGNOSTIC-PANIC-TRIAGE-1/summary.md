# Source-only diagnostic triage

What did we find? All three retained malformed targets were rejected, with environment-extension panics during expression formatting and a raw-printer fallback. The binary still matches its original SHA-256. A clean candidate source checkout provides a concrete exception-environment seam, but the original protocol does not bind that source to the executable. Is it interesting? Yes, as a small diagnostic regression target; this is not an invalid-proof acceptance or confirmed current-upstream defect. Does it require more work? Recover an exact build/source binding or use a separate fresh confirmation with a bound build before attributing the observed panic to this source route. No executable was invoked in this screen.

Outcome: E0 INCONCLUSIVE about exact causal provenance. One source route inspected; zero builds, zero checker launches.

## Bound source map

The retained candidate checkout is clean at ecb3b6661c14f8147be1069b126c629114baf4a8. Source copies and original paths/hashes are in source-inventory.json. Its toolchain is v4.33.0-rc2. Lake traces retain old LeanVerifier build paths and a Lean compiler revision, but do not provide the protocol's binary SHA-256-to-source SHA-256 binding. They are supporting provenance candidates, not an attestation.

* Main.lean: the --import route parses the exported stream and calls Replay.replay with Lean4Lean's empty environment. It bypasses the normal module-import path.
* Replay.lean, addDecl: a Lean4Lean rejection calls throwKernelException.
* Replay.lean, throwKernelException: the comment explicitly warns that the replay environment lacks extension state. It creates mkEmptyEnvironment and maps exception environments before invoking Lean.throwKernelException through CoreM.
* Replay.lean, Exception.mapEnvM: most environment-bearing cases apply f. The declTypeMismatch case returns .declTypeMismatch env d t unchanged. Therefore this candidate source does not perform its intended environment replacement for the exception in the retained diagnostics.
* Original stacks: MessageData.ofExpr / formatAux / toString and ppExprWithInfos reach EnvExtension.getStateImpl from Replay.throwKernelException. The final messages report declaration type mismatch at d01, d06 and d12, include the raw fallback, and exit 1. Baseline accepts with no such formatting panic.

These source and stack facts are consistent with a useful regression hypothesis, not proof of the binary's causal implementation. The exact-source requirement is not satisfied by a nearby clean checkout alone.

## Smallest separate confirmation target

Use one malformed theorem value (d01 fixture) and its valid baseline. Bind exact adapter source, dirty patch if any, compiler, dependencies and resulting binary hash before fresh supervised execution. Require both an expected semantic rejection and a usable diagnostic with no invalid-extension panic; baseline must accept. A focused unit regression for Exception.mapEnvM can additionally assert that declTypeMismatch receives the replacement environment, with an environment-bearing sibling as control. Keep formatting success separate from kernel rejection. No patch, build, launch or upstream communication has been performed or authorized by this E0 record. Recovering provenance is a prerequisite to a causal historical claim; a fresh build can instead test this separately as a new hypothesis.
