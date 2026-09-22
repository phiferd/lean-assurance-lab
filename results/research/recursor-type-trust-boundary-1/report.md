# Recursor type trust boundary result

Outcome: **VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY**

## Conclusion

At exact Kiota revision `9fa2c297`, the importer reads the serialized recursor
type, checks its manifest telescope length against metadata, stores that same
type, and exposes it through constant inference. Its later inductive checks
validate several group, constructor, positivity and elimination properties, but
do not construct and compare a complete recursor type. A declaration later in
the input stream can consequently be checked against that stored type.

Official Lean 4.33.0 follows a different concrete import policy. Its parser also
retains the serialized record, but replay reconstructs the inductive declaration
and its recursors, postpones supplied recursor records, and finally compares the
complete supplied and regenerated records. Replay first processes dependencies.
That ordering explains both preserved observations:

- the bare candidate reaches the postponed comparison and reports
  `Invalid recursor LALNest.rec_1`;
- the extended candidate first checks `LALNest.rec_1_impact` under the regenerated
  type and reports the fifth-argument `LALNest` versus `LALWrap LALNest` mismatch.

The supported local policy is therefore narrow: downstream typing must not rely
on an unvalidated serialized recursor type. A checker should validate it against,
or replace it with, a type reconstructed from the same accepted inductive and
constructor group, while retaining acceptance for unchanged agreeing inputs.
Official complete-record equality is evidence for one concrete importer policy,
not a universal independent-checker or format law.

## Regression and repair readiness

The exact preserved pair is frozen as the minimal local regression:

- candidate: reject;
- unchanged control: accept;
- no adaptive replacement and no reuse of a completed attempt as a new result.

This is a validated regression target, not an authorized production algorithm.
Kiota has no source-bound constructor for the complete recursor type and the
inspected sources do not decide whether a later comparison should be structural,
normalized or definitional. Before any production edit, a successor must commit
and validate a Kiota-specific construction covering supported ordinary, mutual
and nested groups, specify its comparison or replacement rule, and bind
acceptance-preservation fixtures.

No checker was launched, no production checker file was changed, and no external
action occurred. The item makes no checker-soundness, false-theorem,
inconsistency, exploitability or universal-format claim.
It does not change the declaration-validation catalog.
