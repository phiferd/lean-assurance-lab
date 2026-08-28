# Nanoda Let Value-Type Witness Transfer

Mutant: `nanoda-gen-e551a17020ce`

The mutation skips `assert_def_eq(val_ty, binder_type)` while checking a let
expression in `infer_let` at `src/tc.rs:654`.

The existing Milestone 7 malformed-let artifact was generated for an analogous
Kiota mutation and evaluated against a held-out Lean4Lean mutation. Applying it
to Nanoda gives the same result:

- baseline Nanoda: `REJECT`;
- mutant Nanoda: `ACCEPT`;
- matched valid control: `ACCEPT` in both builds.

In test terms, the malformed-let test passes without the mutation and fails
with it. This is a meaningful semantic kill, not a timeout or crash-only
difference.

Official Lean establishes the exact artifact's expected outcome as `REJECT`.
Fresh standard cross-validation confirms that official Lean, Kiota, and
Lean4Lean all reject it. The artifact is therefore a regression candidate with
no unresolved checker disagreement.

Evidence:

- `transfer-reproduction.json`
- `control-reproduction.json`
- `results/expected-outcomes/m7-let-value-type.json`
- `results/cross-validation/nanoda-gen-e551a17020ce-let-value-type/results.json`

The checker source was restored and rebuilt after each differential run.
