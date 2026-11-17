# Draft pull request: validate complete ordinary recursor rules

Status: local draft only; not submitted.

Target: `Julian/rpylean`, based on
`b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb`.

## Proposed title

Validate complete ordinary recursor-rule applications

## Proposed body

Arena's `rec-rule-wrong-arg` case applies the correct constructor minor to a
wrong field value. rpylean currently checks only the peeled rule body's head,
so that export reaches iota reduction and a dependent motive yields `False`.

This patch adds a constructor-derived comparison for an explicit first
fragment: one ordinary inductive and motive, no parameters or indices, no
nested types, and direct (not higher-order) recursive fields. It derives all
field and recursive induction-hypothesis arguments, assembles the expected
telescope independently of the rule RHS from the recursor declaration and
constructor telescopes, checks the imported rule type, and requires
definitional equality of the complete rules. The recursor being validated is
opaque to iota during this comparison so an imported rule cannot validate
itself.

The regression changes the public wrong-field shape from accepted to rejected.
Separate honest controls retain a field-dependent rule and a Nat-like direct
recursive rule. Constructor order is also checked. More complex recursors keep
their current validation and are not claimed fixed by this PR.

Validation:

- focused recursor-rule class: 12 passed;
- upstream CI-equivalent suite: 815 passed, 1 skipped, 1 pre-existing xfailed;
- RPython translation: passed;
- translated tests: 9 passed; and
- exact Arena #350 export: accepted before, rejected after in both untranslated
  and translated execution.

A local sibling Arena checkout exposes the existing `rec-missing-ih` failure;
the same focused case fails on the unmodified base and is unrelated to this
patch.

## Submission guard

Do not submit this draft, create a branch, or contact the maintainer without
explicit owner authorization for that exact action.
