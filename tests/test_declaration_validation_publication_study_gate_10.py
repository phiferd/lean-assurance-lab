import importlib.machinery
import importlib.util
import copy
import json
import unittest
import tempfile
import sys
from contextlib import ExitStack
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
loader = importlib.machinery.SourceFileLoader(
    "publication_study_gate10", str(ROOT / "scripts/publication_study_gate10.py")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
gate10 = importlib.util.module_from_spec(spec)
loader.exec_module(gate10)


class Gate10ConstructionMathTests(unittest.TestCase):
    def test_shift_preserves_bound_variables_and_shifts_outer_variables(self):
        # In the body of the lambda, bvar 0 is bound by that lambda while
        # bvar 1 refers to the surrounding context.
        expression = ("lam", ("sort", 0), ("pi", ("bvar", 0), ("bvar", 2)))
        self.assertEqual(
            gate10.shift(expression, 2),
            ("lam", ("sort", 0), ("pi", ("bvar", 0), ("bvar", 4))),
        )

    def test_infer_checks_nested_binder_scope_and_types_on_synthetic_ast(self):
        # forall (x : Prop), x -> x
        theorem_type = ("pi", ("sort", 0), ("pi", ("bvar", 0), ("bvar", 1)))
        # fun (x : Prop) (h : x) => h
        proof = ("lam", ("sort", 0), ("lam", ("bvar", 0), ("bvar", 0)))

        self.assertEqual(gate10.infer(theorem_type), ("sort", 0))
        self.assertEqual(gate10.infer(proof), theorem_type)

    def test_infer_rejects_loose_variable_and_non_sort_binder_domain(self):
        with self.assertRaisesRegex(ValueError, "loose bound variable"):
            gate10.infer(("bvar", 0))
        with self.assertRaisesRegex(ValueError, "binder domain is not sort-valued"):
            gate10.infer(("pi", ("lam", ("sort", 0), ("bvar", 0)), ("sort", 0)))


class Gate10NormalizationTests(unittest.TestCase):
    def test_timeout_crash_and_unknown_are_preserved_as_exceptional_outcomes(self):
        self.assertEqual(
            gate10.normalize("arena-nanoda", 0, b"", b"", timed_out=True)["outcome"],
            "TIMEOUT",
        )
        self.assertEqual(
            gate10.normalize("arena-nanoda", -9, b"", b"")["outcome"], "CRASH"
        )
        self.assertEqual(
            gate10.normalize("arena-nanoda", 1, b"generic failure", b"")["outcome"],
            "UNKNOWN",
        )

    def test_zero_declaration_success_is_not_attributed_acceptance(self):
        result = gate10.normalize(
            "arena-official-importer.lean4-4.33.0",
            0,
            b"Accepted 0 declarations.\n",
            b"",
        )
        self.assertEqual(result["outcome"], "UNKNOWN")
        self.assertEqual(result["pipeline_stage"], "UNKNOWN")

    def test_exact_named_nanoda_diagnostic_is_attributed_rejection(self):
        result = gate10.normalize(
            "arena-nanoda.6ae1f0c.default-four-thread",
            1,
            b"m6TransferNonPropTheorem must be `Prop` (sort 0)\n",
            b"",
        )
        self.assertEqual(result["outcome"], "REJECT")
        self.assertTrue(result["target_attributed"])


class Gate10ProtocolInputTests(unittest.TestCase):
    def test_protocol_inputs_validates_against_historical_gate9_bytes(self):
        with patch.object(gate10, "git_binding", wraps=gate10.git_binding) as bound:
            protocol, freeze, baseline = gate10.protocol_inputs(full_chain=False)

        self.assertEqual(protocol["run_id"], "publication-study-theorem-control-0001")
        self.assertIsInstance(freeze, dict)
        self.assertIsInstance(baseline, dict)
        expected = {
            gate10.PROTOCOL,
            "schemas/declaration-validation-publication-study-gate-9.schema.json",
            "scripts/validate-declaration-validation-publication-study-gate-9",
            "tests/test_declaration_validation_publication_study_gate_9.py",
        }
        self.assertTrue(expected.issubset({call.args[0] for call in bound.call_args_list}))
        for call in bound.call_args_list:
            if call.args[0] in expected:
                self.assertEqual(call.kwargs.get("commit", gate10.PROTOCOL_COMMIT), gate10.PROTOCOL_COMMIT)

    def test_mutable_gate9_protocol_bytes_are_rejected(self):
        protocol_path = ROOT / gate10.PROTOCOL
        original = Path.read_bytes

        def changed(path):
            return b"changed current protocol" if path == protocol_path else original(path)

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "frozen Gate-9 bytes changed"):
                gate10.protocol_inputs(full_chain=False)


