# Deterministic `Eq` Remap Analysis

Target: `nanoda-gen-d39c873fbcb7` (the `src/quot.rs:89` prerequisite
assertion). This note records structural evidence only.

## Inputs inspected

- `SEARCH_NOTES.md`
- `alt-eq-template.ndjson`
- `external/lean-kernel-arena/_build/tests/tutorial/good/130_quotLiftType.ndjson`
- `external/lean-kernel-arena/_build/checkers/nanoda/src/src/quot.rs`
- `results/investigations/nanoda-quot-eq-type/reproduction.json`

The alternate template is a valid `Type`-valued inductive:

```text
LALAltEq (alpha : Type u) (a : alpha) : alpha -> Type u
```

Its recursor has `k: false`. The canonical tutorial export instead defines
proposition-valued `Eq`, has `k: true`, and then appends the canonical `Quot`
primitive declarations. Nanoda's `check_eq` explicitly expects one universe
parameter, two parameters, one constructor named `Eq.refl`, and a type ending
in `Prop`; therefore a `Type`-valued `Eq` can only be used to test the
precondition's isolation if the ordinary inductive/constructor/recursor checks
are independently made consistent first.

## Deterministic remap procedure

An implementation should treat the exports as an expression graph, not as
text. The procedure is:

1. Parse every NDJSON record and index each `ie` expression and declaration
   reference by its original integer ID.
2. Select the alternate inductive declaration, constructor, and recursor as
   the authoritative `Eq` graph. Rename only the interned declaration and
   constructor strings: `LALAltEq` -> `Eq` and `LALAltEq.refl` -> `Eq.refl`.
3. Allocate fresh expression IDs for the alternate graph in dependency order.
   Recursively rewrite every `bvar`, `const`, `app`, `forallE`, `lam`, and
   `sort` edge through the fresh-ID map. Preserve level-parameter references,
   binder order, constructor indices, recursor `k`, `numIndices`, and rule
   bodies exactly. Do not map IDs by position or perform global string
   replacement.
4. Parse the canonical quotient suffix and recursively rewrite its references
   to canonical `Eq` and `Eq.refl` expression IDs through explicit semantic
   anchors: the `Eq` constant, the `Eq.refl` constant, and the equality
   application in the `Quot.lift` proof argument. All other quotient nodes
   should retain their canonical structure and level parameters.
5. Emit declarations in dependency order: remapped `Eq` family/constructor/
   recursor first, then canonical `Quot`, `Quot.mk`, `Quot.lift`, and
   `Quot.ind`. Validate that every edge points to an emitted ID and that the
   resulting declaration names are unique.
6. Run the ordinary Nanoda declaration checks on this candidate before
   comparing the target mutant. A candidate that fails those checks is an
   invalid prerequisite probe, not evidence about line 89.

The crucial semantic anchor is the equality proof type in the `Quot.lift`
declaration. It must refer to the remapped `Eq` constant at the same universe
and argument positions; changing only the string `Eq` leaves stale expression
IDs and is insufficient.

## Current exact outcomes

- Existing direct probe: baseline `REJECT`, mutant `REJECT`; both panic at
  `src/tc.rs:921` while comparing declaration types. `different: false`.
- Existing alternate template alone: structurally valid `Type`-valued Eq
  analogue, but it contains no quotient primitives.
- No valid merged `Eq`+`Quot` candidate was present in the repository.
- No baseline/mutant differential was run from this analysis because a
  graph-consistent merged candidate was not available. No Passed/Failed
  classification is claimed.

## Conclusion

The next useful implementation is a small ID-aware NDJSON graph rewriter
following the procedure above, with structural checks before invoking Nanoda.
Renaming the alternate template and appending the canonical quotient records
without reference rewriting would reproduce the known invalid probe and should
not be used.
