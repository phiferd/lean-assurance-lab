# CVC-2: a supplied-sort interpretation contract

Date: 2026-09-06. Outcome: **SUCCESS for contract specification**.
Scientific status: **SPECIFICATION_PROPOSAL_UNCHECKED**. No Lean elaboration,
proof build, validator launch or toolchain installation was performed.

The selected universe fragment admits a non-circular preservation target.
For the supplied definition value `Sort l` and its declared type `Sort t`,
model **CVC-U1** requires `meaning(l, ρ) + 1 = meaning(t, ρ)` for every natural
number assignment `ρ` to the declared universe parameters. The body, type and
parameter domain are fixed by the supplied artifact. Existence of a different
term with the declared type would not establish this contract.

The [canonical contract](contract.json), [formal signature](../../../../research/conditional-validation-contracts/cvc2/Contract.lean),
[examples](examples.json), [assumption ledger](assumptions.json) and
[successor protocol](execution-protocol.json) jointly state the target.
The signature contains definitions of propositions to prove, not an asserted
theorem, a `sorry` proof or a new axiom.

## Meaning and supplied-artifact fidelity

The independent syntax has `zero`, `succ`, `max`, `imax`, and named parameters.
Its interpretation uses natural numbers directly: `imax(x, 0) = 0`; for
positive `y`, `imax(x, y) = max(x, y)`. It does not call Lean's universe
normalizer or comparator. Supported inputs declare distinct parameter names
and own every level parameter reference. There are no input constants,
axioms, universe constraints, local hypotheses or ambient dependencies.

The object-language judgment is limited to the supplied sort and declared
sort type. It is not a full declaration-admission or environment-extension
judgment. The requested statement of this research item is preservation of
that judgment, rather than a theorem declaration contained in the input.
Lean's host proof environment and its conditional axioms are separate from
the empty dependency environment of these object-language examples.

Two existing NDJSON artifacts supply the exact required acceptance set:

| ID | Supplied value level `l` | Declared sort level `t` | Obligation |
| --- | --- | --- | --- |
| E-POS | `imax(u, succ(v))` | `succ(max(u, succ(v)))` | Accept this exact artifact |
| E-CONTROL | `max(u, succ(v))` | `succ(max(u, succ(v)))` | Accept this exact artifact |

Their complete bytes, including declaration name, parameter order, safe
status, opaque hint, exporter metadata and unused serialized nodes, are hashed
in `examples.json`. The narrow structural decoder checks record fields,
namespace IDs, backward references, ownership and the final sort definition;
it expands references without normalization or semantic comparison. Its
decoded output must match the specified AST, and the validator renders those
same ASTs to check the corresponding Lean example definitions. Duplicate JSON
keys, duplicate IDs, unowned names, extra fields and other declaration or
expression families are excluded. Even unused level records must be owned.

This defines an inspectable interpretation of the exact two byte strings.
The Python/JSON implementation and its mapping to the Lean syntax remain a
trust boundary; there is no proved general NDJSON parser. Outside those two
byte strings, no raw-artifact acceptance coverage is promised. The proposed
soundness theorem instead quantifies the larger, explicitly structured domain
of all finite supported `SortDefinition` ASTs. A future model proof will not
silently become a theorem about arbitrary input bytes or actual validators.

Reconstruction may expand sharing, encode constructors structurally and map a
declared string name to `Lean.Name.str anonymous name`. The comparison
algorithm may normalize internally. It may not replace the supplied body,
alter its type, infer missing parameters, rewrite `imax` unconditionally to
`max`, or introduce assumptions. This distinguishes interpretation fidelity
from a successful check on a replacement term.

## One strategy and one preservation target

S1 first checks the syntactic support conditions, then applies pinned
`Lean.Level.isEquiv'` to `succ(encode(l))` and `encode(t)`.
The target is `∀ a, Accepts a → Contract a`. Its only premise is syntactic
support plus this actual comparison result. Semantic equality and the
correctness of the structural encoding are conclusions to prove.

`EncodingTarget` names the missing intermediate result: for an owned
expression and duplicate-free parameter list, structural encoding converts
successfully through `VLevel.ofLevel`, produces a well-formed positional
`VLevel`, and preserves the independent named interpretation for every
assignment. Injectivity of the string-to-name map and the correspondence
between list lookup and parameter assignment are explicit proof work.
They are not accepted as assumptions of `PreservationTarget`.

The source mapping binds Lean4Lean
`8223d223ed98661882e95d9d6a7126df7097cd76`, using unchanged CVC-1 excerpts:

| Lab component | Pinned source interface | Remaining connection |
| --- | --- | --- |
| `meaning`, `Owned` | `VLevel.WF`, `eval`, `Equiv` (E1–E2) | Named versus positional interpretation |
| `encode`, `EncodingTarget` | `VLevel.ofLevel`, `WF.of_ofLevel` (E3) | Structural conversion and lookup preservation |
| `Accepts`, preservation | `isEquiv'_wf` (E5), implementation (E16) | Compose soundness with the encoding bridge |
| Two required accepts | `isEquiv'_complete` (E6) | Check both exact obligations; infer no broader coverage |
| Conditional assumptions | Helper-axiom source (E8–E9) | Print actual transitive dependencies after compilation |

