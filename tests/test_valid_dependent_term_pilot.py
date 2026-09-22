from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib import valid_dependent_term_pilot as pilot


META = {
    "meta": {
        "exporter": {"name": "lean4export", "version": "3.1.0"},
        "format": {"version": "3.1.0"},
        "lean": {"githash": "lean-revision", "version": "4.29.1"},
    }
}


def export_bytes(*rows: dict) -> bytes:
    return b"".join(pilot.canonical_bytes(row, newline=True) for row in (META, *rows))


def simple_export(*, body: dict | None = None, binder_info: str = "default",
                  nondep: bool = False) -> bytes:
    expression = body or {
        "ie": 1,
        "forallE": {"name": 3, "type": 0, "body": 0, "binderInfo": binder_info},
    }
    return export_bytes(
        {"in": 1, "str": {"pre": 0, "str": "ValidDependentTermPilot1"}},
        {"in": 2, "str": {"pre": 1, "str": "pi01"}},
        {"in": 3, "str": {"pre": 0, "str": "x"}},
        {"il": 1, "succ": 0},
        {"ie": 0, "sort": 0},
        expression,
        {"ie": 2, "sort": 1},
        {"def": {"all": [2], "hints": "opaque", "levelParams": [], "name": 2,
                 "safety": "safe", "type": 2, "value": 1}},
    )


def design() -> dict:
    return {
        "case_contract": {"order": ["pi", "lambda", "application", "let", "mixed"]},
        "producer_profile": {"lean_revision": "lean-revision"},
        "observer_profiles": [{"id": "official-lean-4.33.0"}, {"id": "nanoda-6ae1f0c"}],
    }


def case() -> dict:
    return {
        "case_id": "vdtp1-pi-01", "category": "pi", "category_index": 1,
        "term": {"tag": "pi", "domain": {"tag": "sort", "level": 0},
                 "body": {"tag": "sort", "level": 0}},
        "expected_type_nf": {"tag": "sort", "level": 1},
        "derivation": {"fake": True},
    }


class ExportBridgeTests(unittest.TestCase):
    def test_reconstructs_exact_closed_fragment(self):
        graph = pilot.ExportGraph(simple_export(), lean_revision="lean-revision",
                                  expected_name="ValidDependentTermPilot1.pi01")
        receipt = graph.checked_receipt(
            case(), case_binding={"path": "case", "bytes": 1, "sha256": "0" * 64},
            audit_binding={"path": "audit", "bytes": 1, "sha256": "1" * 64},
            source_binding={"path": "source", "bytes": 1, "sha256": "2" * 64},
            export_binding={"path": "export", "bytes": 1, "sha256": "3" * 64})
        self.assertEqual(receipt["reconstructed_value_sha256"],
                         pilot.object_sha256(case()["term"]))
        self.assertEqual(receipt["reconstructed_type_sha256"],
                         pilot.object_sha256(case()["expected_type_nf"]))
        self.assertTrue(receipt["fragment_proof"]["closed_bound_variables"])

    def test_existing_let_fixture_rehydrates_without_generator_helpers(self):
        path = pilot.ROOT / "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson"
        graph = pilot.ExportGraph(path.read_bytes(),
                                  lean_revision="f72c35b3f637c8c6571d353742168ab66cc22c00",
                                  expected_name="EcosystemCase")
        declaration = graph.declaration
        assert declaration is not None
        self.assertEqual(
            graph.expression(declaration["value"]),
            {"tag": "let", "type": {"tag": "sort", "level": 1},
             "value": {"tag": "sort", "level": 0},
             "body": {"tag": "bvar", "index": 0}})

    def test_rejects_forbidden_expression_tag(self):
        bad = simple_export(body={"ie": 1, "const": {"name": 2, "us": []}})
        with self.assertRaisesRegex(pilot.BridgeError, "forbidden expression tag"):
            pilot.ExportGraph(bad, lean_revision="lean-revision",
                              expected_name="ValidDependentTermPilot1.pi01")

    def test_rejects_nondefault_binder(self):
        with self.assertRaisesRegex(pilot.BridgeError, "binder info"):
            pilot.ExportGraph(simple_export(binder_info="implicit"),
                              lean_revision="lean-revision",
                              expected_name="ValidDependentTermPilot1.pi01")

    def test_rejects_loose_bound_variable(self):
        graph = pilot.ExportGraph(
            simple_export(body={"ie": 1, "bvar": 0}), lean_revision="lean-revision",
            expected_name="ValidDependentTermPilot1.pi01")
        assert graph.declaration is not None
        with self.assertRaisesRegex(pilot.BridgeError, "loose bound variable"):
            graph.expression(graph.declaration["value"])

    def test_rejects_duplicate_json_key(self):
        data = b'{"meta":{"exporter":{},"exporter":{}}}\n'
        with self.assertRaisesRegex(pilot.BridgeError, "duplicate JSON key"):
            pilot.ExportGraph(data, lean_revision="lean-revision", expected_name="x")

    def test_rejects_let_nondep_true(self):
        row = {"ie": 1, "letE": {"name": 3, "type": 0, "value": 0, "body": 0,
                                   "nondep": True}}
        with self.assertRaisesRegex(pilot.BridgeError, "nondep"):
            pilot.ExportGraph(simple_export(body=row), lean_revision="lean-revision",
                              expected_name="ValidDependentTermPilot1.pi01")


