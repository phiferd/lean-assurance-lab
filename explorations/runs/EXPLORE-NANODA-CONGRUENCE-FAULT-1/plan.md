# Prospective trial record

Question, fixed sample, controls, signal criteria and stop boundary are governed by `docs/research/E0_NANODA_CONGRUENCE_FAULT_PILOT_1_PLAN.md`.

Source: `ammkrn/nanoda_lib` at `3a2407216ee84a75f9e1aead6803d0578be06ae7`.

The retained `fault.patch` removes exactly one pairwise argument-equality conjunct in `try_eq_const_app`. The candidate and control differ only in the final declared type (`F B` versus `F A`) and final declaration name. Every axiom is explicitly permitted.

Expected baseline: control ACCEPT, candidate REJECT. Expected seeded fault: control ACCEPT, candidate ACCEPT. Existing-corpus failure means the fault was already covered; existing-corpus success means this exact public case is a potential local regression asset. Any malformed-input, branch-masking, incomplete-resource or build failure is INCONCLUSIVE until feasibly repaired.
