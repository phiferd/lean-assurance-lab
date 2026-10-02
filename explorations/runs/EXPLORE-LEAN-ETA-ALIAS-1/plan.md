# Fixed four-case execution

Run `results/research/lean-eta-alias-pilot-preparation-1/prospective-cases.lean` once with the official PR15373 Linux toolchain under `linux/amd64`. The four logged cells are explicit-negative, alias-negative, explicit-constructor-positive and alias-constructor-positive. Kernel is observed before Meta inside each fresh local context. Expected results are false/false for both negatives and true/true for both positives.

Retain the official artifact digest, extracted runner identities, fixture assertions, raw output, supervisor receipt, Docker container limit and post-run absence. No other semantic case is in scope.
