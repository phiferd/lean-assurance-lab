# Nanoda Binder-Sort Survivor Classification

This investigation closes `nanoda-0004` (lambda binder sort) and
`nanoda-gen-9a8edf073073` (let binder sort) as whole-checker equivalents at
Nanoda's public declaration entrypoint.

Both mutations skip a local `infer_sort_of(binder_type, Check)` call. The
remaining checked dataflow re-establishes the same requirement:

- a let annotation must be definitionally equal to the checked value's type;
- a lambda's inferred Pi telescope is recursively compared with a checked
  expected type, ultimately the declaration type, which is independently
  sort-checked;
- ordinary Pi inference validates every domain.

Under single-mutant isolation and conversion typing, a malformed binder cannot
be definitionally equal to the corresponding well-formed type. Source-derived
loose-bound-variable probes confirm the concrete failure path: baseline and
mutant Nanoda reject both candidates, with the mutant reaching the later
mandatory validation instead of the skipped local check.

The classification is intentionally scoped. It does not cover direct internal
`TypeChecker` callers, simultaneous mutations, or a separate defect in
definitional equality that would violate conversion typing.
