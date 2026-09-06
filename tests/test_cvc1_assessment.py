import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.cvc1_assessment import CVC_DIR, LIMITS, validate_cvc1_assessment

SCRIPT = ROOT / "scripts" / "validate-cvc1-assessment"


class Cvc1AssessmentTests(unittest.TestCase):
    def test_completed_repository_artifacts_validate(self):
        validate_cvc1_assessment(ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ("CONSTITUTION.md", "docs/RESEARCH_STATUS.md"):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(path)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "inputs"], check=True)
        self.commit = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.base = self.root / CVC_DIR
        self.base.mkdir(parents=True)
        self.write_valid()

    def tearDown(self):
        self.temp.cleanup()

    def sha(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()

    def write_json(self, name, value):
        (self.base / name).write_text(json.dumps(value, indent=2))

    def refresh_manifest(self):
        files = [{"path": str(CVC_DIR / name), "sha256": self.sha(CVC_DIR / name)} for name in ("work-record.json", "assessment.json", "report.md", "source-excerpts.json")]
        self.write_json("evidence-manifest.json", {"schema_version": 1, "item_id": "CVC-1", "files": files})

    def write_valid(self):
        inputs = [{"path": p, "sha256": self.sha(p)} for p in ("CONSTITUTION.md", "docs/RESEARCH_STATUS.md")]
        record = {
            "schema_version": 1, "item_id": "CVC-1", "status": "COMPLETE", "predecessor_commit": self.commit,
            "limits": LIMITS, "inputs": inputs,
            "sessions": [{"id": 1, "started_at": "2026-09-06T00:00:00+00:00", "ended_at": "2026-09-06T00:30:00+00:00", "active_minutes": 30}],
            "cumulative_active_minutes": 30,
            "queries": [{"id": "Q1", "session": 1, "reserved_at": "2026-09-06T00:01:00+00:00", "status": "COMPLETE", "query": "formal preservation"}],
            "sources": [{"id": "S1", "session": 1, "reserved_at": "2026-09-06T00:02:00+00:00", "status": "COMPLETE", "source_kind": "PAPER", "url": "https://github.com/example/repo", "question": "scope", "version": "v1", "claim": "bounded", "assumptions": ["local fixture"], "gap": "no remote observation", "reviewed_sections": ["section 1"], "content_identity": {"url": "https://example.invalid/paper", "sha256": "d" * 64, "bytes": 1, "retrieved_at": "2026-09-06T00:04:00+00:00"}}],
            "code_inspections": [{"id": "I1", "session": 1, "reserved_at": "2026-09-06T00:03:00+00:00", "status": "COMPLETE", "repository": "https://github.com/example/repo", "revision": "a" * 40, "declared_file_group": ["src/**"], "question": "scope", "source_id": "S1", "files": [{"path": "src/a", "url": "https://raw.githubusercontent.com/example/repo/" + "a" * 40 + "/src/a", "sha256": "b" * 64, "bytes": 1}]}],
            "execution_counts": {"builds": 0, "checker_launches": 0, "toolchain_installs": 0},
        }
        self.write_json("work-record.json", record)
        (self.base / "report.md").write_text("report")
        excerpt_text = "one\ntwo"
        self.write_json("source-excerpts.json", {"schema_version": 1, "item_id": "CVC-1", "excerpts": [{"id": "E1", "inspection_id": "I1", "path": "src/a", "source_sha256": "b" * 64, "start_line": 4, "end_line": 5, "text": excerpt_text, "sha256": hashlib.sha256(excerpt_text.encode()).hexdigest()}]})
        assessment = {"schema_version": 1, "item_id": "CVC-1", "outcome": "SUCCESS", "decision": "REUSE", "selected_fragment": "UNIVERSE_EXPRESSIONS", "comparisons": [{"fragment_id": x, "rank": i, "rationale": "bounded comparison", "gap": "fixture", "evidence_refs": [str(CVC_DIR / "report.md")]} for i, x in enumerate(["UNIVERSE_EXPRESSIONS", "RECURSOR_METADATA", "DECLARATION_IMPORT"], 1)], "source_ids": ["S1"], "evidence_refs": [str(CVC_DIR / "report.md")], "recommendation": {"action": "reuse", "target": "contract", "priority": 1, "prerequisites": [], "evidence_refs": [str(CVC_DIR / "source-excerpts.json")]}}
        self.write_json("assessment.json", assessment)
        self.refresh_manifest()

    def data(self, name):
        return json.loads((self.base / name).read_text())

    def assert_invalid(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            validate_cvc1_assessment(self.root)

    def test_valid_ledger_and_cli(self):
        validate_cvc1_assessment(self.root)
        result = subprocess.run(["python3", str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS")

    def test_budget_and_elapsed_time_tampering_fail(self):
        record = self.data("work-record.json"); record["limits"] = copy.deepcopy(LIMITS); record["limits"]["search_queries"] = 19; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("limits")
        self.write_valid(); record = self.data("work-record.json"); record["sessions"][0]["active_minutes"] = 29; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("active minutes")
        self.write_valid(); record = self.data("work-record.json"); record["limits"] = copy.deepcopy(LIMITS); record["limits"]["max_sessions"] = True; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("limits")
        self.write_valid(); record = self.data("work-record.json"); record["execution_counts"]["builds"] = False; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("permits no execution")

    def test_fabricated_initial_hash_and_source_linkage_fail(self):
        record = self.data("work-record.json"); record["inputs"][0]["sha256"] = "0" * 64; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("historical input")
        self.write_valid(); record = self.data("work-record.json"); record["code_inspections"][0]["source_id"] = "invented"; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("source_id")

    def test_modified_evidence_fails_manifest(self):
        (self.base / "report.md").write_text("tampered")
        self.assert_invalid("modified or missing evidence")

    def test_query_cap_nonfinite_accounting_and_file_bindings_fail(self):
        record = self.data("work-record.json")
        record["queries"] = [dict(record["queries"][0], id=f"Q{index}") for index in range(19)]
        self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("queries: exceeds")
        self.write_valid(); record = self.data("work-record.json"); record["cumulative_active_minutes"] = float("nan"); self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("cumulative")
        self.write_valid(); record = self.data("work-record.json"); record["code_inspections"][0]["files"][0]["path"] = "other/a"; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("outside declared")
        self.write_valid(); record = self.data("work-record.json"); record["code_inspections"][0]["files"][0]["url"] = "https://raw.githubusercontent.com/example/repo/" + "c" * 40 + "/src/a"; self.write_json("work-record.json", record); self.refresh_manifest(); self.assert_invalid("repository and revision")

    def test_excerpt_linkage_and_historical_successor_are_checked(self):
        excerpts = self.data("source-excerpts.json"); excerpts["excerpts"][0]["source_sha256"] = "c" * 64; self.write_json("source-excerpts.json", excerpts); self.refresh_manifest(); self.assert_invalid("does not bind")
        self.write_valid(); (self.root / "docs/RESEARCH_STATUS.md").write_text("mutable successor")
        validate_cvc1_assessment(self.root)


if __name__ == "__main__":
    unittest.main()
