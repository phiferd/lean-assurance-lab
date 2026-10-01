When setup is needed, the guard checks one policy pathname while the writer uses another. The original branch overwrites an existing destination-file fixture in the synthetic model; the patch refuses it and preserves its bytes. This is worth fixing to honor the existing-policy refusal. Check both policy filenames before writing.

Private standalone review draft for [lean-action PR191](https://github.com/leanprover/lean-action/pull/191), head `686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345` (stacked on PR190). Not sent; publication requires separate approval and applicable E2 gates.

Suggested review text:

> Could the existing-policy guard also check `/etc/apparmor.d/lean-action-bwrap`? [Lines153–156 guard `/etc/apparmor.d/bwrap`](https://github.com/leanprover/lean-action/blob/686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345/scripts/run_lake_check.sh#L153-L156), whereas [lines158–171 write/load `/etc/apparmor.d/lean-action-bwrap`](https://github.com/leanprover/lean-action/blob/686ffeb3765c6bf5edfb3193ac5cb6a46d2ac345/scripts/run_lake_check.sh#L158-L171). If the initial probe fails and only the latter file exists, the current guard does not refuse the write. The attached minimal patch checks both filenames and names the existing file in the diagnostic, preserving the current conventional-profile refusal.

Minimal expected tests, with synthetic filesystem/command fixtures: absent policies permit one writer/loader call; either existing filename or both refuse with exit2 and no writer/loader calls; existing destination bytes remain unchanged. When the initial probe succeeds, both versions must skip setup regardless of an existing destination file. This preserves that existing no-op behavior rather than promising general idempotency.

Local evidence: `CONFIRM-LEAN-ACTION-191-POLICY-1`, frozen at local lab commit `872221b`. Ten fresh supervised original/patched branch controls pass. The extracted branch retains the trust-check call under an explicitly assumed precondition, remaps the policy directory into a fresh fixture and replaces the two privileged operations with unprivileged model writer/loader functions. Original destination-only fixture exits0 and replaces its content; the patched fixture exits2 with content and operation log unchanged.

Caveats: this demonstrates projected shell guard/write behavior, not an actual host overwrite, AppArmor parser behavior, exploitability, trusted-path enforcement, race/symlink safety or general idempotency. No `/etc` write, sudo, AppArmor load, sysctl or setuid operation ran. The existing working-sandbox fast path still skips setup. Coverage review is restricted to28 pinned functional-test/workflow paths: the AppArmor happy-path functional test exists, but no existing-file fixture guard test was found in those searched paths.

Local materials: `pr191.patch`, `pr191-fixed.sh`, `run-regressions.py`, exact `input-manifest.json`, `coverage-inventory.json`, and `attempts/0001/`.
