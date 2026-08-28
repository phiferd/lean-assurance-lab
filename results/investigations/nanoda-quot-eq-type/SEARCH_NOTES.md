# Quotient Eq Prerequisite Search Notes

Target: `nanoda-gen-d39c873fbcb7`, which skips the exact built-in `Eq` type
assertion performed when Nanoda checks `Quot.lift`.

## Direct Probe

The probe starts from tutorial `130_quotLiftType` and changes built-in `Eq` from
proposition-valued to universe-valued by redirecting the final codomain of its
type from expression `3` (`Prop`) to expression `0` (`Sort u`).

Three isolation stages were attempted:

1. Replacing expression `3` itself created a duplicate interned expression and
   was rejected by the parser. The durable candidate instead reuses expression
   `0` and changes only the relevant reference.
2. With the original recursor metadata, both builds rejected and Nanoda also
   reported restored recursor auxiliary-data mismatch.
3. Changing the serialized recursor `k` flag from `true` to `false` removed the
   auxiliary-data failure. Both builds still reject on recursor/declaration type
   equality, so this is not yet a valid witness for the target assertion.

The latest matched result is `reproduction.json`. It must not be classified as
an equivalent mutant or a kill.

## Generated Structural Template

Lean rejects an inductive returning `Sort u` because that universe may collapse
to `Prop`. A valid analogue was therefore generated as:

```lean
universe u
inductive LALAltEq (alpha : Type u) (a : alpha) : alpha -> Type u where
  | refl : LALAltEq alpha a a
```

Its 60-record export is preserved as `alt-eq-template.ndjson` with SHA-256
`2cc53c64bb7d2069022bfc7b6e21e381809587d82c7f44a9626c88c66c44ef9d`.
It contains the correct `k: false`, recursor type, and rule body for a
non-proposition-valued equality analogue.

## Completed Structural Remap

The first `Type u` template was structurally remapped but remained rejected
after the line-89 mutation because its parameter domain and constructor shape
also differed from canonical `Eq`. A second valid analogue preserved those
parts while changing only the result universe:

```lean
universe u
inductive LALAltEq (alpha : Sort u) (a : alpha) : alpha -> Sort (max 1 u) where
  | refl : LALAltEq alpha a a
```

The final remap:

- names the alternate family `Eq` with constructor `Eq.refl`;
- preserves canonical universe-parameter names used by quotient checking;
- imports a separate canonical Prop-valued relation graph for `Quot`;
- remaps the complete canonical quotient suffix without duplicate IDs.

The baseline rejects exactly at `src/quot.rs:89`; the mutant accepts. The
canonical control is accepted by both. Official Lean and Lean4Lean reject the
candidate, while Kiota accepts it, so this is a meaningful mutation kill with
an unresolved checker disagreement.

Next, perform the analogous constructor-shape search for
`nanoda-gen-cd41c71bc814` (`Eq.refl` exact type). Do not infer either
classification from the four reference-aligned quotient primitive fields.
