# Real proof slices pilot 1

Outcome: **SUCCESS**, scoped to the retained inputs and supported observer profiles.

The fixed selection produced twelve declarations from `init`, `std`, and `cedar`. Independent closure audit passed all twelve receipts. Nine slices fit the 8,000,000-byte and 120,000-record ceilings; official Lean 4.33.0 and Nanoda `6ae1f0c` accepted every one of their 18 bound cells. Three fixed `std` slices were oversize and were not launched.

| Case | Selected declaration | Closure rows | Derived bytes | Disposition |
| --- | --- | ---: | ---: | --- |
| `init-01` | `Nat.add_assoc` | 889 | 48,333 | ACCEPT_BOTH |
| `init-02` | `Nat.add_left_comm` | 1,387 | 71,838 | ACCEPT_BOTH |
| `init-03` | `Nat.add_le_of_le_sub` | 5,730 | 300,276 | ACCEPT_BOTH |
| `init-04` | `Nat.lt_of_succ_le` | 255 | 15,070 | ACCEPT_BOTH |
| `std-01` | `Std.DHashMap.Internal.mkIdx._proof_2` | 118,859 | 6,024,449 | ACCEPT_BOTH |
| `std-02` | `Std.DHashMap.Raw.mem_iff_contains` | 120,082 | 6,098,511 | OVERSIZE |
| `std-03` | `Std.DHashMap.Raw.WF.size_buckets_pos` | 159,544 | 8,273,554 | OVERSIZE |
| `std-04` | `Std.DHashMap.Internal.Raw.contains_eq` | 159,665 | 8,280,343 | OVERSIZE |
| `cedar-01` | `Cedar.Spec.Value._sizeOf_4_eq` | 11,434 | 646,470 | ACCEPT_BOTH |
| `cedar-02` | `Cedar.Data.Set.mk.sizeOf_spec` | 865 | 50,129 | ACCEPT_BOTH |
| `cedar-03` | `Cedar.Spec.Value._sizeOf_2_eq` | 11,562 | 652,939 | ACCEPT_BOTH |
| `cedar-04` | `Cedar.Spec.Value.set.sizeOf_spec` | 11,577 | 653,675 | ACCEPT_BOTH |

The independent auditor reconstructed typed name, universe, expression, declaration, grouped inductive/recursor, quotient and environment closure from the retained source bytes, checked row provenance and order, and rejected the planned negative controls. The first real-case audit exposed a prose-only protocol/manifest binding defect; its failed attempts and reviewed R2 tooling repair remain preserved. The initial RSS preflight encountered sandbox denial of `/bin/ps`; the actual-host retry passed with five positive samples and complete cleanup. All 18 observed cells had positive RSS and complete cleanup.

Observed process time across the 18 cells was 1.472 seconds, and maximum recorded child-group RSS was 50,561,024 bytes. The exact raw execution is in [`attempt-0001/result.json`](execution/attempt-0001/result.json); the [independent observation review](independent-observation-review.json) verifies its 18 receipts and streams.

The selected libraries were already observed, and the Gate-8 legacy coverage-revision mismatch remains. Checker agreement is not semantic authority or a soundness claim. Nanoda's supported profile reports silent exit-zero success, with no per-declaration checked-object trace. The three oversize cases have no semantic observation; none was replaced after selection.

**Recommendation:** Retain the slicer, auditor, and nine accepted slices as a local regression asset at normal priority. No external contribution is warranted by this all-agreement result. Any extension of sources, feature rule, or ceilings needs a separately frozen successor and exact source/tooling/observer review.
