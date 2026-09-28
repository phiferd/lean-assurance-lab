# Binder model pilot: result

## What did we find?

Two implementations of moving and replacing variables inside expression
trees matched a separately written model on all 10,000 selected records.
Each returned 15,000 checked outputs, including intermediate results of
two-step operations. No difference appeared in 30,000 output comparisons.
The 10,000 rows contain **5,091 distinct structural operation inputs** after
ignoring IDs and names. Their variables were validly placed within declared
contexts. The pilot did not check whether these trees form valid typed Lean
programs or proofs, nor did it test other APIs or terms.

## Is it interesting?

**Yes, as a local regression asset.** The corpus includes 2,000 cases designed
to catch a replacement variable being wrongly bound by a surrounding
variable binder, alongside variable moves at zero, interior and end cutoffs
and nested lambda/let cases. A separate auditor
checked the named-to-index translation and every expected operation result.
An independent replay then checked every raw implementation output and all
40 process receipts. This run found no implementation problem. Agreement on
these finite records does not prove either implementation or the model
correct.

## Does it require more work?

Retain the frozen model, auditor, vectors and replay as a normal-priority local
regression for future binder-operation changes. No distinguishing case exists
to minimize, and this result does not warrant an external issue or
contribution. The next queue item addresses a separate research question.

## Scope and evidence

| Measure | Result |
| --- | ---: |
| Selected vector rows | 10,000 |
| Distinct structural operation inputs | 5,091 |
| Capture-collision rows | 2,000 |
| Operation × syntax-family strata | 20 |
| Official Lean checked outputs | 15,000 of 15,000 matched |
| Kiota checked outputs | 15,000 of 15,000 matched |
| Scientific processes | 40; all cleanly completed under the bound controls |
| Distinguishing outputs | 0 |

The selected public operations were official Lean 4.33.0
`Expr.liftLooseBVars` and `Expr.instantiate1`, and Kiota at revision
`2d2a9fa` `shift` and `instantiate1`. The fragment used
bound variables, sort zero, application, lambda and let. Its contexts were
finite and its trees were syntactically well scoped. The named model used
free-name substitution with binder renaming and context insertion for lift;
the independent expectation auditor used separate translation and index
rules. The auditor is a cross-check of this finite specification, not a
proof of the APIs' semantics.

The exact selection rule and model are in the [scientific manifest](scientific-manifest.json)
and [protocol](protocol.md). The [execution manifest](execution-manifest.json)
binds the runtime, source versions, adapters and resource controls. The
[corpus lock](corpus-lock.json) binds all 10,000 records and twenty byte-exact
500-row batches. The [raw result](runs/attempt-0001/result.json),
[independent observation review](independent-observation-review.json), and
[portable replay](../../../../lib/binder_model_replay.py) support the counts
above. Recorded process time is not a performance comparison; it omits
preparation and review work.

Four selected rows had appeared in an early auditor test before the formal
construction gate. Their source bytes and hashes remain preserved. The item
owner and independent reviewer accepted them unchanged; the committed
producer reproduced and independently audited each one before constructing
the full corpus. An early Kiota adapter build check failed and was repaired
before science; its full first-revision input and precise cost are unknown.
The first memory preflight was denied by the sandbox before a child launch;
the same preflight passed with actual-host process-monitor access. None of
these preparation events is a scientific negative result.
