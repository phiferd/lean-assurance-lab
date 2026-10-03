# Nanoda quoted-name contract assessment

**What did we find?** Nanoda PR 38 already introduced a component model for
Lean names, but declaration selection and pretty-printing still flattened those
components into dotted text. That made three valid names from Nanoda issue 17
either unselectable or unreadable: `«b c»`, `A.«b c»`, and `A.«b.c»`. The
attached patch makes `pp_declars` parse and compare components and makes the
pretty-printer escape each string component independently. The four-case
regression also covers ordinary `A`, and rejects the invalid flattened alias
`A.b c`.

**Is it interesting?** Yes. The beneficiary is Nanoda issue 17: a caller can
reliably select the intended valid declaration and receive a name that retains
the relevant component boundaries. This is ordinary configuration and output
correctness, not a proof-acceptance, security, or universal name-fidelity
claim.

**Does it require more work?** The bounded implementation is ready for
maintainer consideration, but no upstream PR or message was authorized or
performed. A maintainer may decide whether to apply the portable patch on top
of PR 38. Components containing the closing delimiter `»` remain PR 38's
documented non-round-tripping boundary and are outside issue 17's four cases.

## Source and contract

- Repository: `https://github.com/ammkrn/nanoda_lib.git`
- Unchanged PR 38 base:
  `86060d51a69e91445bbae6b6b1366c12e05e67f0`
- Local patch head:
  `a3e17bf3d0f30a66384967929fba0d5c33d1e765`
- Current upstream `master` observed during assessment:
  `3a2407216ee84a75f9e1aead6803d0578be06ae7`
- Lean source revision named by PR 38 and the regression fixture:
  `470d5ce1400764999581fd26d5d72b00d990b0f4` (Lean 4.35.0-rc3).

Lean's `String.toName` documentation distinguishes a hierarchical `a.b` from
the simple component `«a.b»`, and `LeanExport.lean` decodes requested constants
as name literals with `Syntax.decodeNameLit`. The export format independently
stores string and numeric components with prefix links. Therefore selection by
component identity is the narrow contract needed here; raw dotted-text equality
is not sufficient.

## Exact change

The portable patch
[`0001-Fix-quoted-declaration-name-handling.patch`](0001-Fix-quoted-declaration-name-handling.patch)
contains the complete immutable range above. Its SHA-256 is
`aad3097be9a190967e1bda4483fbaadd8ba64831b0b9b16817381bf783bb5181`.

```text
src/name.rs           | 32 ++++++++++++++++++++-
src/parser.rs         | 10 ++++---
src/pretty_printer.rs | 68 ++++++++------------------------------------
src/tests/name.rs     | 78 ++++++++++++++++++++++++++++++++++++++++++++++++++-
src/util.rs           |  4 ++-
5 files changed, 129 insertions(+), 63 deletions(-)
```

The implementation adds internal conversion between arena names and
`Vec<NameComponent>`, validates `pp_declars`, performs the missing-declaration
check structurally, constructs selected names structurally, and formats each
component. It preserves the syntax-specific anonymous-root rendering `«»`.

## Scope boundaries

The new end-to-end fixture contains only valid axiom declarations named `A`,
`«b c»`, `A.«b c»`, and `A.«b.c»`. It does not construct malformed proof
terms or test checker acceptance.

PR 38's existing tests, not these four cases, define the nearby parser
boundaries: numeric components remain distinct from quoted numeric strings;
leading-zero numeric text normalizes to its numeric value; malformed delimiter
forms, empty input, and `[anonymous]` are rejected; `«»` denotes an empty
string component rather than the anonymous root. A component containing `»`
cannot be emitted as a round-tripping quoted literal by the existing formatter.
No broader Lean name fidelity is inferred.

## Result and stop criterion

The stop criterion was a smallest ordinary fix for reliable selection and
readable output, with regressions that fail on the unchanged PR 38 base and
pass on the patch head. That criterion is met. See `validation.md` and
`independent-review.md`. No upstream repository was changed.
