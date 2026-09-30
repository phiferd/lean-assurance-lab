# Prepare one narrow Lean eta pilot

What did we find? Pinned PR15373 source has a candidate mismatch between a reducing elaborator telescope and a kernel syntactic-Pi loop. The source-supported alias-preserved negative case is not a confirmed defect. Is it interesting? Yes, as a narrow boundary test of the proposed eta fix; existing issue12520 and renovation14977 already cover the broader problem. Does it require more work? Prepare exactly four cases and establish whether an existing exact pinned runner can observe them without a new large build. This selection leaves preparation unstarted and authorizes no checker launch.

See [the source/duplicate assessment](../../results/research/lean-eta-pilot-feasibility-1/assessment.md) for pinned links and expected shapes.

Source/fixture preparation only. Pin 015d54649bcaaa0861f355b59761ce308e629fbb.
Use a nonrecursive Box structure with one Bool field and zero parameters; compare
an arbitrary local f with the unapplied Box.mk. Preserve either an explicit
Bool → Box type or a reducible FnAlias := Bool → Box in the local/binder type.
Negative explicit/alias cases expect rejection; direct/eta controls expect acceptance.
Document Meta and kernel observations separately (a prospective eight-observation
matrix). Do not treat elaborator refusal as a kernel result or trust a generated
negative fixture from elaborator success alone.

Go only if raw fixture inspection retains .const FnAlias, an unvalued variable,
zero constructor arguments, distinct nonlambda negative heads, and a supported
exact pinned runner already exists without a new large build. Stop if type
normalization removes the alias, a valued let/lambda or full application masks
the seam, duplicate tests cover the same negative boundary, or the exact runner
is unavailable under the build restriction. Retain the boundary, not a larger
alias search or build campaign. No dynamic defect, acceptance or current-main
claim follows from source inspection. A future E0 launch requires its own selected
campaign, start, exact identities, expected-result review and existing supervision.

PR15374 is secondary: metadata-confirmed n=m−1 / n=m / n>m arity tests with
separate kernel/Meta outcomes only after this preparation is resolved. Do not
rerun copied Eq/PUnit/Prod examples from12520 or claim broad novelty. No upstream
communication or publication is authorized by this plan.
