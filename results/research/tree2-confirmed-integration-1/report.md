# Confirmed restricted constructor-representation proof — local candidate

We found a Lean-checked agreement between two restricted ways to describe
constructors, and a fresh build reproduced the exact result. This is interesting
because it connects the models at every List-nesting depth with frame-local holes,
instead of merely checking more accepted examples. Further work here is lab
integration validation and owner review; datatype behavior and production-kernel
correctness remain outside the claim.

`Tree2TowerCorrespondence.representation_package N F` has only hypothesis
`N+5<=F`. It packages exact simplified official lowering at fuel N+2, constructed
native PosDR at index N+1, existential automatic run success, and actual
constructor-crest interpretations equal to the independent polynomial signature
T=alpha+R_N;R0=T;Rj=1+R(j-1)*Rj. Allocation/frame mapping and zero case are checked.
The exact statement and source/proof/axiom hashes are in claim.json, source-lock.json
and compiled-proof-identities.json. The seven AI-authored sources are unchanged
from local commit e94d00b624951ccc0b4dd0a317eb5e952d948696, over pinned con-leche
10fe085e21773ff0b62a6aacf6db29fccf849bae and Lean4.33.0.

Fresh isolated import build compiled101 upstream and seven proof modules in frozen
order, using official Lean libraries and no original con-leche import cache.
Aggregate134.742seconds, sampled peak1,804,779,520bytes, complete cleanup. Final
stdout exactly matches frozen theorem/16 reports, each with only propext,
Classical.choice, Quot.sound. Prior preexecution rejection and corrected review,
94 original proof attempts including failures, and confirmation evidence are
preserved byte-for-byte with custody paths/hashes. Absolute old paths are data,
not replay dependencies. Dedicated portable replay tests copy evidence to a
foreign checkout, forbid host processes and reject source/raw tampering.

Independent claim/confirmation review passed. Fast portability/registry, frozen
resource execution inputs and existing historical dependent-term closure passed.
Full local E2 closure is not claimed by this candidate text: its exact-input
validation outcome is recorded separately under
results/workflow-validation/tree2-confirmed-integration-1/attempts/*/result.json.
A COMPLETE closure receipt with matching inputs is required before calling the
candidate locally publication-ready. No declaration-validation milestone advance.

Remaining unproved: exact native returned observation identity, datatype/fold
semantics, arbitrary containers, minimum fuel, generated recursor correctness,
official whole positivity acceptance, whole-validator and compiled/C++ parity.
No upstream contribution or community message is recommended by this bounded
model result. Recommendation: retain this scoped reproducible evidence in the
own lab after gates pass and the owner approves main integration/push. No push,
PR or publication has occurred; no further scientific direction started.
