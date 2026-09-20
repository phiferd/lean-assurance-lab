# Representation-preserving metamorphic pilot

Item `METAMORPHIC-REPRESENTATION-PILOT-1`, frontier
`F-DISCOVERY-AND-CONFORMANCE`, selected READY and unstarted on 2026-09-20.
This is one staged experiment, not a series of source-only planning items.

## Question and beneficiary

For a precisely supported NDJSON fragment, does changing only a permitted
representation detail change a checker's semantic acceptance of the same
declarations and expression graph? The primary relationship is within each
checker between original and variant; agreement between checkers is not the
semantic oracle.

The intended shared assets are a small transformation tool, an independently
auditable preservation check, exact reusable original/variant pairs and a
complete observation matrix. Arena and independent checker maintainers are
potential beneficiaries; contribution requires demonstrated usefulness and
duplicate/contract review, not merely another generated file.

## Finite allocation

All preparation, investigation, implementation, diagnosis and repair share
**360 cumulative active minutes (21,600 seconds)**. Queue encoding is four
90-minute allocations; checkpoints and work intervals do not consume or reset
whole allocations. Use paired UTC/monotonic interval accounting and a remaining
active-second ceiling under `docs/RESEARCH_WORKFLOW.md`.

- At most 16 read-only literature/source/duplicate/setup requests, including
  failures and dependency/archive downloads. Prefer retained bound sources and
  working local toolchains. No external writes.
- At most four build reservations, each at most 600 seconds; failed/interrupted
  and compiling-test invocations consume a reservation.
- At most eight tooling-test process attempts, each at most 120 seconds, with
  finite case sets recorded before each run. Every invocation of a checker or
  semantic validation API, including one hidden in a tooling test, additionally
  consumes its checker budget.
- At most 12 original artifacts, four transformation kinds and 48 variants.
  Each input/output is at most 1 MiB and 20,000 records; at most 60 MiB retained
  scientific payload. Bind lower limits if the independent decoder needs them.
- Exactly two implementation lineages if the scientific phase is reached;
  at most 120 checker process attempts at 30 seconds each, including baselines,
  failed attempts and reruns. At most 96 attempts in the initial frozen matrix;
  reserve at least 24 for fixed-pair diagnosis or confirmation. Twelve originals
  times two transformations plus originals on two checkers would use 72.
- Combined actual build, tooling-test and checker process wall time at most
  6,960 seconds. Remaining active time can impose a tighter bound. Input
  generation and preservation audit count within tooling attempts/caps; stream
  records and do not materialize an unbounded graph expansion.
- Per-process memory ceiling 2 GiB, with verified host-supported enforcement
  and process-tree termination/cleanup before launch. If the existing runner
  cannot enforce/observe this safely, diagnose within the same item before
  running; do not claim a memory limit from an unsupported setting.

Zero proof search, kernel-source mutation, production-checker edits, external
research writes or milestone advancement. Repository validation at closure is
administrative, separately logged, and cannot be used to run the pilot's
scientific cases outside these counters.

## A. Entry and source/reuse gate

When execution is requested, commit a fresh work record identifying the owner,
plan, starting queue/status, cumulative-time origin, retained evidence and request
log. Mark the selected item ACTIVE through the existing entry-review path before
substantive research. This queue-selection task does not perform that entry.

Use at most 90 of the total 360 active minutes for focused literature/reuse,
format/import contract and local-profile feasibility. Record dated primary
sources, exact source identities, scope and a reuse/extend/build-only-the-missing-
part/stop decision. The previous methods map is explicitly a background snapshot.
Reuse existing NDJSON parsing, observer adapters and accounting where their
contracts fit; do not create a general validation framework.

Candidate transformations are dependency-respecting reordering with complete
contiguous reference renumbering, or legal interleaving of independent record
kinds. These are candidates, not established legal relations. Retained Nanoda
source requires continuous back references and rejects duplicate interned
Name/Level/Expr records. Therefore arbitrary sparse-ID permutations and
duplicate-versus-shared encodings are NOT default legal transformations.
Declaration order, reserved names, binder levels, universe parameters,
reconstruction metadata and configuration-sensitive admission need explicit
treatment. Never change a semantic field just to create a difference.
Initially restrict reordering to declaration-free blocks, preserving header,
declaration sequence and mutual-inductive grouping. Distinguish typed name,
level and expression references from ordinary integer payloads; never remap
every integer generically. Preserve implicit zero entries and uniqueness.

Two existing local official-Lean/Nanoda profiles supply a feasibility path, but
their presence is not a fresh source/binary attestation. Prefer exact usable
profiles within setup bounds; bind source, exporter/parser, binary, toolchain,
configuration and observation semantics before selection. A pinned historical
profile supports a claim about that profile, not current upstream. Keep direct
raw diagnostics: a wrapper that collapses parser failure or panic into REJECT
must not turn those failures into semantic refusal evidence.

The gate passes only with at least one justified legal transformation, two
supported profiles, a finite original-selection rule, an independent preservation
design and a named useful output. Failure yields an evidence-bound contract,
setup or oracle boundary after feasible local repairs are exhausted, not another
unbounded design successor. Passing proceeds within THIS item.

