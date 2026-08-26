# Frozen Collatz Retrospective Report

Status: **PASS**  
Classification: **FULL_CLASS_REDISCOVERY (amended)**

## Result

The amended bounded retrospective rediscovered both specified fault components. The original generated nested-inductive artifact distinguishes affected official Lean 4.29 from fixed official Lean 4.33. The repaired projection candidate distinguishes pre-fix nanoda `ddfac2b` from fixed nanoda `6ae1f0c`. Kiota and Lean4Lean reject both candidates.

The original zero-input projection result is invalid and is not counted as a negative result. It is preserved under `results/collatz-retrospective/invalid-zero-input-run`. The projection branch was rerun through two frozen protocol amendments after diagnosing coverage-path and candidate-materialization defects.

This remains retrospective, operator-informed capability evidence. The amendments preserve the original corpus, generator semantics, seed, limits, modeled mutant, and candidate-before-historical-evaluation boundary, but a post-disclosure repair cannot recreate the original pre-disclosure blind execution. The repair was developed after the original historical evaluation, so those outcomes were known even though repaired generation did not execute historical checkers or use candidate-specific historical feedback. This is not prospective discovery evidence or a general bug-finding rate.

## Frozen Boundary

- Historical Arena revision: `dd345f6a5c034d73b5889b318cbd88252c7627c9`
- Historical corpus: 152 materialized tests, 16175717 bytes
- Corpus composite SHA-256: `b99eb360b7dd36364c939bffcda704e57f1a5f4d4799f555016332bcbab8b34d`
- Original protocol freeze SHA-256: `ef298e01f26799cb295df4e14ff549864a56e28452464f972069bd10b082ec37`
- Random seed: `20260824`
- Projection candidate budget: 64
- Disclosed Arena and published Collatz artifacts used during generation: no
- Historical checker binaries executed by either generation stage: no

## Protocol Repair

The frozen coverage binary identifies its nanoda source as an absolute path under the repository's former `LeanVerifier` checkout. The original runner requested the current `LeanAssuranceLab` path, received an empty `llvm-cov show` report, and incorrectly converted that infrastructure mismatch into zero covering tests and zero search attempts.

The first amendment switched extraction to `llvm-cov export` JSON and matched the bound target by repository-relative suffix, with fail-closed checks for missing, ambiguous, or empty mappings. Of 26 projection-bearing pre-disclosure inputs, 11 covered the frozen `def_eq_proj` target.

The restored schedule exposed a second implementation defect: the nominally bounded generator deep-copied every possible payload before truncating to 64. The second amendment constructs and shuffles the same complete substitution-reference list, then materializes and deduplicates payloads in that same seeded order until the frozen limit. Unit tests compare its order and prefix directly against the frozen eager generator on tractable fixtures.

## Permanent Remediation

The general coverage pipeline now remaps checkout, Cargo, target, and Rust
sysroot paths to stable virtual roots and records repository-relative coverage
identities. Operational paths and timings are excluded from content identity,
and a known coverage sentinel prevents an empty export from being accepted.
`results/reproducibility/nanoda-portability.json` records two relocated builds,
including a path with spaces and both nested and external target layouts, with
identical raw binary, build-manifest, and canonical coverage hashes.

The complete 197-test corpus has now been recollected under schema 2 using the
pinned host and toolchain in `config/reproducibility.json`. This does not
rewrite the archived frozen binary or retroactively make the original blind
run valid.

## Nested Component

`corpus/collatz-retrospective/nested-phantom-candidate.ndjson` (11217 bytes, SHA-256 `2167ca8678c772b7bef0d0210fe9ed5f54a29e49d3d14b69e96b792ed5e48a61`)

| Checker | Outcome |
| --- | --- |
| Affected official Lean 4.29 | ACCEPT |
| Pre-fix nanoda `ddfac2b` | ACCEPT |
| Fixed official Lean 4.33 | REJECT |
| Fixed nanoda `6ae1f0c` | ACCEPT |
| Kiota `58e8636` | REJECT |
| Lean4Lean `ecb3b66` | REJECT |

This candidate establishes the dropped nested-unused-parameter distinction. Both pre-fix and fixed nanoda accept it, so it is not the projection-component witness.

## Projection Component

`corpus/collatz-retrospective/projection-identity-candidate-repair-v2.ndjson` (10184927 bytes, SHA-256 `a6586716c3f188cff9af0840107b2c6ed9078249e6438e605da49f98f2b8c0dc`)

| Checker | Outcome |
| --- | --- |
| Affected official Lean 4.29 | REJECT |
| Pre-fix nanoda `ddfac2b` | ACCEPT |
| Fixed official Lean 4.33 | REJECT |
| Fixed nanoda `6ae1f0c` | REJECT |
| Kiota `58e8636` | REJECT |
| Lean4Lean `ecb3b66` | REJECT |

The repaired search evaluated all 11 original target-covering seeds against fixed nanoda and the modeled source mutant; none distinguished them. Seeded structured mutation attempt 1 changed projection structure name `98` to `2090` in `external/lean-kernel-arena-collatz-pre/_build/tests/perf/grind-ring-5.ndjson`. Fixed nanoda rejected it while the modeled mutant accepted it. After candidate freeze, pre-fix nanoda accepted it and fixed nanoda rejected it, establishing the projection-structure-identity component.

Both official Lean versions reject this projection candidate. That is expected: this component models the separate historical nanoda defect, not the official Lean nested-parameter defect.

## Disclosed Holdout

The Arena `nested-unused-param` artifact was evaluated only after the original candidate freeze. Affected official Lean accepted it; fixed official Lean, fixed nanoda, Kiota, and Lean4Lean rejected it. The pinned pre-fix nanoda revision rejected this reduced Arena artifact, which is narrower than the original Collatz development discussed in the postmortem. The repaired projection branch did not evaluate the disclosed holdout.

## Cost

- Original generated/holdout checker runs: 12
- Original generated/holdout checker seconds: 1.5016
- Repaired coverage inputs: 26
- Repaired source-model checker runs: 24
- Repaired source-model checker seconds: 13.0606
- Repaired historical/fixed checker runs: 6
- Repaired historical/fixed checker seconds: 5.1038

Mechanical audit: `results/collatz-retrospective/assurance.json` (36 combined checks) and `results/collatz-retrospective/projection-repair-v2/assurance.json` (15 repair checks).