The separate `AcceptanceTarget` requires both positive artifacts. A proof of
soundness for an always-refusing strategy would not discharge it. Broader
completeness over every supported AST is not promised, even though the pinned
source comparator has a completeness theorem that may help prove this set.

Two model examples characterize the boundary before proof feedback:

- **E-ZERO:** value level `imax(u, 0)` with declared level `succ(u)` is
  well formed but violates the judgment at `u = 1`: the body's type level is
  1 and the declared type level is 2. This refutes the tempting unconditional
  `imax = max` rewrite. It is an expected model-invalid example, not a
  counterexample to S1 preservation or a newly observed validator defect.
- **E-UNOWNED:** `Sort u : Sort (succ u)` with only `v` declared is outside
  the supported domain. Algebraic equality alone does not excuse the missing
  owner. It must not be silently assigned zero or an implicit parameter.

These two boundary ASTs have no new serialized witness or checker outcome.
`BoundaryTarget` requires their formal characterization later. Refusal,
unsupported input, proved model invalidity, timeout, error and interruption
remain distinct in the contract and execution protocol.

## Assumptions and execution readiness

The model choices are not normative-source approvals. Standard logical
assumptions and three explicitly named source helpers are conditionally
permitted: `Std.TreeMap.all_eq_all_toList`,
`Std.TreeMap.any_eq_any_toList`, and `Lean.Level.normalize_eq`.
The later result must print the actual transitive dependencies of every
target and reused comparator. `sorryAx`, new Lab axioms, assumed preservation,
and unlisted axioms are disallowed. Importing a file does not show which of its
axioms a theorem uses. In particular, `Lean.Level.mkData_eq` is not silently
admitted because the source file also contains it.

The delegated [runtime inventory](runtime-inventory.json) found the exact
Lean 4.33.0-rc2 installation and Batteries source revision
`76e1c118b0700b4ceafe99532e887d6431625e1a`. The existing older Lean4Lean
checkout can donate the selected 12 source modules whose bytes match the
pinned tree, but it is not the target checkout. Ten Lean4Lean verification or
theory modules and fourteen Batteries modules in the inspected import closure
lack compiled artifacts. The source-only inventory neither builds them nor
proves that a complete runnable bundle can be reproduced within the later
budget. The exact proof environment is therefore not yet available.

Protocol `CVC3-U1-PROOF-0001` fixes one theorem family, four 90-minute sessions,
twelve counted proof-build attempts, 300 seconds per attempt, zero observer
launches, and zero runtime downloads during attempts. It specifies exact
command structure, immutable contract and input bindings, permitted mutable
proof bytes, reservation before launch, cumulative failure accounting,
exclusive ownership, process-group termination, crash/resume behavior and
required theorem/axiom outputs. Its status is **SPECIFIED_NOT_EXECUTABLE**.
A content-bound dependency bundle and a tested successor runner must exist
before CVC-3 entry. The old campaign runner and historical run IDs confer no
authorization. Upstream dependency preparation has its own explicitly budgeted queue item
and ledger, linked into aggregate phase cost; it may not elaborate the Lab
signature, targets or fixed examples. First signature elaboration is CVC-3
attempt 1 under the same 300-second deadline, leaving at most eleven proof
attempts. A signature failure consumes that attempt and stops for successor
review. Missing dependencies cannot trigger implicit compilation in CVC-3.

## Stopping-point recommendation

CVC-2 stops with a specification success and an unproved semantic target.
The source-based static review found no obvious circular premise or theorem
interface mismatch; reviewer agreement is not assurance evidence. Structural
mapping and artifact-integrity tests are the mechanical result of this item.
No proof reproduction, model-soundness result, normative promotion or
implementation observation is claimed.

Select **OPS-UPSTREAM-1** next: one bounded, read-only disposition check on
Arena PRs #181 and #182, preserving the deferred Kiota clarification. This
small maintenance item has remained eligible through two research stops;
the proof continuation currently lacks its compiled prerequisites. No fresh
upstream feedback or urgency is inferred here, and no status check was
performed as a second item.

Promote **ALT-PAYLOADS** as the next eligible local alternative: prepare an
exact, isolated materialization and compilation proposal for the recorded
universe-proof dependency gap, including source identities, commands, finite
cost limits and the successor runner prerequisite. Its diagnostic scope
permits no builds. Keep CVC-3 through CVC-5 PLANNED until their own gates are
met. The CVC-1 reuse assessment remains current for unchanged pins and scope.

No external message is recommended now. A later checked result may justify a
Lean4Lean reuse contribution or a precise artifact-boundary question, after
its implementation connection is established and target-specific submission
authorization is granted. Existing withdrawn imax defect recommendations,
historical studies and unresolved assurance disagreements remain preserved.

The work record and evidence manifest bind this item. Exact repository
validation commands and outcomes are retained under
`results/workflow-refresh/cvc-2-2026-09-06/validation.json`; validation does not
execute either the proposed proof protocol or the selected next queue item.
