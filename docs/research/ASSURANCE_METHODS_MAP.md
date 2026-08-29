# Assurance Methods Map

- Research snapshot: 2026-08-29
- Repository revision inspected: `debb4606597da9bd27ca4cbca7e3742f294a68dc`

## Purpose and authority

This document is institutional memory for assurance methods encountered by
Lean Assurance Lab. It records what each method does, what sources were
actually consulted, what the project has learned from it, and what evidence
would justify reconsidering it.

This is not a roadmap, priority list, project objective, or claim that any one
method should dominate the project. [Research Status](../RESEARCH_STATUS.md)
remains the authority for active work and prioritization. The dispositions in
[Research-Backed Improvements](RESEARCH_BACKED_IMPROVEMENTS.md) are prior
research recommendations, not silently activated work.

The current
[checker-rule inventory](../../results/investigations/checker-rule-inventory.md)
is an assurance-boundary inventory: at this snapshot it aggregates 37 exact
boundaries from eight bounded matrices. It is not a denominator over Lean
semantics. Appropriate descriptions include *known-rule characterization*,
*assurance-boundary inventory*, and *characterized rule set*; this document
does not call it semantic coverage.

## Source and maturity discipline

Each entry separates source-verified claims from Lean Assurance Lab
interpretation. “Consulted” means the linked paper, official proceedings page,
official documentation, or artifact record was read for this review; retrieval
limitations are stated rather than filled from memory.

The maturity labels are descriptive and deliberately non-prioritizing:

- `LITERATURE_ONLY`: primary or official literature was consulted, but the
  method has not been exercised locally.
- `PROJECT_ANALOGUE`: related project work exists, but it is not an execution
  of the cited method.
- `PILOTED`: a bounded local experiment exercised part of the method.
- `EVIDENCE_SUPPORTED`: local mechanical evidence supports one explicitly
  scoped use of the idea, not the method in general.

These labels neither assign execution priority nor establish semantic
authority.

## Mechanized negative semantic obligations

