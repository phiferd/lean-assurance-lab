# Adopt a lightweight exploration lane

Status: IMPLEMENTED; final full validation and refresh required before delivery.
Owner-directed on 2026-09-29 within F-DISCOVERY-AND-CONFORMANCE.

**What did we find?** The current workflow applies full research closure to
hypothesis screening. This item changes prospective handling, not past results.
**Is it interesting?** Yes: separate exploration from confirmation so ordinary
negative screening does not require repeated model-mediated closure.
**Does it require more work?** Implement one protocol, one event schema, one
record/validate command, and one append-only ledger with separate confirmation
proposals. Test the boundary and normal negative path; do not run a new study.

## Scope and completion

Implement E0 identity, prior question, raw observations and classification.
Record starts before execution, preserve interrupted attempts and all outcomes,
and reject incomplete observation as NO_SIGNAL. Promotion creates a separate
planned confirmation identity; it neither relabels E0 nor authorizes launches.
Use existing supervisors; no new process runner, model orchestrator or dashboard.
No changes to frozen science, historical tooling, milestone gates or external
projects. Explicitly amend prospective workflow/agent guidance so a routine E0
record does not invoke the full-suite/assurance-refresh/independent-review path.
One or two commits is the normal E0 delivery target, not a scientific stop rule.

Run focused schema/lifecycle/path/append/promotion/denominator regressions, queue
and historical-transition checks, then the full current/historical payload suite
for this shared workflow change. Refresh current derived artifacts through the
existing script and verify freshness. Select a feasible successor without
executing it. Ordinary E0 records thereafter need only their lightweight checks;
shared tooling changes retain affected validation. Main-only delivery applies.

## Selection

This owner-directed process change outranks the unstarted memory attribution
audit: it reduces overhead across future semantic investigations. The earlier
closure-controller repair remains useful separate work. Compare it with a
semantic exploration campaign at closure; do not claim measured savings until
actual use. Reuse local JSON Schema validation and the existing queue; no new
scientific method or external literature claim is introduced here.
