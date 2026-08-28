# Add reject coverage for IMax right-successor comparisons

## Summary

Add two focused `bad_raw_consts` tutorial cases:

- `imax u 1` compared with `max u 1`;
- `imax u (v+1)` compared with `max u (v+1)`.

Official Lean 4.33 and Lean4Lean reject both declarations with a type mismatch.
Nanoda and Kiota currently accept both. Every checker accepts the matched
direct-`max` controls.

## Rationale

The current Arena corpus does not directly characterize this definitional
equality boundary. The minimal case makes the expected rejection easy to audit;
the parameterized case prevents an implementation from special-casing only the
literal level `1`.

## Evidence

- Expected outcomes were established with the official checker, without
  majority voting.
- Current Nanoda `master`, Kiota `main`, and Lean4Lean `arena` were rebuilt and
  tested against the exact artifacts.
- Exact duplicate searches found no existing Arena issue for these cases.
- Evidence: https://github.com/phiferd/lean-assurance-lab/blob/main/results/investigations/nanoda-universe-definitional-equality-matrix.md

## Scope

This PR would add regression coverage only. It does not claim a general
soundness defect in either accepting implementation.
