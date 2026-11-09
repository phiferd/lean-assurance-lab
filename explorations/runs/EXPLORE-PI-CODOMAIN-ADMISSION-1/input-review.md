# Pi codomain input review — 2026-11-09

**What did we find?** Four closed, sort-only raw definitions decode to the
fixed A/B control and negative trees. Each negative replaces only the Pi
codomain `Sort 1` with the closed, well-typed lambda `F`; the other member of
its pair is unchanged. The independent audit passed. No checker case ran.

**Is it interesting?** Yes. `F : (forall (_ : Sort 1), Sort 1)`; that inferred
type is a Pi, not a sort. The Pi with codomain `F` therefore fails formation.
In contrast, the Pi with codomain `Sort 1` has type `Sort 2`. The A control's
lambda has exactly that Pi type, and the B control's value has declared type
`Sort 2`. These derivations explain the expected outcomes without treating
checker agreement as authority.

**Does it require more work?** Register the E0 start and run the eight fixed
cells through the bound supervisor, then classify the first attributable
admission stage. A parser refusal, unrelated panic, missing declaration
identity or cleanup failure is not a valid negative rejection.

The task-local `audit.py` independently decodes 3.1.0 records and verifies one
safe ordinary definition per file, exact tree and metadata, closed binder
syntax, no constants or applications, the two codomain-only changes, all four
Nanoda configs, SHA-256 identities and a restricted typing derivation. The
generator, decoder, source and runtime hashes are bound in `protocol.json`.
The retained container's four runtime/importer hashes match the preceding
screen. Its inspected network map is empty; memory, CPU, PID and security
limits match the prior isolated setup. The bound Lean importer will print
parsed constructors before trust-0 replay. Nanoda's parser shape is supported
by pinned source and byte-identical staged inputs; no independent Nanoda AST
trace is claimed.

Current upstream Lean tip `e5723d5b311aa9151b38e2baaa59f08f004a19e9`
changes neither the relevant `type_checker.cpp` nor `environment.cpp` blob
from the intake. Current Nanoda tip remains
`0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929`. The experiment will measure
the older exact runnable Lean 4.34.1 and Nanoda `3a240721` profiles. It will
not claim runtime behavior of the newer source tips.
