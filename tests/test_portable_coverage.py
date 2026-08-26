from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from portable_coverage import (  # noqa: E402
    PortableCoverageError,
    VIRTUAL_CHECKER_ROOT,
    build_environment,
    canonical_coverage,
    validate_sentinel,
)


class PortableCoverageTests(unittest.TestCase):
    def test_encoded_rustflags_remap_checkout_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="portable coverage ") as temp_name:
            root = Path(temp_name)
            checker = root / "checkout with spaces"
            target = root / "target with spaces"
            checker.mkdir()
            env, flags = build_environment(checker, target)

        self.assertNotIn("RUSTFLAGS", env)
        self.assertEqual(env["CARGO_ENCODED_RUSTFLAGS"].split("\x1f"), flags)
        self.assertIn(f"{checker.resolve()}={VIRTUAL_CHECKER_ROOT}", flags)
        self.assertIn("codegen-units=1", flags)

    def test_coverage_is_canonicalized_to_relative_source_ids(self) -> None:
        export = {
            "data": [
                {
                    "files": [
                        {
                            "filename": "/different/local/root/src/tc.rs",
                            "segments": [[869, 5, 1, True], [870, 1, 0, True]],
                        },
                        {
                            "filename": "/different/local/root/src/env.rs",
                            "segments": [[10, 1, 2, True]],
                        },
                    ]
                }
            ]
        }

        embedded, covered = canonical_coverage(export, ["src/env.rs", "src/tc.rs"])

        self.assertEqual(embedded, "/different/local/root")
        self.assertEqual(covered, ["src/env.rs:10", "src/tc.rs:869"])

    def test_ambiguous_anchor_fails_closed(self) -> None:
        export = {
            "data": [
                {
                    "files": [
                        {"filename": "/one/src/tc.rs", "segments": [[1, 1, 1, True]]},
                        {"filename": "/two/src/tc.rs", "segments": [[1, 1, 1, True]]},
                    ]
                }
            ]
        }

        with self.assertRaisesRegex(PortableCoverageError, "expected one embedded checker root"):
            canonical_coverage(export, ["src/tc.rs"])

    def test_uncompiled_source_file_may_be_absent(self) -> None:
        export = {
            "data": [
                {
                    "files": [
                        {
                            "filename": "/portable/root/src/tc.rs",
                            "segments": [[869, 5, 1, True]],
                        }
                    ]
                }
            ]
        }

        embedded, covered = canonical_coverage(export, ["src/lib.rs", "src/tc.rs"])

        self.assertEqual(embedded, "/portable/root")
        self.assertEqual(covered, ["src/tc.rs:869"])

    def test_sentinel_fails_closed(self) -> None:
        rows = [{"test": "proj-of-prop", "covered": ["src/tc.rs:868"]}]

        with self.assertRaisesRegex(PortableCoverageError, "was not covered"):
            validate_sentinel(rows, "proj-of-prop", "src/tc.rs:869")


if __name__ == "__main__":
    unittest.main()
