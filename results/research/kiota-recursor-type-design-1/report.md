# Kiota recursor type design 1 report

Outcome: `VALIDATED_COMPLETE_KIOTA_DESIGN`

The missing design is now complete for pinned Kiota revision `9fa2c297`. Kiota
already has the term, universe, inference and definitional-equality operations
needed by a native builder. An already archived, provenance-bound copy of Lean
4.33.0 `src/kernel/inductive.cpp` supplies the exact missing reference
algorithm for ordinary, mutual and nested groups.

## Construction

For an ordinary or mutual group, derive the elimination universe, one motive
per group member, one minor per constructor, and one induction hypothesis per
recursive field. The exact recursor order is:

`parameters → all motives → all minors → target indices → major → result`.

Fields precede induction hypotheses inside a minor. Motives follow group order;
minors follow group order and then constructor order. Recursor universe
parameters are the fresh elimination universe followed by declaration
universes when unrestricted elimination is legal, and just the declaration
universes when elimination is restricted to `Prop`.

Nested groups use Lean's complete auxiliary transform, not Kiota's current
counting and name-order heuristics: discover nested prior-inductive
specializations breadth-first, copy every member of the prior mutual group,
replace occurrences with auxiliary types, run the ordinary/mutual construction,
then restore the nested types and rename auxiliary recursors `.rec_1`, `.rec_2`,
and so on in discovery order. Restored types must be type-checked before use.

## Import rule

Current-block recursors must remain absent while validation runs. The supplied
closed type must first infer to a sort in the checked type/constructor
environment. Map supplied and reconstructed universe parameters positionally,
then require Kiota's own definitional equality. Structural equality is too
strong because binder annotations and alpha universe names are non-semantic;
normalized structural equality has no source-bound canonical normalization
contract in Kiota.

An equality mismatch is a rejection. An inference, restoration or conversion
decline fails closed. After agreement, Kiota installs only the reconstructed
type. It never exposes the supplied type to later declarations. This preserves
the predecessor's exact regression: candidate reject, unchanged control accept.

## Preservation gate

The later repair must preserve four exact accepted fixtures spanning indexed
ordinary, same-container nested specialization, deep parametric nesting and a
mutual-plus-nested LCNF group. It must also reject the unchanged fifth-domain
candidate, accept the unchanged control, pass focused builder tests and pass the
complete existing Kiota suite. All bytes and expected results are frozen in
`acceptance-fixtures.json`.

No checker was launched, no build ran, no production source changed, no
scientific fixture byte was generated, and no network, catalog or external
action occurred. This item completes a local source-bound design; it does not
claim runtime success, a universal format rule, checker soundness or current-tip
behavior. Production work remains separately gated under
`KIOTA-RECURSOR-TYPE-REPAIR-1`.
