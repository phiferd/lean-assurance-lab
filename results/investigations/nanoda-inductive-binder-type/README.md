# Nanoda Inductive Binder-Type Equivalence

Mutant: `nanoda-gen-96211e002bfd`

The mutation skips `self.assert_def_eq(binder_type, t2)` in
`check_inductive_spec_0th` at `src/inductive.rs:459`.

The comparison is redundant by construction:

1. `collect_unmodified_mutuals` copies the first exported inductive's exact
   `info.ty` pointer into `unmodified_tys_ctors[0].ty`.
2. `specialize_nested` calls `get_local_params` on that type. Each local's
   `binder_type` is the corresponding telescope binder type.
3. The same unmodified vector is stored in
   `st.all_inductives_incl_specialized`; nested specialization rewrites
   constructors but not inductive type headers.
4. `check_inductive_spec_0th` traverses
   `st.all_inductives_incl_specialized[0].ty` in the same order. At each
   parameter position, `binder_type` and the local's `t2` therefore come from
   the same binder. Weak-head normalization and identical prior substitutions
   preserve definitional equality.

The skipped assertion cannot distinguish any input that reaches this path. The
mutant is classified `EQUIVALENT`; a witness search is not applicable.
