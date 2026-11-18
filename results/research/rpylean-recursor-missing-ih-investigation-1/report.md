# What the retained records establish about the rpylean disagreement

**What did we find?** Provisional. The earlier study reported that rpylean
accepted an Arena test case expected to fail. Both retained checker test caches
name that case. Two archived Arena checkouts contain the exact file selected
for this review, but the earlier run did not record a digest of the file it
opened. The cause of acceptance remains unknown.

**Is it interesting?** Yes. We can identify the file for future comparison and
show that the same test name failed on both checker revisions. The file contains
22 induction principles, called recursors, with 27 computation rules between
them. Official Lean accepted three fresh examples that exercise valid
uses of induction. A blanket restriction on these forms would exclude useful
Lean code.

**Does it require more work?** Yes. The item remains active. The current plan
requires a causal trace through rpylean before it can support a particular
repair. The inventory and valid examples leave that question open. Retain the
existing repair's documented support limits. Establishing precisely which
bytes the historical process read would separately require evidence from that
run.

## How closely can we identify the earlier input?

The prior repair study records 835 passes, one expected failure and one failure
on the patched tree with a sibling Arena checkout. It also reports the same
focused failure on the unmodified checker. The saved test caches in both local
worktrees retain the same test identifier and expected rejection. Those caches
are mutable. Neither they nor the run record bind the file opened by that
process to a digest. The digest at the top of the prior run record belongs to
the repair study's separate input. [Earlier run](../rpylean-recursor-rule-argument-repair-1/validation.json)
· [Cache observations and archive checks](observations.json)

The public file selected in the investigation plan is 296,514 bytes. Its digest
and its companion YAML file agree across two archived Arena revisions and the
source checkout bound at entry. This provides an independently checkable
identity for the present review. [Bound inputs](work-record.json)

## What is in the fixed file?

The 5,526 lines contain 22 inductive groups, each with one type and one
recursor. Together the groups declare 27 constructors and 27 computation rules.
The file also contains 62 definitions, 33 theorems and one opaque declaration.
The recursors have 14 distinct combinations of parameter, index, motive and
branch counts and the K flag. A motive describes the result promised by
induction. The K flag is export metadata for a special form of elimination.
These counts describe the declarations as stored. They establish neither the
validity of any rule nor a cause of acceptance. [Ordered inventory](inventory.json)

From the repository root, the following command reproduces the inventory on
the source-locked input.

```sh
python3 results/research/rpylean-recursor-missing-ih-investigation-1/inventory.py \
  external/lean-kernel-arena/tests/rec-missing-ih.ndjson
```

## Which valid uses should a checker preserve?

| Fresh example | What Lean checked |
| --- | --- |
| A list with labeled stops | A recursive sum computes the expected value for a two-stop list. |
| An indexed equality proposition | A proof that two stops coincide transports a value of a type that depends on the stop. |
| Accessibility along a relation | Induction proves a property of a node from that property at each predecessor. |

The examples derive from the standard library's list, equality and accessibility
declarations. Lean 4.34.1 checked all three in a single file with no diagnostics.
The first draft used a direct recursor call in an executable definition that
Lean's code generator could not compile. The checked version expresses the
same list sum by structural recursion. Only official Lean checked these
examples. [Valid Lean source](ValidControls.lean) · [Both attempts](observations.json)

A defensive criterion for extending checker support is to establish the type
of each induction branch from the inductive declaration and account for the
induction hypotheses that branch is entitled to use. Its conclusion must have
the type promised by the motive at the constructor. The examples illustrate
legitimate inputs for this criterion. Determining whether the reported case
violates a particular obligation, and how rpylean handled it, remains open.
