# Nanoda projection-identity regression screen

Evidence class: E0

## Question and value

Can one small test against current Nanoda isolate the historical
`def_eq_proj` guard that requires projection type names to match? The useful
candidate must enter through public `TypeChecker::def_eq`, use a nonreducing
well-typed structure expression, and distinguish the fixed source from the
exact historical one-conjunct omission.

This follows a demonstrated coverage gap. Nanoda's historical fix
`404660c` added the type-name check, but its tests covered name-prefix helpers,
and the current upstream test inventory contains no direct projection-identity
regression. Official Lean's other historical fault is out of scope because the
Arena already retains `tests/nested-unused-param.lean` as a direct shared
regression.

## Fixed scope and entry gate

Target upstream Nanoda revision
`3a2407216ee84a75f9e1aead6803d0578be06ae7`. Before observation:

- retain the exact current source identity and confirm that the guard remains
  present and no equivalent test exists;
- retain one test-only patch and one exact mutant patch that removes only the
  `ty_name_l == ty_name_r` conjunct;
- use one negative pair with the same projection index and the same
  nonreducing, well-typed structure expression but distinct projection type
  names;
- include neighboring controls showing that equal type names with the same
  structure compare equal and that a different projection index does not;
- append the E0 start before building or running either source variant.

Run the focused test on fixed and mutant source, then run the full current
suite with the test patch on the fixed source. Preserve commands, patches,
stdout, stderr, exit status and source/tool versions. A useful signal requires
all controls to pass on the fixed source, the target assertion to fail under
the exact mutant, and the fixed full suite to pass. Ordinary build or fixture
failures are repaired within this screen and retained.

## Completion and limits

Close with `SIGNAL` only if the test reaches `TypeChecker::def_eq`, is sensitive
to the exact historical omission, and passes the current full suite. That
supports a recommendation for one small test-only Nanoda PR; it does not claim
a current checker defect, a security issue or a general semantic rule for all
projections. Close `NO_SIGNAL` if a maintainable non-helper test is shown to be
duplicate or insensitive. Use `INCONCLUSIVE` if the property cannot be isolated
without an invented Lean contract or unresolved infrastructure failure.

No upstream write, issue, PR, comment, release, checker fix, Box/FnAlias work,
assurance promotion or unrelated source change is authorized. External action
requires separate human approval after the exact local candidate and results
are reviewable.
