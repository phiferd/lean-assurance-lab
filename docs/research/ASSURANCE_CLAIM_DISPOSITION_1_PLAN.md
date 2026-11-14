# Explain the disposition of the published assurance cases

The public assurance snapshot reports fifteen semantic disagreements and one
parse-behavior case against its exact older inputs. Later work records repairs,
adoption and unresolved custody separately. Yes, readers need to distinguish
those facts without interpreting an old failure as a current defect. Build a
dated companion that accounts for every case; this item is READY and unstarted.

Item: `ASSURANCE-CLAIM-DISPOSITION-1`. This is evidence reconciliation and
reader-facing maintenance, with no checker execution or new assurance claim.
Consumer: a Lean user reading `docs/PUBLIC_STATUS.md` and deciding which findings
still need investigation or reproduction.

## Scope and deliverable

At activation bind `results/assurance/current.json`, its exact disagreement
inventory and source evidence, the contribution ledger, and the later result
artifacts actually used. Confirm the inventory's fifteen-plus-one count from
canonical records; prose is not the enumeration. Produce one machine-readable
row per case and a generated dated reader companion linking the original
observation to any later disposition. Do not regenerate a historical claim
against newer checker bytes or silently change the snapshot's failing gate.

Each row must distinguish original observation, later source/maintainer policy,
upstream repair or adoption, fresh local execution (if present), and unknown
current behavior. Record dates, exact versions, evidence paths and limitations.
Multiple cases may share a repair, but cannot disappear into a merged count.
Missing original cloud evidence remains unknown; do not replay the eta witness
or historical recursor audit to fill it. A merged PR alone does not prove that a
particular old case now passes. New upstream observations update the ledger via
its existing generator; do not imply that unrefreshed entries were checked.

## Completion

Every original case has exactly one row, all evidence references resolve, counts
reconcile mechanically, and each unresolved row names a concrete next action or
an evidence-based no-action decision. A reviewer must be able to tell what was
observed then and what is known now without treating consensus as authority.
Use a small validator and meaningful missing/duplicate/misclassification tests
if introducing a machine-readable successor; reuse existing schemas where they
already express the contract. Link the companion through an existing maintained
entry point without hand-editing generated public status or frozen reports.

If normative adjudication becomes necessary, record it as unresolved and use
the declaration-validation skill and existing gates in a separately scoped
item. This item does not alter catalog authority, resolve a disagreement by
majority, or cross an assurance milestone. Finish with the applicable generation,
regression/current-historical and queue checks and a specific recommendation.
External communication remains human-gated. Select a successor and stop.
