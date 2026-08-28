# IMax right-successor comparison accepts exports rejected by Lean

Current Nanoda `master` accepts two small exported declarations that official
Lean 4.33 and Lean4Lean reject. Their matched controls are accepted by every
checker.

Current-head reproduction:

- Nanoda revision: `05055695879dfebb6628a67da88ceca6cd6b0421`
- `universe-imax-right-one.ndjson`: Nanoda `ACCEPT`, official Lean `REJECT`,
  Lean4Lean `REJECT`
- `universe-imax-right-succ.ndjson`: Nanoda `ACCEPT`, official Lean `REJECT`,
  Lean4Lean `REJECT`
- Both direct-`max` controls: `ACCEPT`

The minimal case compares `imax u 1` with `max u 1`; the general case compares
`imax u (v+1)` with `max u (v+1)`. Official Lean reports a declaration type
mismatch between those levels.

Artifacts and current-head results:

- https://github.com/phiferd/lean-assurance-lab/tree/main/corpus/generated
- https://github.com/phiferd/lean-assurance-lab/tree/main/results/investigations/upstream-action-preflight
- https://github.com/phiferd/lean-assurance-lab/blob/main/results/investigations/nanoda-universe-definitional-equality-matrix.md

Could you clarify whether Nanoda intends to match official Lean's definitional
equality here? The source-level simplification behavior may be relevant, but we
have not treated the mutation that exposed this boundary as a proposed fix.

This is a checker-conformance report over public export artifacts. We have not
demonstrated a false-theorem exploit or broader Nanoda unsoundness.
