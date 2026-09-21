# Pipeline-completeness pilot

## Purpose and claim boundary

This pilot tests whether a successful checker process can be tied to the exact
theorem identity, statement and dependency closure the user intended to check.
It is a pipeline-assurance experiment, not a vote among kernels and not semantic
authority for Lean.

The independently authored expected contents are
`results/research/pipeline-completeness-pilot-1/expected-module.json`. The bound
protocol is `results/research/pipeline-completeness-pilot-1/protocol.json`.
Neither may be regenerated from the eventual export.

## Supported path

Use the clean pinned Lean Kernel Arena checkout at revision
`37f7525b732808a49b746dc6999d53c3717db124`. Its already-built Lean 4.29.1
`lean4export` producer emits format 3.1.0. The two supported adapters are the
official Arena kernel and Lean4Lean, using the exact binary hashes and command
shapes in the protocol. Comparator-style normalization may be reused, but a
normalized `ACCEPT` alone never satisfies this pilot.

## Checked-object receipt

A passing cell binds three layers:

1. intention: expected-module hash, root target, all twelve ordered theorem
   names, their `True` statements and the `d01` through `d12` value-dependency
   chain;
2. artifact: exact export bytes and metadata plus a parsed declaration,
   statement-fingerprint and dependency-closure inventory; and
3. execution: the exact artifact hash passed to the exact adapter binary,
   command, raw streams, exit status, sampled RSS, timeout and cleanup receipt.

Only a zero-exit checker process whose artifact layer matches the independent
intention layer is complete. A process can therefore accept while the sentinel
correctly fails.

## Fixed matrix and rubric

Produce one baseline export for the twelve-declaration module. Derive three
fault copies without changing the intention receipt:

- `OMISSION`: remove the final target declaration records; require
  `FAIL_MISSING_TARGET`;
- `SUBSTITUTION`: pass a different existing compatible Arena artifact; require
  `FAIL_ARTIFACT_OR_DECLARATION_IDENTITY`; and
- `TRUNCATION`: remove the final nonempty NDJSON record bytes; require
  `FAIL_PARSE_OR_DEPENDENCY_CLOSURE`.

Run baseline plus all three faults through official and Lean4Lean: eight primary
cells. The baseline must pass the sentinel and both checkers. Every fault must
fail the sentinel regardless of checker exit. The remaining four of twelve
checker reservations exist only for receipt-preserving engineering repair and
may not repeat or expand the scientific matrix.

## Stages and gates

1. Implement the exact Lean module, receipt parser/sentinel, structural fault
   constructor and focused unit tests. No checker launch is allowed.
2. Run one supervised Arena producer build, freeze the export and its parsed
   inventory, and verify that it matches the independent expectation. Stop on
   any source, metadata, identity, dependency or process-control mismatch.
3. Commit the module, export, manifest, tools, tests and process controls. Only
   then change the item from READY to ACTIVE.
4. Run controls before faults under the fixed eight-cell matrix. Preserve raw
   evidence and close with either the expected sentinel matrix or an exact
   unsupported/observability boundary.

The total cap is 180 active minutes, one producer build up to 600 seconds and
4 GiB, twelve checker reservations up to 120 seconds and 2 GiB each, and zero
network requests or external writes. Ordinary tooling failures are repaired
inside this item without changing expected contents, faults or budgets.
