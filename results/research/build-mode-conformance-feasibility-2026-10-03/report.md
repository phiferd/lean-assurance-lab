# Build-mode conformance feasibility assessment

**What did we find?** The retained Nanoda source does not support the planned
three-way `debug` / `release` / `overflow-check` comparison as three distinct
project configurations. Its manifest explicitly enables overflow checks in
both the `release` and `test` profiles, while Rust's development profile also
enables overflow checks by default. The only source-visible mode distinction
with a plausible checker effect is therefore whether `debug_assert!` is
compiled. Ten such assertions occur in the retained source snapshot. Two in
`tc.rs` are directly downstream of imported expression shape, but exercising
their false branches would require deliberately malformed checker input.

**Is it interesting?** Yes, as a negative feasibility result. It removes the
configuration premise that has blocked `BUILD-MODE-CONFORMANCE-PILOT-1` since
2026-09-28 and prevents a broad three-build matrix whose third column would not
represent a distinct supported Nanoda policy. It does not establish that debug
and release behavior agree, that any assertion is reachable, or that Nanoda has
a validation defect.

**Does it require more work?** Do not promote the existing three-configuration
pilot. A future owner-approved successor could compare only the supported
development and release profiles, but only after a maintainer-facing assurance
property is named and valid or documented expected-behavior fixtures reach the
selected site. This assessment intentionally does not construct malformed
proofs, execute a checker, or demonstrate acceptance after a disabled
assertion.

## Beneficiary and missing property

The direct beneficiary is the planned Nanoda build-mode conformance pilot. Its
missing property was: “the same documented checker verdict is invariant across
three supported build configurations.” The retained build contract shows that
the proposed three configurations are not distinct. The narrower property that
could still matter to Nanoda maintainers is: “documented public-input verdicts
do not depend on compilation of `debug_assert!`.” No existing retained evidence
binds a valid or documented expected-behavior fixture to a potentially
observable assertion site, so that narrower property is not ready for
execution.

## Exact evidence and novelty check

This review uses the complete retained Nanoda source snapshot at revision
`6ae1f0cd962f081f6c423454c5da729d841236a7`, whose source lock is
`results/research/alt-survivors-2026-09-08/source-lock.json`.

- `Cargo.toml` SHA-256
  `04b9d07cfa907f587abc7541b1bf400960e54d6df596d07c0a50c4ce1808d375`
  sets `overflow-checks=true` for `[profile.release]` and `[profile.test]`.
- The retained source contains exactly ten `debug_assert!` calls: three in
  `tc.rs`, one in `expr.rs`, five in `inductive.rs`, and one in
  `union_find.rs`.
- `tc.rs:770` checks that a `Sort` head has no application arguments before
  rebuilding the sort; `tc.rs:803` checks that a `Pi` head has no application
  arguments before returning the head. Both consume expression structure
  originating from checker input and are the only small direct candidates for
  a verdict-level build-mode question.
- `tc.rs:785` is guarded by the preceding `Lambda { .. } if !args.is_empty()`
  arm, so its empty-argument assertion is structurally redundant in that
  match. The other seven assertions protect substitution, nested-inductive,
  pointer-identity, or union-find invariants and lack an already documented
  public-input fixture in the retained evidence.
- Repository history contains no completed build-mode feasibility artifact;
  current planning repeatedly records the missing supported configurations and
  selected source sites. Existing mutation, resource, and test-effectiveness
  results address different questions and are not evidence for build-mode
  invariance.

Rust profile defaults are relevant only to interpreting the retained manifest;
this report makes no claim about arbitrary command-line overrides. An override
could manufacture a third build, but it would not satisfy the plan's requirement
for a supported project configuration without separate upstream evidence.

## Smallest useful deliverable and stop criterion

The useful deliverable is this source-and-manifest feasibility disposition:

1. reject the current three-configuration matrix as non-distinct;
2. retain `tc.rs:770` and `tc.rs:803` as review leads, not executable cases;
3. require a valid or documented expected-behavior fixture and a named
   maintainer-facing verdict property before any two-profile successor; and
4. avoid treating assertion presence alone as defect evidence.

The stop criterion is met: the exact build contract and bounded source
inventory either had to identify three distinct supported configurations and a
safe observable site, or explain the blocking boundary. It establishes the
latter. No build, checker process, candidate generation, source mutation,
reserved historical-fault artifact, Box/alias artifact, or external action was
performed.
