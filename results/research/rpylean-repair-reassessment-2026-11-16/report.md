# Reassess the current rpylean work — 2026-11-16

**What did we find?** Current rpylean source still acknowledges that its
recursor-rule check validates the selected minor-premise head but not the
arguments supplied to that minor. Arena #350 already publishes a dependent
wrong-argument rule that rpylean accepted and that yields `False`. No current
Lab run has reproduced the case. A standalone reproduction would mostly restate
public evidence; the concrete opportunity is a tested local repair and direct
regression.

**Is it interesting?** Yes as repair work, not as discovery. The semantic
consequence is severe and the validation-to-reduction path is identified.
Changing the checker so it rejects the malformed minor application while
preserving honest dependent and recursive rules would improve an actual
independent validator. That is more useful than another report that the known
case still fails.

**Does it require more work?** Replace the READY reproduction-only E0 with
`RPYLEAN-RECURSOR-RULE-ARGUMENT-REPAIR-1`. Reproduce the public candidate only
as the failing baseline, derive the expected minor application for the smallest
semantically justified supported fragment, implement and test the repair, and
retain a reviewable patch and pull-request draft. Stop before any external
submission. Keep recursive Arena fixture discovery as a separate supporting
repair unless the direct regression cannot be made reliable without it.

## Current evidence

The reviewed rpylean revision remains
`b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb` on 2026-11-16. Narrow repository
search found no open recursor issue or pull request; this does not exclude
unpublished work.

The source path is concrete:

- `parser.py` retains the imported rule right-hand side.
- `_check_rule_rhs_head` in `objects.py` peels the expected lambdas and checks
  that the body is headed by the corresponding minor premise. It does not
  compare the application's arguments, and the nearby source comment records
  that the right minor with wrong arguments still passes.
- `machine.py` later selects and applies that imported rule during reduction.

[Arena #350](https://github.com/leanprover/lean-kernel-arena/pull/350) supplies
the exact public witness: for a one-field structure, the rule uses `mk true`
instead of `mk b`. A dependent motive exposes the mismatch and produces
`False`. The expected rejection follows from the constructor's computation rule,
not checker consensus.

The ordinary rpylean Arena harness also scans only top-level YAML files while
the new bug fixtures live under `tests/bugs/`. That is a real coverage problem,
but it is not the semantic repair itself. Add one direct regression in the
repair item; consider recursive discovery as a separate patch if it can preserve
explicit expected outcomes and fail on missing built inputs.

## Alternatives considered

- Lean #15705 is closed with maintainer guidance that the unchecked nonnested
  generated hypotheses are inside the trusted generator boundary. It needs a
  concrete generator counterexample before further work.
- Lean #16489–#16491 are current open issues with public reproducers and proposed
  repair directions. #16490's auxiliary-name guard is a reasonable small patch,
  but no inconsistency is reported and the rpylean false-proof boundary has the
  clearer assurance consequence.
- The Nanoda universe-capture route is closed `NO_SIGNAL` for its exact case.
  Historical replay, assurance companion and checked-import packaging still lack
  a decision-changing consumer or available original evidence.

## Research value

This reassessment changes the intended output from “current reproduction” to a
changed checker with fault-sensitive regression evidence. The consumer is the
rpylean maintainer, who can review and adopt a bounded patch. The known witness
provides a strong oracle; the remaining uncertainty is whether a safe,
constructor-derived validation can cover the supported ordinary fragment
without rejecting valid rules. That is an engineering and semantic question
worth answering. Reproduction without the repair would add little.
