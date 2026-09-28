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

The first command replays each registered host-bound evidence family through an
alternate checkout path. Add a regression there whenever a new evidence family
records absolute paths. GitHub Actions runs this gate explicitly on Linux before
the complete unit suite. Passing only on the evidence-producing machine is a
closure defect, not an allowed CI exception.

One frozen trust-pipeline unit fixture used the same host-root record for both a
historical failed attempt and receipts synthesized during the test. A foreign
checkout cannot truthfully make both roots identical. Its successor preserves
the historical root while deriving one consistent construction root for the
temporary receipts. The portability gate runs the complete legacy synthetic
tampering test through that successor; do not rewrite historical host metadata
or skip its negative cases.
