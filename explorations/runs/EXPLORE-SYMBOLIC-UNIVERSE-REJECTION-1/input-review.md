The six concrete files match the selected question: three unchanged valid
controls and three invalid declarations, each differing from its control in
exactly one JSON row. Source inspection predicts acceptance of the controls
and rejection of all three invalid candidates. No checker was run during this
review, so these are prospective expectations, not observed outcomes.

Yes, this is useful as a small rejection-boundary screen: it tests behavior
absent from the earlier positive-only sample. It does not measure a general
fault-detection rate or establish soundness. No flaw in the prescribed semantic
expectations was found.

The owner should execute only the fixed six files on the two bound profiles
and classify the retained diagnostics using the distinctions below. No
additional scientific case or checker modification follows from this review.

Reviewed 2026-10-20 against `AGENTS.md`, `CONSTITUTION.md`, the current Active
frontier, and `docs/research/E0_SYMBOLIC_UNIVERSE_REJECTION_1_PLAN.md`.
The retained Nanoda `parser.rs`, `tc.rs`, `level.rs`, `env.rs`, and `main.rs`
are byte-identical to the cached checkout at revision
`3a2407216ee84a75f9e1aead6803d0578be06ae7`; that checkout had no reported changes.
Lean references below are the retained sources in
`../EXPLORE-SYMBOLIC-UNIVERSE-1/sources/`, bound there to revision
`5045d0056413266e57c625dcd7c365b10e377c52`.

| Pair | Independently inspected change | Source-derived rejection argument |
| --- | --- | --- |
| P1 | `P1-invalid.ndjson:8` changes only `levelParams: [2]` to `[]`; the parameter node and both expressions remain intact. | A used universe parameter must occur in the declaration's list. Lean `type_checker.cpp:85–89` rejects an undefined parameter; `:345–347` applies the check to a sort, and `:364–366` supplies the declared parameter list. Nanoda `tc.rs:199–204` checks the declared type, `:552–557` checks its level, and `level.rs:139–145` makes membership in the empty list false. |
| M1 | `M1-invalid.ndjson:13` changes only the definition's type reference from expression 0 to expression 1, so both type and value are `Sort(max u v)`. | The value infers `Sort(succ(max u v))`, by Lean `type_checker.cpp:345–347` and Nanoda `tc.rs:552–557`. The ascribed and inferred levels differ: at `u=v=0`, they are 0 and 1. Lean compares sorts by level equivalence (`type_checker.cpp:814–819,843–844`; `level.cpp:518–520`); Nanoda compares levels in both directions (`tc.rs:1170–1185`; `level.rs:229–235`) and asserts the final type equality (`tc.rs:88–93,955`). The unused original higher-level type node remains in the file and does not alter the declaration's new reference. |
| I1 | `I1-invalid.ndjson:6` changes only the level constructor from `imax` to `max`, retaining operands `[2,1]`. | The value `forall X : Sort u, X` infers `Sort(imax(succ u,u))`: Lean `type_checker.cpp:144–165`; Nanoda `tc.rs:655–673`. At `u=0`, this level is 0, while the ascribed `max(succ u,u)` is 1. Lean `level.cpp:112–122` and Nanoda `level.rs:67–77` preserve this zero distinction. Hence the symbolic levels cannot be equal. Nanoda's comparison includes a zero/nonzero parameter split (`level.rs:158–172,188–191`), but no executed branch-coverage claim is made. |

Read-only byte comparisons established exact control identity with the earlier
P1, M1, and I1 files, equal row counts in every pair, and exactly the row
differences shown above. SHA-256 values matched the new `cases.json`:

| Invalid input | SHA-256 |
| --- | --- |
| P1-invalid | `a40f442b7bb174d8f96e3f836fbd20a5c845766af4aac91863c73839bdc0b3ff` |
| M1-invalid | `2be119819fe648e4e5582b7ec7a41cfa5a309b3b9640b3b45017ddbed41ea474` |
| I1-invalid | `1757a2887c12a23d999e7545463260ed60978b80341e55ec252be18599ff1f28` |

Parameter omission should survive both parsers. Lean `Parse.lean:251,259,278`
copies the provided empty array into the definition's parameter list, while
`:118–120` constructs the separate `Level.param u`. Nanoda
`parser.rs:500–509` builds an empty parameter slice without adding parameters,
`:637–643` retains the independent parameter node, and `:783–791` stores
the declaration with that slice. Omitting a parameter from the list is not
omitting the required JSON field. Raw `max` and `imax` constructors are preserved
by Lean `Parse.lean:104–120` and Nanoda `parser.rs:611–643`.
The structural auditor likewise represents the parameter node and declaration
list independently (`lib/metamorphic_ndjson_audit.py:144,201–204`); it does not
silently repair the omitted parameter.

Lean's importer prints the parsed parameter list, type and value before replay
(`Replay.lean:23–32`). Require those exact printed structures, including the
empty `PARAMS ` line for P1-invalid. Nanoda checks before pretty-printing
(`sources/main.rs:26–30`), so missing pretty-printed output on an invalid case
does not establish a parse failure. Nanoda preservation here is established by
the retained parser source and bound input identity, not a runtime AST dump.

Nanoda deliberately uses Rust assertions as rejection mechanisms. An observed
P1 panic at `tc.rs:554` with `all_uparams_defined`, or an M1/I1 panic at
`tc.rs:955` with `self.def_eq(u, v)`, is a source-attributed semantic rejection
if the bound input/profile and diagnostic match. Preserve its panic transport
in the evidence; do not report an unrelated diagnostic crash merely because
Rust labels it a panic. Other panics, parser errors, unsupported constructs,
timeouts and unexplained exits require their own classification. A Lean
exception-formatting or diagnostic failure, if observed, must also remain
distinct from clean rejection; the retained files establish the semantic
expectation but do not establish every exception-rendering path. Neither a
nonzero exit alone nor absence of the success message is sufficient.

Review scope ended after source inspection, read-only file comparisons and this
review file. No checker execution, source edit, queue edit, new experiment or
external action was performed by the reviewer.
