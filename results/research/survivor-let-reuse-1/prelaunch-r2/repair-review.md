# Prelaunch attribution adapter revision 2

No build or checker reservation exists. Revision 1 is preserved at commit
b0ada5b and in config/survivor-let-reuse-0001.json. The symbol-only preflight
(prelaunch/baseline-symbols.log) shows that the release binary has retained
TypeChecker::infer and TypeChecker::check_declar_info symbols, while infer_let
and the one-line assert_def_eq are inlined. Requiring their literal frame names
would make a valid refusal unclassifiable for an output-format reason.

Revision 2 requires the exact src/tc.rs:921:71 assertion text, code 101, empty
stdout, retained infer and check_declar_info frames, and a clean complete
supervisor receipt for the exact baseline candidate. The caller path through
inlined infer_let is a source/input attribution, not an observed literal frame.
The fixed value is Sort 1 (type Sort 2), the let annotation is Sort 1, and the
substituted body has type Sort 2 matching the outer declaration. Thus the
baseline encounters the value/annotation mismatch inside infer_let before the
outer type comparison. The exact control validates the same route with Sort 0.
Generic panic, a wrong site, missing retained frames, nonempty stdout, parser
error, timeout, or unsafe process receipt does not count as this refusal.

No science input, configuration, selected binary, build recipe, budget or old
attempt changes. This is a prospective tooling revision before the first
launch, not a scientific negative or a new research item. Focused tests and
committed revision-2 tooling remain required before executing its manifest.
