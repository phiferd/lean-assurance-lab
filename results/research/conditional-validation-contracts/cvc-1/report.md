# CVC-1: literature and reuse assessment

Date: 2026-09-06. Frontier: `F-CONDITIONAL-VALIDATION-CONTRACTS`.
Decision: **EXTEND**, selecting **universe-expression interpretation**.
Outcome: `SUCCESS` for the bounded assessment; formal results remain
`SOURCE_REVIEW_ONLY`. No proof build, checker launch, or installation occurred.

Reuse Lean4Lean's existing level semantics and comparison theorems. The useful
missing work is a small interpretation contract connecting the Lab's supplied
artifact to those judgments. CVC-2 should state that connection and its proof
target. This assessment does not provide the connection, reproduce a proof, or
establish that any deployed validator satisfies it.

The canonical decision is [assessment.json](assessment.json). The dated search
log, source descriptions, exact revisions, retrieved-file hashes, reservations,
and session accounting are in [work-record.json](work-record.json). The search
used five queries, eight primary sources, and four code inspections. All counts
include failures where applicable. Two cited works were followed beyond the
initial seeds. Nonprimary search hits were excluded without in-depth review.

| Source and inspected version | Claim or reusable component | Assumptions and gap |
| --- | --- | --- |
| S1: [Lean4Lean, arXiv v3](https://arxiv.org/html/2403.14064v3), sections 2–6; paper references `cpp2026` and Lean 4.20.1 | Abstract typing and component preservation, including `inferLambda.WF`. | Unique typing and strengthening are conjectural in this version; section 4 exposes representation assumptions. It supplies no NDJSON import theorem. The paper and current code must remain separate versioned evidence. |
| S2: [Lean4Less author PDF](https://rish987.github.io/files/lean4less.pdf), 27 pages, exact retrieved SHA in ledger | Cast insertion, target typing checks, and checks of original/translated constant-type equality; sections 3.3 and 4.2 describe correspondence. | Lean-minus uses propositional proof irrelevance; congruence and bootstrapping premises matter. Output typing alone does not prove fidelity to the submitted term. Experiments use Lean 4.16.0-rc2. |
| S3: [MetaRocq](https://github.com/MetaRocq/metarocq/tree/c8cd46054518193103c3bb33aa6e15c7f489e72c), `c8cd460`, SafeChecker development | `check_wf_env_bool_spec` concludes typing of the same input term after successful Boolean checking. | Requires `NormalizationIn`, configured flags, a well-formed context, and an abstract-environment relation. PCUIC syntax and universe constraints differ from Lean. No complete transitive assumption audit was run. |
| S4: [Lean4Lean](https://github.com/digama0/lean4lean/tree/8223d223ed98661882e95d9d6a7126df7097cd76), `8223d22`; Lean/Batteries 4.33.0-rc2 | `VLevel.WF`, `eval`, `Equiv`, `ofLevel`; source proofs `normalize_complete`, `isEquiv'_wf`, and `isEquiv'_complete`. | Conversion premises exclude undeclared parameters and metavariables. Inspected proof paths use explicit helper axioms. Neither a build nor `#print axioms` was run. The artifact interpretation remains a separate obligation. |
| S5: [Lean4Less implementation](https://github.com/rish987/Lean4Less/tree/5b66bbc4af5c2c11313fcfb5098630dadaf19281), `5b66bbc`; Lean 4.28.0-rc1 | `patchTheorem` constructs a translated body; repository documents verification and resource limits. | Its `allowAxiomReplace` branch must be accounted for in any fidelity promise; it defaults false. No universal fidelity theorem was located in the declared inspected group. That is not a repository-wide absence claim. |
| S6: [Lean4Lean divergences](https://github.com/digama0/lean4lean/blob/8223d223ed98661882e95d9d6a7126df7097cd76/divergences.md) | Explains the complete level-comparison fallback and deliberately different accepted pairs. | Policy explanations are not semantic authority. Nested-restoration bullets conflict about retained rechecks; this assessment preserves that inconsistency and does not use it to adjudicate recursor behavior. |
| S7: [Eliminating Reflection from Type Theory](https://sozeau.gitlabpages.inria.fr/www/research/publications/drafts/Eliminating_Reflection_from_Type_Theory.pdf), retrieved 19-page author draft | Theorem 4.4 translates derivations to related terms; Corollary 4.5 preserves an ITT-typable target statement. | Requires UIP, function extensionality, annotated syntax, and a well-typed global context. Section 5 leaves the ITT-to-TemplateCoq bridge unproved. The draft's placeholder header is not evidence of identity with the CPP 2019 final. |
| S8: [Coq Coq Correct!](https://www.ps.uni-saarland.de/Publications/documents/SozeauEtAl_2020_CoqCoqCorrect.pdf), POPL 2020, Article 8 | Figure 10 and section 3.5 return a typing derivation for the supplied PCUIC term. | This version assumes metatheory/guard properties and strong normalization, and does not prove inference completeness. Those historical limits must not be silently assigned to current MetaRocq. |

The first network revision lookup failed because sandbox DNS was unavailable;
the approved read-only retry succeeded. No source remained inaccessible. Exact
paper hashes identify the retrieved versions; mutable author URLs may require
an archived copy to reproduce those same bytes later. Repository file URLs use
full Git revisions. [source-excerpts.json](source-excerpts.json) retains the
decisive code statements with line ranges, full-file hashes, and excerpt hashes.

| Rank | Candidate fragment | Comparison and missing work |
| --- | --- | --- |
| 1 | Universe expressions | Strongest combination of an existing semantic model, source-level soundness/completeness results, and exact Lab `imax` artifacts. A finite raw-level interpretation is a plausible small extension. Parameter ownership, duplicate names, unresolved IDs, and correspondence to the supplied sort body still need a contract. |
| 2 | Ordinary declaration/import boundary | Existing `VDecl.WF` rules preserve a supplied definition body against its declared type, but importer order, dependency environments, permitted primitives, and reconstruction widen the task. The historical target explicitly excludes parsing/reconstruction. Better as a later extension after one smaller connection works. |
| 3 | Restricted non-nested recursor metadata | Relevant to real Lab questions, but the inspected `VInductDecl.WF` and `VEnv.addInduct` definitions contain `sorry`. The strongest retained restored-recursor cases also involve nested machinery outside this candidate. Reuse does not currently avoid a substantial modeling gap. |

The selected theorem interface is narrower than whole-checker correctness.
At the pinned revision, `Lean.Level.isEquiv'_complete` says that, given
successful conversions of both levels with `VLevel.ofLevel`, the comparator
returns true exactly when the converted levels are equivalent under `VLevel.eval`.
`Lean.Level.Normalize.normalize_complete` provides the normal-form comparison
interface. The finite parameter list, its ordering, and successful interpretation
are meaningful premises, not consequences of comparator acceptance alone.
See excerpts E1–E6 and E16.

There is visible trust left to audit. The standard-library fast path uses
`normalize_eq` through `eval_normalize` and `isEquiv_wf`; the normal-form proof
uses TreeMap helper axioms such as `all_eq_all_toList`. Other imported axioms
must not be called actual theorem dependencies solely because they are imported.
The complete dependency set remains unknown until bounded reproduction and an
axiom printout. A commented `sorry` in `Verify/Level.lean` is not an active hole;
the `sorry` definitions in `Theory/Inductive.lean` and the projection proof in
`Verify/TypeChecker/InferType.lean` are active source holes. This is a scoped
source inspection, not a proof of the absence of other holes.

The Lab connection is concrete. The retained `universe-imax-right-succ` artifact
contains levels `max u (succ v)` and `imax u (succ v)` and a supplied sort body.
Its existing records show a profile disagreement with accepted controls. The
newly inspected Lean4Lean revision is distinct from the historically observed
`ecb3b66` Arena profile; no current outcome is inferred from the new theorem.
The later ecosystem closure already withdrew the old implementation-fault
recommendations after Arena accepted `either`. This model-relative research
does not reopen those recommendations or replace raw observations.

CVC-2 is recommended at queue priority 2, the highest eligible successor. Its
target is one universe-expression contract using this pinned formalization
and at most two strategies. It must fix an independent interpretation of the
exact supplied artifact, the environment and parameter domain, an acceptance
obligation, positive and negative examples, and one non-circular preservation
or counterexample target. It must also record a finite successor execution
protocol and an assumption ledger before later proof or observer feedback.
These are deliverables for CVC-2, not work executed here.

The prospective shared asset is a reproducible semantic explanation attached
to existing universe corner cases. No external issue, PR, or message is
recommended at this stop: first establish the interpretation and determine
whether the result adds value beyond existing corpus policy. The assessment
supports an extension decision, not global novelty, a universal Lean contract,
new normative-source approval, or correctness of a deployed validator.

Validate the local accounting and evidence with
`scripts/validate-cvc1-assessment`. It checks declared budgets, historical input
bindings, source/inspection links, excerpts, and local content hashes. External
hashes are retrieval receipts; offline validation does not authenticate remote
source contents, prove the scientific interpretation, or observe unrecorded
operations. Repository closure checks are recorded separately under
`results/workflow-refresh/cvc-1-2026-09-06/`.
