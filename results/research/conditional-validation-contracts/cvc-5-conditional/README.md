# Reusing the CVC-U1-A7 conditional validation result

This package connects a checked conditional theorem to exact serialized artifacts,
finite validator observations, and a local serialization regression. It explains
a model-relative acceptance difference and separates an importer prerequisite
from an ownership check. **Reuse this result; further scientific execution is
paused pending a named, authorized successor.**

The canonical [result](result.json) is a checked projection of retained records.
The [input manifest](evidence-manifest.json) binds them to the package's entry
commit, including historical planning and upstream snapshots. The
[phase decision](decision.json) records value, alternatives, and prerequisites.
No new proof, observer, setup/build, research-network launch, or scientific byte
variant was produced for this package.

## What the theorem says

The [fixed contract](../../../../research/conditional-validation-contracts/cvc2/Contract.lean)
models one supplied safe nonrecursive definition whose value and type are Sorts,
in an empty object-language environment. Supported universe expressions use
zero, successor, max, imax and owned, uniquely declared parameters. For every
assignment of natural numbers to those parameters, the supplied value level
plus one must equal the supplied type level. The submitted body stays fixed.

The selected structured strategy is `Lab.CVC2.Accepts`: support plus the pinned
`Lean.Level.isEquiv'` predicate with Lean4Lean correctness/completeness theorems. The
[checked proof](../cvc-a7-repair-1/run-0002/attempts/03/CVC2Proof.lean)
and [audited result](../cvc-a7-repair-1/result.json) establish:

| Declaration | Checked obligation | Scope |
| --- | --- | --- |
| `encoding_preserves` | `EncodingTarget` | Owned structured levels preserve interpretation and well-formedness under encoding. |
| `preservation` | `PreservationTarget` | For every structured artifact, `Accepts a → Contract a`. |
| `required_acceptance` | `AcceptanceTarget` | Exactly `rightSucc` and `rightSuccControl`, bound to E-POS and E-CONTROL. |
| `boundary` | `BoundaryTarget` | E-ZERO is supported but violates the model; E-UNOWNED is unsupported. Neither satisfies model acceptance. |

The host envelope A7 is `propext`, `Classical.choice`, `Quot.sound`,
`Lean.Level.instLawfulBEqLevel`, `Lean.Level.isExplicitSubsumedAux_eq`,
`Lean.Level.normalize_eq`, and `Std.TreeMap.all_eq_all_toList`.
Encoding uses only `propext` and `Quot.sound`; the other three Lab results use
all seven. The four helper assumptions remain substantive conditional inputs.
Their exact statements and discharge alternatives are in the
[assumption review](../cvc-axioms-1/assessment.json).

Proof checking used Lean `v4.33.0-rc2` and Lean4Lean revision
`8223d223ed98661882e95d9d6a7126df7097cd76`. The official observer uses
Lean `v4.33.0`; Nanoda uses revision `6ae1f0c`. The exact binary hashes,
configurations and source mappings remain bound in the
[observer mapping](../cvc-4-ownership-1/source-mapping.json) and execution manifests.
The model strategy is not an executable-validator correctness theorem.

## What the exact observers did

The [original comparison](../cvc-4-conditional/result.json) contains every row,
input digest, request, raw output and process receipt. The
[ownership successor](../cvc-4-ownership-1/result.json) is a distinct input record.

| Exact case | Model status | Official | Nanoda |
| --- | --- | --- | --- |
| E-CONTROL | Checked required acceptance | Accept | Accept |
| E-POS | Checked required acceptance | Type-comparison refusal | Accept |
| E-ZERO-CONTROL | Valid by definition | Accept | Accept |
| E-ZERO | Checked model-invalid | Type-comparison refusal | Type-comparison refusal |
| Original E-OWNED-CONTROL | Valid by definition | Accept | Parser error |
| Original E-UNOWNED | Checked unsupported | Not run | Not run |
| E-OWNED-CONTROL-PARAM-RECORD | Valid by definition | Accept | Accept |
| E-UNOWNED-PARAM-RECORD | Checked unsupported | Ownership refusal | Ownership refusal |

