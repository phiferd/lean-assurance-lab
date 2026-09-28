# CI evidence replay portability

Completed process evidence intentionally preserves the original absolute
command, executable, environment and working-directory strings. Those strings
describe what ran; they are not instructions that a later validator must run
from the same checkout path or operating system.

Current replay code must:

- compare recorded invocation strings with their frozen manifests and
  repository-relative artifact identities;
- verify committed source, fixtures, raw output and receipts without launching
  the observer again;
- require the original host executable or runtime only for a new launch or an
  explicit same-host capability check; and
- evolve through a successor validator when the original validator is itself a
  frozen tooling input. Never edit a bound historical validator or manifest to
  make a new checkout pass.

The gate discovers process receipts in every `results/research/*` family on
each run. `config/evidence-replay-portability.json` registers the exact receipt
file inventory and an active replay test for each family. A new family is
rejected until it also has a dedicated alternate-checkout portability test;
new receipt files in an existing family require an explicit inventory update.
The gate verifies repository-relative raw output bytes and hashes without
resolving the recorded executable or working directory on the current host.
The complete unit suite runs the registered replay tests. This registration
is an inventory and custody control, not a substitute for a family's semantic
validator.

Before delivery, run:

```sh
python scripts/check-portable-evidence-replay
python scripts/run-unit-tests
```

The original pilot-specific validation commands are frozen tooling inputs and
retain their original same-host behavior. Use their explicit successors for
portable replay:

```sh
python scripts/validate-lazy-reduction-conformance-pilot-1-portable
python scripts/validate-stateful-validation-pilot-1-portable
```

The first command inventories all recorded process families and runs the
dedicated alternate-checkout regressions. Add a replay test and a dedicated
portability regression when a new family records process receipts. GitHub
Actions runs the gate with `--require-foreign-checkout` on Linux before the
complete unit suite; this refuses a checkout whose path equals any recorded
production working directory. Passing only on the evidence-producing machine
is a closure defect, not an allowed CI exception.

The frozen Kiota recursor type-repair package has one pre-launch infrastructure
failure without a process receipt. Of its 31 launched attempts, 22 refer to
manifest hashes that no longer match the current manifest files. Portable
replay preserves and checks their reservation/result identity and raw-stream
custody, reports that historical binding gap explicitly, and verifies the nine
remaining exact manifest/command bindings. It does not claim to reconstruct
the missing historical manifest bytes or edit frozen evidence. The related
refinement package has nine exact manifest-bound launched attempts.

One frozen trust-pipeline unit fixture used the same host-root record for both a
historical failed attempt and receipts synthesized during the test. A foreign
checkout cannot truthfully make both roots identical. Its successor preserves
the historical root while deriving one consistent construction root for the
temporary receipts. The portability gate runs the complete legacy synthetic
tampering test through that successor; do not rewrite historical host metadata
or skip its negative cases.
