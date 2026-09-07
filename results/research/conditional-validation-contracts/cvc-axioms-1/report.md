# CVC-AXIOMS-1: comparator assumption review

Recorded 2026-09-06 (America/New_York). Outcome: **SUCCESS** for a source-only
review. Decision: **SUCCESSOR**. Scientific status: `SOURCE_ASSUMPTION_REVIEW_ONLY`.
No checked Lab theorem, counterexample or discharged axiom is claimed.

The seven transitive assumptions in both retained imported comparator reports
support a useful explicitly conditional successor. The omitted equality and
partial-helper axioms are substantive trust conditions. The frozen CVC-2
allowlist and terminal CVC-3 failure remain unchanged.

Canonical inputs and findings: [assessment](assessment.json),
[exact source excerpts](source-excerpts.json),
[independent review](independent-review.json),
[unexecuted successor proposal](successor-proposal.json), and
[work record](work-record.json). Validate with `scripts/validate-cvc-axioms`;
add `--require-full-source` to compare every slice to the retained local files.

## Assumption table

Every row occurs in both `Lean.Level.isEquiv'_wf` and
`Lean.Level.isEquiv'_complete`. Exact declarations and source/context references
are bound in the assessment, with a feasible discharge or replacement route.

| Assumption | Old policy | Trust role |
| --- | --- | --- |
| `propext` | `STANDARD_ALLOWED` | Host propositional extensionality |
| `Classical.choice` | `STANDARD_ALLOWED` | Host nonconstructive choice |
| `Quot.sound` | `STANDARD_ALLOWED` | Host quotient equality |
| `Lean.Level.instLawfulBEqLevel` | `UNLISTED` | Lawfulness of opaque runtime Level equality |
| `Lean.Level.isExplicitSubsumedAux_eq` | `UNLISTED` | Opaque partial helper equals its total copy |
| `Lean.Level.normalize_eq` | `HELPER_ALLOWED` | Opaque core normalization equals the supplied total algorithm |
| `Std.TreeMap.all_eq_all_toList` | `HELPER_ALLOWED` | Map-wide Boolean traversal agrees with its entry list |

`Std.TreeMap.any_eq_any_toList` was allowed previously but does not occur
in either actual comparator report. It is excluded from the proposed A7 list.
Other axioms present in imported source files are not automatically dependencies.
Failed Lab declarations contain error-recovery `sorryAx`; those outputs are
preserved as failures and supply no theorem evidence.

## What this establishes

None of the seven exact statements mentions Lab.Accepts, Contract, EncodingTarget or PreservationTarget. The four helper axioms concern primitive equality, normalization/helper correspondence and map traversal. Conditional reuse still leaves owned-name encoding, positional evaluation and the fixed acceptance/boundary obligations to prove. Their lower-level scope does not establish their truth or joint consistency.

The retained CVC-3 stdout mechanically establishes all seven transitive leaves for both imported comparators. Source-visible paths explain uses but are not a reconstructed proof-term DAG. Verify.LevelStd internals remain uninspected; printed membership must not be relabeled as a complete intermediate path.

The two Lean4Lean files match earlier exact hashes. Four source files from the already-selected v4.33.0-rc2 installation are newly hashed local observations; the old runtime inventory binds compiled products, not those source bytes. Neither local hashes nor matching release labels prove source-to-binary correspondence. A future baseline must print the imported declaration types and compare them to the reviewed statements before claiming correspondence.

In particular, `LawfulBEq Level` promises equality of the actual Level values
and reflexive Boolean equality, not just equal numerical denotations.
`normalize_eq` asserts an extensional algorithm correspondence. Side-by-side
source comparison does not turn either opaque runtime bridge into a proof.

The initial attempt to find installed source hashes in the old runtime manifest
failed because that manifest excludes `src/lean`. The work record preserves
this diagnostic and the subsequent weaker release-source binding. No source
revision was changed and no compilation was used to repair the inventory.

## Discharge and alternatives

- **propext**: Retain as an explicit foundation of the named host theory. Avoiding it would require a separately checked constructive/relation-based development; source review cannot discharge a foundation axiom.
- **Classical.choice**: Retain as an explicit foundation. Constructive separation/completeness may be an alternative, but a full proof-term dependency graph and choice-free replacement were not extracted in this bounded review.
- **Quot.sound**: Retain the quotient foundation. Replacing function equalities with pointwise relations is a research alternative, not evidence that the pinned comparator reports no longer depend on this axiom.
- **Lean.Level.instLawfulBEqLevel**: No proof of the opaque extern is available in the inspected sources. A new transparent structural equality with a proved lawfulness instance could support a changed comparator; equivalence to the existing extern would still need a separate bridge. Testing equality cannot prove this universal axiom.
- **Lean.Level.isExplicitSubsumedAux_eq**: Use a total helper directly in an explicit new comparator/model or formalize a source-to-runtime refinement. A local induction about the total copy does not prove equality to the imported opaque partial constant. No such discharge was checked here.
- **Lean.Level.normalize_eq**: A transparent total comparator could avoid the opaque normalizer, but would change the accepted strategy and require fresh proof and exact acceptance checks. Source similarity and finite tests are insufficient to discharge normalize_eq. Do not describe this assumption as already proved or trivial.
- **Std.TreeMap.all_eq_all_toList**: Prove the map traversal lemma against pinned implementation internals or explicitly use toList.all in a successor comparator. Those internals are outside this source allocation; existing calls and the printed reports justify retaining it as conditional, not asserting discharge.

The pure normal-form comparator is a credible alternative: omitting the
core fast path may remove some runtime bridge dependencies. Its reduced
transitive closure has not been printed, the map helper is still visibly
used, and changing acceptance requires another explicit contract. The
independent review supports this distinction; reviewer agreement supplies
no semantic authority.

## Selected next item

`CVC-CONDITIONAL-1` is selected READY and unstarted. It prepares a new
protocol/runner for model `CVC-U1-A7`, preserving the semantic signature
and examples with an explicit seven-assumption envelope. Its ceiling is
two 60-minute sessions and 64 supervised inert fixture launches, each at
most five seconds and together at most 320 reserved seconds, including
required regression fixtures. It permits no proof, dependency or observer
launches, network requests or external messages.

`CVC-3-CONDITIONAL` remains PLANNED. Only a later committed entry review
can promote its new run ID. Its proposed ceiling is six counted builds
in two 60-minute sessions, each build at most 300 seconds: signature,
an exact imported-type/seven-axiom baseline, then normally at most four
proof attempts. Failure reservations count. This is a new bounded
successor, never a resumption of the old ten unused slots. Original plus
proposed proof attempts are at most eight. Per-result dependencies must
be printed; missing, extra, forbidden or unlisted axioms fail the gate.

The original CVC-4 and CVC-5 remain PLANNED with unmet dependencies.
A successful conditional proof would require an explicitly scoped
implementation-connection successor. No upstream message is recommended
now: the result identifies a Lab assumption-accounting gap, not a new
implementation defect.

## Scope and costs

Six files under the existing source/release pins were allocated across
the owner and independent reviewer. Their overlapping work is covered
by the owner session; no separate worker elapsed total is invented.
Research operations were source reads, local hashing and evidence analysis.
Required repository closure tests and their instrumented inert fixture
processes are separately measured in the validation record. Their costs
are not proof attempts, and zero research launches does not mean zero
administrative test processes.

All previous measured costs and the unknown CVC-RUNNER-1 fixture duration
remain as recorded. Normative approvals, catalog dispositions, assurance
counts and historical attestations are unchanged.
