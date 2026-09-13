# Draft: acceptance guarantees for derived declaration metadata

Local review draft; not submitted. Intended target: a grouped documentation
clarification for `leanprover/lean4export/format_ndjson.md`, coordinated with the
existing [#48 import-acceptance discussion](https://github.com/leanprover/lean4export/issues/48).
Review the current conversation before deciding whether this belongs as an
appendix there or as a separate documentation change. This draft authorizes neither.

The 3.1.0 format includes both inductive inputs and generated information, and
[describes some metadata as redundant](https://github.com/leanprover/lean4export/blob/411dce7db58a3afc60ecab2d211acd1042b593dc/format_ndjson.md#L24-L28).
It also [distinguishes the kernel's inductive input from derived recursors and fields](https://github.com/leanprover/lean4export/blob/411dce7db58a3afc60ecab2d211acd1042b593dc/format_ndjson.md#L282-L284).
Could the documentation state, per field or importer profile, what acceptance
promises about that information?

The distinction matters even within the reference importer. In the retained
[Lean v4.34.0-rc2 replay source](https://github.com/leanprover/lean4/blob/v4.34.0-rc2/src/Lean/Replay.lean#L102-L120),
the safe, nonpartial declaration replay path rebuilds inductive declarations
from their core inputs. Supplied constructors
and recursors are subsequently [compared with generated records](https://github.com/leanprover/lean4/blob/v4.34.0-rc2/src/Lean/Replay.lean#L144-L164),
while supplied inductive `numIndices` is not part of that core input or a later
inductive-record comparison. That is a source observation, not a new execution.

For example, should a profile document these choices explicitly?

| Field | Question to document |
| --- | --- |
| Recursor `k` | Is the serialized flag a consistency assertion, or may reduction use an independently derived condition? |
| Recursor `type` | Must the supplied type match a derived type; if so, under which comparison? If it is retained for constant typing, what validation is promised? |
| Constructor `cidx` | Is consistency with constructor order sufficient, or must the full constructor record match a reconstructed declaration? |
| Inductive `numIndices` | Is the supplied count validated and retained, or replaced by the count derived from the type? |

A useful clarification would identify (1) fields used as inputs, (2) fields
reconstructed or ignored for semantic operations, (3) the relation checked before
retaining other supplied fields, and (4) whether acceptance attests to the supplied
serialization, a reconstructed environment, or a stated profile of both.
This would avoid treating every accepted metadata mismatch as a defect, or
assuming that metadata described as redundant is harmless when still consumed.

Current [Kiota documents recomputation of `k`](https://github.com/sankalpsthakur/kiota/blob/9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/README.md)
and [checks constructor index membership](https://github.com/sankalpsthakur/kiota/blob/9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/parser.rs#L432-L482).
Its recursor-type checks and retained type lookup follow a different path from
Lean replay. Those choices make a profile description useful; we are not asking
all checkers to implement the reference importer identically.

The accompanying [field assessment](field-assessment.json) and
[historical evidence](historical-observations.json) preserve four unchanged
candidate/control pairs and their exact versioned observations. Each pair changes
one scalar, without editing expression nodes. Three older Kiota accepts cannot
be projected to the present source; in the fourth case its control failed and
its candidate was not run. No current checker run or soundness defect is claimed.
The related proof-parameter example is not used as an isolated constructor-only
witness because its edited expression nodes also reach recursor annotations.

Is there an existing documented acceptance relation covering these choices, or
would a short profile-oriented section in the format documentation be useful?
