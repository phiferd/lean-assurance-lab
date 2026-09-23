# Kiota recursor-type reconstruction repair

Outcome: `SUCCESS`

At pinned Kiota revision `9fa2c297`, the local patch removes the concrete trust
path in which a serialized current-block recursor type could enter the
environment and later type declarations. The parser now stages the complete
inductive block transactionally, reconstructs ordinary, mutual and nested
recursor signatures from checked type and constructor declarations, compares
the closed supplied signature only after positional universe alpha-normalization
using Kiota definitional equality, and installs only the reconstructed type.

The builder follows the bound Lean construction order: shared parameters, every
motive, every minor, target indices, major premise and result. Nested prior-type
specializations are discovered breadth-first, restored without exposing an
auxiliary declaration, and assigned global motive/minor order. Failures roll the
entire staged block back, including type, constructor, recursor and ownership
metadata.

Patch revision 5 changes three production files and three test/fixture files.
The two new fixture copies preserve the exact inherited control and candidate
bytes. Focused tests cover exact candidate rejection and atomic rollback,
ordinary indexed recursion, two same-container nested specializations, deep
parametric nesting and a mutual-plus-nested group.

The final exact revision passed its offline build, all seven focused tests, the
six single-fixture matrix cells, and the full suite: 83 unit plus 77 integration
tests, 160 total, with zero failures or ignored tests. Every supervised process
reported complete cleanup and positive RSS observation.

Engineering failures were retained rather than erased. They exposed and led to
repairs for a test wrapper dereference, two-region de Bruijn relocation,
integration-harness accounting, universe-parametric constructor-field
classification, and reducible recursive targets. The penultimate full run
isolated one legacy synthetic whose `Type`-valued `List` and `Tree` blocks carry
Prop-only dummy recursors. The final patch preserves those 2,858 fixture bytes
unchanged but correctly makes them an expected rejection; weakening the source
gate would have recreated the trust flaw.

This is a pinned local result, not a universal format rule or proof of complete
Kiota soundness. It makes no current-tip, duplicate, maintainer-capacity or
upstream-acceptance claim. The exact patch and PR text are held locally. Any
submission requires a fresh target/duplicate/capacity preflight, rebase and
retest if needed, and exact human approval.

The project-wide closure comparison selects
`TRUST-ASSUMPTION-PIPELINE-PILOT-1` READY and unstarted for its source/reuse and
protocol-binding phase. It should not launch its scientific matrix until exact
six-fixture expectations and both observable report paths are bound.
