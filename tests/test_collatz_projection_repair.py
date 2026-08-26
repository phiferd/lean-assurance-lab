import importlib.machinery
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collatz-retrospective-projection-repair"


def load_repair_module():
    loader = importlib.machinery.SourceFileLoader("collatz_projection_repair_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


REPAIR = load_repair_module()


class CollatzProjectionRepairCoverageTests(unittest.TestCase):
    def test_extracts_target_counts_by_relative_suffix(self):
        export = {
            "data": [
                {
                    "files": [
                        {
                            "filename": "/old/checkout/nanoda/src/tc.rs",
                            "segments": [
                                [868, 1, 7, True, True, False],
                                [869, 5, 1, True, True, False],
                                [870, 15, 0, True, True, False],
                                [875, 18, 2, True, True, False],
                            ],
                        }
                    ]
                }
            ]
        }

        filename, covered = REPAIR.extract_target_coverage(
            export, "src/tc.rs", set(range(869, 877))
        )

        self.assertEqual(filename, "/old/checkout/nanoda/src/tc.rs")
        self.assertEqual(covered, [869, 875])

    def test_rejects_missing_target_source(self):
        export = {
            "data": [
                {"files": [{"filename": "/old/checkout/nanoda/src/env.rs", "segments": []}]}
            ]
        }

        with self.assertRaisesRegex(REPAIR.CoverageExtractionError, "expected one LLVM coverage file"):
            REPAIR.extract_target_coverage(export, "src/tc.rs", {869})

    def test_rejects_ambiguous_target_source(self):
        export = {
            "data": [
                {
                    "files": [
                        {"filename": "/one/src/tc.rs", "segments": [[869, 1, 1, True]]},
                        {"filename": "/two/src/tc.rs", "segments": [[869, 1, 1, True]]},
                    ]
                }
            ]
        }

        with self.assertRaisesRegex(REPAIR.CoverageExtractionError, "found 2"):
            REPAIR.extract_target_coverage(export, "src/tc.rs", {869})

    def test_rejects_source_map_without_target_segments(self):
        export = {
            "data": [
                {
                    "files": [
                        {"filename": "/old/checkout/nanoda/src/tc.rs", "segments": [[100, 1, 1, True]]}
                    ]
                }
            ]
        }

        with self.assertRaisesRegex(REPAIR.CoverageExtractionError, "no target-line segments"):
            REPAIR.extract_target_coverage(export, "src/tc.rs", {869})


if __name__ == "__main__":
    unittest.main()
