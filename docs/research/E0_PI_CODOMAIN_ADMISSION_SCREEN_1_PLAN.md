# Pi codomain admission screen

**What did we find?** A source-only intake found a reachable, previously
unmeasured raw-import question: whether a dependent function with a
well-typed but non-type result is rejected before an ordinary definition's
final type comparison. No checker has run on the proposed inputs.

**Is it interesting?** Yes. It tests a distinct formation premise in both
declared-type and value positions with closed sort-only expressions and valid
paired controls. An unexpected acceptance could be a candidate defect.

**Does it require more work?** First bind and audit the exact raw inputs and
checker profiles, then register a separate E0 trial before any launch. Close
with retained raw outcomes and a campaign handoff; stop before the next item.

Evidence class: E0. Campaign: `E0-PI-CODOMAIN-ADMISSION-SCREEN-1`.
Frontier: `F-DISCOVERY-AND-CONFORMANCE`. This plan is READY and unstarted.

## Fixed question and four-input sample

Do official Lean and Nanoda reject an ordinary checked definition when a Pi
codomain is a well-typed expression whose inferred type is a Pi rather than a
sort, in (A) the declared type or (B) the definition value? Use exact raw
expression trees corresponding to:

```text
S0 = Sort 0                      S0 : S1
S1 = Sort 1                      S1 : S2
F  = fun (_ : S1) => S0          F : (forall (_ : S1), S1)
G  = forall (_ : S1), S1         G : S2
N  = forall (_ : S1), F          INVALID: F has a Pi type, not a sort

A-control  : G  := fun (_ : S1) => S0     ACCEPT
A-negative : N  := fun (_ : S1) => S0     REJECT
B-control  : S2 := G                      ACCEPT
B-negative : S2 := N                      REJECT
```

Each negative replaces only the Pi codomain node `S1` with the same closed
well-typed `F`; surrounding declaration metadata, order and value/type pairing
stay fixed. The only primary fault is codomain sorthood. The A negative may
also imply a later value/type mismatch, but the earlier Pi check must reject
without relying on that derivative mismatch. The B negative's declared type
is valid, so checked value inference is the intended rejection point. There
are no named constants, axioms, applications, lets, recursors, metavariables,
free variables or universe parameters. The sample is separate from the
ignored-argument E0, merged-Lean eta replay and historical recursor audit.

## Entry and launch gates

1. The campaign must be ACTIVE in queue, Active status and this fixed plan
   together. Recheck [the dated source/corpus map](../../results/research/fresh-import-admission-target-1/report.md)
   for material upstream drift. Bind exact official Lean, Nanoda, exporter,
   importer, runtime and configuration revisions. The current source tips are
   selection evidence only; no checker executable is bound by this plan.
2. Produce four separate 3.1.0 raw exports for ordinary safe definitions,
   their Nanoda configs, and a structural audit independent of checker outputs.
   Audit declaration reachability, actual parsed trees, closedness, every
   binder scope, the single codomain replacement per pair and the typing
   derivation above. Bind input and runner hashes before the first checker
   process. An importer refusal or different parsed tree is not a semantic
   rejection.
3. Append the E0 trial start to `explorations/ledger.jsonl` before checker
   observations. Run four inputs on each of two exact checker profiles, eight
   planned cells, in supervised fresh processes. Preserve every failed setup,
   audit and launch attempt; repair ordinary engineering failures within the
   campaign without replacing the fixed scientific question. Record actual
   first attributable rejection stage, not just exit status.

## Result and handoff

Expected outcomes are two accepted controls and two rejected negatives per
checker. `SIGNAL` requires an unexpected checked-definition acceptance of an
intact negative, a passing paired control, the independent typing argument and
complete supervision. This is a candidate only; E1 confirmation requires a
separate fresh experiment and gates. `NO_SIGNAL` requires all eight
attributable expected outcomes. Otherwise close `INCONCLUSIVE` with the exact
missing observation or genuinely unavailable capability.

At closure run the exploration ledger and diff checks and
`scripts/exploration-handoff --base <pre-campaign-commit> --write` then
`--check`; retain raw records and select one project-wide successor. Deliver
on main through `scripts/push-main`. No new checker family, version sweep,
recursor/eta replay, production checker edit, frozen-history edit, external
write or assurance milestone advance is authorized here.