class Gate10ResultValidationTests(unittest.TestCase):
    RUN = ROOT / "results/research/publication-study-theorem-control-0001"
    RESULT = RUN / "result.json"

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(cls.RESULT.read_bytes())

    def assert_rejected(self, document):
        errors = gate10.validate_result(document=document, full_payload=False, check_report=True)
        self.assertTrue(errors)

    def test_actual_result_validates(self):
        self.assertEqual(
            gate10.validate_result(document=self.document, full_payload=False, check_report=True), []
        )

    def test_count_status_isolation_and_attributed_outcome_tampering_rejected(self):
        mutations = []
        changed = copy.deepcopy(self.document)
        changed["counts"]["final_isolated_covered"] += 1
        mutations.append(changed)

        changed = copy.deepcopy(self.document)
        changed["status"] = "ISOLATION_UNRESOLVED"
        mutations.append(changed)

        changed = copy.deepcopy(self.document)
        changed["isolation_elements"][0]["status"] = "SATISFIED" if changed["isolation_elements"][0]["status"] == "UNRESOLVED" else "UNRESOLVED"
        mutations.append(changed)

        changed = copy.deepcopy(self.document)
        changed["observer_results"][0]["outcome"] = "UNKNOWN"
        mutations.append(changed)

        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assert_rejected(mutation)

    def test_raw_process_blob_tampering_is_rejected(self):
        experiment = json.loads((self.RUN / "experiment.json").read_bytes())
        row = experiment["completed"][0]
        raw_dir = self.RUN / "ledger/raw"
        stdout = raw_dir / row["capture"]["stdout_sha256"]
        original = Path.read_bytes

        def tampered(path):
            return b"tampered raw stdout" if path == stdout else original(path)

        with patch.object(Path, "read_bytes", tampered):
            errors = gate10.validate_result(document=self.document, full_payload=False, check_report=True)
        self.assertTrue(errors)

    def test_control_expression_tampering_is_rejected(self):
        control = self.RUN / "control.ndjson"
        original = Path.read_bytes

        def tampered(path):
            return original(path).replace(b'"body":3', b'"body":1') if path == control else original(path)

        with patch.object(Path, "read_bytes", tampered):
            errors = gate10.validate_result(document=self.document, full_payload=False, check_report=True)
        self.assertTrue(any('bound bytes differ' in error and 'control.ndjson' in error for error in errors), errors)

    def test_control_typing_and_exact_constructor_are_both_enforced(self):
        negative = (self.RUN / 'negative.ndjson').read_bytes()
        control = (self.RUN / 'control.ndjson').read_bytes()
        malformed = control.replace(b'"body":3', b'"body":1')
        self.assertNotEqual(control, malformed)
        with self.assertRaisesRegex(ValueError, 'sort-valued|typing failed'):
            gate10.inspect_pair_member(malformed)
        plan, freeze, _ = gate10.protocol_inputs()
        with self.assertRaisesRegex(ValueError, 'deviates'):
            gate10.analyze_pair(negative, malformed, plan, freeze)

    def test_unrelated_successor_current_state_does_not_rebind_gate8_or_gate9(self):
        successor = ROOT / "docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_PLAN.md"
        original = Path.read_bytes

        def changed(path):
            return b"simulated successor wording" if path == successor else original(path)

        with patch.object(Path, "read_bytes", changed):
            self.assertEqual(
                gate10.validate_result(document=self.document, full_payload=False, check_report=True), []
            )


class Gate10SyntheticLifecycleTests(unittest.TestCase):
    """Test wrapper integration with invented bytes, never a real candidate."""
    def run_synthetic(self, fail_construction=False):
        import publication_study_execution as execution
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            (root / 'dependency').write_bytes(b'engineering fixture')
            manifest = {'run_id': 'fake', 'observer_ids': ['o0', 'o1', 'o2', 'o3'],
                        'dependencies': [{'path': 'dependency', 'sha256': gate10.sha(b'engineering fixture')}],
                        'budget': {'checker_executions': 8, 'checker_timeout_seconds': 30, 'wall_seconds': 600}}
            stack.enter_context(patch.object(gate10, 'ROOT', root))
            stack.enter_context(patch.object(gate10, 'protocol_inputs', return_value=({}, {}, {})))
            stack.enter_context(patch.object(gate10, 'make_run_manifest', return_value=manifest))
            stack.enter_context(patch.object(gate10, 'frozen_negative', return_value=b'synthetic negative'))
            def fake_construct(_):
                self.assertTrue((root / gate10.RUN / 'ledger/candidates/pair-1.reservation.json').exists())
                self.assertTrue((root / gate10.RUN / 'run-manifest.json').exists())
                if fail_construction:
                    raise ValueError('synthetic construction failure')
                return b'synthetic control'
            stack.enter_context(patch.object(gate10, 'construct_control', side_effect=fake_construct))
            stack.enter_context(patch.object(gate10, 'analyze_pair', return_value={'expected_outcomes': {'control': 'ACCEPT', 'negative': 'REJECT'}}))
            observers = [execution.Observer(o, 'a' * 64, ('fake', '{artifact}')) for o in manifest['observer_ids']]
            stack.enter_context(patch.object(gate10, 'observers_for', return_value=observers))
            def fake_process(*args, **kwargs):
                self.assertTrue((root / gate10.RUN / 'ledger/candidates/pair-1.freeze.json').exists())
                return SimpleNamespace(returncode=0, stdout=b'', stderr=b'')
            process = stack.enter_context(patch.object(execution.subprocess, 'run', side_effect=fake_process))
            stack.enter_context(patch.object(gate10, 'render_outputs', side_effect=lambda: gate10.read(gate10.RUN + '/experiment.json')))
            result = gate10.run_once()
            completion = gate10.read(gate10.RUN + '/ledger/session-completion.json')
            self.assertEqual(completion['result_binding'], gate10.binding(gate10.RUN + '/experiment.json'))
            self.assertEqual(completion['candidate_reservations'], 1)
            self.assertEqual(completion['checker_reservations'], 0 if fail_construction else 8)
            self.assertEqual(process.call_count, 0 if fail_construction else 8)
            self.assertEqual(result['terminal_state'], 'EXECUTION_UNRESOLVED' if fail_construction else 'COMPLETE')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                gate10.run_once()

    def test_two_phase_freeze_and_eight_launch_integration(self):
        self.run_synthetic()

    def test_failed_construction_consumes_pair_and_cannot_retry(self):
        self.run_synthetic(fail_construction=True)


if __name__ == "__main__":
    unittest.main()
