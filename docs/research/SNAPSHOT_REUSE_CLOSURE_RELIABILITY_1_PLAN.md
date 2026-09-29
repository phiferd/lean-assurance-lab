# Validation snapshot and stage reuse closure reliability 1

Status: PLANNED on 2026-09-29. Frontier: `F-DISCOVERY-AND-CONFORMANCE`.

This prospective engineering item repairs two known closure risks before any new E1 confirmation. It is separate from the current E0 screen and the fresh-checkout exploration-ledger CI repair. Do not start it merely because it is recorded here.

First, advisory ownership alone does not prevent arbitrary edits to validation inputs during a run, including an edit followed by restore (ABA). At entry, inventory the exact closure inputs and current validation controller. Run validation against an immutable input checkout or content snapshot, with a matching publication check that refuses to publish a result if the current source no longer matches the validated input. Preserve an attempted arbitrary concurrent edit-and-restore as a regression and prove it cannot contaminate the published validation receipt. Bind historical scientific attempts to their original bytes.

Second, current global inventory includes `HEAD`, so an unrelated documentation or report commit invalidates costly stages. Define each stage's complete direct and transitive dependencies and reuse decisions from those exact dependencies. A regression must show that an unrelated report/doc change reuses the costly unchanged suite, while an actual test dependency change invalidates that suite. Fail closed on incomplete or unexplained dependencies; preserve previous receipts and all failed attempts.

Run focused controls and the full current/historical suite because the shared closure path changes. Exercise an ordered closure in a separate checkout against exact committed inputs. Do not edit frozen scientific evidence, waive a gate, launch a scientific experiment or contact an external project.

Completion is a reproducible passing closure receipt for immutable validation input and matching publication, ABA resistance, unrelated-change reuse, dependency-change invalidation and historical binding preservation. **Future E1 entry gate:** no LazyLean or other successor confirmation proposal may become READY or launch until this item is COMPLETE with a passing exact-input receipt; the E1 queue item must name this dependency and bind the passing receipt in its own launch review. A PLANNED proposal may still be drafted. The E0 screen has no such dependency because it makes no confirmatory claim.
