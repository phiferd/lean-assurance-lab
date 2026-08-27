# Nanoda IMax Equality Survivor

## Mutation

`nanoda-gen-0bb50147dff2` changes the `leq_core` fast path for two `IMax`
levels from `a == x` to `a != x`. The existing corpus exercised the line in 10
tests but did not distinguish the mutant.

## Witness

The source-directed witness compares `Sort (imax u v)` with
`Sort (imax w v)` for distinct universe parameters `u` and `w`. These levels
are not equal for every assignment. Baseline Nanoda rejects the declaration;
the mutant accepts it because both order checks take the inverted-equality fast
path.

The first candidate compared plain parameters and did not distinguish the
mutant, confirming that the mutation applies specifically to the `IMax` fast
path. The second candidate found the distinction.

## Expected Outcome

Official Lean 4.33, Kiota, and Lean4Lean all reject the exact witness and accept
the structure-matched control. The expected outcome is therefore established as
`REJECT` without a checker disagreement or majority vote.

The mutant remains a survivor of the original 197-test corpus and is classified
`MEANINGFUL_SEMANTIC`. The generated witness is a confirmed regression
candidate; historical coverage-guided evidence is not rewritten as an
original-corpus kill.
