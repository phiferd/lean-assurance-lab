# Nanoda Quotient Primitive Type Contract Family

Four Nanoda mutants skip exact expected-type assertions for serialized quotient
primitives. A source-derived candidate for each primitive replaces only its
canonical type expression with an in-scope sort expression and truncates the
export immediately after the target primitive.

| Primitive | Mutant | Candidate change | Nanoda baseline / mutant | Official / Kiota / Lean4Lean |
| --- | --- | --- | --- | --- |
| `Quot` | `nanoda-gen-7b386d7135bb` | type `43` to `17` (`Sort u`) | REJECT / ACCEPT | ACCEPT / ACCEPT / ACCEPT |
| `Quot.mk` | `nanoda-gen-962509604870` | type `49` to `17` (`Sort u`) | REJECT / ACCEPT | ACCEPT / ACCEPT / ACCEPT |
| `Quot.lift` | `nanoda-gen-5dd8a3776055` | type `69` to `50` (`Sort v`) | REJECT / ACCEPT | ACCEPT / ACCEPT / ACCEPT |
| `Quot.ind` | `nanoda-gen-cdebd265971c` | type `86` to `17` (`Sort u`) | REJECT / ACCEPT | ACCEPT / ACCEPT / ACCEPT |

Every canonical control is accepted by both Nanoda builds. Official Lean is the
designated reference and establishes expected `ACCEPT` separately for each
candidate hash; Kiota and Lean4Lean confirm all four outcomes.

These mutants are `REFERENCE_ALIGNED`. The evidence demonstrates a consistent
contract difference: Nanoda treats the serialized types of quotient primitive
records as fixed and authoritative, while the other three tested checkers do
not reject these altered fields. This should be discussed as one contract issue,
not four implementation bugs or four separate reports.

The two remaining quotient-related survivors check the pre-existing `Eq` and
`Eq.refl` declarations when `Quot.lift` is processed. They require separate
whole-checker redundancy analysis because those declarations are already
validated as an inductive and constructor.
