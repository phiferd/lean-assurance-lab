# Should a checker reject a let type mismatch that disappears after substitution?

We are preparing shared regression tests for external Lean checkers and want
to clarify what a checker is expected to validate when it reads an exported
declaration.

Consider this existing serialized declaration, shown here in readable notation:

```text
def EcosystemCase : Sort 2 := let u : Sort 1 := Sort 1; u
```

The let contains a type mismatch: its value, `Sort 1`, has type `Sort 2`, but
its annotation says `Sort 1`.

If we first substitute the value for `u` (zeta reduction), the expression becomes:

```text
def EcosystemCase : Sort 2 := Sort 1
```

That resulting declaration has matching types. The simplification has removed
the incorrect annotation.

**Should a full external checker reject the original declaration because of
that mismatch, or is it permitted to simplify the let first and accept the
result?** If the interface assumes that incoming expressions have already been
type-checked, could that assumption be stated explicitly instead?

This matters for shared tests: we need to know whether acceptance promises that
the supplied expression was checked, or that a permitted transformation of it
was checked. We are asking about that guarantee, not reporting a false theorem
or asking every reducer to repeat checks on already-validated expressions.

We found separate checking and reduction paths in Lean v4.33.0:
[`infer_let`](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.cpp#L200-L222)
checks the annotation/value relationship in checking mode, while the
[let reduction branch](https://github.com/leanprover/lean4/blob/d8b18978322de05a8f3dba51ef03cf5461676c17/src/kernel/type_checker.cpp#L504-L506)
substitutes directly. The
[3.1.0 format description](https://github.com/leanprover/lean4export/blob/f297dfe2a8557e8674fe892bb49dffe4bfadc0e9/format_ndjson.md)
lists the let fields but does not state which acceptance guarantee applies.
Is there an existing policy we should cite, or would a short clarification in
that document or the Lean reference manual be appropriate?

For reproducibility, the unchanged [candidate NDJSON](https://github.com/phiferd/lean-assurance-lab/blob/4a760173ea7e3e155ce46fa5631d4b447ee7682b/corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson)
and [matching control](https://github.com/phiferd/lean-assurance-lab/blob/4a760173ea7e3e155ce46fa5631d4b447ee7682b/corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson)
are each 601 bytes. The notation above explains those bytes; it is not an
elaboration result or a new test run. The body uses `u`, and the control changes
both the let value and the enclosing declaration type. The
[source review](https://github.com/phiferd/lean-assurance-lab/blob/4a760173ea7e3e155ce46fa5631d4b447ee7682b/results/research/semantic-let-contract-1/clarification-packet.md)
records the exact versions and remaining qualifications.
