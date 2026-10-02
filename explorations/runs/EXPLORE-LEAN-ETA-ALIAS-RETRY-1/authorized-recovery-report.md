# Authorized recovery: Lean PR15373 preserved-alias eta pilot

The exact repaired four-case fixture completed once with the official PR15373 runner. Three cells matched the independently frozen oracle. The preserved-alias arbitrary-function negative did not:

| Case | Expected | Meta | Kernel |
| --- | ---: | ---: | ---: |
| explicit negative | false | false | false |
| alias negative | false | false | **true** |
| explicit constructor control | true | true | true |
| alias-context constructor control | true | true | true |

This is a bounded E0 `SIGNAL`. In the exact raw fixture, `Kernel.isDefEq` accepted an arbitrary unvalued `f` against unapplied `Box.mk` when the stored local type remained exactly `.const ``FnAlias []`; `Meta.isDefEq` rejected the same comparison. The explicit-type negative excludes unconditional arbitrary-function acceptance, and both positive controls show the constructor eta path remained operational.

The compatibility repair does not alter the scientific expressions or oracle. It replaces unsupported rendering of `Kernel.Exception` with a literal error marker and renames the reserved local identifier `meta` (plus its paired `kernel` name for clarity). All raw-shape assertions, the unvalued declaration checks, zero-argument constructor check, kernel-before-Meta order, case labels and run order remain unchanged.

The one replay exited 0 in 5.722 seconds with no monitor error. A terminal inspection recorded an exited, non-OOM state with code 0. The exact task-created container was then removed, and a lookup by its full ID returned `No such object`.

## Interpretation boundary

This is evidence about the exposed `Kernel.isDefEq` behavior of the exact PR15373 build on one preserved reducible-alias fixture. It is not C++ kernel verification, whole-validator acceptance, an exploitability result, a claim about current Lean main, a general theorem about aliases, or publication authorization. The append-only earlier INCONCLUSIVE finish remains the truthful record of the point where sandbox access was unavailable; this recovery is a separately retained post-closure observation after the permitted approval mechanism was clarified.