For every assignment, `imax u (v+1) = max u (v+1)`. E-POS therefore shows a
finite acceptance limitation of the pinned official profile relative to this
model. For E-ZERO, assigning `u=1` separates the value's type level 1 from the
requested type level 2. For E-UNOWNED the algebraic equality still holds, but
`u` is absent from the declaration's parameter list.

Both parsers preserve raw imax. The retained Nanoda source mapping shows the
right-successor simplification. The original comparison did not bind the
internal C++ comparator source to the official executable; installed
`Lean/Level.lean` contains the rewrite and cannot fill that gap. A later
source-only master comparison recorded in
[upstream participation](../../../../docs/UPSTREAM_ISSUES.md) adds no current-master
execution result.

The original Nanoda ownership control failed at `parser.rs:506`, before checking
ownership. After adding the explicit unused parameter record, fresh controls
accepted and the candidate reached `tc.rs:520`; official reported undefined
universe parameter `u`. The original parser failure and both unrun candidates
remain unchanged. The earlier reporting failure also remains raw failure evidence.

## Reuse the regression and inspect the evidence

The [two-stream regression](../../../../tests/test_cvc4_ownership_inputs.py)
and [implementation](../../../../lib/cvc4_ownership_inputs.py) enforce the sole
inserted level record immediately before the final definition: level index 3,
parameter name index 3 in the control and 2 in the candidate. Deleting that line
recovers each predecessor byte-for-byte. Name, ordered parameters, referenced
value and type syntax remain identical. The strict decoder still refuses the
unowned candidate. These are Lab-authored streams; metadata does not establish
that the named exporter produced them.

From the repository root, inspect the package offline:

```sh
scripts/validate-cvc5-package
scripts/build-cvc5-package
python3 -m unittest discover -s tests -p 'test_cvc4_ownership_inputs.py'
scripts/validate-cvc-a7-repair --closure
scripts/validate-cvc4-evidence
scripts/validate-cvc4-ownership --without-runtime-payloads
```

These commands inspect retained evidence and exercise the existing pure
regression. They do not rerun Lean or either observer. The three external binary/configuration paths in observer profiles remain historical identity metadata;
portable package validation does not check executable availability. The complete payload-aware
closure checks and inert administrative fixture accounting are recorded in
[closure validation](../../../workflow-refresh/cvc-5-conditional-2026-09-08/validation.json).
Historical runs remain terminal. Four ownership reservations plus twelve prior
reservations consume the combined sixteen-launch ceiling; the package grants
no new reservations. Prior proof failures, active-time scopes and unknown
historical fixture duration remain visible in their original records.

## Contribution and phase decision

The immediate target is reuse inside Lean Assurance Lab. No new external action
is recommended. Arena PR #176 already carries the imax pair with outcome `either`;
Lean #12747 already received declaration-level replay and conditional evidence.
These are dated local records, not fresh upstream observations. The ownership
change repairs a Lab serialization prerequisite and provides a focused local
regression; it does not establish a new Nanoda/Kiota defect. The formal bridge
reuses existing Lean4Lean theory, and no distinct upstream-ready improvement to
that formalization has been demonstrated. Another draft would currently
repackage the same evidence without a supported target need.

Select **CVC-NEXT-AUTHORIZATION**, **WAITING and unstarted**. The concrete decision
is whether to authorize a bounded survivor-triage proposal (`ALT-SURVIVORS`, the
strongest current alternative), choose another named direction after the required
method review, or retain the pause. Substantive maintainer guidance can instead
justify ranking a focused follow-up. New scientific work requires durable
selection, authority, finite budget and entry gates; publishing to another
repository also requires exact target-specific approval.

Another universe pair is outside the completed comparison. A new contract slice
needs authorization and additional import/environment or recursor bridges.
Transfer needs independent inputs and preregistration. Arena access repair and
maintainer replies are not established by these local records. The September 6
literature review remains applicable to reuse of this same slice; it does not
establish global novelty or replace a review for a new method.

No A7 assumption or consistency result is discharged. No arbitrary-byte parser,
importer, source-to-binary or executable-validator refinement is proved. The later
controls do not enlarge `AcceptanceTarget`. No invalid accepted proof, broad
coverage, method superiority or universal obligation follows. The catalog's
`DECL.UNIVERSE.PARAM_OWNERSHIP` stays PROVISIONAL; original CVC-4/CVC-5 dependencies
and withdrawn imax defect recommendations remain unchanged.
