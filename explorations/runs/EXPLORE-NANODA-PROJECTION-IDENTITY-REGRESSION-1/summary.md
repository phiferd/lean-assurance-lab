# Nanoda projection-identity regression screen

**What did we find?** Current Nanoda at `3a240721` still enforces the historical
projection type-name guard, but its source tree has no direct regression for
that branch. We constructed one test through public `TypeChecker::def_eq`. It
passed on the fixed source, failed at the intended assertion when only the
historical guard was removed, and the fixed full suite passed all 45 tests. We
did not test maintainer acceptance, other Nanoda revisions, or a general rule
for all projection expressions.

**Is it interesting?** Yes. The earlier 90-input corpus miss exposed a real
coverage gap, and this screen turned it into a small test that detects the exact
historical omission without changing production code. It does not reveal a
current checker defect or security issue.

**Does it require more work?** Recommend one small test-only PR to
`ammkrn/nanoda_lib`, using the retained patch below. The proposed PR should say
that it protects the projection-name fast path added by PR #23 and should cite
the fixed/mutant/full-suite results. No further research or official-Lean action
follows: Lean Kernel Arena already has a direct regression for its separate
nested-unused-parameter fault. Submitting the Nanoda PR remains a separate
external action requiring the owner's explicit approval.

## Exact result

- Target: Nanoda `3a2407216ee84a75f9e1aead6803d0578be06ae7`.
- Historical fix: `404660cc2fbf04d8040d25a15ddd55b6b15c8e5e`
  (merged as [PR #23](https://github.com/ammkrn/nanoda_lib/pull/23)).
- Candidate: [`regression.patch`](regression.patch), adding one Rust unit test,
  one 75-line exported two-field structure fixture, and its config; no
  production source changes.
- Fixed focused run: 1 passed, 0 failed.
- Exact-mutant focused run: 1 failed at
  `!tc.def_eq(left, other_type)` after the equal-name and distinct-index
  controls passed.
- Fixed full suite: 45 passed, 0 failed; 8 documentation tests remained ignored.
- Duplicate check: current source contains no equivalent direct test; the
  GitHub projection search found the merged fix PR and an unrelated historical
  projection-from-Prop PR, but no open equivalent test PR.

Two invalid attempts remain visible. The first never reached a test because the
sandbox blocked supervisor process observation. The second used an unqualified
exact Rust filter and ran zero tests. Neither contributes to the result; both
were repaired without changing the candidate.

## Recommendation for the PR

Suggested title: `test: cover projection type names in def_eq`

Keep the contribution test-only and state the obligation narrowly: the
projection-congruence fast path must not return true solely because the index
and structure match when the recorded projection type names differ. Cite the
one-conjunct mutant result as test-sensitivity evidence. Avoid claiming that
all differently named projections are semantically unequal after reduction,
or that current Nanoda has a production defect.
