# Survivor cache comparison

`SURVIVOR-CACHE-1` completed successfully at pinned Nanoda revision
`6ae1f0cd962f081f6c423454c5da729d841236a7`. Two offline builds and four
source-bound tests produced the preregistered pattern: baseline and mutant
controls passed; the baseline candidate caught the exact let annotation
mismatch; the mutant candidate failed at `src/tc.rs:1383:23` with the fixed
message `expected checked inference to reject warmed malformed let`.

The comparison establishes a narrow internal cache-contract distinction. An
`InferOnly` call warms `infer_cache_no_check`; the original guard prevents a
subsequent `Check` from consulting that entry, while the mutation permits it.
The result does not show that ordinary export validation reaches this history,
does not establish semantic authority or production impact, and does not
change the canonical survivor classification.

Daybreak source review identified a concrete same-checker possibility through
a K-recursor major, but no exported witness is yet constructed. The project-wide
closure review therefore selects `SURVIVOR-CACHE-EXPORT-1` READY and unstarted,
after comparing the universe survivor, transfer/CVC blockers, upstream state,
and current methods and reuse assets.
