# Research-Backed Improvements: Near-Term Plan and Future Work

Status: proposal review, not an implementation directive
Review date: 2026-08-27
Repository revision at the start of the review: `829c72efb56ef83c8ad2cfd2c34bf1fab914670b`

## Decision summary

The short-term work should strengthen the existing assurance loop rather than
replace it:

1. add reusable dynamic infection observations for a deliberately narrow subset
   of mutation operators;
2. make held-out generalization metrics explicit across both validators and
   mutation families;
3. represent real-disagreement lineage as typed, machine-readable evidence;
4. benchmark mutant schemata before deciding whether to build them; and
5. use the infection work as the first stage of a conservative equivalent or
   unreachable-mutant pipeline.

Higher-order mutation should wait for a complete first-order behavioral matrix.
The symbolic semantic-adequacy toy model is independent exploratory research;
it is not an immediate direction for Lean Assurance Lab and should not be
implemented in this repository now.

Recommendations:

| Direction | Recommendation | Earliest useful action |
|---|---|---|
| Reach → Infect → Propagate → Reveal | `IMPLEMENT_NEXT` | Generalize the successful `nanoda-0001` infection probe to a small operator subset. |
| Held-out validator and fault-model metrics | `IMPLEMENT_NEXT` | Add explicit opportunity, novel-transfer, and family-transfer counts to rotating-fold reports. |
| Durable real-defect provenance | `IMPLEMENT_NEXT` | Add typed lineage edges from mutation through upstream disposition. |
| Mutant schemata | `EXPERIMENT` | Benchmark 8–12 compatible mutants; keep independent builds as certification. |
| Equivalent and unreachable classification | `EXPERIMENT` | Reuse infection probes and add evidence-scoped classifications. |
| Strongly subsuming higher-order mutants | `DEFER` | First collect complete first-order kill vectors for a bounded cohort. |
| Behavioral/symbolic semantic adequacy | `DEFER` | If desired, build a separate toy-language POC outside the main project. |

## Repository baseline used for this review

The following are current repository facts, not assumptions from the proposal:

- [`docs/DESIGN.md`](../DESIGN.md) describes per-test portable Rust source
  coverage, coverage-selected mutant execution, deterministic structure-aware
  witness generation, minimization, cross-validator checking, immutable
  held-out freezes, and content-addressed invalidation.
- [`mutation-model/catalog.json`](../../mutation-model/catalog.json) defines
  five active operator families: validation elision, predicate negation,
  relational boundary changes, equality discrimination, and binder-depth
  adjustment.
- [`results/assurance/current.json`](../../results/assurance/current.json)
  reports 65 evaluated Nanoda semantic mutants, 38 killed by the existing
  corpus, three killed by generated corpus additions, four classified
  equivalent, one reference-aligned case, 19 unresolved cases, and no cases
  classified unreachable.
- The same snapshot records 54 active mutation-batch builds taking 576.64
  seconds and 633 active mutation-batch executions taking 7,113.31 seconds.
  Compilation is material, but test execution is currently the larger cost.
- [`results/rotating-heldout/milestone-7/report.json`](../../results/rotating-heldout/milestone-7/report.json)
  contains two folds. The original corpus killed one of two held-out mutants;
  the augmented corpus killed both. The report correctly warns that this is not
  a general transfer-rate estimate.
- All 65 evaluated mutants have a scheduled comparison, but only five have a
  full `comparison.json` with a complete or full-corpus difference set. Early
  stopping is appropriate operationally, but does not provide the complete
  mutant-by-test matrix needed by behavioral clustering or SSHOM analysis.
- [`results/investigations/kiota-universe-ownership/upstream-main.json`](../../results/investigations/kiota-universe-ownership/upstream-main.json)
  and its investigation manifest already bind the minimized witness, positive
  control, designated reference outcome, exact Kiota revision, binary/source
  hashes, and upstream issue. The artifact graph expresses file dependencies,
  but the semantic lineage is not yet a typed edge chain.
- The witness generator is not presently blind LLM search. It is bounded and
  deterministic. The `nanoda-0003` universe template found a witness on its
  first candidate; its metadata records 132 checker runs including
  minimization/final checks and 0.60 checker-seconds, while build preparation
  dominated the 21.44-second wall cost.

