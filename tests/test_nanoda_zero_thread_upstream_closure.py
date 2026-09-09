import unittest
from pathlib import Path

from lib.nanoda_zero_thread_upstream_closure import validate, validate_source

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "results/research/nanoda-zero-thread-upstream-readiness-1/evidence/requests/source-archive/body"


class NanodaZeroThreadUpstreamClosureTests(unittest.TestCase):
    def test_retained_source_routes_zero_serially(self):
        result = validate_source(ARCHIVE.read_bytes())
        self.assertEqual(result["zero_thread_dispatch"], "SERIAL")
        self.assertEqual(result["head"], "05055695879dfebb6628a67da88ceca6cd6b0421")

    def test_complete_closure_passes(self):
        result = validate(ROOT)
        self.assertEqual(result["gate_decision"], "NO_GO")
        self.assertEqual(result["selected_item"], "SURVIVOR-CACHE-PREDICATE-TRANSFER-1")


if __name__ == "__main__":
    unittest.main()
