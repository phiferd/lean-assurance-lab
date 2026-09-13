# Arena-let decision after lean4export #48

The [reply by nomeata](https://github.com/leanprover/lean4export/issues/48#issuecomment-5654286873),
observed on 2026-09-13, changes the practical recommendation. It directly answers
the exact let mismatch question by allowing implementation choice under a
pragmatic policy: accept ordinary elaborator/kernel inputs, reject likely
unsound cases, and tolerate ambiguity. It explicitly lacks a completely
authoritative answer and presents this as the author's own take.

The old Arena-let result remains BOUNDED_UNRESOLVED as recorded. Its current
blanket rationale—no affirmative support for permitting both outcomes—has now
been overtaken by this response. There is positive scoped support to propose
an `either` characterization for the unchanged 601-byte candidate. The Lab's
affirmative-support rule was a portfolio rule, as the historical erratum
explains; it was not an Arena schema restriction.

Select **ARENA-LET-POLICY-FOLLOWUP-1 READY and unstarted**, ahead of the still
READY Nanoda nested-namespace design. Its task is a current Arena duplicate,
policy and practical-value review followed by at most one existing-byte
package, or a concrete no-value result. Check semantic overlap and executable
behavior, not just byte hashes. An `either` case must provide useful corpus
coverage or diagnostics. Include the matching control only for a distinct
benefit. The historical pair changes both the let value and the enclosing
declaration type; it is not a single-field control. Do not wait for universal formal authority as a prerequisite to this
practical review. No package or label has yet been adopted by Arena.

This feedback supplies neither universal semantic authority nor a soundness
proof. The author's optional suggestion to use the official kernel as a
stricter specification does not amend the Lab's frozen authority registry.
Historical observations, raw bytes, original closures and catalog decisions
remain unchanged. Comment timestamps were absent from the connector receipt;
the issue's update time is not used as a substitute.

The response also informs the held-local metadata appendix: do not repeat the
general request for one universal policy. A further question must identify a
distinct practical documentation need. There is no authorization to reply,
submit a test, or create another upstream issue in this checkpoint.

Exact receipts, source attribution, preserved predecessor bindings and
prospective gates are in [recommendation-successor.json](recommendation-successor.json).
The original waiting trigger is now observed and incorporated. This checkpoint
records the changed recommendation and successor; it does not execute it.
