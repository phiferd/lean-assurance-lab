# Proposed title

test: cover String reconstruction shape and configuration boundaries

# Proposed body

Add two tests for `TcCtx::str_lit_to_constructor`. They cover all four Nat/String
extension settings with cached constructor names present or absent, using the
existing empty export fixture and configuring each DAG before construction.

With both extensions and the required names, the tests inspect the complete
`String.ofList` / `List.cons` / `Char.ofNat` / `List.nil` expression: constructor
names, argument counts, universe levels, scalar order, and list termination.
The fixed inputs are an empty string and `Aé𝄞`, whose expected scalars are
`65, 233, 119070`. This protects against accidentally using UTF-8 bytes or UTF-16
code units, reversing characters, or changing the constructor structure.

The remaining configurations require `None` from reconstruction. Raw String
literal construction is checked separately, so String-only construction cannot
be mistaken for successful reconstruction. Fixture assertions distinguish cached
names from declarations: the declaration map remains empty in every case.

This test-only patch exercises an internal expression-shape contract. It does
not establish declaration validity, semantic equivalence, or a current defect.
The missing-name control removes all required names together; it does not isolate
each individual missing-name branch.

Validation on Nanoda `4c544ed4099c8227f07d5de77ad1e69fb0740a27`:

- `cargo test --offline --locked string_reconstruction -- --nocapture`: 2 passed.
- `cargo test --offline --locked -- --nocapture`: all 40 library tests passed;
  the binary suite has no tests and eight existing doc examples remain ignored.
