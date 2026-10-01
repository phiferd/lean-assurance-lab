# Deterministic elimination: a reusable prerequisite

What did we find? Lean checked five generic official-model equations and two
consumers. Every successful elimination run returns the same state, even when
its fuel differs. This removes fuel-case enumeration from acceptance extraction.
The arbitrary-depth function-to-List bridge is still unproved.

Is it interesting? Yes, modestly: this applies to every official context and
declaration, not a larger example list. Actual acceptance now yields checks at
an independently proved exact output. It proves neither termination nor native
positivity conversion. This is useful supporting infrastructure, not a completed
completeness result or a scientific novelty claim.

Does it require more work? Yes. Continue the same campaign with a new exact
parametric function source/lookup environment and root-row queue invariant, then
construct native function/List derivations with separate constructor budgets.
No folds or broad grammar follow from this prerequisite.

## Checked statements and assumptions

`loop_success_mono`: a successful queue run at fuel f has identical output at
any g≥f. Induction follows the actual deterministic mapM replacement step.
`loop_success_unique`: any two successful queue runs from the same context,
queue position and starting state have identical output, via max(f,g).
`lowering_success_mono` and `lowering_success_unique`: lift those facts through
actual declaration parameter stripping; do not assume it succeeds.
`acceptance_at_exact_output`: from a PROVED elimination equation and actual
OfficialPosAccepts, recover every constructor check at that exact state.
The reducer is universally quantified because this theorem only transfers
existing checks; it does not assert reducer success or native correctness.

`tower_acceptance_at_target`: all N, existing canonical List^N source, exact
proved official target; output equation discharged by official_lowering_family.
`arrow_acceptance_domain`: actual depth2 function schema and fixed verified
opaque official Core16 reducer; acceptance excludes Tree domain, using generic
uniqueness rather than prior exhaustive fuel computation.

All seven new axiom reports: [propext, Classical.choice, Quot.sound]. No sorry,
admit, new axioms, native_decide or run_tac. Failed attempts that printed sorryAx
are rejected elaborations and remain in the archive. Nothing from a failed
attempt is part of the accepted replay.

## Precise next model obligation

Tree2TowerNative.node N encodes List^N(Tree)→Tree. The desired new source encodes
(alpha→List^N(Tree))→Tree (and its inadmissible Tree-domain control).
Tree2ArrowNative.En(_N) ignores N and stores the fixed depth2 function node.
Neither existing environment is the desired parametric source environment.
The official queue proof's rootRow/root_frontier also assumes the old root type.
Reusing either unchanged would prove a different theorem. Needed: new exact
source, context/lookups, changed root-row replacement/queue induction, opaque
lowered oracle and verified finite Core facts. This is model work, not an
ordinary fuel adjustment; user continuation now authorizes this bounded step.

For arbitrary N, native function node index is expected N+2, leaf index1;
prove actual separate walk bounds. The leaf fuel is fixed1026, so a common
indexN+2 cannot fit it once N>1024. This is a limitation of the common-bound
wrapper, not a completeness counterexample. Use singleton posDR_run and append.

## Reproduction and evidence

Run replay-chain.py with explicit compiler/cache/source/destination arguments
as retained fresh-replay/*command.json. It verifies compiler SHA and all108
historical import hashes before replay. Schema dependency is replayed unchanged.
Seven retained development attempts include four rejected proof/identifier
repairs; final0005 and0007 pass. Focused fresh replay and independent review PASS.
Exact timings/resource/cleanup are in checkpoint.json and every raw receipt.
Prior canonical/allN and exact fixedN2 sources and archives remain unchanged.
No full E2 closure, C++ kernel verification, whole-validator acceptance,
checker parity, generated recursor or fold claim follows.
