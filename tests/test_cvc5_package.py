"""Prevent packaging from changing scoped proof, observation or accounting claims."""
from copy import deepcopy
from pathlib import Path
import unittest
from lib import cvc5_package as p

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.result = p.read(ROOT, p.OUTPUT / 'result.json')

    def test_retained_projection(self):
        p.validate_result(ROOT, self.result)

    def test_cannot_discharge_assumptions(self):
        self.result['evidence']['proof']['transitive_axioms']['Lab.CVC2.preservation'].pop()
        with self.assertRaisesRegex(ValueError, 'retained evidence'):
            p.validate_result(ROOT, self.result)

    def test_cannot_hide_parser_failure_or_unrun_candidate(self):
        for index in (9, 10, 11):
            changed = deepcopy(self.result)
            changed['evidence']['original_observations']['rows'].pop(index)
            with self.assertRaisesRegex(ValueError, 'retained evidence'):
                p.validate_result(ROOT, changed)

    def test_cannot_promote_unsupported_or_control_acceptance(self):
        for field, value in [('model_status', 'CHECKED_MODEL_INVALID'), ('model_status', 'CHECKED_REQUIRED_ACCEPTANCE')]:
            changed = deepcopy(self.result)
            changed['evidence']['regression']['cases'][1][field] = value
            with self.assertRaisesRegex(ValueError, 'retained evidence'):
                p.validate_result(ROOT, changed)

    def test_cannot_reset_prior_costs_or_drop_raw_receipt(self):
        changed = deepcopy(self.result)
        changed['evidence']['prior_costs']['ownership']['combined_observer_launches'] = 4
        with self.assertRaisesRegex(ValueError, 'retained evidence'):
            p.validate_result(ROOT, changed)
        self.result['evidence']['ownership_observations']['rows'][3]['raw_receipts'].pop()
        with self.assertRaisesRegex(ValueError, 'retained evidence'):
            p.validate_result(ROOT, self.result)

    def test_no_new_work_or_broader_claim(self):
        for field in self.result['nonclaims']:
            changed = deepcopy(self.result); changed['nonclaims'][field] = True
            with self.assertRaisesRegex(ValueError, 'unsupported assurance claim'):
                p.validate_result(ROOT, changed)
        self.result['research_counts']['observer_launches'] = 1
        with self.assertRaisesRegex(ValueError, 'new scientific work'):
            p.validate_result(ROOT, self.result)

    def test_incomplete_manifest_rejected_before_git(self):
        with self.assertRaisesRegex(ValueError, 'missing or duplicate'):
            p.check_bindings(ROOT, {'base_commit': 'a' * 40, 'inputs': []})

    def test_embedded_scientific_bytes_and_raw_receipts_must_be_bound(self):
        manifest = p.read(ROOT, p.OUTPUT / 'evidence-manifest.json')
        p.check_receipt_coverage(self.result['evidence'], manifest)
        for path in ('corpus/generated/universe-imax-right-succ.ndjson',
                     str(p.BASE / 'cvc-4-ownership-1/run-0001/attempts/04/stderr')):
            changed = deepcopy(manifest)
            changed['inputs'] = [row for row in changed['inputs'] if row['path'] != path]
            with self.assertRaisesRegex(ValueError, 'unbound embedded receipt'):
                p.check_receipt_coverage(self.result['evidence'], changed)
