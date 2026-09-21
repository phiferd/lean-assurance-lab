from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/source-lock-completeness-audit-1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SourceLockAuditClosureTests(unittest.TestCase):
    def test_ledger_has_exact_missing_readme_edge(self):
        audit = load(BASE / "run-0001/audit.json")
        self.assertEqual(audit["audit_revision"], "R3")
        self.assertEqual(audit["source_file_count"], 22)
        self.assertEqual(audit["directives"], [{
            "source_path": "src/main.rs", "macro": "include_str", "literal": "../README.md",
            "resolved_path": "README.md", "locked": False, "pinned_evidence_exists": False,
            "disposition": "MISSING_FROM_LOCK_AND_EVIDENCE"}])
        self.assertEqual(audit["missing"], audit["directives"])

    def test_result_binds_the_written_ledger(self):
        result = load(BASE / "result.json")
        audit = BASE / "run-0001/audit.json"
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(result["audit"], {
            "path": "results/research/source-lock-completeness-audit-1/run-0001/audit.json",
            "sha256": hashlib.sha256(audit.read_bytes()).hexdigest()})

    def test_preserved_repairs_are_not_scientific_processes(self):
        result = load(BASE / "result.json")
        self.assertEqual(result["attempt_accounting"]["builds"], 0)
        self.assertEqual(result["attempt_accounting"]["checkers"], 0)
        self.assertEqual(result["attempt_accounting"]["network_requests"], 0)
        self.assertEqual(result["attempt_accounting"]["external_actions"], 0)


if __name__ == "__main__":
    unittest.main()
