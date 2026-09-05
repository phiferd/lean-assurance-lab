import copy
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    'gate9_validator', str(ROOT / 'scripts/validate-declaration-validation-publication-study-gate-9'),
)
spec = importlib.util.spec_from_loader(loader.name, loader)
validator = importlib.util.module_from_spec(spec)
loader.exec_module(validator)


class Gate9PublicationStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = validator.load_json(validator.PLAN_PATH)
        cls.schema = validator.load_json(validator.SCHEMA_PATH)

    def errors(self, plan):
        return validator.validate_gate9(plan, full_chain=False)

    def test_schema_is_valid(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_actual_plan_validates_against_immutable_inputs(self):
        self.assertEqual(self.errors(self.plan), [])

    def test_rejects_wrong_predecessor_bindings(self):
        for key, value in [('git_blob', '0' * 40), ('sha256', '0' * 64), ('git_commit', '0' * 40)]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.plan)
                changed['bindings']['gate8_baseline'][key] = value
                self.assertTrue(self.errors(changed))
        changed = copy.deepcopy(self.plan)
        changed['bindings']['gate8_baseline'] = changed['bindings']['preregistration']
        self.assertTrue(any('unexpected binding path' in e for e in self.errors(changed)))

    def test_rejects_target_substitution_or_semantic_change(self):
        for key, value in [('entry_id', 'EXPR.LET.VALUE_TYPE_MATCH'), ('semantic_denotation_sha256', '0' * 64)]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.plan)
                changed['targets'][0][key] = value
                self.assertTrue(self.errors(changed))
        changed = copy.deepcopy(self.plan)
        changed['targets'][0]['predicate']['violation_expectation'] = 'ACCEPT'
        self.assertTrue(any('predicate' in e for e in self.errors(changed)))

    def test_rejects_missing_competing_obligation(self):
        changed = copy.deepcopy(self.plan)
        changed['targets'][0]['competing_obligation_ids'].pop()
        self.assertTrue(any('18 frozen competing' in e for e in self.errors(changed)))

    def test_rejects_budget_expansion(self):
        for key, value in [('tier_3_candidates', 1), ('checker_executions', 9), ('wall_seconds', 601)]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.plan)
                changed['budget'][key] = value
                self.assertTrue(self.errors(changed))

    def test_rejects_weakened_control(self):
        for key, value in [('declaration_kind', 'def'), ('must_have_matching_valid_proof', False), ('minimizes_unrelated_differences', False)]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.plan)
                changed['targets'][0]['matched_control'][key] = value
                self.assertTrue(self.errors(changed))

    def test_rejects_execution_expansion(self):
        changed = copy.deepcopy(self.plan)
        changed['targets'][0]['strategy']['adaptive_repair'] = 'ALLOWED'
        self.assertTrue(self.errors(changed))
        changed = copy.deepcopy(self.plan)
        changed['execution_protocol']['observer_ids'].reverse()
        self.assertTrue(self.errors(changed))
        changed = copy.deepcopy(self.plan)
        changed['execution_protocol']['outcome_vocabulary'].remove('UNKNOWN')
        self.assertTrue(self.errors(changed))

    def test_rejects_unregistered_seed_and_early_feedback(self):
        changed = copy.deepcopy(self.plan)
        changed['targets'][0]['negative_input_id'] = 'another-seed'
        self.assertTrue(self.errors(changed))
        changed = copy.deepcopy(self.plan)
        changed['scope_closure']['checker_feedback_obtained'] = True
        self.assertTrue(self.errors(changed))

    def test_full_chain_refuses_mutable_validator_before_import(self):
        original = Path.read_bytes
        validator_path = ROOT / validator.EXPECTED_BINDINGS['gate8_validator']

        def substituted(path):
            return b'changed validator' if path == validator_path else original(path)

        with patch.object(Path, 'read_bytes', substituted), patch.object(validator, 'load_gate8_module') as load:
            errors = validator.validate_gate9(self.plan)
        self.assertTrue(any('live predecessor differs' in e for e in errors))
        load.assert_not_called()

    def test_successor_changes_do_not_rebind_historical_gate8(self):
        # A later current file may differ; historical reads must still use Git blobs.
        original = Path.read_bytes
        baseline_path = ROOT / validator.EXPECTED_BINDINGS['gate8_baseline']
        before, errors = validator.bound_bytes(self.plan['bindings']['gate8_baseline'], 'Gate8')
        self.assertEqual(errors, [])
        changed = copy.deepcopy(self.plan)
        changed['reporting']['recommendation'] += ' Successor wording.'

        def successor_bytes(path):
            return b'future current baseline' if path == baseline_path else original(path)

        with patch.object(Path, 'read_bytes', successor_bytes):
            self.assertEqual(self.errors(changed), [])
            after, errors = validator.bound_bytes(changed['bindings']['gate8_baseline'], 'Gate8')
        self.assertEqual(errors, [])
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
