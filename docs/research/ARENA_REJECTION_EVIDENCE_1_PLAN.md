# What evidence supports Arena's reported rejections?

**What did we find?** Four checker commands in the November 18 Lean Kernel
Arena publication turn every nonzero command exit into code 1. Arena reads 1
as a rejection and credits it on tests that require rejection. In separate
local rpylean runs, three startup failures and two genuine rejections all
returned 1. Whether an operational failure received credit in Arena is unknown.
[Arena scoring code](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/lka.py#L1756-L1783)
· [Local runs](../../results/research/rpylean-published-three-case-verification-1/report.md)

**Is it interesting?** Yes. People use Arena to learn which invalid inputs
independent checkers can detect. Its published diagnostics give the Lab a way
to check what that claim rests on across four integrations.

**Does it require more work?** Audit one dated publication. Give Arena
maintainers the exact rows that support their labels, need better evidence,
or warrant a correction. The audit is selected and unstarted.

## Input and selection

Use the archived November 18, 00:10:29 UTC publication. Its uncompressed SHA-256
is `78f7fc5897df9357f77db123f28ecfee3c6b7acd4fafa9fc98265d556b4a87eb`,
recorded by the preceding investigation. Verify it before extraction. The
publication names Arena revision `ef915093da536931892f1bfdaffb2a2d59529fe7`.
[Archived public JSON](../../results/research/arena-publications/2026-11-18-results.json.gz)
· [Earlier digest and publication identity](../../results/research/rpylean-recursor-missing-ih-investigation-1/upstream-review.json)

Use all four published commands containing the unconditional `|| exit 1`
mapping. They belong to rpylean, nanobruijn, nanoclo and mathgraph. Select
every result for those profiles with test metadata `outcome=reject` and result
`status=rejected`, `correctness=correct`. Record the denominator and exclusions
by checker. Link checker and test hashes, original job, dates and captured
output for each selected row. Results may have been reused from earlier jobs.
Establish the descriptor and checker identity that produced a row before
attributing its outcome to a particular command.

## Decision rules and deliverable

- Credit a checker rejection when the diagnostic or a traceable checker code
  path shows a deliberate input rejection. A parser rejection can be the
  intended result for a malformed file. Distinguish validation of a different
  property from evidence that the intended defect was detected.
- Identify an operational failure only from positive evidence such as failure
  to start the process or open its input. Identify explicit unsupported-input
  refusals separately. A panic, bare exit code or missing diagnostic alone
  leaves the reason unresolved. Respect Arena's separate timeout handling.
- Use the published `corner-cases/proof-param-ok` row for each profile as a
  valid-file comparison. Record its actual outcome and job identity. Success
  in another run cannot establish what happened on a rejected file.
- Deliver a reproducible row inventory and counts for each disposition. For a
  demonstrated mislabeled row, identify the smallest change to the specific
  integration or result label that would distinguish the two outcomes and a
  regression check for it. If evidence is missing, identify exactly what a
  future run must retain. If the rows support their labels, close with a
  bounded no-change recommendation. This is an audit of existing runs.

The [Arena exit-code contract](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/README.md#L198-L208)
governs the reporting question. Agreement between checkers supplies no
semantic authority over the tests.
