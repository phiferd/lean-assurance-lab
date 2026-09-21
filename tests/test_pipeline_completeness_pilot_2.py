from __future__ import annotations

import tempfile
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from lib import pipeline_completeness_pilot_2 as p


class PipelineCompletenessPilot2Tests(unittest.TestCase):
    def test_attempt_allocator_never_overwrites_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / p.BASE / "preflight-run-0001").mkdir(parents=True)
            with patch.object(p, "ROOT", root):
                index, run, workspace = p._next_attempt("preflight")
            self.assertEqual(index, 2)
            self.assertTrue(str(run).endswith("preflight-run-0002"))
            self.assertTrue(str(workspace).endswith("preflight-0002"))

    def test_workspace_controls_leave_manifest_to_lake(self):
        controls = p.workspace_control_files()
        self.assertEqual(set(controls), {"lean-toolchain", "lakefile.toml"})
        self.assertNotIn("lake-manifest.json", controls)

    def test_fixed_matrix_has_eight_cells(self):
        self.assertEqual(len(p.expected_matrix()), 8)

    def test_three_field_file_binding_is_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence.txt"
            path.write_bytes(b"evidence")
            row = {"path": "evidence.txt", "bytes": 8,
                   "sha256": hashlib.sha256(b"evidence").hexdigest()}
            with patch.object(p, "ROOT", root):
                self.assertEqual(p._verify_binding(row), path)
                row["bytes"] = 7
                with self.assertRaisesRegex(ValueError, "byte count differs"):
                    p._verify_binding(row)


if __name__ == "__main__":
    unittest.main()
