# Nanoda Constructor Parameter-Binder Search

Mutant: `nanoda-gen-da679d93da63`

The mutation skips equality between an inductive parameter type and the
corresponding constructor parameter binder in `check_ctor` at
`src/inductive.rs:892`.

The valid seed declares `LALWide (alpha : Type 1)`. The source-derived
candidate keeps the inductive parameter unchanged but changes the constructor's
corresponding binder to `Type`. Its result application remains independently
well-typed through universe cumulativity, while `Type` and `Type 1` are not
definitionally equal. This isolates the skipped binder-uniformity check.

## Result

The cumulative-sort probe is rejected by both baseline and mutant Nanoda. A
single-thread mutant backtrace shows the surviving rejection occurs later in
`check_declar_info` while Nanoda independently infers the constructor's full
type.

This exposes a whole-checker invariant:

1. `check_ctor` requires the constructor result to apply the parent inductive
   to the exact substituted `local_params` pointers.
2. Consequently, each constructor parameter bound variable occupies the
   corresponding inductive parameter position in the original constructor
   result type.
3. `check_all_declars` later invokes `check_declar_info` on every serialized
   constructor. Inferring that application requires the bound variable's binder
   type to be definitionally equal to the inductive parameter domain.
4. Therefore any mismatch rejected by line 892 is also rejected by mandatory
   standalone constructor-type inference, even when line 892 is skipped.

The mutant is `EQUIVALENT` at whole-checker scope. The failed probe and matched
control are retained as supporting evidence; baseline source was restored and
rebuilt after the diagnostic instrumentation.
