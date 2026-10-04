Adds a direct regression for the projection congruence path introduced in #23. The target case uses the same valid field index and the same well-typed structure with different projection type names, and requires `def_eq` to reject the pair. Neighboring controls cover same-name equality and different-index inequality.

This is test-only. It does not claim a current Nanoda defect.

Validation:

- `cargo test tests::util::projection_type_name_participates_in_def_eq -- --exact`
- `cargo test` (45 passed; 8 existing doc tests ignored)
- An exact sensitivity check in Lean Assurance Lab removed only the projection type-name comparison; the target assertion then failed.

Developed with AI assistance through Lean Assurance Lab. [Experiment and validation evidence](https://github.com/phiferd/lean-assurance-lab/tree/main/explorations/runs/EXPLORE-NANODA-PROJECTION-IDENTITY-REGRESSION-1)
