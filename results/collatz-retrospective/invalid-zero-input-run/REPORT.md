# Frozen Collatz Retrospective Report

Status: **PASS**  
Classification: **PARTIAL_REDISCOVERY**

## Result

The bounded retrospective partially rediscovered the disclosed fault class. The generated artifact was accepted by affected official Lean 4.29 and rejected by fixed official Lean 4.33. Kiota and Lean4Lean also rejected it, providing independent implementation evidence. The projection-structure-identity component was not rediscovered within the frozen schedule.

This is retrospective capability evidence under an operator-informed protocol. It is not evidence that the project prospectively discovered the 2026 incident, and it is not a general bug-finding rate.

## Frozen Boundary

- Historical Arena revision: `dd345f6a5c034d73b5889b318cbd88252c7627c9`
- Historical corpus: 152 materialized tests, 16175717 bytes
- Corpus composite SHA-256: `b99eb360b7dd36364c939bffcda704e57f1a5f4d4799f555016332bcbab8b34d`
- Protocol freeze SHA-256: `ef298e01f26799cb295df4e14ff549864a56e28452464f972069bd10b082ec37`
- Random seed: `20260824`
- Projection candidate budget: 64
- Disclosed Arena and published Collatz artifacts used during generation: no
- Historical checker feedback used during generation: no

## Generated Artifact

`corpus/collatz-retrospective/nested-phantom-candidate.ndjson` (11217 bytes, SHA-256 `2167ca8678c772b7bef0d0210fe9ed5f54a29e49d3d14b69e96b792ed5e48a61`)

| Checker | Outcome |
| --- | --- |
| Affected official Lean 4.29 | ACCEPT |
| Pre-fix nanoda `ddfac2b` | ACCEPT |
| Fixed official Lean 4.33 | REJECT |
| Fixed nanoda `6ae1f0c` | ACCEPT |
| Kiota `58e8636` | REJECT |
| Lean4Lean `ecb3b66` | REJECT |

The result establishes the dropped nested-unused-parameter distinction. It does not distinguish pre-fix from fixed nanoda: both accepted the generated artifact.

## Negative Result

The coverage stage examined 26 pre-disclosure inputs containing serialized projections. None covered the frozen nanoda projection-equality target, so the coverage-guided schedule and structured projection search contained zero eligible attempts. No projection-identity witness was generated. This is recorded as a failed component, not as equivalence and not as full rediscovery.

## Disclosed Holdout

The Arena `nested-unused-param` artifact was opened only after the candidate freeze. Affected official Lean 4.29 accepted it; fixed official Lean 4.33, fixed nanoda, Kiota, and Lean4Lean rejected it. The pinned pre-fix nanoda revision rejected this reduced Arena artifact, which is narrower than the original Collatz development discussed in the postmortem.

## Cost

- Generated/holdout checker runs: 12
- Generated/holdout checker seconds: 1.5016
- Source-model checker runs: 0
- Nested candidate build/export seconds: 6.3868

Mechanical audit: `results/collatz-retrospective/assurance.json` (23 checks).
