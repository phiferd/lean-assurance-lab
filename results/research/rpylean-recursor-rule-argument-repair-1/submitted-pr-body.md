## What this fixes

rpylean currently accepts a malformed recursor computation rule that applies
the correct constructor case to the wrong field value. In the public
`rec-rule-wrong-arg` case, that is enough to derive `False`:

```text
fun motive mk b => mk true
```

is accepted where the rule must be:

```text
fun motive mk b => mk b
```

The existing validation checks that the rule calls the expected minor premise,
but not that it supplies the constructor fields and recursive induction
hypotheses correctly.

## What changes

For a deliberately bounded ordinary-recursion fragment, this PR derives the
complete expected rule from the recursor and constructor declarations and
requires definitional equality with the imported rule. It also:

- checks that rules follow constructor order;
- supplies every constructor field in source order;
- derives induction-hypothesis arguments for direct recursive fields;
- checks the independently assembled rule telescope and body; and
- keeps the recursor being validated opaque during the comparison, so an
  imported rule cannot justify itself through iota reduction.

The public wrong-field case is accepted before this change and rejected after
it. Honest dependent and direct-recursive controls continue to pass.

## Scope

The complete comparison currently applies to one ordinary inductive with one
motive, no parameters or indices, no nested types, and no higher-order
recursive fields. Direct recursive fields are supported.

Parameterized, indexed, mutual, nested, multiple-motive, and higher-order
recursive recursors retain the previous validation path. This PR does not claim
to close those cases.

## Validation

- focused recursor-rule tests: 12 passed;
- full untranslated suite: 815 passed, 1 skipped, 1 expected failure;
- RPython translation: passed;
- translated tests: 9 passed; and
- exact 27-declaration `rec-rule-wrong-arg` export: accepted before, rejected
  after.

The separately observed `rec-missing-ih` acceptance also occurs on the
unmodified base and is outside this PR's stated fragment.
