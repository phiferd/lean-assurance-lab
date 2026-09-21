from __future__ import annotations

import tempfile
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


if __name__ == "__main__":
    unittest.main()
