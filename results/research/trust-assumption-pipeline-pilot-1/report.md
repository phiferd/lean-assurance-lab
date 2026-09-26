# Trust-assumption pipeline pilot 1

Outcome: **SUCCESS** for the six frozen fixtures and two reporting routes in official Lean 4.33.0.

| Fixture | Local body traversal | Imported .olean metadata |
| --- | --- | --- |
| pure | ∅ | ∅ |
| explicitLeaf | `TrustAssumptionPilot.explicit` | `TrustAssumptionPilot.explicit` |
| propextLeaf | `propext` | `propext` |
| choiceLeaf | `Classical.choice` | `Classical.choice` |
| sorryLeaf | `sorryAx` | `sorryAx` |
| nativeLeaf | `_private.TrustFixtures.0.TrustAssumptionPilot.nativeEval._native.native_decide.ax_1` | `_private.TrustFixtures.0.TrustAssumptionPilot.nativeEval._native.native_decide.ax_1` |

All twelve canonical assumption sets match the source-derived expectations. The two paths share one Lean implementation: local collection traverses checked declaration bodies, while import reads the serialized `exportedAxiomsExt` entries. This is preservation evidence for these exact inputs, not independent-checker agreement or a soundness result. The compiled export is `.olean` metadata, not lean4export NDJSON.

The explicit assumption remains visible through `explicitMid` and `explicitLeaf`. On each route, the local report consumer permits the leaf with `{TrustAssumptionPilot.explicit}` and denies it with the empty set, naming exactly that unpermitted axiom. These four decisions test report policy; they are not kernel or Comparator rejection observations.

Native evaluation in this toolchain creates a declaration-specific private axiom. The report retains its full internal name; the deprecated `Lean.ofReduceBool` mechanism is not the fixture mechanism. Successful compilation does not remove native-evaluation or `sorryAx` assumptions.

The first local attempt is preserved under R1 with five matching reports and one native-name rendering mismatch. Its printing options were scoped inside the namespace and reverted before the reports. R2 sets both printing options globally through the command line, keeps the scientific fixtures and expected sets byte-identical, and reruns the local route in a fresh attempt. The exact R1 raw output is still replayed by its original tooling; no alias mapping or historical relabeling is used.

The R2 producer observation and all five generated `.olean`/IR files were committed before the imported route launched. All three process attempts recorded positive RSS, stayed within their controls and completed cleanup. The final twelve cells exclude the preserved R1 preparation incident.

Recommendation: retain the strict report parser, six fixtures, permission comparison and receipts as a local regression asset for Lean assumption-reporting consumers. Priority: normal. Before applying the result to another toolchain or module, bind that exact source/runtime and reviewed expected sets in a successor. No external issue or checker patch is recommended from this all-preserved matrix.

Canonical evidence: [result-r2.json](result-r2.json), [scientific manifest](scientific-manifest.json), [R2 protocol](protocol-r2.json), [R1 repair/replay](repair-r2.json), and [closure validation](validation.json).
