"""Retained source bytes must match the pinned lazy-observer comparison."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/workflow-closure-automation-1/observer-comparison"


class LazyObserverSourceInventoryTests(unittest.TestCase):
    def test_complete_declared_source_matches_hashes_and_git_blobs(self):
        inventory_path = BASE / "source-inventory.json"
        inventory = json.loads(inventory_path.read_text())
        comparison = json.loads((BASE / "comparison.json").read_text())
        binding = comparison["candidate"]["source_inventory"]
        raw_inventory = inventory_path.read_bytes()
        self.assertEqual(binding["bytes"], len(raw_inventory))
        self.assertEqual(binding["sha256"], hashlib.sha256(raw_inventory).hexdigest())
        entries = inventory["source_entries"]
        self.assertEqual(len(entries), 24)
        paths = [row["path"] for row in entries]
        self.assertEqual(len(paths), len(set(paths)))
        for row in entries:
            with self.subTest(path=row["path"]):
                source = ROOT / row["path"]
                self.assertTrue(source.is_file())
                raw = source.read_bytes()
                self.assertEqual(row["bytes"], len(raw))
                self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())
                blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
                self.assertEqual(row["git_blob"], hashlib.sha1(blob).hexdigest())


if __name__ == "__main__":
    unittest.main()