## B. Freeze scientific design, then implement

Before generating variants or running semantic checks, commit the scientific
manifest: exact original cohort selected by predeclared format/size/features,
all original byte hashes, prior-outcome exposure, exact observer identities,
transformation domains/algorithms and deterministic seed, preservation semantics,
finite generation work bounds, expected within-checker relationships, diagnostic
classification rubric and complete maximum observation matrix.
Specify a nonidentity representation-delta check for each transformation kind.
Identity or inapplicable outputs remain recorded, but are ineligible metamorphic
comparisons and do not count as new coverage. Whitespace/key-order changes alone
are controls, not a substantive representation delta.

Use existing small baseline artifacts with retained acceptance evidence, then
recheck that premise in the frozen matrix. If a bound baseline fails, retain the
failure and mark dependent comparisons ineligible with a reason; do not replace
it with an easier seed. No adaptive sample expansion, outcome-directed transform
selection or unbudgeted minimization. Contract-based exclusions happen before
scientific freeze; after freeze retain every planned cell and its disposition.

Implement the bounded transformer and preservation audit. The latter must compare
all relevant declaration roots, names, levels, dependencies, assumptions and
record fields through an independent decoder/canonical representation. Only
specifically justified representational coordinates may be normalized away.
Unknown tags, missing/extra records, unresolved references and changed semantic
fields fail closed. A transformer plus its own inverse is not an independent
oracle. Avoid exponential expansion of shared DAGs.
Preserve raw universe syntax (including `imax` and `max`), ordered parameters,
binder information and distinct name constructors; dotted-string flattening or
checker definitional equality is not structural preservation.

Include deliberately changed-object controls that the preservation audit must
reject, missing/duplicate/invalid-reference controls, legal positive controls and
determinism/round-trip checks. Independent review must inspect the preservation
argument and those controls. If reusable code makes transformer and auditor
share a critical assumption, disclose and independently test that assumption.
Do not call the relation a theorem unless an actual proof is supplied.

Bind each exact tooling revision, its source/test hashes and validation evidence
before its permitted test/generation attempt. Scientific input meaning remains
fixed; ordinary parser/audit/runner repairs version tooling within the same item,
preserve raw failures and carry all consumed counters. A checkpoint is not closure.

## C. Generated-byte and checker-launch gate

After bounded generation and preservation checks, commit an execution manifest
binding exact generated-byte hashes, the scientific manifest and tooling revision,
passed preservation controls/review, exact original/variant observer cells and
expected relations, executable/runtime/configuration identities and commands.
Each eligible variant must have its nonidentity representation delta recorded
and mechanically checked as well as preservation passing. Do not launch an
all-identity matrix as a discovery experiment.
Bind timeouts, memory enforcement, process groups, termination/cleanup evidence,
actual accounting and remaining budget. Use one launch owner and mechanical
fail-closed prelaunch checks. A listed budget never substitutes for this gate.

Run only frozen cells. Retain stdout/stderr, raw exit codes, timing/memory and
all failures. Distinguish ACCEPT, semantic REJECT, parser/import rejection,
crash, timeout and infrastructure/audit failure. Compare within-checker outcomes
only for valid preservation pairs and compatible baselines. Cross-checker
differences remain profile observations; consensus confers no authority.

Pause launches for accounting, timeout, process-control or cleanup faults and
reconcile conservatively. Use reserved attempts for exact-pair confirmations
under recorded tooling repairs, not additional scientific cases. A changed
scientific premise requires a recorded boundary/successor rather than silently
weakening preservation, replacing the cohort or resetting costs.

## D. Completion and next decision

Produce one executable transformation/preservation package with the complete
bounded observation matrix, exact pair provenance and scoped findings; or a
precise negative/unresolved contract, oracle or setup boundary that explains why
no feasible authorized repair remained. A successful source review by itself
does not complete the pilot when implementation and execution remain feasible.
Successful executed-pilot closure requires at least one nonidentity,
preservation-passing pair tested on both bound profiles with compatible baselines.
If the frozen cohort yields none, retain the no-eligible-transformation result;
do not replace seeds or count identity pairs as a successful pilot.

Classify a demonstrated difference first as representation sensitivity and
identify its phase. Do not equate a crash, importer policy distinction or differing
resource cost with kernel unsoundness. If no difference occurs, retain the
tested relation/domain/count and decide whether the suite has preventive shared
value; do not claim global equivalence or expand until a bug appears.

Recommend a concrete shared corpus case, checker regression, implementation
investigation or evidence-based no-action decision, with target, priority and
remaining prerequisites. Any prospective PR draft must enter the contribution
ledger; publishing remains separately human-gated. No new catalog authority is
established by this pilot; any later adjudication uses its repository skill.

Run focused controls while developing, then affected validators and the complete
current/historical full-payload suite at closure, refresh generated state and
check queue/status agreement. Compare intended-theorem completeness, valid-term
generation, conditional impact work, other candidate methods, held contributions
and the unchanged one-thread reserve before selecting the next unstarted item.
