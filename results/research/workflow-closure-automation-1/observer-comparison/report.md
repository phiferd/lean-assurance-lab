# One observer versus STATEFUL — source/reuse comparison

Dated 2026-09-27. Source-only work under WORKFLOW-CLOSURE-AUTOMATION-1.
Recommendation: prepare **LAZY-REDUCTION-CONFORMANCE-PILOT-1** next, keeping
STATEFUL-VALIDATION-PILOT-1 as a feasible alternative. Reuse lazylean and the
Lab's bounded typing/audit machinery; build only a portable adapter and six
demand-directed conversion cases. Root owns the actual queue decision.
Neither experiment started here.

## Evidence and independence

Arena added lazylean on September 23.
[Arena's pinned definition](https://github.com/leanprover/lean-kernel-arena/blob/8384b217ee3bf2da27e078af03cb647136427d57/checkers/lazylean.yaml)
binds v0.3.0 to **68c66fa18c1afe029512b90ecfe0b162c0dcd8fb**.
All twenty source files, CMake target, README, NOTICE and license are retained;
[source-inventory.json](source-inventory.json) verifies their exact Git blob
identities and byte lengths, 335,468 bytes total. This is complete for the
declared checker CMake target, not its benchmark corpus or external toolchain.

[NOTICE](https://github.com/corun1024/lazylean/blob/68c66fa18c1afe029512b90ecfe0b162c0dcd8fb/NOTICE.md)
says the implementation was written for this project, with no source copied
from Lean, Lean4Lean or Coq. This is an author provenance statement, not a
code-genealogy audit. Checking and recursor algorithms explicitly follow Lean
and Lean4Lean; reduction follows Coq's closure-machine design. C++ does not add
language diversity against official Lean's C++ kernel, but does against the
retained Rust Kiota/Nanoda implementations. A separately implemented lazy
machine provides useful implementation diversity; shared algorithms, export
format, tests, human/LLM development inputs and specification lineage remain
correlated. No independent semantic authority or kernel-correctness claim follows.

## Actual checking and format boundaries

The pinned loader consumes lean4export NDJSON, with indexed names, levels,
expressions and declarations. It has fast and general JSON paths and range
checks. tc.cpp:979–1028 checks ordinary declaration types and values before
insertion. inductive.cpp:654–675 compares recursor counts, universes, metadata,
full types and rules with reconstructed results; line 670 rejects a
non-convertible supplied full type. This is source-demonstrated negative
capability. No build or rejection was executed here. README test and whole-library
counts are upstream claims, not Lab observations.

Native reduction is unsupported. There is a source/documentation discrepancy:
README/Arena describe unsupported native reduction as exit 2, but tc.cpp:654–655
throws KernelError and main.cpp:312–319 maps declaration KernelError to exit 1;
worker_exit likewise reports failure as 1. Treat this as an unexecuted
classification question and keep native reduction outside the proposed fragment.
Do not use a generic nonzero exit as semantic rejection. The adapter must
separate type failure, parser failure, process failure and resource limits.

The CLI's keep-going mode is not rollback isolation: main.cpp:325–326 explicitly
adds failed declaration constants unchecked so later declarations can proceed.
It therefore cannot substitute for STATEFUL's promised failure-recovery API.

## Small useful experiment

The retained dependent-term suite is compatible in syntax: closed numeric
universes, Pi/lambda/application/let, no constants, literals or native reduction.
Its existing application-01/05/10 and mixed-01/05/10 artifacts provide six
source-assessed positive reuse assets only; no additional launch matrix is
proposed for them. The preserved 6,332-byte recursor
candidate/control pair supplies a negative-capability gate, not a new discovery
question or an independent semantic oracle.

A simple replay of these positives does **not** test lazy beta/zeta demand:
all six declarations have Sort 0 as declared type, and inference need not
normalize their value redexes. Moreover tc.cpp:413–417 defaults LL_KAM_MODE to 2:
only full whnf uses the lazy machine; cheap whnf_core uses substitution.
This defeats the tempting inference from syntactic redex count to coverage.

The proposed scientific question is instead: do six independently justified,
demand-directed type-conversion checks preserve acceptance between the
substitution and closure-machine paths, with observed beta/zeta demand?
Freeze exactly six case templates before generation: beta, zeta,
beta-under-let, let-under-beta, shadowed binder and repeated bound variable.
Use only the existing bounded beta/zeta typing fragment and independently
reviewed rules; introduce no constants, inductives, native operations, eta,
proof-irrelevance obligation, benchmark or broad formalization.
Make the conversion necessary in the declaration's type/value comparison.

Use two explicitly experimental profiles of the same pinned observer:
--engine subst and --engine kam with LL_KAM_MODE=3, one worker, clean environment.
The source supports both bits (whnf and whnf_core). Mode 3 is source-exposed,
not the Arena default and not a documented cross-version public API promise.
Freeze this distinction in claims. Twelve scientific cells plus the two
retained capability fixtures on both profiles (four gate cells); retries do not
enlarge the scientific matrix. The six retained positives are source-assessed reuse
assets only, with no planned executions or replacement of scientific cases.

Require a static demand argument and exact output-counter contract before
launch; audit actual machine beta/let counts after execution. Missing demand
makes the coverage claim unsupported, even if acceptance is preserved. Do not
replace a frozen case to obtain coverage. Diagnose supervision/parser defects
inside the same item. A real reachability/design boundary is useful evidence.
--engine both shares data/caches and cannot constitute a second independent
observer; it is not part of this matrix.

## Preparation cost and launch gates

The host inventory is Darwin arm64, /usr/bin/c++ exists, Homebrew GMP 6.3.0
headers exist, and cmake is not on PATH. This is not a build result or dependency
lock. CMake is unnecessary in principle: its target lists ten C++ translation
units, C++20, -O2 -g, src include path, and gmpxx/gmp/pthread. A direct compiler
invocation with explicit GMP include/library paths can implement that target.

Actual portability work is narrow but must be verified: main.cpp includes
malloc.h and calls malloc_trim; name.cpp uses MADV_HUGEPAGE; kam.cpp:28 has an
unguarded x86 rdtsc profiling helper. Guard the allocator and huge-page hints and
disable only the nonsemantic cycle counter on arm64. These are proposed repairs,
not an already reviewed patch or a guarantee that no additional incompatibility
exists. tc.cpp reads /proc/self/statm and silently returns if unavailable:
never rely on its --max-rss on this host. Reuse the Lab's independently tested
process-group RSS/timeout/cleanup supervisor. main.cpp's pthread calls also need
checked process-start/completion evidence; the 4 GiB requested stack is virtual,
not evidence of actual RSS. Pin compiler, SDK, GMP libraries, command, adapter,
patch and complete transitive source inputs before the first controlled build.

Preparation and repairs belong inside the same successor. Stages are:
(1) activate plan and bind provenance; (2) review exact nonsemantic portability
patch and build/process controls; (3) controlled build, the existing-byte recursor positive/control
and negative/candidate capability checks, fail-closed output adapter; (4) freeze and
independently review six derivations, demand arguments, producer/auditor and
expected relations; (5) generate once under those bindings, verify object
custody, commit exact manifest, and run the fixed twelve cells. No successful
experiment is required merely to select the preparation phase READY.

## Symmetric comparison and consequences

STATEFUL remains useful: six fresh-versus-prefixed comparisons can expose public
environment/cache/recovery behavior not tested by pure input variation. Its
current plan identifies no exact APIs or recovery contract, so it still needs
source selection, supported history design, two adapters at most, fixtures and
independent audit before launches. That is preparation uncertainty, not a blocker
or evidence it is harder. Neither proposal is launch-ready.

The lazy pilot narrowly outranks it on present evidence because it has an exact,
source-complete implementation with a different reduction mechanism, a specific
reachable conversion seam, reusable independent fragment rules and object
receipts, and known local portability tasks. It would add a reusable observer
adapter alongside its twelve-cell result. Its comparative advantage is not
language novelty, presumed defects, the recursor pair, or completed planning.
STATEFUL has broader session novelty but less source-qualified reachability
today. This ordinal preference could reasonably change if its API contracts
prove immediately reusable; no numeric cost or defect-rate estimate is claimed.

An all-preserved lazy result retains the adapter and six demand-qualified local
regressions, with no external action. A verified relation violation yields a
minimized, provenance-bound regression and exact target recommendation; source
attribution and portability effects must be separated before alleging a checker
defect. Insufficient demand or an unavailable capability after feasible repairs
yields the precise boundary and returns comparison to STATEFUL. External
publication, upstream patch/issue and deployment remain separately authorized.

The study made zero builds, checker launches, generated scientific bytes and
external writes. One staging extra-newline incident was caught by Git-blob
verification and repaired before any launch; hashes are preserved in the source
inventory. Web search located the primary source but the Arena HTML open failed
with cache miss; the pinned GitHub definition and exact source, not the website
snapshot or search snippet, control all conclusions.
