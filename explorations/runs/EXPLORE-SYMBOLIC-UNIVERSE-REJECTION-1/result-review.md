Both pinned checkers accepted the three valid controls and rejected the three
prescribed invalid declarations. The twelve retained observations support six
accepts, six expected rejections and the scoped E0 `NO_SIGNAL` outcome.
No unexpected acceptance, unsupported/parser failure, diagnostic crash or
checker timeout appears in the reviewed evidence.

Yes, this is modestly useful: it adds concrete rejection coverage to the
positive-only predecessor. It establishes the behavior of these exact files
and profiles, not soundness, a general fault-detection rate or a fresh holdout
result.

No result-driven repair or confirmation experiment is needed. Retain the
three pairs as the recommended local boundary corpus. The owner can complete
the existing campaign handoff separately; this review authorizes no new
science or external action.

**Independent result review: PASS. No blocking findings.**
Reviewed 2026-10-20 by the bounded source/result reviewer, independently of
matrix execution and result authoring.

The frozen start, protocol and cases agree on exactly P1, M1 and I1 plus their
three invalid variants, checked once by each validator. A separate read-only
comparison reconfirmed all three predecessor control hashes and the exact
single-row mutations: P1 clears only `levelParams`; M1 redirects only the type
reference to the value expression; I1 changes only `imax` to `max`.
All six Nanoda configurations select the matching input, one thread, no
permitted axioms and explicit completion reporting. The twelve per-cell
execution records agree with the aggregate matrix record.

| Invalid case | Inspected official Lean diagnostic | Inspected Nanoda diagnostic | Classification |
| --- | --- | --- | --- |
| P1 | Undefined universe parameter `u`; raw parsed output contains the preserved empty `PARAMS ` line. | `src/tc.rs:554:13`, failed `self.ctx.all_uparams_defined(l, declar_info.uparams)`. | Expected semantic rejection in both. |
| M1 | Declaration has `Type (max u v)` but requires `Sort (max u v)`. | `src/tc.rs:955:71`, failed `self.def_eq(u, v)`. | Expected semantic rejection in both. |
| I1 | Declaration has `Sort (imax (u + 1) u)` but requires `Sort (max (u + 1) u)`. | `src/tc.rs:955:71`, failed `self.def_eq(u, v)`. | Expected semantic rejection in both. |

All six control logs contain explicit one-declaration acceptance and empty
stderr. All six Lean logs preserve exactly the expected parsed name, universe
parameters, type and value. Nanoda's invalid cases have empty stdout and the
predicted assertion diagnostic, with exit 101; Lean's rejected cases exit 1.
The assertions match the semantic paths established in `input-review.md`.
They are correctly retained as `EXPECTED_CHECKER_ASSERTION_PANIC`, separate
from diagnostic crashes. The verdicts do not depend on exit codes alone.
Nanoda parser preservation remains source-and-input evidence, without a
runtime AST or branch-coverage claim.

The retained `analyze.py` passed against the evidence. To honor the restriction
against writing any existing artifact, its sole `Path.write_text` call was
intercepted in memory and required to propose bytes exactly identical to the
existing `result.json`. No analyzer source or result bytes were changed.
Its checks verified all 31 ledger-bound scientific input hashes, the twelve
cells, parser output and diagnostics, and the retained postflight identities.
An additional independent check matched all 24 prospective runtime, source
and staged-input identities to the preflight/staging logs.

All ten supervision receipts have exit 0, complete reap/cleanup, no accounting,
monitor, pipe or cleanup errors, no trace-gap fault and no stop reason.
Their stdout/stderr byte counts and SHA-256 hashes match the retained logs.
The postflight process listing contains only the container's `sleep infinity`
and the inspection commands. Final state is
`Running=false Status=exited ExitCode=137 OOMKilled=false`; the stop receipt
supports treating 137 as the container-stop outcome, not a checker verdict.
The reported 5.285233 checker seconds and 19.081053 supervision seconds agree
with the retained records.

The summary's result and recommendation are appropriately limited. Its
separate preparation-denial/queue-preflight narrative is contextual and was
not independently reconstructed in this result-only review. The protocol's
short Lean source names refer to the predecessor's retained sources; the
full, hashed paths are explicit in the frozen start/ledger bindings, so no
source evidence is missing. Original whitespace, including the empty
parameter-list output, remains present and hash-validated.

This review binds the following bytes:

| Artifact | SHA-256 |
| --- | --- |
| `result.json` | `a1a4bcd6343f8f3ddc326bcaba17d6ea161b344efe6aff53753e0fd8acab4ca2` |
| `analyze.py` | `97928abb9abe4fffc575e8d25f3987b8e95d55613f3637dea4fbab25c9710622` |
| `summary.md` | `e90e34c714575da0f7c40d50922491c28e363a8532f37b210a7b44270de0a252` |
| `start.json` | `7980af612b86667ba6c9d6e17fb4098b524e8ebcab15a89276be112b8bca3eda` |
| `protocol.json` | `00a17e19c46cc948de821c413271f0f503c66d3df38bc4a15584bc403841db02` |
| `cases.json` | `8c4452a44d3d6b5c5b99a97cecbfb72961276561c7738f46216d0c69a014fe05` |

Only this review file was written. No checker, new experiment, source edit,
queue edit or external action was performed by the result reviewer.
