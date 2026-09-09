# Declaration free-variable reachability result

`SURVIVOR-FVAR-REACHABILITY-1` closed `SUCCESS` with a scoped
`EQUIVALENT` classification for `nanoda-gen-399895fa0b72`.

Pinned Nanoda represents free variables as `Expr::Local`. Its exported JSON
grammar has no Local/free-variable form: it reconstructs bound variables as
`Expr::Var`, and every compound expression's `has_fvars` bit is only the
disjunction of already reconstructed children. Insertion-order induction
therefore gives `has_fvars = false` for the complete persistent parser DAG.
Every exported declaration type directly references that DAG.

All current `check_declar_info` callers pass original parsed declarations.
Inductive checking invokes it before creating checker-local expressions, and
Quot uses a separate path. The removed assertion is consequently outcome-
equivalent for declarations produced by `Config::to_export_file` and checked
through `check_all_declars`/`check_declar` at revision `6ae1f0c`.

This is not universal redundancy. A crate-internal caller can construct an
`Expr::Local`, put it in a synthetic declaration type and reach the assertion;
the original rejects it while the mutant can continue when the Local's binder
type is a Sort. The guard should remain defense in depth, and input non-
representability must not be described as semantic enforcement.

The historical 184-test match is supporting observation only. No build,
checker, proof, network request, scientific export byte, mutation identity or
external action ran. The canonical registry receives one append-only scoped
`EQUIVALENT` row.

The next selected item is `SURVIVOR-THREAD-CONFIG-REACHABILITY-1`, READY and
unstarted, for a source-only assessment of the two remaining declaration-
dispatch predicate survivors.
