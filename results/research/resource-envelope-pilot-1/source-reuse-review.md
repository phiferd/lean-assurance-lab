# Resource envelope pilot 1: source and reuse review

**Provisional finding:** Retained local sources support a common one-definition checking task for official Lean and Nanoda, but no selected resource inputs or measurements exist yet. **Is it interesting?** Yes: the two implementations handle Pi towers and let chains through different source paths, which makes the fixed comparison worth measuring. **Does it require more work?** Yes: freeze the exact inputs, audit every generated case independently, and validate the measurement controls before any observer run.

Status: preparation evidence, before selected input construction. This document is not an observer result or a validity certificate for a generated case.

## What the retained sources establish

The selected comparison can use two existing executables that read the same lean4export 3.1.0 NDJSON encoding. The official Lean 4.33.0 adapter parses an export and invokes `env.replay constMap`; Nanoda parses the export and invokes `check_all_declars`. Both can check a single safe definition with no dependencies. Their internal paths differ, so elapsed time and memory are implementation observations for this fixed task, not a universal checker ranking.

| Role | Retained identity | Evidence and constraint |
| --- | --- | --- |
| Export arena | `external/lean-kernel-arena` revision `37f7525b732808a49b746dc6999d53c3717db124` | Existing build layout and exporter/checker pair; reuse lead only. |
| Export producer | `lean4export` 3.1.0, Lean 4.29.1; source revision `cacf989bd75f608700820f6afc595f32e7a99a4d`; binary SHA-256 `11c28bf9a0e1dfd0cb1130fb5d79ab5bff10503a67990039e23e23f03bd5cecc` | One dependency-closed declaration export; exact producer invocation and source bytes must be frozen before selection. |
| Official checker | Lean 4.33.0; binary SHA-256 `87efe83ae56410a4689b49ff5276dd9663fc85ae3641849d123b5fcef1692585`; local `Main.lean` SHA-256 `f0c209172f79e2b0b6599f7acc989e15a158f4118a6ddab0a567773b75f333bb` | `runKernel` calls `env.replay`; `--parse-only` exists but is not a matching Nanoda mode and will not be used as a comparative baseline. `Lean.Replay` skips unsafe and partial constants, so output count alone cannot prove checking. |
| Nanoda checker | revision `6ae1f0cd962f081f6c423454c5da729d841236a7`; binary SHA-256 `55a3686145143e1ca4403848659163cb6b67c07f6b6a7807916cbbc4be96bc41` | `main.rs` invokes `check_all_declars`; the new fixed config uses one thread, strict unpermitted-axiom handling and explicit success output. Prior four-thread/silent config is not reused as a comparable profile. |
| Format/importer | official `lean4export` importer revision `f297dfe2a8557e8674fe892bb49dffe4bfadc0e9` | Exact schema and version are audited per export, not inferred from a successful parse. |

The retained Nanoda `tc.rs` `infer_pi` iterates a Pi tower and `infer_let` checks the annotation/value and substitutes the body. These source paths motivate two structurally different families. They do not predict a measured curve. The official replay source shows kernel declaration addition for selected safe definitions, subject to the independent per-input audit.

## Reuse boundaries

The prior valid-dependent-term pilot retained 50 audited positive closed declarations, including Pi and let terms, with 3–48 AST nodes and binder depth at most 6. Its type auditor and export pipeline are useful examples; its historical size/fuel bounds and previous observer outputs do not certify this pilot's selected depth-512 inputs. The real-proof-slices pilot retained nine accepted cases; its three oversize, unobserved selections are not valid inputs here. The binder-model pilot contributes custody/supervision ideas but measured different operation harnesses and cannot supply baseline time or RSS values.

The proposed six sizes are 16, 32, 64, 128, 256 and 512 binders. This geometric finite span is chosen before measurements from the simple linear source grammar, export format, and planned independent DAG audit. It may produce flat, startup-dominated outcomes; no observed threshold may be used to expand or replace the sizes. Report export byte size, reachable unique expression nodes, expanded value-node count and binder depth separately, because DAG sharing changes the meaning of “size.”

No external action follows from this source review. The next local gate is a frozen exact protocol, independent validity/identity auditor, and negative-capable measurement controls before any selected term is generated.
