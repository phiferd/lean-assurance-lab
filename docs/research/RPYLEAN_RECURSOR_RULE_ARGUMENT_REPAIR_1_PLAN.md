# Repair rpylean recursor-rule argument validation

Arena #350 already reports that rpylean accepts a recursor computation rule
which calls the correct minor premise with the wrong constructor argument and
thereby proves `False`. Current source still documents the missing argument
check, but the Lab has not run the current revision. Yes, this is useful work if
it ends in a reviewable checker repair and durable regression. Reproduction is
only the baseline, not the deliverable.

Item: `RPYLEAN-RECURSOR-RULE-ARGUMENT-REPAIR-1`, READY and unstarted.
Target: rpylean `b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb`.
Consumer: an rpylean maintainer deciding whether to adopt the local patch.

## Entry and fixed semantic obligation

Bind the exact source/runtime and obtain the byte-identical Arena
`rec-rule-wrong-arg` candidate plus an honest control. Before modifying source,
show on the pinned revision that the control completes and the candidate reaches
the intended recursor-rule path. If current source already rejects the candidate,
close with the attributable repair evidence and do not manufacture a patch.

The semantic obligation is stronger than checking the minor head: after peeling
the rule's parameters, motives, minors and constructor fields, the rule body
must be definitionally equal to the constructor-derived application of the
corresponding minor premise, including every field and recursively generated
induction-hypothesis argument in the right order and at the right dependent
types.

Start with the smallest ordinary, single-motive fragment needed by the public
one-field witness. Map rpylean's actual supported recursor shapes before coding.
Do not silently claim coverage for mutual, nested, quotient, K-like or multiple-
motive rules unless their expected spines are derived and tested. If a partial
check would accept unknown shapes or reject valid supported inputs, stop with a
precise implementation design instead of shipping an unsound compatibility
shortcut.

## Implementation and validation

Work in a pinned local checkout; retain the exact patch separately in this
repository. Add a direct regression that fails before the repair and passes
after it, plus honest dependent and recursive controls that exercise the
supported fragment. Prefer deriving the expected application from constructor
and recursor metadata already checked by rpylean. Do not use checker consensus as
the oracle or weaken definitional equality to make tests pass.

Run the focused regression and the upstream full test suite on the exact repaired
tree. Preserve any pre-existing failures separately from changes caused by the
patch. If reliable direct execution requires a harness correction, make only the
smallest local change needed for the regression and keep general recursive Arena
discovery as a separately reviewed follow-up.

Deliver:

- failing-before and passing-after evidence for the public candidate;
- passing honest controls and upstream tests;
- the exact local patch and source identities;
- a concise implementation note defining covered and unsupported recursor
  shapes; and
- a `*-pr.md` submission draft and external-contribution ledger entry marked as
  prepared, not submitted.

No issue, pull request, comment, review, branch, push or other external write is
authorized. External submission requires the owner's explicit approval for the
exact rpylean pull request. Finish this one implementation item, perform the
project-wide successor review, and stop before any external action or successor.
