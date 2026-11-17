# rpylean recursor-rule argument repair scope

The patch rejects Arena #350's published wrong-field computation rule and keeps
the fixed honest dependent and direct-recursive controls valid. This is useful:
the imported rule no longer reaches reduction merely because it names the right
minor premise. It does not complete general recursor validation.

The strengthened comparison applies only when the whole recursor has one
ordinary inductive, one motive, no parameters, no indices, no nested types and
no reflexive (higher-order recursive) fields. Within that fragment it:

1. requires rules to follow authoritative constructor order;
2. derives the corresponding minor application with every field in source
   order;
3. adds a canonical recursive call for every direct recursive field;
4. assembles the expected telescope independently of the rule RHS, using the
   recursor declaration's motive/minor binders and constructor field binders,
   then infers and compares the imported and expected rule types;
5. requires definitional equality of the complete imported and derived rules;
   and
6. makes the recursor under validation opaque to iota reduction during those
   comparisons, preventing its untrusted rules from justifying themselves.

Parameterized, indexed, mutual, nested, multiple-motive and higher-order
recursive rules retain the prior head-only or shape-only validation. They are
explicitly unsupported by this repair and remain a semantic gap; the patch does
not claim they are safe. Extending them requires the full parameter, index,
global-minor and lambda-IH derivation used by Lean's `mk_rec_infos` and
`mk_rec_rules`, plus matching controls.

The patch is bound to rpylean
`b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb`; its SHA-256 is
`44b2778c2511d17c9e7b813bad6f0b49a881a2717dc5e648b0b53d0636746757`.
No upstream branch, issue, pull request, comment or other external write was
created.
