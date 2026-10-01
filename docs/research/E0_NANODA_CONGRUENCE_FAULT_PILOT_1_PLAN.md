# Nanoda constant-application congruence fault pilot

Evidence class: E0

## Prospective question

At Nanoda `3a2407216ee84a75f9e1aead6803d0578be06ae7`, does the public declaration-checking path reach `try_eq_const_app` in a case where omitting only its pairwise application-argument equality guard changes a well-formed but invalid definition from rejection to acceptance? If so, does Nanoda's existing test corpus kill that same fault?

The fixed fault removes only
`l_args.iter().copied().zip(r_args.iter().copied()).rev().all(|(x, y)| self.def_eq(x, y))`
from the guarded constant-application comparison. Head equality, regular-hint equality, arity, universe equality and failure-cache checks remain unchanged.

## Fixed sample and controls

The sample uses explicit lean4export 3.1.0 NDJSON with opaque axioms `A : Type`, `B : Type`, `v : F A` and regular definition `F (X : Type) : Type := X`. The negative candidate declares `bad : F B := v`; the matched positive control declares `ok : F A := v`. The configuration permits exactly `A`, `B` and `v`, uses one checker thread and disables native extensions.

The negative candidate is independently invalid under Lean conversion: reducing `F` gives inferred type `A` and declared type `B`, and distinct opaque type constants have no definitional-equality rule. The axioms do not postulate `A = B`; a model can interpret them as distinct types and `v` as an inhabitant of `A`. This is a typing test, not a theorem of inequality between arbitrary models.

Signal requires all of: the control is accepted by baseline and faulted binaries; the candidate is rejected by baseline specifically through the compared `F A`/`F B` path; the faulted binary accepts that same candidate; and all processes have complete supervised receipts. If the existing corpus also fails under the fault, this is only a selector/classification correction. If the corpus passes, the exact pair may justify a separate local regression candidate. Masking, unreachable code, malformed input or incomplete execution is INCONCLUSIVE.

## Execution and stop boundary

Use the existing tested `lib/resource_envelope_supervisor.py` for every compile, test and checker process, with 3600 seconds, 16 GiB sampled RSS, 3 second sampling, 10 second cleanup and 20 MiB output limits. Build baseline and faulted copies from separate task-local source directories; retain the exact patch and source hashes. Run the two fixtures against both binaries, then run the existing Rust test corpus against the faulted source. Preserve raw stdout, stderr, exit, timeout, memory and cleanup receipts.

Stop after this one fault is classified. Do not try a second helper, broaden the mutation framework, claim a production Nanoda defect from an intentional fault, push Nanoda changes, contact maintainers, or make a security/exploit claim. A useful result is limited to corpus sensitivity and public-path regression value at the exact revision.