- **Lineage and sources consulted:** *Failing with Purpose: Dangling
  Coverage-Guided Negative Test Generation from a Mechanized P4 Type System*;
  [official FSE 2026 paper page](https://conf.researchr.org/details/fse-2026/fse-2026-research-papers/196/Failing-with-Purpose-Dangling-Coverage-Guided-Negative-Test-Generation-from-a-Mechan),
  [paper DOI](https://doi.org/10.1145/3797109), and
  [official artifact record](https://doi.org/10.5281/zenodo.19508213). The
  official abstract and artifact description were consulted; the full paper
  was not retrieved for this review.
- **Source-verified core:** the work mechanizes a P4 type system with SpecTec,
  identifies typing-rule premises whose violation should produce type errors,
  defines dangling coverage over those negative obligations, and guides
  mutation of well-typed programs toward them.
- **Project analogue:** the specification-derivation pilot, checker-rule
  inventory, and current axiom/`isUnsafe` investigation infer and exercise
  candidate boundaries from implementations and artifacts.
- **Potentially useful insight:** a candidate Lean assurance object may need a
  judgment or applicability context, dependent premises, a target premise,
  and the expected effect of violating that premise.
- **Important mismatch:** P4 starts from an authoritative, machine-readable
  rule system whose premises are enumerable. Many Lean Assurance Lab findings
  start from implementation behavior. The project cannot infer equivalent
  completeness, semantic authority, or a coverage denominator from that
  analogy.
- **Maturity:** `PROJECT_ANALOGUE`.
- **Reconsider when:** a bounded Lean subsystem has mechanically enumerable
  premises, or implementation-derived findings can be promoted while keeping
  authority and uncertainty explicit.
- **Planning/status context:** completed `F-SPEC-DERIVATION-PILOT` and
  `F-CHECKER-RULE-INVENTORY` are recorded under
  [Recently Completed](../RESEARCH_STATUS.md#recently-completed); the relevant
  unresolved trust-policy work is
  [`F-AXIOM-UNSAFE-DECLARATIONS`](../RESEARCH_STATUS.md#active).

## JEST and N+1-version differential testing

- **Lineage and sources consulted:** Park et al., *JEST: N+1-Version
  Differential Testing of Both JavaScript Engines and Specification*;
  [authors' full paper](https://plrg.korea.ac.kr/assets/data/publication/icse21-park-jest.pdf),
  [ICSE 2021 proceedings page](https://2021.icse-conferences.org/details/icse-2021-papers/43/JEST-N-1-version-Differential-Testing-of-Both-JavaScript-Engines-and-Specification),
  and [DOI](https://doi.org/10.1109/ICSE43902.2021.00015).
- **Source-verified core:** JEST adds a mechanized specification to multiple
  implementations, synthesizes programs from specification syntax and
  semantics, injects assertions, executes the tests across implementations,
  and analyzes specification/implementation disagreement. Its localization
  method also uses statistical and majority signals.
- **Project analogue:** designated-reference expected outcomes, generated
  semantic witnesses, and full cross-validator observation vectors keep an
  expected result distinct from implementation results.
- **Potentially useful insight:** expected semantics and implementation
  observations should be first-class, separate evidence. A disagreement can
  implicate a specification, a checker, a reconstruction path, or an
  unresolved contract.
- **Important mismatch:** Lean Assurance Lab does not have one comparably
  complete mechanized specification, and checker majority is not a Lean
  semantic oracle. Counts may summarize observations but cannot establish an
  expected result.
- **Maturity:** `PROJECT_ANALOGUE`.
- **Reconsider when:** a bounded semantic source can generate expected results
  independently of the compared checkers, while disagreements still retain
  full per-checker provenance.
- **Planning/status context:** the closest planned work is
  [`D-IMPLEMENTATION-SPECS`](../RESEARCH_STATUS.md#future-directions), which
  explicitly begins with characterization rather than conformance claims.

## Feature-sensitive and selective conformance testing

- **Lineage and sources consulted:** Park et al., *Feature-Sensitive Coverage
  for Conformance Testing of Programming Language Implementations*;
  [authors' full paper](https://plrg.korea.ac.kr/assets/data/publication/pldi23-park-jestfs.pdf)
  and [DOI](https://doi.org/10.1145/3591240). The 2026 selective extension was
  consulted through its [official ACM record](https://doi.org/10.1145/3808231)
  and [official artifact record](https://doi.org/10.5281/zenodo.19436781); its
  full paper was not retrieved.
- **Source-verified core:** feature-sensitive coverage refines requirements
  over a mechanized specification by retaining enclosing language-feature
  context; feature-call-path-sensitive coverage retains call-path context.
  The selective extension targets implementation-relevant feature stacks to
  control test growth.
- **Project analogue:** matrices already preserve bounded families and exact
  boundary context, but no current artifact provides a mechanically justified
  denominator over Lean rules.
- **Potentially useful insight:** the same apparent premise may require
  different evidence under different enclosing features or rule-call paths.
- **Important mismatch:** source subsystem, function, operator, or current
  rule-inventory diversity is not feature-sensitive semantic coverage. Calling
  it that would claim a denominator that the project does not have.
- **Maturity:** `PROJECT_ANALOGUE`.
- **Reconsider when:** a bounded subsystem has enumerable semantic premises
  and a mechanical test-to-premise and feature-context mapping.
- **Planning/status context:** there is no active or planned coverage item in
  [Research Status](../RESEARCH_STATUS.md). Completed bounded matrices remain
  characterization evidence, not a semantic-coverage program.

## SpecTec, ESMeta, and mechanized-specification architectures

- **Lineage and sources consulted:** SpecTec's
  [full paper](https://people.mpi-sws.org/~rossberg/papers/spectec1.pdf),
  [DOI](https://doi.org/10.1145/3656440), and
  [official overview](https://github.com/Wasm-DSL/spectec/blob/main/spectec/doc/Overview.md);
  ESMeta's [official repository documentation](https://github.com/es-meta/esmeta)
  and the [full CACM article](https://ecma-international.org/wp-content/uploads/JavaScript-Language-Design-and-Implementation-in-Tandem.pdf)
  ([DOI](https://doi.org/10.1145/3624723)).
- **Source-verified core:** SpecTec defines WebAssembly semantics in a DSL and
  derives multiple representations from that semantic source; its 2024 paper
  leaves some testing and prover backends as future work. ESMeta extracts a
  mechanized ECMAScript representation and uses it to support execution,
  conformance-test synthesis, visualization, and analyses.
- **Project analogue:** one stable boundary identity could organize controls,
  negative artifacts, generator targets, infection evidence, and checker
  observations even when those artifacts are produced by replaceable methods.
- **Potentially useful insight:** semantic identity and generated evidence need
  not be the same object.
- **Important mismatch:** Lean semantic authority may be incomplete, plural,
  or disputed. This is an architectural lesson, not a proposal to build
  “SpecTec for Lean” or to manufacture a single authoritative source.
- **Maturity:** `PROJECT_ANALOGUE`.
- **Reconsider when:** the project has a bounded semantic identity whose
  authority is explicit and for which multiple derived artifacts would reduce
  drift without hiding disagreement.
- **Planning/status context:** the closest planned work is
  [`D-IMPLEMENTATION-SPECS`](../RESEARCH_STATUS.md#future-directions).

## Reach → Infect → Propagate → Reveal

- **Lineage and sources consulted:** DeMillo and Offutt's constraint-based
  mutation work ([DOI](https://doi.org/10.1109/32.92910)); Zhang et al.'s
  mutation-test-process study
  ([authors' full paper](https://lingming.cs.illinois.edu/publications/icsm2010.pdf),
  [DOI](https://doi.org/10.1109/ICSM.2010.5609672)); and Vercammen et al.'s
  reachable mutant schemata work ([DOI](https://doi.org/10.1002/stvr.1865)).
- **Source-verified core:** mutation-directed work separates execution of a
  mutated location, immediate state divergence or infection, propagation, and
  observable failure.
- **Project analogue and local evidence:** the
  [`nanoda-0001` experiment](../../results/research/reach-infect/nanoda-0001.json)
  mechanically reduced 67 covering tests to one dynamically infecting test,
  which was also the sole known killer, while preserving instrumented baseline
  outcomes. The larger interpretation is reviewed in
  [Research-Backed Improvements](RESEARCH_BACKED_IMPROVEMENTS.md#1-reach-infect-propagate-reveal).
- **Potentially useful insight:** a semantic-negative-test account may have
  related stages:

  `rule applicable → target reached → target premise violated → violation propagates → observable rejection`

- **Important mismatch:** this correspondence is a Lean Assurance Lab
  hypothesis, not a claim verified by the mutation literature. Mutation
  infection is not automatically semantic-premise violation; competing
  violations, earlier rejection, skipping, and reconstruction can break the
  sequence.
- **Maturity:** `PILOTED (mutation-level reach/infection only)`.
- **Reconsider when:** several rule families can mechanically distinguish
  applicability, reach, target violation, competing violations, and the final
  observation without altering baseline behavior.
- **Planning/status context:** no active item in
  [Research Status](../RESEARCH_STATUS.md); the prior research review proposes
  a wider experiment but does not activate it.

## Semantics-directed artifact generation

- **Lineage and sources consulted:** Li et al., *Semantic Reification: A New
  Paradigm for Random Program Generation*
  ([authors' full paper](https://connglli.github.io/pdfs/reify_pldi26.pdf),
  [DOI](https://doi.org/10.1145/3808268)); the official PLDI entry and artifact
  for *Enumerating Ill-Typed Programs for Testing Type Analyzers*
  ([paper page](https://pldi26.sigplan.org/details/pldi-2026-papers/77/Enumerating-Ill-Typed-Programs-for-Testing-Type-Analyzers),
  [DOI](https://doi.org/10.1145/3808320),
  [artifact](https://doi.org/10.5281/zenodo.20679048)); and the P4 sources above.
- **Source-verified core:** Semantic Reification constructs programs from a
  selected control-flow/path semantics using symbolic reasoning and
  semantics-preserving composition. The ill-typed-program work constructs
  guaranteed type incompatibilities. The P4 work targets selected rule-premise
  violations.
- **Project analogue:** the deterministic universe-ownership template encoded
  the relevant environment condition and found a baseline/mutant distinction
  with its first generated candidate.
- **Potentially useful insight:** keep a target such as “satisfy premises
  A/B/C, violate target P, avoid competing violation Q” stable while allowing
  templates, graph rewriting, bounded enumeration, constraint solving, or
  LLM-guided realization to remain replaceable.
- **Important mismatch:** a rejected Lean export can contain several competing
  defects. Generation must establish the intended violation and its isolation;
  obtaining rejection alone is insufficient.
- **Maturity:** `PROJECT_ANALOGUE`.
- **Reconsider when:** rule factoring can represent dependent premises and
  isolation, then reproduce one difficult existing witness with a replaceable
  realization strategy.
- **Planning/status context:** no active generator item in
  [Research Status](../RESEARCH_STATUS.md). This is a research direction, not
  an implementation directive.

## Metamorphic testing and equivalence modulo inputs

- **Lineage and sources consulted:** Le et al., *Compiler Validation via
  Equivalence Modulo Inputs*;
  [Microsoft Research project page](https://www.microsoft.com/en-us/research/publication/compiler-validation-via-equivalence-modulo-inputs/),
  [authors' full paper](https://www.cs.ucdavis.edu/~su/publications/emi.pdf), and
  [DOI](https://doi.org/10.1145/2594291.2594334).
- **Source-verified core:** EMI constructs variants equivalent to a program for
  a fixed set of inputs using information from executions, then compares
  compiler behavior on the variants.
- **Project analogue:** matched controls and structure-preserving probes show
  the value of related artifacts, but they are not presently justified
  metamorphic relations.
- **Potentially useful insight:** a mechanically justified
  semantics-preserving transformation could complement mutation and reduce the
  need for a wholly new oracle per artifact.
- **Important mismatch:** a proposed Lean transformation may change theorem
  identity, serialization authority, reconstruction behavior, trust policy, or
  semantics. Structural similarity is not proof that a contract is preserved.
- **Maturity:** `LITERATURE_ONLY`.
- **Reconsider when:** a narrow transformation has a proof or independent
  mechanical justification, with its guarantee explicitly bounded to the
  relevant revisions, configuration, and observation.
- **Planning/status context:** no active or planned item in
  [Research Status](../RESEARCH_STATUS.md).

## Mutation acceleration, composition, and trajectories

These related lines remain one entry so that mutation infrastructure does not
dominate the methods landscape merely because the current implementation uses
mutation heavily.

### Mutant schemata

- **Sources consulted:** Untch, Offutt, and Harrold, *Mutation Analysis Using
  Mutant Schemata* ([DOI](https://doi.org/10.1145/154183.154265)); only primary
  publication metadata and abstract were retrieved.
- **Source-verified core:** many selectable mutant alternatives are encoded in
  one metaprogram to amortize compilation and execution costs.
- **Project analogue:** the repository review analyzed a selectable-mutant
  build path, but did not implement it; independently materialized mutants
  remain the certification path.
- **Potential insight and mismatch:** compilation amortization might help only
  if build cost dominates, while schemata can change build and runtime
  behavior. An exact equivalence and performance benchmark is required rather
  than an assumed speed benefit.
- **Maturity and reconsideration:** `PROJECT_ANALOGUE`; reconsider only under
  the benchmark and equivalence conditions in
  [Research-Backed Improvements](RESEARCH_BACKED_IMPROVEMENTS.md#2-mutant-schemata).

### Higher-order mutation

- **Sources consulted:** Jia and Harman, *Higher Order Mutation Testing*
  ([publisher source](https://doi.org/10.1016/j.infsof.2009.04.016)); the 2026
  behavioral-clustering extension was consulted through its
  [official IEEE record](https://doi.org/10.1109/ICSTW72326.2026.00049).
- **Source-verified core:** higher-order mutants apply more than one mutation;
  strongly subsuming higher-order mutants are harder to kill and subsume the
  constituent first-order kill behavior. Recent work uses first-order
  behavioral similarity to guide combinations.
- **Project analogue:** the project records first-order mutants and checker
  vectors but has not piloted higher-order mutation.
- **Potential insight and mismatch:** combinations might expose interaction
  trajectories, but they can entangle independent assurance boundaries.
  Complete frozen first-order behavior vectors and compatible edits are
  prerequisites; early-stop vectors cannot establish subsumption.
- **Maturity and reconsideration:** `LITERATURE_ONLY`; the prior disposition is
  `DEFER`, not active priority. Reconsider only after the prerequisites in
  [Research-Backed Improvements](RESEARCH_BACKED_IMPROVEMENTS.md#3-strongly-subsuming-higher-order-mutants)
  hold.

### Argus-style mutation trajectories

- **Sources consulted:** Zhang et al., *Argus: A Guided and Traceable Mutation
  Testing Engine*; [authors' full paper](https://www.cs.ucr.edu/~qzhang/argus-fse26.pdf),
  [official FSE 2026 page](https://conf.researchr.org/details/fse-2026/fse-2026-demonstrations/12/Argus-A-Guided-and-Traceable-Mutation-Testing-Engine), and
  [DOI](https://doi.org/10.1145/3803437.3806410).
- **Source-verified core:** Argus models mutation as seed-controlled walks over
  AST locations and records compositional edit paths/trees, replay manifests,
  and traces.
- **Project analogue:** deterministic mutation manifests and provenance exist,
  but the project does not implement compositional AST-walk trajectories.
- **Potential insight and mismatch:** reproducible semantic edit trajectories
  may be more interpretable than unordered compound changes, but composition
  can destroy rule attribution. The tool paper does not establish benefit for
  Lean Assurance Lab.
- **Maturity and reconsideration:** `LITERATURE_ONLY`; reconsider only after
  first-order boundary isolation and complete behavior evidence are mature.

- **Planning/status context for this cluster:** no active item in
  [Research Status](../RESEARCH_STATUS.md). `D-MUTATION-SURFACE` is a different
  [future direction](../RESEARCH_STATUS.md#future-directions), not authorization
  for these methods.

## Symbolic semantic adequacy and residual semantic freedom

- **Lineage and sources consulted:** the
  [NIST specification-based coverage report](https://doi.org/10.6028/NIST.IR.6403),
  specification/behavioral adequacy work
  ([full paper](https://eprints.whiterose.ac.uk/id/eprint/95332/1/WRRO_95332.pdf),
  [DOI](https://doi.org/10.1002/stvr.1575)), semantic mutation
  ([full paper](https://eprints.whiterose.ac.uk/id/eprint/196292/1/1_s2.0_S0167642311000992_main.pdf),
  [DOI](https://doi.org/10.1016/j.scico.2011.03.011)), and symbolic model-based
  mutation ([primary preprint](https://arxiv.org/abs/1202.6123)).
- **Source-verified core:** these sources study specification-derived coverage,
  inferred behavioral models, semantic/specification mutation, and symbolic
  reasoning over bounded mutation or refinement conditions.
- **Project interpretation:** *residual semantic freedom* is a separate toy-model
  idea, not a metric established by those papers. Mutation samples alternative
  semantics individually; a symbolic model could represent a bounded family of
  alternatives simultaneously.
- **Potentially useful insight:** an explicit finite hypothesis class can make
  “what alternatives remain observationally possible?” a mechanical question.
- **Important mismatch:** without an explicit bounded hypothesis class,
  observation model, and equivalence relation, any number would be
  uninterpretable. It must not be generalized to Lean semantics or mixed with
  the current mutation score.
- **Maturity:** `LITERATURE_ONLY`.
- **Reconsider when:** as a separate finite toy-language experiment outside
  this repository; do not implement or report a Lean percentage here.
- **Planning/status context:** no active or planned item in
  [Research Status](../RESEARCH_STATUS.md); the conceptual disposition remains
  in [Research-Backed Improvements](RESEARCH_BACKED_IMPROVEMENTS.md#5-behavioral-adequacy-and-semantic-test-strength).

## Independent-checker diversity

- **Lineage and sources consulted:** the
  [official Lean proof-validation guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/),
  Knight and Leveson's study of independently developed versions
  ([DOI](https://doi.org/10.1109/TSE.1986.6312924)), the JEST paper above, the
  local [checker-rule inventory](../../results/investigations/checker-rule-inventory.md),
  and the [Collatz case study](../CASE_STUDY_COLLATZ.md).
- **Source-verified core:** independently developed implementations can still
  exhibit coincident failures; Lean's validation guide explicitly retains the
  risk that relied-upon checkers share an effective defect. JEST preserves a
  mechanized specification as a distinct source alongside implementations.
- **Local analogue and evidence:** cross-validation records implementation
  families, revisions, compatibility, positive controls, and full observation
  vectors. The Collatz case demonstrates why checker count alone does not
  establish assurance.
- **Potentially useful insight:** evidence diversity depends on semantic source,
  code lineage, parser/reconstruction route, shared algorithms, configurations,
  and tested blind spots—not merely checker count.
- **Important mismatch:** those dimensions do not support an invented scalar
  independence score. Independence is claim- and failure-mode-relative.
- **Maturity:** `EVIDENCE_SUPPORTED` for preserving lineages and full vectors;
  not for claiming checker independence in general.
- **Reconsider when:** a concrete assurance claim can identify plausible shared
  failure modes and add evidence from a genuinely different semantic or
  reconstruction source.
- **Planning/status context:** completed cross-validation work appears under
  [Recently Completed](../RESEARCH_STATUS.md#recently-completed); the closest
  planned extension is
  [`D-IMPLEMENTATION-SPECS`](../RESEARCH_STATUS.md#future-directions).

## Durable guardrails

- Do not turn this map into a second backlog; add or activate work only through
  [Research Status](../RESEARCH_STATUS.md).
- Do not use majority voting as a Lean semantic oracle.
- Do not report the current characterized rule set as semantic coverage or
  calculate an aggregate semantic-coverage percentage.
- Do not infer conformance authority from one designated implementation without
  recording that epistemic limitation.
- Do not treat matched controls as metamorphic relations without a mechanical
  preservation argument.
- Do not reduce checker diversity to a count or independence score.
- Keep semantic targets stable where possible while generators, mutants,
  validators, and other evidence strategies remain replaceable.
