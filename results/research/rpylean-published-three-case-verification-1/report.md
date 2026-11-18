# Verification of Julian’s published rpylean change

**What did we find?** The published checker rejected both disputed Arena files
and accepted the valid proof-parameter example. All three outcomes matched the
predictions committed before execution. This run covered the untranslated
checker at Julian’s cited commit. The earlier checker’s reason for accepting
the files remains unverified.

**Is it interesting?** Yes. For the missing-induction-hypothesis case, the
checker reported an invalid recursive use in a constructor field. For PR #36’s
case, it reported that the declared computation rule differed from the one
derived from its type. The valid file passed all three of its declarations.
These are direct observations for the two reported gaps and the control.

**Does it require more work?** The behavior question is closed for these three
files. No further checker patch, PR resubmission, or investigation of the old
source is warranted by this result. The separate next maintenance question is
whether Arena can use a released checker that includes the repair.

## Case-by-case evidence

| Arena file | Expected | Observed | Evidence |
| --- | --- | --- | --- |
| `bugs/rec-missing-ih` | Reject | Exit 1. Invalid recursive occurrence in a constructor field. | [Checker diagnostic](attempt-2/rec-missing-ih/stderr.txt) |
| `bugs/rec-rule-wrong-arg` | Reject | Exit 1. Computation rule differs from the rule derived from the inductive declaration. | [Checker diagnostic](attempt-2/rec-rule-wrong-arg/stderr.txt) |
| `corner-cases/proof-param-ok` | Accept | Exit 0. All 3 declarations checked. | [Checker summary](attempt-2/proof-param-ok/stderr.txt) |

The rejection summaries counted 151 and 21 declarations seen, respectively,
when the checker stopped at its first error. The field diagnostic is consistent
with Julian’s explanation about strict positivity, the restriction on where a
type being defined may occur inside its constructor fields. It establishes
which error the published checker reported. The experiment did not test the
historical source, the translated binary, or another release.
[Per-case results and digests](result.json) · [Earlier source review](../rpylean-recursor-missing-ih-investigation-1/upstream-review.md)

## Execution record

Commit `f5ac2a82` fixed the files, expectations, checker source archive
and runtime before launch. The PR example uses the exact export retained by
the original repair study. The other two exports came directly from pinned
Arena Git blobs. Each process received one hash-verified file via the standard
checker command. Its output and exit code were saved separately and the file
digest verified again afterward. [Preregistration](inputs.json)

The first three processes failed during import because their environment
omitted the `py` package. They produced zero checker verdicts. Commit
`c5542ae1` added the package from the same dependency revision, a startup check,
and a guard against counting an empty checker summary. The second launch
produced three semantic verdicts. Host warnings about CPU-cache information
also appeared in the successful control. [Tooling change](tooling-v2.json)
· [Raw launches](result.json)
