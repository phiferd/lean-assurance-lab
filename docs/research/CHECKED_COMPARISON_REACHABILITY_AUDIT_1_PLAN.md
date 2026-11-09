# Audit ordinary checked comparisons for missing typing premises

**What did we find?** Two small E0 screens now show expected rejection for
ignored application arguments and non-type Pi codomains on pinned Lean and
Nanoda. Those samples found no candidate defect and leave other comparison
paths unexamined.

**Is it interesting?** Yes. A bounded source-level map of where checked
ordinary imports compare expressions, and which typing facts hold at each
call, could identify a different reachable omission before spending checker
runs. The map would be a hypothesis inventory, not semantic authority.

**Does it require more work?** Inspect the current ordinary-declaration
admission paths and adjacent public tests, then either select one genuinely
new, independently justified prospect for a separate E0 campaign or record
that no such prospect cleared the gates. No checker cell starts in this item.

Item: `CHECKED-COMPARISON-REACHABILITY-AUDIT-1`, READY and unstarted.
Frontier: `F-DISCOVERY-AND-CONFORMANCE`.

Trace current official Lean and Nanoda ordinary axiom, definition, theorem and
opaque checked-import paths from parsing through any definitional equality or
other semantic comparison used for admission. For each concrete comparison,
record the origin of each operand, the preceding checked-inference or
formation call that establishes its typing, any infer-only/reduction shortcut,
and whether a malformed imported expression could reach the comparison.
Inspect adjacent public validation cases and distinguish direct coverage from
related tests. Pin exact source revisions and file/blob identities. Use
deterministic source search for the inventory, then review the reachable call
chains; do not infer safety from a checker vote or merely from a function name.

Explicitly exclude the completed ignored-argument and Pi-codomain E0 families,
the Lean eta alias witness, and recursor fault families. Avoid the extensively
studied let annotation/value case unless a distinct untested path is proved.
Compare at least two other candidate paths for raw-import representability,
independent expected behavior, public overlap and execution cost. Deliver a
dated source-to-operand matrix and one selected separate experiment with valid
control or a precise negative result. A follow-up experiment requires its own
fixed plan and E0 start; do not launch it here. Do not edit production checkers,
frozen evidence, external repositories or assurance milestones. Finish this
one item, rerank project-wide and stop before its successor.
