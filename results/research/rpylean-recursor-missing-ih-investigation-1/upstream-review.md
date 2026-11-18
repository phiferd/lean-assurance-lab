# What the November 18 rpylean change establishes

**What did we find?** Julian closed PR #36 unmerged after publishing his own
implementation. The Lab inspected the three changed files and ran the checker’s
environment tests at his exact commit. Eighty tests passed and one had its
expected failure. The two disputed Arena cases were absent from those tests.
The published Arena results for both cases use an older checker.

**Is it interesting?** Yes. The new checker derives the rules for induction
from the type and its constructors, then checks the declared rules against
them. It also checks what forms of recursion are allowed in constructor
fields. That supports Julian’s explanation as a lead. The reason the older
checker accepted the file, and how the published commit handles that exact
file, remain independently unverified.

**Does it require more work?** Yes, for a verdict on either case. Prioritize
evidence that identifies the published checker revision, the input bytes and
the observed result. Hold further work on the older checker until such a
result shows which maintenance question remains. There is no current reason
to extend or resubmit PR #36.

## Two claims with different evidence

| Case | What Julian reported | What the Lab established |
| --- | --- | --- |
| `rec-missing-ih` | The commit names the case as fixed and attributes its earlier acceptance to the strict-positivity check. This check restricts how the type being defined may appear in constructor arguments. | The cited commit implements constructor-field validation and derives the expected induction rules. The tests and public results inspected provide no case-specific verdict on this revision. |
| `rec-rule-wrong-arg` (PR #36) | Julian believes his published changes also cover the PR case and welcomed reports of other gaps. | The published checker compares each declared computation rule with a derived rule. The PR closed without merge. Equivalence on the submitted case remains unverified. |

The published change is commit `a31ca02a`, based on `0ddcb018`. We verified
the Git object identity of each changed file. Three focused unit tests accepted
a parameterized type, constructors of a mutually defined pair of types, and
a valid induction rule. Those three are included in the 81 tests in the
environment suite. The Lab ran the suite with the untranslated PyPy checker.
[Commit](https://github.com/Julian/rpylean/commit/a31ca02a158b9aabeb040b9984c21b1f4c8e3216)
· [Maintainer’s closing comment](https://github.com/Julian/rpylean/pull/36#issuecomment-6985520690)
· [Input identities](upstream-inputs.json) · [Observations and test output](upstream-review.json)

## Which checker did the public tests cover?

GitHub listed zero Actions runs with the cited commit as their head. Two
successful CI runs covered `2fbc3f71`, seven commits later. Across both runs,
all eight jobs skipped the optional Arena module in both the interpreted and
translated tests. An intervening commit added collection of grouped Arena
tests, which addresses the collection issue in the Lab’s earlier report.
[CI job](https://github.com/Julian/rpylean/actions/runs/44350640878/job/134964990855)
· [Collector change](https://github.com/Julian/rpylean/commit/377a7abbb95d2cee5db9a9f5bc25767544f95bc2)

Arena’s November 18 results snapshot records that rpylean `463a3101` accepted
both cases on November 14. Arena marked both verdicts incorrect. That
independent observation concerns a third, older revision. A future record of
rejection on the cited commit could establish the behavior for a specific file.
Attributing rejection to a particular check would also require evidence that
identifies which check decided it.
[Arena run](https://github.com/leanprover/lean-kernel-arena/actions/runs/43535627343/job/132264316384)
· [Arena checker pin](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/checkers/rpylean.yaml)
· [November 18 snapshot digest and rows](upstream-review.json)
