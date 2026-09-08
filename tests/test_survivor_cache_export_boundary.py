import tempfile
import unittest
from pathlib import Path

from lib.survivor_cache_export_boundary import ordered_unique, validate


class SourceOrderTests(unittest.TestCase):
    def test_ordered_unique_accepts_exact_sequence(self):
        ordered_unique("alpha beta gamma", ["alpha", "beta", "gamma"], "fixture")

    def test_ordered_unique_rejects_reordering(self):
        with self.assertRaisesRegex(ValueError, "source order changed"):
            ordered_unique("beta alpha", ["alpha", "beta"], "fixture")

    def test_ordered_unique_rejects_duplicate_anchor(self):
        with self.assertRaisesRegex(ValueError, "not unique"):
            ordered_unique("alpha alpha beta", ["alpha", "beta"], "fixture")


class RepositoryEvidenceTests(unittest.TestCase):
    def test_current_boundary_validates(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate(root)["status"], "PASS")

    def test_missing_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                validate(Path(directory))


if __name__ == "__main__":
    unittest.main()
