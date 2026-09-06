import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.cvc2_contract import CVC_DIR, CVC1_DIR, FINAL_FILES, SIGNATURE, _git_blob, validate_cvc2_contract


class CVC2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        record = json.loads((ROOT / CVC_DIR / "work-record.json").read_text())
        cls.commit = record["predecessor_commit"]
        paths = {row["path"] for row in record["inputs"]} | {str(CVC1_DIR / "work-record.json")}
        # Read only the small committed predecessors, not a full repository copy.
        cls.blobs = {path: _git_blob(ROOT, cls.commit, path) for path in paths}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = {str(CVC1_DIR / "assessment.json"), str(CVC1_DIR / "source-excerpts.json"),
                  "corpus/generated/universe-imax-right-succ.ndjson",
                  "corpus/generated/universe-imax-right-succ-control.ndjson"}
        for path in FINAL_FILES | inputs:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        self.refresh_manifest()
        def historical(root, commit, path):
            self.assertEqual(commit, self.commit)
            return self.blobs[path]
        self.git = patch("lib.cvc2_contract._git_blob", side_effect=historical).start()
        self.addCleanup(patch.stopall)

    def read(self, name):
        return json.loads((self.root / CVC_DIR / name).read_text())

    def write(self, name, value):
        (self.root / CVC_DIR / name).write_text(json.dumps(value, indent=2) + "\n")

    def refresh_manifest(self):
        self.write("evidence-manifest.json", {
            "schema_version": 1, "item_id": "CVC-2", "files": [
                {"path": path, "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest()}
                for path in sorted(FINAL_FILES)
            ],
        })

    def assert_rejected(self, pattern=None, refresh=True):
        if refresh:
            self.refresh_manifest()
        if pattern is None:
            with self.assertRaises(ValueError):
                validate_cvc2_contract(self.root)
        else:
            with self.assertRaisesRegex(ValueError, pattern):
                validate_cvc2_contract(self.root)

    def rebind_signature(self, old, new):
        path = self.root / SIGNATURE
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for name in ["contract.json", "execution-protocol.json"]:
            data = self.read(name)
            data["signature"]["sha256"] = digest
            self.write(name, data)

    def test_completed_evidence_passes_without_running_inventory_commands(self):
        with patch("lib.cvc2_contract.subprocess.run", side_effect=AssertionError("unexpected execution")):
            validate_cvc2_contract(self.root)
        self.assertGreaterEqual(self.git.call_count, len(self.blobs))

    def test_manifest_detects_changed_omitted_and_duplicate_evidence(self):
        report = self.root / CVC_DIR / "report.md"
        report.write_text(report.read_text() + "\nchanged\n")
        self.assert_rejected("manifest content mismatch", refresh=False)
        self.refresh_manifest()
        original = self.read("evidence-manifest.json")
        for rows in [original["files"][:-1], original["files"] + [original["files"][0]]]:
            changed = copy.deepcopy(original)
            changed["files"] = rows
            self.write("evidence-manifest.json", changed)
            self.assert_rejected("manifest", refresh=False)

    def test_rehashed_raw_body_change_cannot_disguise_ast_replacement(self):
        examples = self.read("examples.json")
        binding = examples["examples"][0]["input_binding"]
        path = self.root / binding["path"]
        raw = path.read_bytes()
        path.write_bytes(raw.replace(b'"ie":1,"sort":5', b'"ie":1,"sort":4'))
        self.assertNotEqual(raw, path.read_bytes())
        self.assert_rejected("example input hash mismatch")
        binding["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write("examples.json", examples)
        self.assert_rejected("decoded supplied artifact AST")

    def test_rehashed_lean_example_body_change_is_rejected(self):
        self.rebind_signature('.imax (.param "u") (.succ (.param "v")),',
                              '.max (.param "u") (.succ (.param "v")),')
        self.assert_rejected("Lean example body mismatch")

    def test_rehashed_independent_meaning_ownership_and_target_changes_are_rejected(self):
        replacements = [
            ("if meaning ρ v = 0 then 0 else", "if meaning ρ v = 0 then 1 else"),
            ("| .param n => n ∈ params", "| .param n => True"),
            ("∀ a, Accepts a → Contract a", "∀ a, Contract a → Contract a"),
        ]
        original = (self.root / SIGNATURE).read_bytes()
        for old, new in replacements:
            with self.subTest(old=old):
                (self.root / SIGNATURE).write_bytes(original)
                self.rebind_signature(old, new)
                self.assert_rejected("signature target changed")

    def test_source_mapping_and_pin_tampering_are_rejected(self):
        original = self.read("contract.json")
        for key, value in [("revision", "0" * 40), ("excerpt_sha256", "0" * 64),
                           ("source_sha256", "0" * 64), ("start_line", 9)]:
            data = copy.deepcopy(original)
            target = data["source_mappings"][0]
            if key != "revision":
                target = target["excerpts"][0]
            target[key] = value
            self.write("contract.json", data)
            with self.subTest(key=key):
                self.assert_rejected("source")

    def test_session_bounds_and_consumed_counts_cannot_be_reset_or_promoted(self):
        original = self.read("work-record.json")
        mutations = [
            ("limits", "max_sessions", 3), ("consumed", "active_minutes", 0),
            ("consumed", "sessions", True), ("consumed", "proof_builds", 1),
            ("consumed", "checker_launches", 1), ("consumed", "toolchain_installs", 1),
        ]
        for section, key, value in mutations:
            data = copy.deepcopy(original)
            data[section][key] = value
            self.write("work-record.json", data)
            with self.subTest(section=section, key=key):
                self.assert_rejected()
        data = copy.deepcopy(original)
        data["sessions"][0]["active_minutes"] = float("inf")
        self.write("work-record.json", data)
        self.assert_rejected()
        data = copy.deepcopy(original)
        data["sessions"][0]["ended_at"] = data["sessions"][0]["started_at"]
        self.write("work-record.json", data)
        self.assert_rejected("session active minutes")

    def test_future_protocol_limits_execution_and_required_results_are_fixed(self):
        original = self.read("execution-protocol.json")
        for section, key, value in [
            ("limits", "proof_build_attempts", 13), ("limits", "attempt_timeout_seconds", 301),
            ("limits", "checker_launches", 1), ("limits", "network_requests_during_attempts", 1),
            ("current_execution", "runner_implemented", True),
            ("current_execution", "proof_attempts", 1),
            ("signature_attempt", "attempt_number", 0),
            ("signature_attempt", "argv", []),
            ("preparation_accounting", "lab_elaboration_permitted", True),
            ("preparation_accounting", "aggregate_cost_reporting_required", False),
        ]:
            data = copy.deepcopy(original)
            data[section][key] = value
            self.write("execution-protocol.json", data)
            with self.subTest(section=section, key=key):
                self.assert_rejected()
        data = copy.deepcopy(original)
        data["required_result_declarations"].pop()
        self.write("execution-protocol.json", data)
        self.assert_rejected("required result declarations")

    def test_claim_runtime_availability_and_axiom_promotions_are_rejected(self):
        edits = [
            ("contract.json", ["scientific_status"], "PROVED"),
            ("contract.json", ["strategies"], []),
            ("examples.json", ["required_acceptance_ids"], ["E-POS"]),
            ("runtime-inventory.json", ["entry_gate_satisfied"], True),
            ("runtime-inventory.json", ["scientific_status"], "VERIFIED_RUNTIME"),
            ("runtime-inventory.json", ["other_execution_counts", "lean_executions"], 1),
            ("assumptions.json", ["conditional_axiom_policy", "source_helpers_allowed"], ["sorryAx"]),
            ("assumptions.json", ["proof_runtime", "status"], "AVAILABLE"),
        ]
        for name, keys, value in edits:
            original = self.read(name)
            data = copy.deepcopy(original)
            target = data
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value
            self.write(name, data)
            with self.subTest(name=name, keys=keys):
                self.assert_rejected()
            self.write(name, original)

    def test_fixed_boundary_shape_and_example_inventory_are_required(self):
        original = self.read("examples.json")
        data = copy.deepcopy(original)
        data["examples"][2]["artifact"]["value_level"][0] = "max"
        self.write("examples.json", data)
        self.assert_rejected("fixed example AST")
        data = copy.deepcopy(original)
        data["examples"][-1] = copy.deepcopy(data["examples"][0])
        self.write("examples.json", data)
        self.assert_rejected("exactly four")

    def test_historical_successor_state_may_change_but_bound_inputs_may_not(self):
        for path in ["docs/RESEARCH_STATUS.md", "config/research-queue.json"]:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Successor state has changed.\n")
        validate_cvc2_contract(self.root)
        record = self.read("work-record.json")
        record["inputs"][0]["sha256"] = "0" * 64
        self.write("work-record.json", record)
        self.assert_rejected("historical input hash mismatch")

    def test_unsafe_bindings_malformed_json_and_missing_evidence_fail_cleanly(self):
        original = self.read("contract.json")
        for value in ["../escape.lean", "/tmp/escape.lean"]:
            data = copy.deepcopy(original)
            data["signature"]["path"] = value
            self.write("contract.json", data)
            self.assert_rejected("unsafe path")
        self.write("contract.json", original)
        path = self.root / CVC_DIR / "contract.json"
        path.write_text('{"schema_version":1,"schema_version":1}')
        self.assert_rejected("duplicate JSON key")
        self.write("contract.json", original)
        path.unlink()
        self.assert_rejected("invalid or unavailable", refresh=False)


if __name__ == "__main__":
    unittest.main()
