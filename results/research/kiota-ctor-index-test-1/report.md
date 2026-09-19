# Kiota constructor owner-index regression

`KIOTA-CTOR-INDEX-TEST-1` produced one test-only patch at freshly bound Kiota
`9fa2c297dd700fe8fd1712a86bdbb258e1c01c42`. The focused pair passed 2/2 with
70 integration tests filtered out. The complete current suite passed 83 unit
and 72 integration tests, 155 total, with zero failures or ignored tests. Both
counted build/test reservations completed cleanup and used 14.729227207950316
process seconds.

The entry source/duplicate gate was committed at `8c92b9b87d9b349a67493fbf5305b133eda20e4e`.
The exact patch, dependencies, toolchain, commands, expected counts and process
controls were committed at `15252e96c00f3ebdd51f088c329a1e889fd790be`
before either launch.

The patch copies the exact existing 6,332-byte control and candidate into the
Kiota fixture convention. The control accepts with `LALNest.node.cidx = 0`; the
candidate changes only that scalar to `1` and is required to return
`TcError::Reject` with the exact owner-list/index message. Existing
`orphan-ctor` remains unchanged and covers the separate missing-owner branch.
Every other source-archive byte is verified unchanged by the launch gate.

This is preventive public-import regression coverage, not a demonstrated
current defect, proof of soundness or universal metadata adjudication. It covers
the out-of-range manifestation of the combined predicate, not a separate
in-range wrong-name occupant. Mutation sensitivity and other metadata fields
were not tested. Existing compiler warnings were preserved without production
repair.

Five of six source/setup/duplicate requests were charged, including two failed
browser API attempts. The fresh response reported unchanged `main`; the bound
complete open-PR response contained zero entries. This does not imply later
upstream state or maintainer capacity. Two builds and two test processes used
the exact committed toolchain, dependencies, inputs, commands and process
controls. No checker, proof, mutation, new export or external research write
occurred.

Retain the [local PR draft](../../action-recommendations/drafts/kiota-constructor-index-regression-pr.md).
Submission requires a fresh target/duplicate/capacity preflight, any necessary
rebase and retest, and exact human authorization for a PR to
`sankalpsthakur/kiota`. No submission is authorized here.

The project-wide comparison selects `SURVIVOR-THREAD-ONE-DETERMINISM-1` READY
and unstarted. The theorem companion still lacks distinct-risk evidence,
original CVC-4/CVC-5 gates remain unmet, and transfer intake still lacks an
independently supplied package. The one-thread source assessment is locally
feasible and can clarify whether the final operational survivor admits a safe
deterministic protocol without launching it in this item.
