# 3. Lean expert: review the preserved-alias partial-constructor eta seam

Local task draft for owner review; unpublished and unassigned.

**Question:** In Lean PR15373 at `015d54649bcaaa0861f355b59761ce308e629fbb`, can a local variable's reducible function-type alias survive to the kernel's syntactic-Pi loop while the elaborator opens a reducing telescope?

**Prerequisites:** Familiarity with Lean expressions, local contexts and definitional equality; ability to read Lean/C++ source at a pinned revision. Read-only source access is sufficient for the first artifact. No build or checker launch is part of this task.

**Starting evidence:** `results/research/lean-eta-pilot-feasibility-1/assessment.md`, `docs/research/LEAN_ETA_ALIAS_PILOT_PREPARATION_1_PLAN.md`, pinned kernel `try_eta_struct_core` and Meta `ExprDefEq`. The candidate is nonrecursive `Box` with one Bool field, `FnAlias := Bool → Box`, and arbitrary local `f : FnAlias` compared with unapplied `Box.mk`. It is an unconfirmed source hypothesis. Known issue12520 and renovation14977 exclude a broad eta novelty claim.

**Expected artifact:** An annotated source map showing every normalization/type-inference step and a reviewed four-case prospective matrix: explicit/alias arbitrary-variable negatives; corresponding direct-versus-eta positive controls. Document the raw binder and constructor shapes needed for separate Meta and kernel observations. Inspect the named existing eta tests for this exact negative case and cite any duplicate.

**Go:** The alias remains `.const FnAlias`, the negative variable has no value, constructor has zero arguments, and the compared negative heads remain distinct/nonlambda. **Stop:** Normalization removes the seam, existing tests cover it, or a valued let/lambda/full application makes the route irrelevant. An unavailable exact pinned runner is a launch blocker, not permission to build; report it. No larger matrix or new scientific launch follows.

**Completion:** Reachability and expected fixtures are independently reviewed, or a concrete normalization/duplicate boundary is documented. Agreement is useful review, not dynamic confirmation. Any future four-case execution needs separate selection, exact identities and existing supervision; unexpected acceptance needs independent fixture validation before a defect claim.
