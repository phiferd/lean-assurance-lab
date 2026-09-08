# Candidate-baseline attribution repair

The first candidate-baseline attempt is retained as checker reservation 3 at
commit `3ef224c`. It returned code 101 with the exact `src/tc.rs:921:71`
`assert_def_eq` assertion, an `infer` frame, and a `check_declar` frame. Revision
2 required a literal `check_declar_info` frame. Release optimization inlined
that function, so the normalizer conservatively recorded `CRASH` even though
the remaining raw frames and exact bound source locate the proposed rejection
path. No mutant candidate launched after this audit defect was recognized.

Revision 3 pauses any non-attributed baseline-candidate result before the
mutant candidate. It recognizes only the exact code-101 assertion receipt with
empty stdout, the exact source location, retained `infer` and `check_declar`
frames, and a clean supervisor receipt. It continues to classify a generic
panic, wrong location, missing frame, parser error, timeout, unsafe receipt or
nonempty stdout separately. Focused regressions bind that distinction and the
new pause behavior.

The first focused revision-3 test retained in this directory failed because a
synthetic completed-matrix fixture still labeled the baseline candidate
`ACCEPT`. The new pause gate correctly rejected that fixture. The fixture was
corrected to the fixed hypothesis `TYPECHECK_REFUSAL`; the succeeding immutable
test receipt is stored in `prelaunch-r3-fixed/`. This was an inert test failure:
it consumed no build/checker reservation and changed no production rule or
scientific input.

The exact proposal, source mutation, pair bytes, configurations, runtime,
binary product, budget and previous receipts remain unchanged. Replaying only
the same baseline-candidate cell consumes a fourth checker reservation. The
failed classification and its charge remain in the append-only ledger. This is
an output-attribution repair inside `SURVIVOR-LET-REUSE-1`, not a scientific
negative, new item, new variant, or budget reset.
