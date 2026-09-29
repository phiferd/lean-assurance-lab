# LazyLean delta/iota source review

Evidence class: E0. This review supports fixture construction; it is not a
semantic authority or confirmation result.

The retained loader accepts dense name, level and expression lines, transparent
`def` declarations, and complete `inductive` blocks containing types,
constructors, recursors and rules. `check_and_add` checks ordinary definition
values against their declared types and reconstructs inductive declarations
before installing them.

For delta, `ConstInfo::is_delta` admits definitions and theorems.
`TypeChecker::unfold_definition` checks the head and universe arity, increments
the substitution-engine unfold counter and exposes the value.
`TypeChecker::lazy_delta_reduction_step` invokes that path during definitional
equality. The KAM machine has a separate delta transition, reported by the
existing `machine: ... delta ...` line parsed by
`lib/lazy_reduction_pilot.py`.

For iota, `TypeChecker::inductive_reduce_rec` recognizes a fully applied
recursor, locates its major premise, weak-head reduces the major to a
constructor, selects the matching rule and applies the rule right-hand side.
The substitution path increments its iota counter when this succeeds. The KAM
machine has a recursor frame and reports its own iota transition in the same
machine line. `LL_KAM_MODE=3` routes both ordinary and cheap weak-head reduction
through the machine for the KAM profile.

The retained adapter requires exactly one loader summary, one successful
checker summary and one complete machine counter line for acceptance. The
existing supervisor supplies a fresh process group, timeout, 2 GiB limit,
positive sampled RSS and cleanup verification for every cell.

The planned delta candidate declares `D : Sort 2 := Sort 1 -> Sort 1`, then
`f : D := fun A : Sort 1 => Sort 0`. Candidate conversion requires unfolding
`D`; the matched control gives `f` the literal function type. Both add
`w : Sort 1 := f Sort 0`, which makes the KAM profile weak-head reduce `D` while
inferring the application and therefore provides an observable machine delta
transition. The planned iota candidate uses the standard one-constructor `True`
block shape retained from a Lean 4.29.1 export and declares a definition at
`True.rec (fun _ => Sort 0) True True.intro`; its value is `True.intro`, whose
inferred type is `True`. The matched control changes only that declared type to
direct `True`. Thus candidate conversion demands the named reduction while the
control establishes loader/declaration acceptance without it. The substitution
summary's combined iota/projection/quotient count does not count this recursor
path, so only the KAM machine iota counter is a demand gate.
