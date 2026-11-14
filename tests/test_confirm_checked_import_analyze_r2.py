import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "results/research/confirm-checked-import-cases-1"
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("analyze_r2", HERE / "analyze_r2.py")
analyze_r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_r2)


class AnalyzerRevisionTests(unittest.TestCase):
    def test_accepts_both_docker_absence_spellings_and_empty_array_stdout(self):
        receipt = {"exit_code": 1}
        self.assertTrue(analyze_r2.absence_proven(receipt, "[]\n", "Error: No such container: x\n"))
        self.assertTrue(analyze_r2.absence_proven(receipt, "", "Error: No such object: x\n"))

    def test_rejects_success_or_unrelated_failure(self):
        self.assertFalse(analyze_r2.absence_proven({"exit_code": 0}, "[]\n", ""))
        self.assertFalse(analyze_r2.absence_proven({"exit_code": 1}, "[]\n", "permission denied\n"))


if __name__ == "__main__":
    unittest.main()
