"""The portability gate must notice new process evidence automatically."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from lib import evidence_replay_portability as audit


ROOT = Path(__file__).resolve().parents[1]


class EvidenceReplayInventoryTests(unittest.TestCase):
    def test_repository_receipts_and_registered_replay_tests_are_current(self):
        result = audit.validate(ROOT)
        self.assertEqual(result["families"], 18)
        self.assertGreater(result["raw_streams"], 600)

    def test_new_family_cannot_enter_without_portable_replay(self):
        groups, _ = audit.discover(ROOT)
        registry = json.loads((ROOT / "config/evidence-replay-portability.json").read_text())
        new_groups = {**groups, "new-process-family": [
            "results/research/new-process-family/attempt-0001/receipt.json",
        ]}
        with self.assertRaisesRegex(ValueError, "unregistered receipt families"):
            audit.validate_registration(ROOT, new_groups, registry)
        changed = copy.deepcopy(registry)
        new_paths = new_groups["new-process-family"]
        changed["families"].append({
            "id": "new-process-family",
            "receipt_files": 1,
            "paths_sha256": sha256(("\n".join(new_paths) + "\n").encode()).hexdigest(),
            "replay_test": "test_evidence_replay_inventory.EvidenceReplayInventoryTests.test_repository_receipts_and_registered_replay_tests_are_current",
            "portability_test": None,
        })
        changed["families"].sort(key=lambda row: row["id"])
        with self.assertRaisesRegex(ValueError, "needs a portability test"):
            audit.validate_registration(ROOT, new_groups, changed)

    def test_recorded_host_identity_is_data_and_raw_tampering_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "evidence/raw.stdout"
            raw.parent.mkdir()
            raw.write_bytes(b"accepted\n")
            receipt = {
                "cwd": "/original/mac/checkout",
                "argv": ["/original/mac/python3", "checker.py"],
                "exit_code": 0,
                "raw_stdout_path": "evidence/raw.stdout",
                "stdout_sha256": sha256(raw.read_bytes()).hexdigest(),
                "stdout_bytes": len(raw.read_bytes()),
            }
            streams, roots = audit.validate_raw_custody(root, [("receipt.json", receipt)])
            self.assertEqual((streams, roots), (1, {"/original/mac/checkout"}))
            raw.write_bytes(b"rejected\n")
            with self.assertRaisesRegex(ValueError, "raw stream differs"):
                audit.validate_raw_custody(root, [("receipt.json", receipt)])


if __name__ == "__main__":
    unittest.main()