class ControllerContractTests(unittest.TestCase):
    def test_generator_public_renderer_handles_a_fake_development_case(self):
        from lib.valid_dependent_term_generator import render_module
        source = render_module([case()])
        self.assertIn("namespace ValidDependentTermPilot1", source)
        self.assertIn("def pi01 : Sort 1 := (forall (x0 : Sort 0), Sort 0)", source)

    def test_matrix_is_profile_major_and_exactly_one_hundred_cells(self):
        artifacts = {
            f"vdtp1-{category}-{index:02d}": {
                "path": f"fake/{category}-{index:02d}.ndjson", "bytes": 1, "sha256": "0" * 64}
            for category in ("pi", "lambda", "application", "let", "mixed")
            for index in range(1, 11)
        }
        matrix = pilot.ordered_matrix(design(), artifacts)
        self.assertEqual(len(matrix), 100)
        self.assertEqual(matrix[0]["cell_id"], "official-lean-4.33.0::vdtp1-pi-01")
        self.assertEqual(matrix[49]["cell_id"], "official-lean-4.33.0::vdtp1-mixed-10")
        self.assertEqual(matrix[50]["cell_id"], "nanoda-6ae1f0c::vdtp1-pi-01")
        self.assertEqual(matrix[-1]["ordinal"], 100)

    def test_validate_only_never_calls_process_runner(self):
        fake_design = {"item_id": pilot.ITEM}
        with patch.object(pilot, "_validate_design", return_value=fake_design), \
             patch.object(pilot, "_selected_active"), \
             patch.object(pilot, "_committed_inputs"), \
             patch.object(pilot, "_external_environment", return_value={}), \
             patch.object(pilot, "file_sha256", return_value="0" * 64), \
             patch.object(pilot, "run_supervised", side_effect=AssertionError("launched")):
            with tempfile.TemporaryDirectory() as directory:
                result = pilot.validate_preparation(root=Path(directory), require_commit=False)
        self.assertEqual(result["scientific_processes_launched"], 0)

    def test_execution_validate_only_never_calls_process_runner(self):
        fake_design = {"item_id": pilot.ITEM}
        fake_corpus = {"case_count": 50}
        fake_execution = {"matrix": [{}] * 100}
        with patch.object(pilot, "_selected_active"), \
             patch.object(pilot, "_committed_inputs"), \
             patch.object(pilot, "_validate_manifests",
                          return_value=(fake_design, fake_corpus, fake_execution)), \
             patch.object(pilot, "file_sha256", return_value="0" * 64), \
             patch.object(pilot, "run_supervised", side_effect=AssertionError("launched")):
            result = pilot.validate_execution(require_commit=False)
        self.assertEqual(result["scientific_processes_launched"], 0)
        self.assertEqual(result["matrix_cells"], 100)

    def test_supervised_wrapper_persists_and_checks_fake_receipt(self):
        with tempfile.TemporaryDirectory(dir=pilot.ROOT) as directory:
            base = Path(directory)
            raw = base / "raw/process"
            receipt_path = base / "receipt.json"

            def fake_runner(**kwargs):
                prefix = kwargs["raw_prefix"]
                prefix.parent.mkdir(parents=True)
                stdout, stderr = b"ok\n", b""
                Path(str(prefix) + ".stdout").write_bytes(stdout)
                Path(str(prefix) + ".stderr").write_bytes(stderr)
                return {
                    "exit_code": 0, "timed_out": False, "elapsed_seconds": .01,
                    "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
                    "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
                    "memory_monitor_error": None, "memory_monitor_samples": 1,
                    "maximum_observed_rss_bytes": 4096, "memory_exceeded": False,
                    "cleanup_complete": True,
                }

            receipt, stdout, stderr = pilot._supervised(
                argv=["fake"], cwd=base, stdin=None, env={}, timeout_seconds=1,
                memory_bytes=1024, raw_prefix=raw, receipt_path=receipt_path,
                runner=fake_runner)
            self.assertEqual((stdout, stderr), (b"ok\n", b""))
            self.assertEqual(json.loads(receipt_path.read_text()), receipt)

    def test_safety_failures_are_repair_pauses(self):
        good = {"memory_monitor_error": None, "memory_monitor_samples": 1,
                "maximum_observed_rss_bytes": 1, "memory_exceeded": False,
                "timed_out": False, "cleanup_complete": True}
        for key, value in (("memory_monitor_error", "denied"),
                           ("memory_monitor_samples", 0),
                           ("maximum_observed_rss_bytes", 0),
                           ("memory_exceeded", True), ("timed_out", True),
                           ("cleanup_complete", False)):
            receipt = dict(good)
            receipt[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(pilot.PilotError, "repair|diagnose"):
                pilot._receipt_safe(receipt, "fake")

    def test_stale_binding_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "file"
            path.write_bytes(b"first")
            binding = pilot.file_binding(path, root)
            path.write_bytes(b"changed")
            with self.assertRaisesRegex(pilot.PilotError, "stale file binding"):
                pilot.verify_binding(binding, root)

    def test_process_receipt_replay_rejects_changed_raw_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_out, raw_err = root / "stdout", root / "stderr"
            raw_out.write_bytes(b"accepted\n")
            raw_err.write_bytes(b"")
            receipt_path = root / "receipt.json"
            receipt = {
                "raw_stdout_path": "stdout", "raw_stderr_path": "stderr",
                "stdout_bytes": raw_out.stat().st_size,
                "stderr_bytes": raw_err.stat().st_size,
                "stdout_sha256": pilot.file_sha256(raw_out),
                "stderr_sha256": pilot.file_sha256(raw_err),
            }
            receipt_path.write_bytes(pilot.canonical_bytes(receipt, newline=True))
            binding = pilot.file_binding(receipt_path, root)
            pilot._verify_process_receipt(binding, root)
            raw_out.write_bytes(b"changed\n")
            with self.assertRaisesRegex(pilot.PilotError, "raw stdout"):
                pilot._verify_process_receipt(binding, root)


if __name__ == "__main__":
    unittest.main()
