# String constructor reconstruction regression

`NANODA-STRING-RECONSTRUCTION-TEST-1` produced one test-only patch at Nanoda
`4c544ed4099c8227f07d5de77ad1e69fb0740a27`. Two focused tests and all 40 library
tests passed; zero binary tests and eight ignored documentation examples match
the frozen expectations. Both counted build/test reservations completed with
successful cleanup, using 12.084409499017056 process seconds. Two read-only source
requests confirmed the unchanged source and open PR inventory. No production
change, proof, mutation, new serialized export or external research write occurred.

The patch covers four Nat/String flag combinations with cached names present or
absent, and both an empty payload and `Aé𝄞`. Its two positive cases inspect every
constructor name, argument count, universe level, Unicode scalar and terminal
list node. Fourteen other state/payload combinations require reconstruction
refusal from valid String pointers. Enabled raw literals must be present with
the expected variant and text. These case counts follow the fixed test loops;
the runtime receipts report the two named tests, not independently instrumented
per-cell events.

Flags are set before constructing each permanent/temporary DAG. Existing
Empty/export and permanent name interning supply the fixture; the declaration
map remains empty. Cached names are not declarations. This verifies an internal
expression-shape contract, not typing, definitional equality, public checker
acceptance, a universal obligation or a current bug. All missing constructor
names are absent together, so individual missing-name arms remain unisolated.
Mutation sensitivity was not measured.

The entry was committed at `1fde6e309ae1ef3f365ce5e1ba801ee585789504`; exact
scientific inputs, patch, dependency files, tooling, commands and process controls
were frozen at `67e4c3957e92b15382c714a44d71e27337a02f1e` before either launch.
The implementation reuses the reviewed Nat-dispatch fixture helper and is
independently reviewed in [patch-review.json](patch-review.json). Raw evidence and
accounting are retained under [execution](execution/accounting.json). Lab closure
validation is recorded separately in validation.json and delivery-accounting.json.

Retain the [PR draft](../../action-recommendations/drafts/nanoda-string-reconstruction-tests-pr.md)
locally. Existing PRs #32/#33 were observed open and unmerged on 2026-09-18;
review and CI state were not queried. Submission requires a fresh source,
duplicate and maintainer-capacity review, any necessary rebase/retest, and exact
owner authorization. The present request authorizes no upstream submission.

The project-wide comparison selects the existing
`SURVIVOR-THREAD-ONE-DETERMINISM-1` source-only assessment, unstarted. Four local
Nanoda test candidates now exist alongside two open PRs, while further test or
documentation work lacks a distinct supported gap. The operational survivor has
a concrete unresolved witnessability question and an existing finite plan. Its
analysis gate does not require a trigger already in hand; a trigger is required
before a later separately selected experiment. The original historical survivor
result and budget remain intact. Other Arena, CVC and transfer prerequisites
remain unmet. See strategic-advice.json and the bound closure queue review.
