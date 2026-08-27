# Nanoda Environment Cutoff Survivor

## Investigation State

Status: `COMPLETE`

Mutant `nanoda-gen-8317efea2c7d` changes `Env::get_old_declar` from
`idx < self.cutoff` to `idx <= self.cutoff`. The existing 197-test corpus ran
all 162 tests covering this line without distinguishing the mutant.

## Hypothesis

`EnvLimit::ByIndex` is intended to hide the declaration currently being
checked and every declaration after it. The mutated inclusive comparison may
make the declaration at the cutoff visible. A declaration that refers to the
next visible entry could therefore be rejected by baseline Nanoda but accepted
by the mutant.

## Attempts

### Forward reference through an inductive type

Artifact:
`corpus/generated/nanoda-gen-8317efea2c7d-forward-inductive-type.ndjson`

Result:
`results/investigations/nanoda-env-cutoff-forward-reference/reproduction.json`

The candidate places an inductive declaration before a definition named
`futureType`, and the inductive type refers to `futureType`.

- Baseline Nanoda rejects while resolving `futureType`, as expected.
- The mutant gets past that lookup, showing that the inclusive cutoff changes
  declaration visibility.
- The mutant later panics because the handcrafted empty inductive declaration
  does not populate the parser's required inductive-to-recursor-name map.

Both executions therefore normalize to `REJECT`. This is evidence for the
visibility mechanism, but it is not a distinguishing witness.

Earlier revisions of the same candidate also exposed and corrected
non-contiguous name identifiers and definition-opacity constraints. Those were
input-construction errors, not mutation distinctions.

## Next Action

Source tracing established a simpler path. Ordinary definitions are checked
with `EnvLimit::ByName(current_definition)`, which sets the cutoff to the
current definition's index. Baseline therefore hides the definition from its
own body, while the mutant's inclusive comparison exposes it.

The next candidate is a definition equivalent to
`def cutoffSelf : Sort 1 := cutoffSelf`. Its declared type is independently
well-formed. When checking the body, baseline should fail to resolve
`cutoffSelf`; the mutant may infer the body's type from the now-visible
declaration information and accept without unfolding the recursive body. A
matched positive control replaces the body with `Sort 0`.

Candidate artifacts:

- `corpus/generated/nanoda-gen-8317efea2c7d-self-reference.ndjson`
- `corpus/generated/nanoda-gen-8317efea2c7d-self-reference-control.ndjson`

### Direct reproduction result

Result:
`results/investigations/nanoda-env-cutoff-self-reference/reproduction.json`

In plain terms, the candidate claims that `cutoffSelf` has type `Sort 1`, but
uses `cutoffSelf` itself as the definition's value. This is a circular ordinary
definition, not a valid recursive definition constructed through Lean's
recursion machinery. A checker must not use the declaration currently being
validated as evidence that its own body is well-typed.

The two checker builds respond differently:

- Baseline Nanoda, containing the original `<` boundary: `REJECT` (exit 101).
  It correctly hides `cutoffSelf` while checking that definition's body.
- Mutant Nanoda, containing the deliberately faulty `<=` boundary: `ACCEPT`
  (exit 0). It can see `cutoffSelf`, reads the declaration's claimed type, and
  incorrectly treats the self-referential body as well-typed.

The matched control replaces the circular body with `Sort 0`, which genuinely
has type `Sort 1`. Both checker builds accept that control. This confirms that
the difference concerns self-reference rather than a generally malformed file.
Its result is recorded at
`results/investigations/nanoda-env-cutoff-self-reference/control-reproduction.json`.

In mutation-testing terminology, this is a **mutation kill**: the test input
distinguishes the original implementation from the deliberately faulty one.
It does not mean a process or project was destroyed.

The runner temporarily edited and rebuilt Nanoda to create the mutant binary,
then restored and rebuilt the original source. That restoration is test hygiene
which ensures later commands do not accidentally use the mutant; it is not part
of the semantic result.

At this point in the chronology, independent validation was still pending. The
next section records the completed validation: official Lean and Lean4Lean
reject the candidate, while Kiota accepts it.

### Cross-validation checkpoint

Expected-outcome evidence:
`results/expected-outcomes/nanoda-gen-8317efea2c7d-self-reference.json`

Cross-validation result:
`results/cross-validation/nanoda-gen-8317efea2c7d-self-reference/results.json`

The designated official Lean 4.33 checker rejects the witness and accepts the
control. Lean4Lean independently does the same. Kiota accepts both witness and
control. The aggregate classification is therefore `CHECKER_DISAGREEMENT`, and
the semantic status remains `UNRESOLVED` under project policy; no majority vote
is used.

This does not erase the Nanoda mutation kill. It introduces a second question:
whether Kiota independently exposes a declaration before validating its body.
The next action is to trace Kiota's declaration insertion/checking order and
reproduce its result directly before any regression promotion or registry
reclassification.

### Kiota source trace and upstream-main reproduction

Machine result:
`results/investigations/kiota-self-reference/upstream-main.json`

Kiota's parser inserts a definition into `Environment` in
`handle_def_like` before `handle_line` calls `check_last`. `check_decl` then
retrieves the already-inserted definition and uses that same environment to
infer its value. This permits the value to resolve its own declaration.

The four-outcome predicate was reproduced on the locally fetched Kiota
upstream `main` revision `686063c13b22ce379c05dfe7fc03656655ac60e5`:

- Official Lean: witness `REJECT`, control `ACCEPT`.
- Kiota upstream main: witness `ACCEPT`, control `ACCEPT`.

The dedicated producer is `scripts/reproduce-kiota-self-reference`. It verifies
the exact Kiota revision and clean checkout, binds source and binary hashes, and
validates its result against the validator-investigation schema.

## Current Conclusion

The Nanoda mutant is meaningfully distinguishable: it accepts a declaration
self-reference rejected by baseline Nanoda and the designated official Lean
reference. Lean4Lean agrees with the reference. Kiota's acceptance is preserved
as an exceptional semantic disagreement and is not majority-voted away.

The witness is eligible for the generated regression inventory because its
expected `REJECT` outcome is established by the designated reference, but its
cross-validation status must remain visibly unresolved until the Kiota
disagreement is repaired or otherwise resolved.

An upstream Kiota report is warranted, but filing it is a separate external
write action. The repository evidence is complete without treating maintainer
adjudication as part of this investigation's result.

Any successful distinction must then be checked with official Lean, Kiota, and
Lean4Lean before it is classified or added to the regression corpus.
