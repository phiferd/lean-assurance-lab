import tempfile
import unittest
from pathlib import Path

from lib.survivor_universe_diff import ordered, validate


class SourceOrderTests(unittest.TestCase):
    def test_ordered_accepts_sequence(self):
        ordered("alpha beta gamma", ["alpha", "beta", "gamma"], "fixture")

    def test_ordered_rejects_missing_or_reordered_fragment(self):
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            ordered("beta alpha", ["alpha", "beta"], "fixture")


class RepositoryEvidenceTests(unittest.TestCase):
    def test_current_reachability_result_validates(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate(root)["status"], "PASS")

    def test_missing_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                validate(Path(directory))


if __name__ == "__main__":
    unittest.main()
