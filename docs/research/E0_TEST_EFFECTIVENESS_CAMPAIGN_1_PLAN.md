# Three-case test-effectiveness screen

Evidence class: E0

What did we find? The preceding Nanoda screen found one seeded equality fault
that all 44 upstream tests missed. This campaign has not executed yet.
Is it interesting? Yes: compare actual detection by existing tests with retained
Lab cases, rather than prepare more preventive PRs without demonstrated need.
Does it require more work? Run the three fixed fault cases below, retain all
attempts, and make one campaign-level continuation decision. Box/FnAlias work
belongs to the owner's separate agent and is excluded.

## Question and fixed sample

At Nanoda 3a2407216ee84a75f9e1aead6803d0578be06ae7, which of three
separately introduced guard-omission faults are detected by (a) its unchanged
Rust library tests, (b) a fixed compact Lab input corpus, and (c) the retained
congruence regression pair?

The three cases are: omit the pairwise application-argument equality guard in
try_eq_const_app; omit the Check-mode binder-sort check only in infer_lambda;
omit the definition/theorem/opaque inferred-type versus declared-type check.
Each lives in an isolated copy of the same pristine source. The latter two
reuse the obligations of nanoda-0004 and nanoda-0002; this is a known-case
benchmark, not a prospective bug-discovery or held-out test.

Select all Git-tracked NDJSON files at campaign entry under corpus/generated,
corpus/controls, corpus/probes and corpus/regression-candidates whose bytes are
at most 65,536. Retain the complete sorted list, excluded files and SHA-256
identities before any checker observation. Use unchanged bytes. The two retained
congruence files are a separate augmented pair, not part of the preexisting
compact corpus. Do not substitute successful inputs for parsing/typing failures.
Compare each baseline outcome with all three faulted outcomes. A rejected
baseline that becomes accepted detects altered checking behavior; other changed
outcomes retain their actual category and are not automatically semantic kills.

Keep source identity, exact patches, command versions and all raw streams and
supervisor receipts in the exploration directory. One start/finish per fault
case suffices. Shared baseline attempts are referenced by all three records.
The upstream suite must first pass on pristine source. A nonzero test result
only detects a fault when tests actually ran and their failure is attributable
to the changed checker; build, parser, monitor and cleanup failures stay separate.
No whole-corpus coverage or general correctness claim follows from this sample.

## Execution and endpoint

Use existing lib/resource_envelope_supervisor.py run_direct. Cargo processes:
3,600 seconds, 16 GiB sampled RSS; checker processes: 30 seconds, 2 GiB.
Retain timeout, memory, exit and cleanup observations; use existing 3-second
sampling and 10-second cleanup controls. Repair ordinary engineering failures
within the same case, preserving every attempt. Only task-local source copies
and runner files change; do not modify shared tooling, scientific history or
production upstream source.

Complete the three-case comparison or preserve an exact capability/input
boundary. Summarize evidence and value once, select an unstarted successor, run
exploration-record check and exploration-handoff with the activation commit as
base, then diff check and main-only delivery. No full research replay, assurance
refresh, independent routine closure review, new PR or external communication.
Confirmation, integration and external claims require separate work and gates.
