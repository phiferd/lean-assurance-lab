---
name: declaration-validation-adjudication
description: Adjudicate declaration-validation catalog entries, evidence locks, authority sources, and implementation or observer mappings for the M8/M9 contract slice.
---

# Declaration-Validation Adjudication

Use this procedure for declaration-validation characterization catalog work,
authority or evidence adjudication, evidence locks, implementation/observer
mappings, and Milestones 8–9 of the declaration-validation contract slice.
It does not establish semantic authority; it applies the frozen project rules.

## Read first

Follow `AGENTS.md`, then read:

- `docs/research/DECLARATION_VALIDATION_CONTRACT_SLICE_PLAN.md` (the active
  milestone boundary and completion criteria);
- `config/declaration-validation-catalog.json` and
  `schemas/declaration-validation-catalog.schema.json`;
- `config/declaration-validation-identity-registry.json` (the frozen stable
  ID and denotation);
- `config/declaration-validation-target.json`,
  `config/declaration-validation-source-lock.json`, and the applicable
  versioned evidence lock under `config/declaration-validation-evidence-locks/`;
- `config/declaration-validation-authority-rules.json` and the frozen
  `config/declaration-validation-approved-authority-sources.json`;
- `schemas/declaration-validation-characterization-entry.schema.json` and
  `schemas/declaration-validation-evidence-lock.schema.json`.

## Procedure

1. Identify the frozen stable identity and read its canonical semantic
   denotation. Preserve it exactly; a semantic change requires a new ID.
2. Inspect the pinned semantic target, applicable source/evidence locks, and
   the source-locked implementation and existing Lab evidence. Record only
   evidence the locks mechanically bind.
3. Assign kind, layers, lifecycle, and authority only as supported by that
   evidence. Apply the versioned qualification rule that matches the entry.
   LLM output, checker agreement, and implementation majority are not
   normative authority.
4. Never manufacture or self-approve normative authority. Use only sources
   already permitted by the frozen approved-source registry. If normative
   support is insufficient, retain `PROVISIONAL` or `UNRESOLVED` with the
   explicit unmet requirement and, when required, blocker or contradiction.
5. Populate observer outcomes only from content-bound structured checker result
   bytes and their prescribed pointers. Preserve contradictions and
   shared-lineage caveats. Keep `soundness_relevance = NOT_ASSESSED` while the
   current M8 gate requires it.
6. For M8, create a new sequence-2 evidence-lock successor rather than mutate
   the M7 root. Follow the active plan's separately reviewable five-entry pilot
   boundary; do not claim M8 completion until the validator accepts the exact
   disposition of the complete frozen discovery surface.
7. Regenerate derived artifacts only through their canonical paths:
   `scripts/render-declaration-validation-report`,
   `scripts/render-declaration-validation-freeze`, and
   `scripts/render-declaration-validation-milestone-7-completion` when their
   inputs require them. Do not hand-edit generated outputs.
8. Run `scripts/validate-declaration-validation-catalog` and
   `python3 -m unittest discover -s tests -p 'test_declaration_validation_*.py'`
   before claiming completion. Stop when evidence cannot meet a gate; do not
   weaken the gate to obtain a desired classification.
