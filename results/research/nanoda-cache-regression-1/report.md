# Nanoda staged inference-cache regression

`NANODA-CACHE-REGRESSION-1` completed with `SUCCESS` at exact current inspected
Nanoda revision `4c544ed4099c8227f07d5de77ad1e69fb0740a27`.

Current Nanoda keeps separate checked and unchecked inference maps. Checked
results may satisfy either mode, while unchecked results may satisfy only
`InferOnly`; successful calls write back to the matching map. The new two-test
module makes that policy executable using the existing bounded witness pair.

The control builds a well-typed let, warms its unchecked result, then checks the
same expression pointer in the same checker. Both calls return the expected type
and the test observes distinct map writes. The candidate first confirms that a
fresh `Check` rejects a malformed let. A second equivalent expression succeeds
with `InferOnly`, records only an unchecked result, and still rejects under
`Check` on that identical warmed pointer with the exact
`assertion failed: self.def_eq(u, v)` message.

The focused `infer_cache` run passed both new tests. The complete locked suite
then passed 40 library tests with zero failures; eight documentation tests were
ignored. Both launches used the committed patch, offline locked dependencies,
a 120-second monotonic deadline and process-group cleanup. The only pre-launch
engineering issue was a truncated hand-authored patch hunk; formatting checks
caught it before compilation, and the repaired bytes were committed before any
test.

Repository closure validation then exposed an independent CI regression in the
historical Arena-let repair test: it compared an old successor claim with the
mutable current queue and checked historical bindings against live files. The
repair now reads each historical claim and binding from its exact commit, binds
the evolved regression test by immutable Git blob identity, and separately
validates the current queue. The complete repository rerun passed 926 live, 73
frozen-publication and 9 portfolio-checkpoint tests with zero failures.

This is a preventive internal implementation-contract regression. The earlier
mutant result supplies historical sensitivity evidence only. Ordinary exported
reachability remains bounded unresolved, and no current mutant result,
malformed-export acceptance, production impact, semantic authority, corpus kill
or mutation-registry change is claimed.

The [unsubmitted draft](../../action-recommendations/drafts/nanoda-infer-cache-regression.md)
is ready for a later fresh source/duplicate preflight and explicit human
submission approval. `SEMANTIC-LET-CONTRACT-1` is selected READY and unstarted.
