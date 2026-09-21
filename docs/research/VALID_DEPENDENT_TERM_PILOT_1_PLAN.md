# Valid dependent-term pilot 1

Status: READY and unstarted. Source/reuse review, implementation and independent
auditing are phases of this item. Corpus construction and checker observation
have separate gates below; an exact corpus manifest is produced by construction.

## Question and value

Can a derivation-carrying generator produce a fixed positive suite of closed,
well-typed dependent terms whose expected validity is independently auditable,
then expose conformance differences across supported checkers without selecting
or replacing cases after outcomes are known?

The useful community asset is a small reusable positive conformance corpus plus
its derivations and generator, not merely another set of checker exit codes.

## Scientific scope

The suite contains exactly 50 closed terms, divided before observation into ten
Pi, ten lambda, ten application, ten let and ten mixed cases. Terms use only
Pi/lambda/application/let, variables, sorts and closed numeric universe levels.
Inductives, quotients, native literals, `imax`, prior ownership cases and any
outcome-guided replacement are excluded.

## Phase gates

1. Record a focused reuse review of existing term generators, typing
   formalizations and exporter support at exact revisions.
2. State the fragment's typing rules and derivation representation independently
   of every target checker. Have a separate audit implementation reject malformed
   derivations and term/derivation mismatches.
3. Bind exact exporter and checker profiles, deterministic generation seed,
   category counts, size policy and nonterminal process safety controls. Commit
   this design, the generator, auditor and focused tests before constructing the
   scientific cohort. Construction emits both terms and derivations, not target
   checker outcomes.
4. Construct and independently audit the fixed 50-case cohort. Preserve failed
   construction/audit evidence; repair generator or auditor defects within this
   item without changing the seed, categories or selection rule. Commit the
   exact term/derivation hashes, audit results and execution manifest before any
   target checker observes a scientific case.
5. Execute the complete frozen matrix and interpret its outcomes. Preserve every
   case, including difficult or rejected cases; never replace a case after
   checker observation.

## Implementation approach

Reuse the repaired supervisor, supported exporter workflow and checked-object
receipt checks where compatible. Establish their basic build/export/check path
with existing fixtures before cohort construction; these engineering smoke tests
are not members of the 50-case scientific cohort or evidence about its outcomes.
Generator/auditor development fixtures are also separate from that cohort; the
construction gate does not prohibit implementing and testing the generator.
Use ordinary tool-supported project setup and preserve actual build output.
Successful builds may emit stdout; acceptance must follow the command's contract.

Bind the source inputs actually needed to build, including non-code includes,
and the transitive local tooling used by each attempt, not just its wrapper.
Attempts use fresh evidence directories so a partial failure remains retryable.
Stage generated outputs there and promote the corpus only after its audit passes.
Check timeout, memory, monitoring and cleanup receipts before the next launch,
independently of the semantic outcome label; a safety failure pauses for repair.
Apply these requirements in the pilot's implementation and focused regressions;
do not create a separate supervisor/framework or maintenance research item.

An engineering failure in any phase is repaired and retried inside this item.
Attempt, build, checker, session and elapsed-time counts are observational only.
Per-process timeout, memory and cleanup controls protect the host but never close
the item.

## Completion

Complete with the exact 50-case corpus, derivations, audit results, full supported
checker matrix and scoped reuse/contribution recommendation. Stop without that
result only for owner direction, unavailable required authority/input,
invalidated scientific input, or a required capability that remains unavailable
after feasible repairs. Read-only source/reuse research and exact-input
materialization are permitted as preparation. Production checker edits,
assurance milestone changes and external writes require separate authority.
