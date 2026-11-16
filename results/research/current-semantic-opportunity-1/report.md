# Current semantic opportunity — 2026-11-16

**What did we find?** Current Nanoda source supports a new, testable nested-
recursor hypothesis. An imported rule may contain a universe name that its owning
recursor does not declare. During nested-recursor validation, Nanoda renames the
declared imported universe to the reconstruction's universe name. That operation
can capture the rule's undeclared name and make the malformed rule compare equal
to the reconstructed rule. At runtime, substitution follows the recursor's
declared universe vector, so the undeclared name remains in the rule consumed by
reduction. A neutral recursive case should then reduce a well-typed application
to a term with an ill-typed recursive call. No input was generated or checker
run, so acceptance and the predicted reduct remain unobserved.

**Is it interesting?** Yes. This gives the rule-universe omission left by the
November 14 review a distinct consumed consequence. It is a different mechanism
from the published free-universe, parameter-order and proof-irrelevance cases:
the candidate relies on non-injective universe renaming during nested recursor
comparison. If observed, it would be a current validation-to-execution failure,
not another expected rejection or package exercise.

**Does it require more work?** Yes. Run one prospective E0 screen with a valid
alpha-renamed nested-recursor control and one candidate that changes only a
recursive rule's universe. Observe admission and retain a checked account of the
one-step reduct. Select `E0-NANODA-NESTED-RECURSOR-UNIVERSE-CAPTURE-1` READY and
stop before launch. A current rpylean wrong-argument repair remains useful if
this new hypothesis fails, but its exact witness is already public and therefore
has lower information value.

## Selected mechanism

Nanoda current master is
`0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`; exact blobs and reviewed ranges are
bound in [the source inventory](source-inventory.json).

For a monomorphic genuinely nested type such as a tree with `List Tree`
children, reconstruction selects an elimination universe named `u` because
`gen_elim_level` avoids only the inductive declaration's parameters. Construct
two otherwise identical exports:

1. The valid control consistently alpha-renames the exported recursor's
   elimination universe to `v` in its declared type and rules.
2. The candidate keeps the recursor declaration and ordinary rules under `v`,
   but changes one recursive `RecRule.val` consistently from `R(v)` to `R(u)`.
   The rule therefore remains schematically typable under `u`, while `u` is not
   in the owning recursor's parameter vector.

PR #84 added direct checked inference of every imported rule value. That check
runs without the owning recursor's `DeclarInfo`; the universe-membership check
in `infer_const` therefore does not establish
`universes(rule) ⊆ recursor.uparams`. For nested recursors, comparison then maps
the imported declared vector `[v]` to the restored vector `[u]`. The honest
`R(v)` becomes `R(u)`, while the malformed rule already containing `u` also
remains `R(u)`. The comparison has lost the distinction.

Reduction later substitutes application levels through the persistent imported
rule using only the owning recursor's declared vector. At an application such as
`Tree.rec.{1}`, the honest rule becomes `R(1)` while the candidate retains its
free `u`. With neutral children and motives/minors ending in `Sort 1`, the
candidate's recursive auxiliary call remains at `u` and should not type-check
against those arguments. Keep the recursive call observable rather than erasing
it through proof irrelevance or a closed computation.

This collision is specific to the inspected nested path. The ordinary path
aligns the constructed rule to the imported vector and compares it with the
untouched imported rule; the same `R(u)` versus `R(v)` change remains visible.
This is source reasoning, not a general proof or runtime result.

## Alternative with immediate repair value

Current rpylean main
`b581f0f362aca21a2be5d7ecb925bdbb0d3f8dbb` still checks only that a recursor
rule body calls the corresponding minor-premise head. It does not derive and
compare the arguments. The imported rule is later consumed directly by
reduction. Its source even records that the right minor with wrong arguments
still passes. Arena #350's `rec-rule-wrong-arg` is the exact public consequence:
replace `mk b` by `mk true` and derive `False` through a dependent motive.

That is a concrete repair opportunity. The current Arena harness in rpylean
scans only top-level YAML files while #350's cases live under `tests/bugs/`, so
the new case is not recursively discovered. A reproduction plus an honest
control could support a focused regression and constructor-derived argument
validation. It ranks second because the failure and affected implementation are
already publicly identified; running it would verify current repair need rather
than discover a new mechanism.

## Research value

This investigation changed the decision from “no recursor experiment” to one
precise current experiment with a predicted type-preservation consequence. Its
consumer is a Nanoda maintainer deciding whether nested rule alignment must be
made capture-avoiding and whether rule universe closure must be checked. The
source trace and eventual control/candidate are reusable for that repair. More
source-only refinement would add little: the next uncertainty is whether the
candidate can be represented, admitted and observed as predicted. The rpylean
lead remains a bounded fallback if the candidate premise fails.
