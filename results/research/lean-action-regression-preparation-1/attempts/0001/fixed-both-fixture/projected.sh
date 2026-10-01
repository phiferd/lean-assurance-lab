#!/usr/bin/env bash
set -euo pipefail
sandbox_exe=/usr/bin/bwrap
failure_message=''
assert_trusted_sandbox_exe() { :; }
apparmor_parser() { echo 'forbidden real parser' >&2; exit 99; }
model_tee() { printf 'writer\n' >> "$MODEL_CELL/operation-log"; cat > "$1"; }
model_parser() { printf 'loader\n' >> "$MODEL_CELL/operation-log"; }
trap 'rc=$?; printf "%s\n" "$failure_message"; exit "$rc"' EXIT
if true; then
            # Ubuntu's own mechanism: the restriction denies unprivileged user namespaces to
            # programs whose AppArmor profile does not grant `userns`. Granting it here covers
            # bubblewrap and the processes it starts, which inherit an unconfined profile; it does
            # not cover the rest of the runner.
            assert_trusted_sandbox_exe
            if ! command -v apparmor_parser > /dev/null 2>&1; then
                failure_message="\`lake-check-sandbox: apparmor\` needs \`apparmor_parser\`, which is not on this runner. Use \"sysctl\" or \"setuid\" instead."
                exit 2
            fi
            for policy_file in /Users/danphifer/Documents/Codex/2026-09-30/task-3/lab/results/research/lean-action-regression-preparation-1/attempts/0001/fixed-both-fixture/policies/bwrap /Users/danphifer/Documents/Codex/2026-09-30/task-3/lab/results/research/lean-action-regression-preparation-1/attempts/0001/fixed-both-fixture/policies/lean-action-bwrap; do
                if [ -e "$policy_file" ]; then
                    failure_message="\`lake-check-sandbox: apparmor\` will not overwrite the existing AppArmor policy at ${policy_file}. Remove it, or grant bubblewrap user namespaces yourself."
                    exit 2
                fi
            done
            echo "::warning::\`lake-check-sandbox: apparmor\` is installing an AppArmor profile granting ${sandbox_exe}, and the processes it starts, permission to create user namespaces. The runner's restriction stays in force for everything else. On a persistent self-hosted runner the profile outlives this job."
            if ! model_tee /Users/danphifer/Documents/Codex/2026-09-30/task-3/lab/results/research/lean-action-regression-preparation-1/attempts/0001/fixed-both-fixture/policies/lean-action-bwrap > /dev/null <<PROFILE
abi <abi/4.0>,
include <tunables/global>

profile lean-action-bwrap ${sandbox_exe} flags=(unconfined) {
  userns,
  include if exists <local/lean-action-bwrap>
}
PROFILE
            then
                failure_message="\`lake-check-sandbox: apparmor\` could not write /Users/danphifer/Documents/Codex/2026-09-30/task-3/lab/results/research/lean-action-regression-preparation-1/attempts/0001/fixed-both-fixture/policies/lean-action-bwrap. This runner probably does not offer passwordless sudo."
                exit 2
            fi
            if ! model_parser -r /Users/danphifer/Documents/Codex/2026-09-30/task-3/lab/results/research/lean-action-regression-preparation-1/attempts/0001/fixed-both-fixture/policies/lean-action-bwrap; then
                failure_message="\`lake-check-sandbox: apparmor\` could not load the AppArmor profile for ${sandbox_exe}. Use \"sysctl\" or \"setuid\" instead."
                exit 2
            fi

fi
