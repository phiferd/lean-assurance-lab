from __future__ import annotations

import subprocess
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ValidDependentTermClosureTests(unittest.TestCase):
    def test_committed_closure_evidence(self):
        completed = subprocess.run(
            [str(ROOT / "scripts/validate-valid-dependent-term-pilot-closure")],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("100/100 ACCEPT", completed.stdout)


if __name__ == "__main__":
    unittest.main()
