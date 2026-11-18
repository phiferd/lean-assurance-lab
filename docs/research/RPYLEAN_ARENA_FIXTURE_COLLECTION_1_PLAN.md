# Make shared Arena cases usable in rpylean development

**What did we find?** rpylean accepted all three declarations in Arena's valid
proof-parameter example. Its original suite missed the case from Arena's test
root and passed it from the case directory. With the local collector change,
the full case name selected one passing test from the root. This result covers
one shared example on the pinned checker.

**Is it interesting?** Yes. The maintainer can now see the expected case run
in the ordinary suite. Selecting it without its export yields a named failure,
and an absent optional checkout yields a visible skip.

**Does it require more work?** The collector item is complete. Use the
existing directory override for one-off testing and retain the local patch
for root-based regression coverage. The separate source-only investigation
of the earlier rpylean disagreement is READY and unstarted. [Result](../../results/research/rpylean-arena-fixture-collection-1/report.md)

The following is the fixed protocol used for this item.

## Fixed comparison

Use rpylean `0ddcb018356e4ae59a0e37a395b3c7601b1fd68b` and Arena
`ef915093da536931892f1bfdaffb2a2d59529fe7`. Arena's recursive loader names
cases by relative path. The rpylean collector lists top-level YAML files,
looks for exports by basename, and omits unavailable files. Its default CI
workflow runs the suite without provisioning the optional Arena tree. Confirm
the exact source, control bytes and PyPy test environment at entry. Retain the
actual test IDs and outputs from each comparison. [Pinned collector](https://github.com/Julian/rpylean/blob/0ddcb018356e4ae59a0e37a395b3c7601b1fd68b/tests/test_lka_arena.py)
· [Arena loader](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/lka.py#L874)
· [Source and case identities](../../results/research/strategy-reassessment-2026-11-17/source-observations.json)

The fixed control is `corner-cases/proof-param-ok`. It keeps two proof
parameters in their declared order. Arena declares `accept` and ships the
export with the description. Reuse these exact bytes and that stated expectation.
Measure collection and execution separately. A collected test can skip, and a
checker can disagree with the expected result. [Arena description](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/tests/corner-cases/proof-param-ok.yaml)
· [Earlier shared contribution](../../results/investigations/corpus-integration-2026-09-05/external-actions.json)

## Work and decision

1. Point the unmodified suite at Arena's documented `tests/` root and record
   whether it collects the fixed relative ID. Compare this with passing the
   export directly to the checker and pointing `LKA_TESTS_DIR` at
   `tests/corner-cases/` for this one case. Which route checks the declared
   expectation, shows what ran, and works with the usual corpus layout? If an
   existing invocation meets the developer need, retain it with evidence and
   stop there.
2. If the gap holds, make the smallest collector change that lets a developer
   select that ID and obtain a verdict. Preserve relative paths for both
   shipped and prebuilt inputs. Keep the no-checkout default usable. Give a
   developer who explicitly selects a missing input a visible diagnostic.
   Respect Arena's declared expectations, including `either` where both
   verdicts are allowed. Keep large corpora, performance suites and multi-case
   generators on their existing paths. Recursive discovery need not execute
   every description.
3. Exercise the normal test entry point on the fixed control and record the
   observed verdict against its expected acceptance. Use small local collector
   tests for top-level compatibility, equal basenames in different directories,
   built-file resolution, and the difference between a missing selected file
   and an absent optional checkout. These tests should run in the default suite
   without requiring an Arena download. Run the affected suite and the applicable
   Lab closure checks. Measure any extra setup and runtime.
4. Deliver the before/after collected IDs, exact control identity, outcome,
   tests, developer invocation and local patch if justified. A successful
   explicit run supports a maintainer recommendation with that example. An
   unexpected verdict is a separate bounded compatibility observation. Record
   it and keep checker changes outside this item. If the existing route suffices
   or the change adds no practical coverage, recommend using the existing route
   or dropping the patch, with the reason. Record failed attempts and repair
   ordinary tooling failures within the item.

Success is a developer's ability to tell **which shared case ran against which
working copy and what happened**. The descriptor count measures the search
space only. Compare the result with the independent source-attribution item at
handoff. Any upstream proposal needs current duplicate and maintainer-fit
evidence and exact owner authorization.
