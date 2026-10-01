# A structural function-domain positivity bridge

What did we find? Lean checked a bridge for arbitrary finite function-type
domains and every natural List depth. A domain is built from the label type
alpha, the tree type Tree alpha, and nondependent function arrows. Official
acceptance holds exactly when Tree occurs nowhere in that domain. Acceptance
then yields exact lowering, a constructed native positivity derivation, and
actual native positivity success. All six modules passed fresh replay.

Is it interesting? Yes, modestly. The earlier theorem chose between two fixed
domains. This theorem handles arbitrarily shaped domains by structural induction,
proving the missing occurrence-preserving conversion and actual typing facts.
For example, (alpha -> alpha) -> alpha is an admitted domain. A domain containing
Tree is rejected even when function arrows change its variance: the relevant
upstream rule excludes every recursive occurrence in the outer function domain.
This is a restricted model interface, not general proof reconstruction or a
production-kernel correctness result.

Does it require more work? This bounded class theorem is complete. Independent
review considers it substantial enough for a focused, human-authored maintainer
target-fit inquiry about the parked completeness proof. No upstream message or
posting-ready draft was created. Before investing in containers inside domains,
a human should assess whether this occurrence-preserving interface and its exact
schema assumptions are useful to that proof. The campaign remains ACTIVE, but
no further grammar expansion, fold or recursor trial starts here.

## Exact class and theorem

`D ::= parameter | self | arrow D D`, where parameter denotes alpha:Type and
self denotes Tree alpha. The source constructors are leaf alpha and
node (D -> List^N(Tree alpha)). There is one uniform parameter, no indices,
dependent fields, Prop, aliases or beta wrappers. Every explicit Pi uses
BinderMeta.pw=never. Ordinary List retains its exact one-level-parameter,
one-type-parameter, nil/cons schema. The native environment stores the actual
changed node for each D and N; no arbitrary environment-check oracle is assumed.

The independently specified lowered signature is
`T=alpha+(D->R_N)`, `R_0=T`, `R_j=1+R_(j-1)*R_j`.
Domain replacement is proved state-preserving by induction, so it allocates no
auxiliary type. Only the result List tower drives the existing queue and keys.

`Tree2DomainOfficial.acceptance_iff D N` proves actual OfficialPosAccepts iff
`D.hasSelf=false`, including an actual positive witness for every admitted D,N.
Successful-output uniqueness extracts the actual constructor check from unknown
acceptance fuel, and that check excludes any self occurrence in the domain.

`Tree2DomainBridge.domain_conversion` consumes that actual acceptance and proves
the raw parameter substitution, upstream canonical/key substitution, native
occurrence-free condition, and exact native typing. Those facts are separately
proved by structural induction; no converter is a premise.

`Tree2DomainBridge.restricted_completeness D N` packages the acceptance equivalence
and the bridge: exact elimNested target at queue fuel N+2, constructed native
root PosDR at index N+2, and existential actual native success at Core fuel
`B(D,N)=max(height(D)+2,N+3)+2`. Leaf PosDR remains index1. Each constructor uses
its actual automatic walk budget; no growing common bound is imposed on leaf.
The inferred sorts retain their actual imax expressions. Their zeroness metadata
and the sufficient structural Core bound are proved, not assumed Sort1 equalities.

## Evidence and trust

Six fresh module compiles total 9.137491250s, peak sampled group RSS
1,491,206,144 bytes; all dependency queries, compiles and cleanup completed.
Sixteen retained development compiles include eight rejected proof repairs,
totaling 30.238760331s, with zero resource interruptions. Failed elaborations'
sorryAx output belongs only to rejected attempts. Every final printed theorem
uses exactly propext, Classical.choice and Quot.sound. No sorry/admit/new axiom,
native_decide or run_tac appears in the accepted sources after stripping comments.

The compiler and108 historical cache hashes were checked. Seven prior import
artifacts match the previously published Git blobs; the exact six new source
hashes are bound in fresh-replay-inputs.json and checkpoint.json. Independent
review passed for noncircularity, interpretation and target fit. Pinned-source
coverage search retains the local OfficialPosAccepts definition and parked
completeness context; it supplies no literature-wide novelty claim.

Reproduction uses the retained replay-chain.py with the pinned compiler,
hash-verified confirmation-fresh cache, archived six sources and a NEW destination.
The fresh replay commands and receipts are in fresh-replay/. Prior sources,
published trials and historical evidence remain unchanged. A rejected preparation
command did not execute; an explicit new replay script resolved the review concern
about historical mutation, with old bytes checked unchanged.

Native returned records remain existential. Official rows/keys are not a theorem
about emitted native records or values. This result is occurrence classification
plus constructive derivation for an admitted syntax class; it does not reconstruct
arbitrary official derivations. No full validator acceptance, C++ kernel parity,
compiled checker parity, generated recursor/fold correctness, novelty, or E2
closure is claimed. This record remains exploratory E0, with no candidate
discrepancy observed in the stated model class.
