# Reserved namespace regression design

`NANODA-NESTED-REGRESSION-1` completes **SUCCESS** for one source-supported,
unexecuted Nanoda regression design. At current Nanoda
`4c544ed4099c8227f07d5de77ad1e69fb0740a27`, existing tests do not directly
assert reserved-name detection or the targeted enforcement failures. The
proposed test-only contribution combines traversal coverage with two exact
`ExportFile::check_declar` rejection assertions and a complete positive control.
It is preventive coverage of an implementation safety contract, not a finding
of a current checker defect, universal Lean obligation, or observed test result.

## Source and coverage

One fresh `master` lookup on 2026-09-14 returned the same exact source as the
retained HSBM history bundle. Every tracked file was compared with its git blob
and bound in `source-lock.json`; the relevant source is copied under `source/`.
`404660cc2fbf04d8040d25a15ddd55b6b15c8e5e` introduced the guard and its traversal;
`safety-change.patch` preserves the change and the author's safety motivation.
The motivation does not establish normative semantics.

The independent declared-suite audit finds 38 active tests. Four name tests
check `get_pfx`; they do not call `has_nested_pfx` or `find_e`. The existing
`ProjFromProp` test checks a larger export expecting `infer_proj prop` to panic.
Its earlier `PUnit` and `Wrap` declarations can traverse namespace checks, but
there is no `_nested` token or reserved-name assertion in either retained
fixture. Fixture execution does not isolate each guard or traversal edge.
This is a static inventory and assertion audit, not measured dynamic coverage.
No Cargo test inventory or test process was launched.

The complete returned open-PR list contains #32 and #33, for thread defaults and
literal-test nonvacuity, respectively. No overlapping reserved-prefix proposal
appears in that result; this is not a global novelty claim or review/check
observation. The existing local cache and Nat dispatcher candidates also cover
different paths. Their capacity holds remain. The external ledger records this
fresh dated read without implying maintainer availability or contacting anyone.

## Contract and traversal

`get_pfx` (`name.rs:30`) returns the first hierarchical name component, including
numeric components. `has_nested_pfx` (`expr.rs:694`) matches that component
against the interned root `_nested` on both `Const.name` and `Proj.ty_name`.
It is not a substring search: `_nestedX.Probe` and `user._nested.Probe` do not
match. Binder names and universe parameter names are not tested as constants.

`find_aux` visits App function/argument, Pi and Lambda domain/body, all three
Let children, Local binder type, and Proj structure; it also applies the predicate
to each visited node, including Proj's own type name. Var, Sort, NatLit and
StringLit have no expression children. Per-invocation memoization and Boolean
short-circuiting avoid repeated work; each selected positive child must be
isolated from earlier positive children so a missing traversal arm is observable.
No WHNF, type inference or environment lookup occurs in this predicate.

`check_declar` dispatches inductives to `check_inductive_declar`. This first
checks recursive metadata, then checks the selected inductive type, all listed
mutual inductive types, and the selected type's constructor types, at
`inductive.rs:43`, `:47` and `:56`. It next resolves block metadata and performs
ordinary type checking, specialization, constructor and recursor validation.
Each mutual inductive's constructor list is specific to that type; checking one
member is not evidence that every peer constructor was traversed. Standalone
Constructor dispatch performs its own preliminary type check and does not itself
call the reserved-prefix predicate. This ordering determines the proposed target.

## Exact proposed regression

`regression-design.json` is the canonical cell specification. It proposes:

- Thirteen isolated positive traversal cells, each with the same construction
  rooted at `_nestedX` as a false control; additional exact-root, descendant,
  numeric and non-root-name checks, ignored binder-name checks and repeated-DAG
  calls cover the predicate's name and cache boundaries.
- A fresh parse of the unchanged `ProjFromProp` fixture, checking only its complete
  `PUnit` inductive, must return normally. The full fixture is deliberately invalid
  later, so `check_all_declars` is unsuitable for this positive control.
- In a separate fresh parse, append a correctly interned permanent
  `Const(_nested.Probe, [])`, replace only `PUnit.info.ty`, and check that exact
  updated declaration. Require precisely the selected-type namespace assertion.
- In another fresh parse, replace only `PUnit.unit.info.ty` with that permanent
  constant, then check `PUnit`. Require precisely the constructor-type namespace
  assertion. A bare Const keeps the preceding computed recursive flag false.

Setup and pointer/name preconditions occur outside `catch_unwind`. Only the target
call is caught; its string payload must equal the specified assertion. The
candidate constants are intentionally undeclared. These are early-guard tests,
not well-typed semantic acceptance pairs. A deleted guard may still trigger a
later missing-declaration error; that error must fail the regression assertion.
The unchanged fixture control is a baseline control, not a claim that the changed
type is otherwise valid.

Use crate-internal persistent DAG insertion following the existing parser and
its actual hash constants, with `DagMarker::ExportFile`. Never overwrite
interned nodes, forge hashes, or carry temporary `TcCtx` pointers into a new
context. The traversal-only cells use ordinary `test_ctx`/`mk_*` APIs and do not
invoke inference. The source assessment establishes a feasible design; it does
not establish successful compilation.

The mutual-peer assertion remains a specifically named isolation gap. Passing a
stale detached declaration while changing the same name's map entry would reach
the loop, but that artificial inconsistency is excluded. A complete mutual
fixture needs a separate useful construction decision. Literal leaf behavior is
qualified by source here; adding native-literal setup would duplicate nearby
coverage without improving the namespace-specific test. No serialized export
variant is constructed or proposed as a shared Arena semantic case.

## Recommendation and handoff

Implement this design as **`NANODA-NESTED-TEST-1`**, the highest-value feasible
local successor, before speculative new discovery. Target one small test-only
Nanoda patch and a local PR draft, with focused and full-suite execution evidence.
The finite scope is 90 active minutes, eight source/setup requests, at most three
build reservations (600 seconds each) and four test processes (120 seconds each);
compiling tests consume both counters. Freeze the exact source, patch, fixtures,
expected cells, dependency/tooling identities and runner accounting before any
launch. Source drift or ordinary engineering failures must be addressed within
that item and its remaining budget. No production fix, mutation, proof, new
serialized export or upstream write is authorized by this design.

The source-only assessment used two read-only requests and zero Nanoda scientific
launches. Lab validation and its historical regression fixtures are separately
accounted administrative checks. A subsequent tested candidate remains subject
to upstream capacity/duplicate/source review and exact submission approval.
No PR draft is prepared prematurely in this item.

The project-wide comparison retains the theorem companion's missing distinct
refusal-risk gate, the defeq cache's missing mode witness, independent-transfer
custody requirements and original CVC dependencies. The operational survivor
still lacks a deterministic trigger with comparable shared value. Prior methods
and reuse review remains current and no new research method is introduced.
Selecting this concrete regression successor does not start it. Stop after this
one item's required validation and main delivery.
