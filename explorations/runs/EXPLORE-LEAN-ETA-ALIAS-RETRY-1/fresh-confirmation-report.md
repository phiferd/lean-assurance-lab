# Fresh confirmation of the pinned PR15373 alias signal

One fresh, no-mount `linux/amd64` container reproduced the exact four-case matrix with the retained PR15373 toolchain. Execution was gated by successful in-container SHA-256 checks of the Lean executable, `libleanshared.so` and confirmation fixture. The fixture reported revision `015d54649bcaaa0861f355b59761ce308e629fbb`.

`Kernel.check` succeeded for both operands in every comparison. Critically, it reported the alias-negative left operand type as `FnAlias` and the right constructor type as `Bool → Box`; the raw stored alias was therefore present at the kernel call boundary.

| Case | `Kernel.check` lhs / rhs | Meta | Kernel |
| --- | --- | ---: | ---: |
| explicit negative | `Bool → Box` / `Bool → Box` | false | false |
| alias negative | `FnAlias` / `Bool → Box` | false | **true** |
| explicit constructor control | `Bool → Box` / `Bool → Box` | true | true |
| alias-context constructor control | `Bool → Box` / `Bool → Box` | true | true |

This exactly repeats the first successful run. It confirms a deterministic pinned-artifact API disagreement under the fixed fixture: `Kernel.isDefEq` accepts only the preserved-alias arbitrary-function negative, while `Meta.isDefEq` and the independent semantic oracle reject it.

The scientific run exited 0 in 18.199 seconds with empty stderr, no monitor error and complete supervisor cleanup. Terminal inspection recorded an exited, non-OOM container with code 0. The exact container was removed, and lookup by full ID returned `No such object`.

Two setup attempts remain retained. The first file copy failed because `/work` did not exist. More importantly, the first never-started setup container was removed when review found its command printed hashes but did not fail closed on mismatch. The replacement used `sha256sum -c`; all three identities passed before Lean executed. Neither setup issue launched a scientific process.

## Claim boundary

The confirmed statement is limited to the exposed `Kernel.isDefEq` behavior of the exact pinned artifact. No exact parent binary was locally available, so this does not show that PR15373 introduced the behavior. No declaration-level kernel acceptance was attempted, and no production soundness, exploitability, current-main or general alias conclusion follows. No parent acquisition, build, publication, push or upstream communication occurred.
