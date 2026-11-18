"""Replay both attempts at the three published rpylean cases in an isolated evidence tree."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib import published_rpylean_replay as evidence


ROOT = Path(__file__).resolve().parents[1]


class PublishedRpyleanReplayTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "foreign-checkout"
        self.base = self.root / evidence.BASE
        shutil.copytree(ROOT / evidence.BASE, self.base)

    def test_replay_from_foreign_checkout_without_checker(self):
        original_read = Path.read_bytes

        def read_from_copy(path):
            self.assertTrue(path.resolve().is_relative_to(self.root.resolve()))
            return original_read(path)

        with patch.object(Path, "read_bytes", read_from_copy), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("checker launch")):
            self.assertEqual(evidence.replay(self.root), {
                "processes": 6,
                "cases": {"bugs/rec-missing-ih": "reject", "bugs/rec-rule-wrong-arg": "reject",
                          "corner-cases/proof-param-ok": "accept"},
            })

    def test_rejects_modified_raw_stream(self):
        (self.base / "attempt-1/proof-param-ok/stderr.txt").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "evidence digest differs"):
            evidence.replay(self.root)

    def test_startup_error_cannot_supply_semantic_verdict(self):
        folder = self.base / "attempt-2/rec-missing-ih"
        raw = (self.base / "attempt-1/rec-missing-ih/stderr.txt").read_bytes()
        (folder / "stderr.txt").write_bytes(raw)
        path = folder / "receipt.json"
        receipt = json.loads(path.read_bytes())
        receipt["stderr_sha256"] = sha256(raw).hexdigest()
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "incomplete checker output"):
            evidence.replay(self.root)

    def test_reported_outcome_must_match_raw_evidence(self):
        path = self.base / "result.json"
        result = json.loads(path.read_bytes())
        result["cases"][0]["observed"] = "accept"
        path.write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, "result differs from saved processes"):
            evidence.replay(self.root)
