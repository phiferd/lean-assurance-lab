"""Closure regressions for the bounded child-panic source-materialization stop."""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/survivor-thread-one-child-panic-regression-1"


class SourceMaterializationClosureTests(unittest.TestCase):
    def test_pinned_main_requires_readme_missing_from_frozen_inventory(self):
        main = (ROOT / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src/main.rs").read_text(encoding="utf-8")
        lock = json.loads((ROOT / "results/research/alt-survivors-2026-09-08/source-lock.json").read_text(encoding="utf-8"))
        paths = {row["source_path"] for row in lock["files"]}
        self.assertIn('include_str!("../README.md")', main)
        self.assertNotIn("README.md", paths)

    def test_real_baseline_build_preserves_complete_supervision_receipts(self):
        attempt = BASE / "run-0001-r2/attempts/01"
        supervisor = json.loads((attempt / "supervisor.json").read_text(encoding="utf-8"))
        stderr = (attempt / "process.stderr").read_text(encoding="utf-8")
        self.assertEqual(supervisor["exit_code"], 101)
        self.assertFalse(supervisor["timed_out"])
        self.assertTrue(supervisor["cleanup_complete"])
        self.assertIsNone(supervisor["memory_monitor_error"])
        self.assertIn("couldn't read `src/../README.md`", stderr)

    def test_r1_incident_preceded_any_supervised_process(self):
        repair = json.loads((BASE / "tooling-repair-0001.json").read_text(encoding="utf-8"))
        self.assertFalse(repair["no_process_evidence"]["cargo_or_checker_process_invoked"])
        self.assertFalse(repair["no_process_evidence"]["supervisor_receipt_exists"])


if __name__ == "__main__":
    unittest.main()
