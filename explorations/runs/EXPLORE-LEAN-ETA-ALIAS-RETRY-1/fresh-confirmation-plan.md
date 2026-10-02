# Smallest fresh confirmation plan

Status: planned only; no confirmation execution is authorized by this file.

## Question

Does a fresh process using the already-retained exact PR15373 toolchain reproduce the same four-case matrix after directly recording operand well-formedness, revision and in-container identities?

## Fixed input

Use the existing repaired fixture without changing its four expressions, assertions, order or expectations. Add only observation code that records:

1. the toolchain revision reported by the retained binary;
2. SHA-256 of the in-container fixture, `/toolchain/bin/lean`, and `/toolchain/lib/lean/libleanshared.so`;
3. `Kernel.check env lctx f` and `Kernel.check env lctx Box.mk` for each negative local context, retaining either the returned inferred type or exact exception; and
4. the same four Meta/kernel Boolean observations.

The `Kernel.check` observations must precede the corresponding conversion calls and must not normalize or replace the operands used by `Kernel.isDefEq`. For the alias negative, require the checked local type to remain the stored `FnAlias` constant and the constructor type to be the ordinary `Bool → Box` Pi expression.

## Execution bound

- One fresh process on the already-retained pinned toolchain.
- The same four comparisons only.
- No new image, download, source build, alias variant, wrapper family or publication.
- Stop before scientific interpretation if any revision, fixture or binary identity differs from the retained bindings, if either operand check errors, or if raw-shape assertions fail.

## Interpretation

If identities and operand checks pass and the matrix repeats, classify it as an independently reproduced pinned-artifact API disagreement. This still does not establish declaration acceptance or PR causation.

Compare the unchanged fixture with exact parent revision `2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` only if an identity-verifiable ready binary is already available without download or build expansion. No such binary is currently present. Absence of that comparison does not invalidate the pinned-artifact observation; it only blocks the stronger “introduced by PR15373” claim.

A declaration-level `Kernel.check` witness that relies on the disputed conversion would be a separate subsequent confirmation question. Do not fold it into this smallest reproduction unless operand validation reveals that the direct API result cannot otherwise be interpreted.
