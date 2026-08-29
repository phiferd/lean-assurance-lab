# Proof-Parameter Uniformity Disagreement

`LALProofParameterSwap` has parameters `(P : Prop) (p q : P)`. The valid
control constructor returns `LALProofParameterSwap P p q`. The candidate
changes only that result to `LALProofParameterSwap P q p`; its complete,
exporter-generated recursor metadata and rule are otherwise unchanged.

Official Lean 4.33 and Lean4Lean reject the candidate, while current Nanoda
rejects it at exact constructor-result parameter matching. The controlled
Nanoda omission `nanoda-0006` accepts it, so the candidate is a mutation kill.
All four accept the unchanged control.

Kiota accepts both candidate and control. The disagreement reproduces on
current Kiota `main` revision `686063c13b22ce379c05dfe7fc03656655ac60e5`.
The likely boundary is that proof irrelevance makes `p` and `q` definitionally
equal for later type comparisons, but the inductive formation rule requires
constructor result parameters to be the original parameters in the original
order, not merely definitionally equal terms.

The result is suitable for one Arena reject test and one focused Kiota issue.
Both are held for explicit human approval. It should not be split into multiple
implementation reports, and it does not establish general Kiota unsoundness.

Evidence:

- `proof-parameter-differential.json`: baseline Nanoda reject versus mutant accept;
- `proof-parameter-control-differential.json`: both Nanoda builds accept the control;
- `results/expected-outcomes/ordinary-inductive-proof-parameter-uniformity.json`:
  official Lean establishes rejection;
- `results/cross-validation/ordinary-inductive-proof-parameter-uniformity/results.json`:
  official Lean and Lean4Lean reject, Kiota accepts;
- `upstream-main.json`: current Kiota reproduction.
