# Restored-Recursor Witness Search Notes

## 2026-08-27 source trace

The mutant skips `RecursorData::aux_data_ck` in
`check_restored_recursor1`. That comparison checks `num_params`,
`num_indices`, `num_motives`, `num_minors`, `is_k`, the resolved recursor
name, and the set of associated inductive names. The recursor type and rule
bodies are checked separately after this call.

The first source-derived probe uses the 142-record
`nested-nonuniform-param.ndjson` export. Its final nested block has one base
recursor and one restored auxiliary recursor. Toggle only the serialized `k`
field in each recursor separately; leave types, rules, names, and all other
metadata unchanged. Because this nested block is the final declaration, no
later declaration can observe the changed reduction flag.

The first probe produced the expected differential, but its
`nested-nonuniform-param` seed has an intentionally unresolved semantic
contract. It is retained only as exploratory evidence.

The final witness instead uses a 105-record ordinary nested datatype generated
from `LALWrap` and `LALNest`. Official Lean, Lean4Lean, Kiota, baseline Nanoda,
and mutant Nanoda all accept the unchanged control. Toggling only the restored
auxiliary recursor's `k` field gives:

- baseline Nanoda: reject at the skipped comparison;
- mutant Nanoda: accept;
- official Lean: reject;
- Lean4Lean: reject;
- Kiota: accept.

Official Lean therefore establishes `REJECT` for the exact witness hash. The
Kiota result is a separate unresolved checker disagreement.
