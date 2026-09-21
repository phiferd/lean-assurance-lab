# Valid dependent-term pilot 1

Status: READY for source/reuse and typing-rule review. No generator output or
checker launch is authorized until the phase gates below are committed.

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
   category counts, size policy and nonterminal process safety controls.
4. Commit the generator, auditor, tests and an exact 50-case manifest before
   generating observable checker outcomes.
5. Preserve every generated case and execute the complete frozen matrix.

An engineering failure in any phase is repaired and retried inside this item.
Attempt, build, checker, session and elapsed-time counts are observational only.
Per-process timeout, memory and cleanup controls protect the host but never close
the item.

## Completion

Complete with the exact 50-case corpus, derivations, audit results, full supported
checker matrix and scoped reuse/contribution recommendation. Stop without that
result only for owner direction, unavailable required authority/input,
invalidated scientific input, or a required capability that remains unavailable
after feasible repairs. Network access, production checker edits, assurance
milestone changes and external writes require separate authority.