These facts change the priority of some proposals. In particular, schemata have
a bounded current payoff, and infection constraints should first improve
selection and survivor generation rather than be justified as an LLM-cost fix.

## Concrete Reach → Infect experiment

The review added a deliberately small, reproducible experiment:

- producer: [`scripts/experiment-nanoda-infection-funnel`](../../scripts/experiment-nanoda-infection-funnel)
- schema: [`schemas/infection-funnel.schema.json`](../../schemas/infection-funnel.schema.json)
- result: [`results/research/reach-infect/nanoda-0001.json`](../../results/research/reach-infect/nanoda-0001.json)

`nanoda-0001` suppresses the rejection of a theorem whose inferred type is not
`Prop`. Its infection condition is available at the mutation site without
solving Lean semantics from scratch:

```text
declaration is Theorem
and !is_zero(ensure_sort(infer(theorem_type)))
```

The experiment clones the exact clean Nanoda revision, replaces the predicate
with a semantically equivalent cached predicate plus an infection marker, builds
that instrumented checker, and evaluates coverage-selected tests. It also
requires every instrumented normalized outcome to equal the recorded baseline.

Observed funnel:

```text
197 corpus tests
  ↓ source-line coverage
67 covering tests
  ↓ input contains at least one theorem declaration
63 structurally possible infection candidates
  ↓ exact runtime infection predicate
1 infecting test
  ↓ full recorded baseline/mutant comparison
1 killing test
```

The single test at both final stages is `tutorial/012_nonPropThm`. Thus dynamic
infection reduced the coverage-selected candidate set by 98.5% and retained
every known killer. Relative to the existing early-stop schedule, which reached
the killer after seven executions, perfect infection-first ordering would have
needed one mutant execution (six fewer, an 85.7% reduction for this mutant).

This is strong feasibility evidence, not yet a system-wide speedup result. The
profiling run executed 63 inputs and took 483.47 checker-seconds because it also
classified large accepted corpus artifacts. Infection observations must be
reused across compatible mutants, collected alongside an existing baseline
pass, or derived cheaply enough to beat direct mutant execution.

The experiment also explains an existing witness-generation success.
`nanoda-0003` infects precisely when a referenced constant universe level is not
owned by the enclosing declaration. The existing
`universe-ownership-template` constructs that condition directly and found a
distinction on attempt one. The proposed infection layer should capture this as
declarative operator metadata rather than replace the successful template.

## 1. Reach, Infect, Propagate, Reveal

### Problem addressed

Line coverage proves only reachability. Many covering tests cannot change the
mutated expression's value or trigger an elided check, so they consume mutant
execution time and give survivor search no semantic target.

### Relevant prior research

