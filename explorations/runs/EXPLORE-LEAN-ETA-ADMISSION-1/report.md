# PR15373 checked declaration admission screen

**What did we find?** The exact official Linux artifact for Lean PR15373 accepted the fixed invalid theorem when its function domain remained the reducible constant `FnAlias`. A separately launched, syntactically explicit `Bool → Box` control rejected. Both processes used trust level zero. The accepted declaration claimed `forall f : FnAlias, f = Box.mk` while its supplied value proved only `forall f : FnAlias, f = f`.

**Is it interesting?** Yes. The previously reproduced `Kernel.isDefEq` API disagreement reaches checked `Kernel.Environment.addDeclCore` admission in this one minimal encoding. The raw expression log confirms that the accepted cell retained `FnAlias` as a constant, while the rejected control stored the explicit function type. This is an E0 signal at one exact PR artifact, not a general Lean or current-main claim.

**Does it require more work?** Yes, if the owner wants a stronger claim. The appropriate next step is a separately planned E1 confirmation with independent review and fresh execution. No broader exploit, derivation of `False`, current-main comparison, parent build, or upstream contact follows automatically. The deferred memory audit remains deferred.

The artifact identifies itself as Lean `4.36.0-pre`, commit `015d54649bcaaa0861f355b59761ce308e629fbb`. The official archive was 759,812,626 bytes with SHA-256 `73cbeca7d35f92bf4e67c36ca4f15fe37d8b3bc8e3ec58b560c13f905185e17d`; the extracted `lean` binary SHA-256 was `db7f559d05795e7af52e42bc966c90240a39dcb9712161c54c97afa546e20c00`.

Each final cell ran in a separate fresh Lean process with `-t 0`. The harness asserted closed expressions, no metavariables, the expected forall/lambda structure, the stored alias or explicit domain shape, and successful standalone `Kernel.check` of both the declaration type and supplied value. It used checked `addDeclCore` with its default `doCheck := true`; it used no `sorry`, new axiom, unchecked insertion, or `skipKernelTC`.

The initial harness repairs remain retained. Two calls failed before execution because of monad-plumbing mistakes. A third stopped before any cell because the command's default maximum trust level violated the trust-zero assertion. A fourth imported two fresh environments in one process and was killed after crossing the 4 GiB supervisor ceiling. The final repair used the documented `-t 0` option and one cell per fresh process, preserving the declarations and expectations. Both final processes exited zero with complete cleanup and no supervision or accounting fault.

The authoritative structured result is [`result.json`](result.json). Raw stdout, stderr, input hashes and supervisor receipts for every attempt are under [`attempts/`](attempts/).
