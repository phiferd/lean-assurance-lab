# Universe survivor equivalence result

`SURVIVOR-UNIVERSE-EQUIVALENCE-1` closes `SUCCESS` at pinned Nanoda revision
`6ae1f0cd962f081f6c423454c5da729d841236a7`. The `diff < 0` to `diff <= 0`
mutation is outcome-equivalent for every state reachable from public
`TcCtx::leq` and therefore for its public checker consumers.

The claim is deliberately not unrestricted. Direct private
`leq_core(Max(Zero,Zero), Zero, 0)` is a real counterexample: the baseline
returns `true` by splitting the raw Max, while the mutant returns `false`
early. Public `leq` simplifies that Max to `Zero` first, so both versions return
`true`. The proof establishes, by mutual source induction, that `simplify`
produces the same normal form in both versions and that every non-Zero normal
form compared with `Zero` at diff zero returns `false`. Successor and retained
Max cases follow directly; IMax parameter branches normalize substitutions,
Max-tail rewrites re-simplify, and the one unsimplified nested-IMax Max shape
contains two provably non-Zero retained IMax children.

The registry gains one append-only `SURVIVED` / `EQUIVALENT` row. No mutation,
historical comparison, survivor inventory, corpus or frozen evidence was
rewritten. The old 163-test zero-difference comparison is consistent support,
not the proof or semantic authority. No optional build, focused scientific
test, checker campaign, Lean proof, network request, new export byte, mutation
identity or external action ran.

The next selected item is `SURVIVOR-FVAR-REACHABILITY-1`, READY and unstarted,
for a source-only assessment of the declaration-type free-variable guard.
