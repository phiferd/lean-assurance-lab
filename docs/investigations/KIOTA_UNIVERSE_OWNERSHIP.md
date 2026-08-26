# Kiota Accepts an Undeclared Universe Parameter in a Definition Value

Status: `SUBMITTED_UPSTREAM_AWAITING_ADJUDICATION`

Upstream issue:
[sankalpsthakur/kiota#3](https://github.com/sankalpsthakur/kiota/issues/3)

Suggested upstream issue title:

> Kiota accepts a definition value that references an undeclared universe parameter

## Summary

Kiota accepts a small Lean export containing a definition whose value references
universe parameter `u` even though the definition declares no universe parameters.
The official Lean 4.33.0 kernel rejects the same artifact with
`defnInfo invalid`. Both checkers accept a positive control that differs only by
declaring `u` on the definition.

This disagreement reproduces on Kiota's current upstream `main` revision
`686063c13b22ce379c05dfe7fc03656655ac60e5`, not only on the older Lean Kernel
Arena pin.

## Mechanically Reproduced Outcomes

| Input | Official Lean 4.33.0 | Kiota upstream `686063c` |
| --- | --- | --- |
| Undeclared-universe artifact | `REJECT` (exit 1) | `ACCEPT` (exit 0) |
| Declared-universe control | `ACCEPT` (exit 0) | `ACCEPT` (exit 0) |

The machine-readable reproduction is
[`results/investigations/kiota-universe-ownership/upstream-main.json`](../../results/investigations/kiota-universe-ownership/upstream-main.json),
SHA-256 `1164b49adaa76dc9a078c6a20d880788366205855b3d3aa5dca3a63846d07983`.
Its required predicate is:

```text
official(artifact) = REJECT
and official(control) = ACCEPT
and kiota(artifact) = ACCEPT
and kiota(control) = ACCEPT
```

The predicate evaluated to `true` on 2026-08-24.

## Reproducer

Artifact:
[`corpus/minimized/nanoda-0003-auto-universe-min.ndjson`](../../corpus/minimized/nanoda-0003-auto-universe-min.ndjson),
SHA-256 `6743315bd44cd3ada0eb4a23336f73eca909ecbb6202c3fff3a8068bf0df101a`.

```json
{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},"format":{"version":"3.1.0"},"lean":{"githash":"f72c35b3f637c8c6571d353742168ab66cc22c00","version":"4.29.1"}}}
{"in":1,"str":{"pre":0,"str":"unused"}}
{"in":2,"str":{"pre":0,"str":"u"}}
{"il":1,"param":2}
{"ie":0,"sort":0}
{"axiom":{"isUnsafe":false,"levelParams":[2],"name":1,"type":0}}
{"in":3,"str":{"pre":0,"str":"bad"}}
{"const":{"name":1,"us":[1]},"ie":1}
{"def":{"hints":"opaque","levelParams":[],"name":3,"safety":"safe","type":0,"value":1}}
```

The final declaration is conceptually:

```text
axiom unused.{u} : Prop
def bad : Prop := unused.{u}  // bad declares no universe parameters
```

Positive control:
[`corpus/controls/nanoda-0003-declared-const-universe.ndjson`](../../corpus/controls/nanoda-0003-declared-const-universe.ndjson),
SHA-256 `94530b9892930781b8f91bb8eb5017e444ef564084ed2b6cfd3ce0eb858faab9`.
The control declares `u` in `bad.levelParams`; both validators accept it.

## Reproduction Commands

From a Lean Assurance Lab checkout with the pinned Arena validators built:

```sh
git clone https://github.com/sankalpsthakur/kiota.git /tmp/kiota
git -C /tmp/kiota checkout 686063c13b22ce379c05dfe7fc03656655ac60e5
cargo build --release --manifest-path /tmp/kiota/Cargo.toml

scripts/reproduce-kiota-universe-ownership \
  --kiota-checkout /tmp/kiota \
  --expected-kiota-revision 686063c13b22ce379c05dfe7fc03656655ac60e5
```

The command exits 0 only when the four normalized outcomes differ exactly as
shown above. The reproduction producer is content-bound in the JSON result.

## Validator Identities

Official reference:

- Lean Kernel Arena revision: `f0fe3b379dbce91537417b529140d0ca250f271c`
- checker: official Lean kernel 4.33.0
- binary SHA-256: `87efe83ae56410a4689b49ff5276dd9663fc85ae3641849d123b5fcef1692585`
- artifact stderr: `uncaught exception: defnInfo invalid`

Kiota current upstream:

- repository: <https://github.com/sankalpsthakur/kiota>
- revision: `686063c13b22ce379c05dfe7fc03656655ac60e5`
- version: `0.1.0`
- clean source SHA-256 for `src/tc.rs`:
  `dad9c3ee2a1ccba9e49acce8795bd374c86516ba1585c628072e0c1a63320dfc`
- locally built release binary SHA-256:
  `9810d9615cbe8e2ed8c8324ef0192dc58fbc38e7e26289e7e9a6aee60ad9fc87`

The earlier pinned Kiota revision
`58e8636cfb51cf9c3bf3de7455a0e3c6ab68e87a` produces the same normalized
outcomes. Its full compatibility and raw-output record remains in
[`results/cross-validation/nanoda-0003-minimized/results.json`](../../results/cross-validation/nanoda-0003-minimized/results.json).

## Suspected Validation Gap

This is a source-level hypothesis, not part of the mechanical predicate.

At current upstream revision `686063c`, `Checker::check_decl` checks that the
declaration's `level_params` list has no duplicates, then infers the declaration
type and value and checks definitional equality. The visible path does not
appear to traverse the declaration type and value to require that every level
parameter occurrence belongs to `ci.level_params()`.

Relevant source:
[`src/tc.rs` at the current revision](https://github.com/sankalpsthakur/kiota/blob/686063c13b22ce379c05dfe7fc03656655ac60e5/src/tc.rs#L1394-L1436).

A likely repair is to reject a declaration when a universe parameter occurring
in its type or value is absent from that declaration's declared level-parameter
set, followed by a regression test containing both files above. The exact
placement and treatment of native declaration kinds should be decided by the
Kiota maintainer.

## Expected Semantics and Scope

Lean Assurance Lab designates the compatible official Lean checker as the
reference for this experiment. The expected outcome is mechanically established
as `REJECT` in
[`results/expected-outcomes/nanoda-0003-minimized.json`](../../results/expected-outcomes/nanoda-0003-minimized.json).
No validator majority vote was used.

This report establishes one concrete acceptance disagreement on two exact
inputs and exact validator revisions. It does not claim:

- a defect in Lean itself;
- that arbitrary false propositions can be proved through Kiota;
- general Kiota unsoundness beyond this malformed declaration class;
- that the minimized artifact fails at exactly the same internal condition as
  the larger witness from which it was reduced.

The requested upstream outcome is narrow: confirm the intended universe
ownership rule, add the minimized artifact and control as regression tests, and
make Kiota reject the malformed artifact if the diagnosis is correct.