DeMillo and Offutt's constraint-based method derives reachability and necessity
(infection) constraints and solves them to generate mutation-directed tests
([DOI 10.1109/32.92910](https://doi.org/10.1109/32.92910)). More recent dynamic
symbolic execution work instruments mutant-killing constraints and reports that
weak-mutation guidance can outperform block-coverage-only generation
([Zhang et al., 2010](https://doi.org/10.1109/ICSM.2010.5609672)). The modern
reachable-schemata study explicitly situates reachability and weak mutation in
the RIPR model
([Vercammen et al., 2024](https://doi.org/10.1002/stvr.1865)).

### Relationship to the current implementation

The line-to-test index already implements `REACH`. Mutation specs retain the
operator and source expression. The witness generator already contains one
hand-authored infection-satisfying universe template. What is missing is a
durable infection-condition vocabulary and an observation index analogous to
coverage.

Mechanically tractable initial subset:

| Operator form | Infection condition | Initial mechanism |
|---|---|---|
| `BOOL_NEGATE` | Original and mutant Boolean results differ whenever the expression is evaluated. | Treat reach as weak infection; validate operator/type assumptions. |
| `< ↔ <=`, `> ↔ >=` | Operands are equal at the changed boundary. | Runtime operand probe; SMT only for simple integer/arity inputs. |
| `== ↔ !=` | Equality predicate result flips, subject to the concrete Rust `PartialEq::ne` implementation. | Runtime result probe and type audit. |
| theorem `SKIP_VALIDATION` (`nanoda-0001`) | Inferred theorem sort is nonzero. | Demonstrated runtime predicate. |
| universe-ownership `SKIP_VALIDATION` (`nanoda-0003`) | A used universe is absent from the declaration's owned parameters. | Existing structural template plus runtime confirmation. |
| binder-depth `+1 → +0` | The computed depth differs on reach; semantic relevance additionally needs a bound variable at/above the affected cutoff. | Runtime weak probe plus expression-shape filter. |

Validation elisions such as `assert_def_eq`, `infer_sort_of`, or assertions whose
failure is expressed by panic are harder. Calling a validation twice can alter
caches or cost, and `catch_unwind` can change behavior. These should use a
dedicated non-mutating predicate only where Nanoda exposes one, or a paired
baseline/mutant probe; they should not be forced into an unsound generic rule.

### Expected benefit

- Fewer mutant executions and better early-stop ordering.
- Concrete goals for witness construction rather than generic structural
  perturbations.
- A shared weak-mutation layer for later equivalence/unreachability analysis.
- Better diagnoses: `REACHED_NOT_INFECTED`, `INFECTED_NOT_REVEALED`, and
  `REVEALED` are more informative than one survivor state.

### Soundness and reproducibility risks

- Instrumentation can change optimizer decisions, panic behavior, caches,
  thread schedules, or timeouts.
- A source-level condition may be sufficient only under assumptions about Rust
  traits or Nanoda invariants.
- An infection observation is input/configuration/revision specific.
- Solver `UNSAT` is only global evidence if the encoding covers the complete
  semantic domain. A bounded model yields only `BOUNDED_UNSAT`.

Mitigation: bind source, toolchain, configuration, condition generator,
instrumented source, input hashes, and outcome-preservation checks. Continue to
certify kills with independently materialized mutants.

### Estimated implementation complexity

Medium for three to five operator templates; high for general symbolic Nanoda.
Do not begin with general Rust symbolic execution.

### Required new artifacts/schema

- `infection-condition` record: mutant/operator, expression/type assumptions,
  condition kind, scope (`STATIC`, `DYNAMIC`, `BOUNDED_SYMBOLIC`), and producer.
- `infection-observation` index keyed by mutant identity, test/input hash,
  checker revision, config hash, and instrumentation hash.
- explicit evidence labels: `REACHED`, `INFECTED`, `NOT_INFECTED_FOR_INPUT`,
  `BOUNDED_UNSAT`, and `UNRESOLVED`.

The experiment schema added in this review is intentionally narrower than the
eventual production schema.

### Smallest useful next experiment

Add probes for one relational-boundary mutant and one equality-discrimination
mutant with complete full-comparison evidence. Collect infection during one
instrumented baseline pass, then compare covering, infecting, and killing sets.

### Objective success/failure criterion

Success: across at least three mutants from at least two operator families,
infection filtering retains 100% of known killers and reduces covering tests by
at least 50%, with collection cost amortizing within the measured batch.

Failure: any known killer is filtered out, outcome-preservation checks fail, or
total wall time is not lower after amortization. In that case retain infection
only as diagnostic/witness guidance.

### Recommendation

`IMPLEMENT_NEXT`, narrowly and empirically. General SMT encoding is not the next
step. Prefer custom bounded enumeration for Lean levels/indices and use SMT only
when the mutation condition is already a faithful small integer/Boolean formula.

## 2. Mutant schemata

### Problem addressed

Nanoda mutants are independently compiled. Schemata could activate one mutation
at runtime in a single binary and remove most repeated compilation.

### Relevant prior research

Mutant schemata encode mutants in a metaprogram
([Untch, Offutt, and Harrold, 1993](https://doi.org/10.1145/154183.154265)). The
recent Clang study combines schemata with per-test reachability and reports that
reachable schemata can materially reduce execution, while also documenting
compiler integration and invalid-mutant constraints
([Vercammen et al., 2024](https://doi.org/10.1002/stvr.1865)).

### Relationship to the current implementation

Generated Nanoda mutations are localized AST replacements with deterministic
IDs, which is favorable for schema generation. However, Rust expression types,
borrowing, diverging/panic expressions, and statement/expression placement mean
not every current mutation can share one guard form.

The current cost record bounds the benefit: 54 builds cost 576.64 seconds,
while active batch execution costs 7,113.31 seconds. Eliminating all compilation
would improve that combined recorded phase by only about 7.5% (roughly 1.08×),
before schema runtime overhead. This is worthwhile only if future mutant volume
or rebuild cost grows.

### Expected benefit

Approximately one build per compatible cohort rather than one per mutant, plus
a natural place to collect reach/infection observations.

### Soundness and reproducibility risks

- LLVM may optimize inactive branches, share computations, or change panic and
  inlining behavior.
- A global selector can introduce races in Nanoda's multi-threaded checker.
- Schema-only evidence could make a tool bug look like a corpus result.

Use an immutable selector set before process start, never mutate it during a
run, and keep schema results provisional.

### Estimated implementation complexity

Medium for a homogeneous expression cohort; high for all operator forms.

### Required new artifacts/schema

- schema-batch manifest binding every mutant to a selector and source rewrite;
- schema binary/config/toolchain hashes;
- per-mutant certification comparison between schema-selected and independent
  binaries on all observed distinguishing and control inputs.

### Smallest useful experiment

Encode 8–12 same-typed relational/equality mutants in one binary. Compare build
time, per-test overhead, outcomes, exit codes, and timeout behavior against
independent builds.

### Objective success/failure criterion

Proceed only if schema selection matches independent mutants on every scheduled
test and witness/control, reduces cohort build wall time by at least 4×, and adds
less than 10% median checker overhead. Otherwise the current independent path is
cheap enough to retain exclusively.

### Recommendation

`EXPERIMENT`. Schemata may accelerate search; independently materialized mutants
must remain the certification path.

## 3. Strongly subsuming higher-order mutants

### Problem addressed

Interacting validator mistakes may produce faults harder to reveal than either
first-order component.

### Relevant prior research

Jia and Harman define a strongly subsuming HOM as one whose killing set is a
subset of the intersection of its constituent FOM killing sets and use
search-based methods rather than exhaustive enumeration
([Jia and Harman, 2009](https://doi.org/10.1016/j.infsof.2009.04.016)). A recent
graph-based study clusters FOMs by behavioral similarity to select less-useless
HOM combinations
([ICSTW 2026](https://doi.org/10.1109/ICSTW72326.2026.00049)).

### Relationship to the current implementation

Subsystem labels and deterministic source edits can constrain combinations.
The result corpus is not yet sufficient for behavioral-graph selection: 65
mutants have early-stop scheduled outcomes, but only five have full comparison
files. A truncated vector cannot establish kill-set intersections or SSHOM
subsumption.

Potential future interactions should be semantically motivated: universe
ownership plus level comparison, declaration well-formedness plus definitional
equality, or binder-depth substitution plus reduction. Same-line overlapping
edits and combinations whose components cannot coexist should be rejected.

### Expected benefit

Potentially exposes interaction faults and tests the coupling assumption beyond
first-order models.

### Soundness and reproducibility risks

Combinatorial selection bias, cancellation that creates accidental equivalence,
unclear metric denominators, and loss of first-order interpretability.

### Estimated implementation complexity

High, because complete behavior vectors and composition validation are
prerequisites.

### Required new artifacts/schema

- complete FOM-by-test outcome matrix for a frozen bounded cohort;
- combination manifest with compatibility and semantic rationale;
- constituent and HOM kill sets;
- SSHOM predicate and independent reproduction.

HOMs should be reported separately and never inflate the first-order mutation
score.

### Smallest useful experiment

After the matrix exists, select at most ten pairs within one subsystem whose
complete kill vectors overlap and whose edits are source-compatible. Evaluate
the formal SSHOM predicate; do not search all pairs.

### Objective success/failure criterion

Continue only if at least one independently reproduced SSHOM yields a new,
reference-adjudicated regression not redundant with constituent witnesses.

### Recommendation

`DEFER` until the first-order behavioral matrix and unresolved-mutant pipeline
are mature.

## 4. Equivalent and unreachable mutant classification

### Problem addressed

Nineteen current mutants remain unresolved, while four have focused equivalent
classifications and none are classified unreachable. Failed witness search must
not be mistaken for equivalence.

### Relevant prior research

Offutt and Craft use compiler optimizations and data-flow analysis to detect
classes of equivalent mutants
([1994](https://doi.org/10.1002/stvr.4370040303)). Constraint-based equivalence
work is closely related to infection satisfiability. These techniques are
partial detectors, not a general equivalence decision procedure.

### Relationship to the current implementation

The existing four equivalence findings are stronger than simple search failure:
they use entrypoint-specific semantic arguments in durable investigation
artifacts. The registry already distinguishes `EQUIVALENT`, `UNREACHABLE`,
`SURVIVED_WITHOUT_WITNESS`, and `UNKNOWN_EQUIVALENCE`, but it lacks a uniform
evidence schema and confidence/scope field.

Useful stages for Rust/Nanoda:

1. exact normalized source/AST identity after mutation;
2. compiler elimination evidence (LLVM IR/object function comparison under an
   exact toolchain), treated as configuration-scoped evidence;
3. call-graph and line-coverage unreachability for the declared entrypoint;
4. infection satisfiability or observed infection;
5. bounded domain equivalence for small level/index algebras;
6. adversarial witness search;
7. `UNRESOLVED`.

Binary equality is strong evidence for one exact build configuration but not a
language-level proof. LLVM IR difference is not evidence of semantic
inequivalence.

### Expected benefit

Cleaner denominators, less repeated survivor search, and precise explanations
of which semantic stage remains open.

### Soundness and reproducibility risks

The main risk is promoting bounded or configuration-specific evidence to global
equivalence. Classification labels must include scope and proof obligation.

### Estimated implementation complexity

Medium for syntactic/compiler evidence and reused infection probes; high for
bounded symbolic equivalence.

### Required new artifacts/schema

An `equivalence-evidence` record with classification, scope, assumptions,
method, bound, solver/toolchain identity, source/input hashes, and a mandatory
non-claim. Suggested labels:

```text
EQUIVALENT_PROVED
EQUIVALENT_AT_ENTRYPOINT
EQUIVALENT_FOR_BUILD_CONFIGURATION
UNREACHABLE_AT_ENTRYPOINT
NO_INFECTION_IN_BOUNDED_DOMAIN
UNRESOLVED
```

Only the first two should normally feed the current global equivalent count;
the others should remain separately scoped unless policy explicitly says
otherwise.

### Smallest useful experiment

Run syntactic/LLVM comparison and infection probing over the 19 unresolved
mutants. Attempt bounded solving only for level/index conditions with an
explicit small bound.

### Objective success/failure criterion

Success: mechanically narrow at least three unresolved cases without any later
counterexample and with all evidence scope preserved by reporting. Failure: the
pipeline mostly duplicates existing focused reasoning or creates ambiguous
classifications.

### Recommendation

`EXPERIMENT` after the initial infection infrastructure. Do not create an
automatic global `EQUIVALENT` label from optimizer output or solver timeout.

## 5. Behavioral adequacy and semantic test strength

### Problem addressed

Mutation score measures sampled alternative semantics, not how uniquely or
broadly a corpus characterizes validator behavior.

### Relevant prior research and closer prior art

Fraser and Walkinshaw infer behavioral models from input/output observations and
assess their predictive adequacy, rather than measuring symbolic freedom
directly
([2015](https://doi.org/10.1002/stvr.1575)). Ammann and Black mutate formal
specifications and use model checking to measure test sensitivity to
specification structure
([NIST publication](https://www.nist.gov/publications/specification-based-coverage-metric-evaluate-test-sets)).
Clark, Dan, and Hierons mutate language semantics rather than program syntax,
which is conceptually close to validator semantic fault models
([2013](https://doi.org/10.1016/j.scico.2011.03.011)). Symbolic model-based
mutation testing encodes reachability and refinement as constraints
([Aichernig and Jöbstl, 2012](https://arxiv.org/abs/1202.6123)).

The proposed “remaining semantic freedom” metric is not identical to these.
It requires a declared hypothesis class, prior or counting measure, bounds, and
an observational equivalence relation. Without them, a percentage of semantic
freedom is not well-defined and can be dominated by arbitrary encoding choices.

A closer near-term metric for this repository is distinguishing mutation
adequacy: reward tests that induce distinct mutant behavioral fingerprints, not
only a high killed count
([Shin et al., 2018](https://doi.org/10.1109/TSE.2017.2732347)). This can be
computed from a complete first-order outcome matrix without inventing a
symbolic semantic measure.

### Relationship to the current implementation

Current mutant outcomes, generated witnesses, validator disagreements, and
held-out folds could eventually test whether a proposed semantic-strength metric
predicts unseen validator/fault-family detection. Today there are only two
held-out folds and incomplete first-order behavior vectors, so there is not
enough empirical data to validate such a metric.

### Expected benefit

Long term: identify corpora that achieve the same mutation score through
different or more diverse behavioral observations. Short term: a behavioral
fingerprint matrix can improve test selection and later HOM search.

### Soundness and reproducibility risks

Arbitrary bounds, priors, grammar choices, solver counting approximations, and
confusing branch/path coverage with assertion strength. A scalar can hide
validator disagreements just as majority voting would.

### Estimated implementation complexity

High for symbolic semantic freedom; medium for a complete mutation fingerprint
matrix.

### Required new artifacts/schema

For any independent toy POC: language semantics, bounded hypothesis space,
counting measure, assertion semantics, solver/version, exact/approximate count,
and calibration faults. None is required in Lean Assurance Lab now.

For eventual repository validation: frozen behavioral matrices and correlation
results against held-out validators and held-out mutation families.

### Smallest useful experiment

Outside this project, use a finite toy language where the semantic hypothesis
space can be exhaustively enumerated. Compare the proposed metric with mutation
score and held-out fault detection across many generated programs/test sets.

Inside this project, only collect the complete matrix needed for other work;
do not label it symbolic semantic adequacy.

### Objective success/failure criterion

The toy metric is promising only if it predicts held-out semantic faults better
than mutation score and simple behavior-vector diversity across preregistered
examples, and remains stable under reasonable equivalent encodings/bounds.

### Recommendation

`DEFER`. Keep documentation of the idea, but treat the toy model as independent,
very experimental research and not an immediate Lean Assurance Lab direction.

## 6. Held-out fault models and cross-validator transfer

### Problem addressed

The current two-fold score demonstrates the protocol and one incremental gain,
but cannot support a general transfer claim. Generalization should be measured
across implementation and fault-model boundaries.

### Relevant prior research

Recent real-fault reproduction work finds that ordinary operator sets miss
important real-fault structures and argues for application-specific operators
([Ahmed et al., 2024](https://doi.org/10.1002/stvr.1874)). This supports held-out
fault families and real-defect evidence rather than relying on a single mutation
score as validation of the fault model.

### Relationship to the current implementation

The rotating-fold freeze/evaluate boundary is already the right foundation. One
fold is neutral because the original 197-test corpus already kills the Kiota
held-out mutant; the second is positive because the original corpus does not
kill the Lean4Lean mutant and the generated candidate does. Reporting only the
aggregate 0.5→1.0 score hides this difference unless the fold details are read.

### Expected benefit

Direct evidence of whether generated tests generalize across validators,
subsystems, operator families, and real disagreements.

### Soundness and reproducibility risks

Tiny denominators, opportunistic fold choice, leakage before freeze, treating an
incompatible validator as a negative, or counting a candidate that adds no
incremental value because the original corpus already kills the fault.

### Estimated implementation complexity

Low for metrics/schema; medium to high for acquiring independent folds.

### Required new artifacts/schema

Each fold should record:

- source validator, source mutation family/subsystem, and generation inputs;
- held-out validator, held-out family/subsystem, and whether both axes differ;
- eligibility/compatibility and exclusion reason;
- `original_killed`, `candidate_killed`, and `novel_transfer` where
  `novel_transfer = !original_killed && candidate_killed`;
- direction agreement and control validity;
- preregistered freeze identity.

Aggregate separately:

```text
transfer_successes / eligible_folds
novel_transfer_successes / novel_transfer_opportunities
cross_validator_successes / cross_validator_eligible
cross_family_successes / cross_family_eligible
cross_both_successes / cross_both_eligible
```

Always show raw numerators, denominators, and Wilson intervals when the sample is
large enough; never merge incompatible or unresolved folds into failures.

### Smallest useful experiment

Add two preregistered held-out-operator-family folds: generate only from family
A, freeze, and evaluate a family-B mutant. Prefer one same-validator/different-
family fold to isolate fault-model transfer and one different-validator/different-
family fold to test both axes.

### Objective success/failure criterion

The next milestone succeeds if the report mechanically separates opportunity
from success and at least four independent eligible folds cover two validators
and two fault families without leakage. A positive rate is descriptive until
the sample is materially larger.

### Recommendation

`IMPLEMENT_NEXT` for the metrics and freeze fields; accumulate experiments
gradually.

## 7. Durable real-defect provenance

### Problem addressed

The Kiota universe-ownership case is richly documented but its causal lineage
is distributed across mutation, survivor, witness, expected-outcome,
cross-validation, investigation, and issue artifacts. A process can find file
dependencies, but cannot query typed semantic relationships directly.

### Relevant prior research

This is primarily evidence/provenance engineering rather than a mutation
algorithm. The real-fault literature above motivates preserving the link
between synthetic fault models and independent defects so coupling claims can
be tested rather than narrated.

### Relationship to the current implementation

The artifact graph already binds content digests and invalidation dependencies.
The investigation manifest already records the upstream issue URL and exact
revisions. Extend these structures; do not introduce a second unconnected
provenance system.

### Expected benefit

- Mechanically query real-defect yield and mutation-to-independent-disagreement
  transfer.
- Preserve issue/fix/adjudication state across fresh processes.
- Prevent prose-only claims from entering assurance metrics.

### Soundness and reproducibility risks

An analogous behavior is not automatically the same root cause. Edge types must
distinguish `GENERATED_FROM`, `DISTINGUISHES`, `ANALOGOUS_BEHAVIOR`,
`REPRODUCES_ON`, `REPORTED_AS`, and `FIX_CONFIRMED_BY`; do not use a generic
`CAUSES` edge without proof.

### Estimated implementation complexity

Low to medium.

### Required new artifacts/schema

A schema-validated `finding-lineage` artifact containing typed nodes/edges,
content identities, exact validator revisions, expected-semantics evidence,
disclosure state, upstream issue/fix revisions, and unresolved/non-claim fields.
The artifact graph should depend on it and expose its lifecycle.

### Smallest useful experiment

Encode the existing `nanoda-0003` → generated/minimized witness → official/Kiota
disagreement → Kiota issue #3 chain. Validate every local edge and preserve the
“analogous behavior, root-cause relation unresolved” qualification.

### Objective success/failure criterion

A fresh script can answer “which mutation-derived witnesses exposed an
independent current-upstream disagreement, and what is its disposition?” using
only schema-validated repository artifacts, with no prose parsing.

### Recommendation

`IMPLEMENT_NEXT`. This is small, directly supports the project's central
scientific claim, and does not require architectural change.

## Prioritized milestones

### Milestone R1 — typed finding lineage

Add the lineage schema and encode the existing Kiota universe-ownership case.
Expose real-defect yield as raw counts with strict definitions. This is the
smallest high-value change.

### Milestone R2 — reusable infection pilot

Generalize the experiment to three mutants across at least two operator
families. Store revision-bound infection observations, verify baseline outcome
preservation, and measure end-to-end amortized cost. Integrate infection as
ranking first; hard filtering requires retained-killer evidence.

### Milestone R3 — held-out metric refinement

Add opportunity-aware and axis-specific transfer counts. Preregister and run at
least two held-out-family folds without changing the freeze boundary.

### Milestone R4 — conservative unresolved-mutant triage

Apply syntactic/compiler evidence and the R2 infection infrastructure to the 19
unresolved mutants. Keep bounded/configuration-scoped results separate from
global equivalence.

### Milestone R5 — schemata benchmark decision

Benchmark a homogeneous 8–12-mutant Rust schema cohort. Adopt it only as a
search acceleration layer if equivalence checks and measured speedup meet the
criterion above. Otherwise record the negative result and stop.

### Future prerequisites, not active milestones

- Collect complete FOM behavior vectors for a bounded cohort; then reconsider a
  constrained SSHOM experiment.
- If pursued independently, evaluate symbolic semantic adequacy in a finite toy
  language. Do not make Lean Assurance Lab depend on that POC.

## Bottom line

The strongest immediate evidence is not architectural speculation: one existing
Nanoda mutant admits an exact runtime infection predicate that collapses 67
covering tests to the sole known killer, and the successful universe-ownership
witness is already an informal infection-directed construction. Build a small,
reusable infection layer around those facts, improve held-out/real-defect
measurement, and keep certification on independently materialized mutants.
Everything else should earn its place through bounded experiments.
