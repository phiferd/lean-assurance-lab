import tempfile
import unittest
from pathlib import Path

from lib.survivor_universe_equivalence import ordered, validate


ROOT = Path(__file__).resolve().parents[1]


class SourceOrderTests(unittest.TestCase):
    def test_ordered_accepts_complete_sequence(self):
        ordered("alpha beta gamma", ["alpha", "beta", "gamma"], "fixture")

    def test_ordered_rejects_missing_or_reordered_fragment(self):
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            ordered("beta alpha", ["alpha", "beta"], "fixture")


class RepositoryEvidenceTests(unittest.TestCase):
    def test_scoped_equivalence_admission_validates(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["classification"],
                         "EQUIVALENT_AT_PUBLIC_LEVEL_COMPARISON_ENTRYPOINTS")
        self.assertEqual(result["private_counterexamples"], 2)
        self.assertEqual(result["registry_append_count"], 1)

    def test_missing_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises((FileNotFoundError, ValueError)):
                validate(Path(directory))


if __name__ == "__main__":
    unittest.main()
