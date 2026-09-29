"""Freeze/launch ordering controls; no selected source is rendered here."""

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from lib import resource_envelope_construct as construction
from lib import resource_envelope_control as control
from lib.resource_envelope_producer import sha256
from lib.resource_envelope_supervisor import SupervisedResult


class ResourceEnvelopeControlTests(unittest.TestCase):
    def test_python_runtime_symlink_swap_and_target_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target_a, target_b = base / "python-a", base / "python-b"
            target_a.write_bytes(b"synthetic interpreter A")
            target_b.write_bytes(b"synthetic interpreter B")
            link = base / "python"
            link.symlink_to(target_a)
            science_path, execution_path, review_path = (base / name for name in
                                                         ("science.json", "execution.json", "review.json"))
            science = {"scientific_inputs": [], "source_files": [], "source_revisions": {}}
            science_path.write_text(json.dumps(science))
            with patch.object(control.sys, "executable", str(link)):
                identity = control._python_invocation_identity()
                with self.assertRaisesRegex(control.GateError, "missing/nonregular"):
                    control.binding(link)
                execution = {"execution_inputs": [], "runtime": [],
                             "scientific_manifest": control.binding(science_path),
                             "python_invocation": identity,
                             "option_transport_sources": [], "repair_history": {},
                             "construction_recursion_max_depth": control.CONSTRUCTION_RECURSION_LIMIT}
                execution_path.write_text(json.dumps(execution))
                review_path.write_text(json.dumps({
                    "verdict": "PASS_FOR_CONSTRUCTION",
                    "scientific_manifest_sha256": control.binding(science_path)["sha256"],
                    "execution_manifest_sha256": control.binding(execution_path)["sha256"]}))
                with patch.multiple(control, SCIENCE=science_path, EXECUTION=execution_path,
                                    PRECONSTRUCTION_REVIEW=review_path,
                                    OPTION_TRANSPORT_SOURCES=()), \
                     patch.object(control, "_active_frontier"), \
                     patch.object(control, "_committed"), \
                     patch.object(control, "_repair_history", return_value={}), \
                     patch.object(control, "_source_revisions", return_value={}):
                    control.require_construction_gate()
                    link.unlink()
                    link.symlink_to(target_b)
                    with self.assertRaisesRegex(control.GateError, "Python invocation"):
                        control.require_construction_gate()
                    link.unlink()
                    link.symlink_to(target_a)
                    target_a.write_bytes(b"changed interpreter A")
                    with self.assertRaisesRegex(control.GateError, "Python invocation"):
                        control.require_construction_gate()

    def test_empty_baseline_bytes_match_retained_metadata(self):
        prior = (control.ROOT /
                 "results/research/valid-dependent-term-pilot-1/prepare-run-0003/staged/exports/vdtp1-pi-01.ndjson")
        self.assertEqual(control.EMPTY_EXPORT, prior.read_bytes().splitlines(keepends=True)[0])
        self.assertEqual(len(control.EMPTY_EXPORT), 173)

    def test_active_queue_and_work_record_gate(self):
        valid_queue = {"selected_item": "RESOURCE-ENVELOPE-PILOT-1",
                       "items": [{"id": "RESOURCE-ENVELOPE-PILOT-1", "status": "ACTIVE"}]}
        valid_work = {"item_id": "RESOURCE-ENVELOPE-PILOT-1", "status": "ACTIVE"}
        with patch.object(control, "_committed"), \
             patch.object(control, "_read", side_effect=lambda path: valid_queue
                          if path.name == "research-queue.json" else valid_work):
            control._active_frontier()
        with patch.object(control, "_committed"), \
             patch.object(control, "_read", side_effect=lambda path: {"selected_item": "other", "items": []}
                          if path.name == "research-queue.json" else valid_work):
            with self.assertRaises(control.GateError):
                control._active_frontier()

    def test_construction_manifest_and_review_bindings_fail_closed(self):
        science = {"scientific_inputs": [], "source_files": [], "source_revisions": {}}
        execution = {"execution_inputs": [], "runtime": [],
                     "scientific_manifest": {"sha256": "stale"},
                     "python_invocation": {"synthetic": 1},
                     "option_transport_sources": [], "repair_history": {},
                     "construction_recursion_max_depth": control.CONSTRUCTION_RECURSION_LIMIT}
        review = {"verdict": "PASS_FOR_CONSTRUCTION",
                  "scientific_manifest_sha256": "science", "execution_manifest_sha256": "execution"}
        def fake_read(path):
            return {control.SCIENCE: science, control.EXECUTION: execution,
                    control.PRECONSTRUCTION_REVIEW: review}[path]
        def fake_binding(path):
            return {control.SCIENCE: {"sha256": "science"},
                    control.EXECUTION: {"sha256": "execution"}}[path]
        with patch.object(control, "_active_frontier"), patch.object(control, "_committed"), \
             patch.object(control, "_source_revisions", return_value={}), \
             patch.object(control, "_repair_history", return_value={}), \
             patch.object(control, "OPTION_TRANSPORT_SOURCES", ()), \
             patch.object(control, "_python_invocation_identity", return_value={"synthetic": 1}), \
             patch.object(control, "_read", side_effect=fake_read), \
             patch.object(control, "binding", side_effect=fake_binding):
            with self.assertRaisesRegex(control.GateError, "science binding"):
                control.require_construction_gate()
            execution["scientific_manifest"] = {"sha256": "science"}
            review["execution_manifest_sha256"] = "stale"
            with self.assertRaisesRegex(control.GateError, "independent construction review"):
                control.require_construction_gate()
            review["execution_manifest_sha256"] = "execution"
            execution["repair_history"] = {"stale": True}
            with self.assertRaisesRegex(control.GateError, "original construction attempt"):
                control.require_construction_gate()
            execution["repair_history"] = {}
            execution["construction_recursion_max_depth"] = 16384
            with self.assertRaisesRegex(control.GateError, "recursion setting"):
                control.require_construction_gate()

    def test_changed_bound_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.txt"
            path.write_bytes(b"original")
            locked = control.binding(path)
            path.write_bytes(b"changed")
            with self.assertRaisesRegex(control.GateError, "bound file changed"):
                control._check_binding(locked, committed=False)

    def test_construction_checks_review_before_render(self):
        with patch.object(construction, "require_construction_gate", side_effect=control.GateError("no review")), \
             patch.object(construction, "render_source", side_effect=AssertionError("selected render reached")):
            with self.assertRaisesRegex(control.GateError, "no review"):
                construction.construct()

    def test_construction_process_fault_is_repair(self):
        bad = SupervisedResult({"monitor_errors": ["synthetic"],
                                "pipe_errors": [], "accounting_error": None,
                                "reap_complete": True, "cleanup_complete": True,
                                "trace_gap_fault": False, "child_peak_rss_bytes": 10,
                                "stop_reason": None, "exit_code": 0}, b"", b"")
        with self.assertRaises(control.GateError):
            construction._safe_process(bad, "synthetic build")

    def test_workspace_templates_are_exact_bytes(self):
        self.assertEqual(control.LEAN_TOOLCHAIN, b"leanprover/lean4:v4.29.1\n")
        self.assertEqual(control.LAKEFILE, (
            b'name = "ResourceEnvelopePilot1"\n'
            b'defaultTargets = ["ResourceEnvelopePilot1"]\n\n'
            b'[leanOptions]\nmaxRecDepth = 8192\n\n'
            b'[[lean_lib]]\nname = "ResourceEnvelopePilot1"\n'))
        self.assertEqual(len(sha256(control.LAKEFILE)), 64)

    def test_repair_prefix_requires_byte_identity_not_python_equality(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "synthetic.source"
            original.write_bytes(b"1")
            execution = {"repair_history": {"completed_prefix": [
                {"id": "synthetic-case", "source": control.binding(original)}]}}
            construction._check_repair_prefix_bytes(execution, "synthetic-case", "source", b"1")
            with self.assertRaisesRegex(control.GateError, "changed R1 accepted bytes"):
                construction._check_repair_prefix_bytes(execution, "synthetic-case", "source", b"true")
            original.write_bytes(b"2")
            with self.assertRaisesRegex(control.GateError, "R1 file changed"):
                construction._check_repair_prefix_bytes(execution, "synthetic-case", "source", b"1")

    def test_build_setup_requires_exact_lake_option_transport(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            setup = workspace / ".lake/build/ir/ResourceEnvelopePilot1.setup.json"
            setup.parent.mkdir(parents=True)
            setup.write_text(json.dumps({"name": "ResourceEnvelopePilot1",
                                         "options": {"maxRecDepth": 8192}}))
            self.assertEqual(construction._check_build_setup(workspace), control.binding(setup))
            setup.write_text(json.dumps({"name": "ResourceEnvelopePilot1", "options": {}}))
            with self.assertRaisesRegex(control.GateError, "did not transport"):
                construction._check_build_setup(workspace)
            setup.write_text(json.dumps({"name": "ResourceEnvelopePilot1",
                                         "options": {"maxRecDepth": 8192, "extra": True}}))
            with self.assertRaisesRegex(control.GateError, "did not transport"):
                construction._check_build_setup(workspace)

    def test_pinned_lake_option_transport_chain(self):
        named = {"/".join(path.parts[-3:]): path.read_text()
                 for path in control.OPTION_TRANSPORT_SOURCES}
        self.assertIn('maxSynthPendingDepth = 3', named['Lake/CLI/Init.lean'])
        self.assertIn('def defaultMaxRecDepth := 512', named['lean/Init/Prelude.lean'])
        self.assertIn('register_builtin_option maxRecDepth : Nat', named['Lean/Util/RecDepth.lean'])
        self.assertIn('decodeLeanOptionsAux', named['Lake/Load/Toml.lean'])
        self.assertIn('self.config.leanOptions', named['Lake/Config/Package.lean'])
        self.assertIn('self.pkg.leanOptions', named['Lake/Config/LeanLib.lean'])
        self.assertIn('self.lib.leanOptions', named['Lake/Config/Module.lean'])
        self.assertIn('options := mod.leanOptions', named['Lake/Build/Module.lean'])


if __name__ == "__main__":
    unittest.main()
