from copy import deepcopy
from pathlib import Path
import unittest

from lib.cvc4_adapter_review import BASE, PRIOR, check_proposal, load, validate

ROOT = Path(__file__).resolve().parents[1]


class AdapterReviewTests(unittest.TestCase):
    def setUp(self):
        self.proposal = load(ROOT / BASE / 'successor-proposal.json')
        self.cases = {r['id']: r for r in load(ROOT / PRIOR / 'cases.json')['cases']}
        self.payloads = load(ROOT / 'config/cvc4-u1-a7-0002.json')['payloads']

    def check(self):
        check_proposal(self.proposal, self.cases, self.payloads)

    def test_existing_bound_review_validates_without_variant_generation(self):
        self.assertEqual(validate(ROOT)['decision'], 'SUCCESSOR')

    def test_changed_meaning_is_not_a_representation_transition(self):
        self.proposal['representation_change']['cases'][1]['unchanged_artifact']['params'].append('u')
        with self.assertRaisesRegex(ValueError, 'transition or model status'):
            self.check()

    def test_candidate_cannot_be_promoted_to_invalid(self):
        self.proposal['representation_change']['cases'][1]['model_status'] = 'CHECKED_MODEL_INVALID'
        with self.assertRaisesRegex(ValueError, 'transition or model status'):
            self.check()

    def test_launch_expansion_and_terminal_resume_are_refused(self):
        for field in ('budget', 'accounting'):
            with self.subTest(field=field):
                original = deepcopy(self.proposal)
                if field == 'budget':
                    self.proposal[field]['validator_launches'] = 5
                else:
                    self.proposal[field]['terminal_runs_resumed'] = True
                with self.assertRaises(ValueError):
                    self.check()
                self.proposal = original

    def test_missing_positive_control_or_changed_binary_is_refused(self):
        self.proposal['matrix'].pop(1)
        with self.assertRaisesRegex(ValueError, 'control gate'):
            self.check()
        self.proposal = load(ROOT / BASE / 'successor-proposal.json')
        self.proposal['retained_inputs']['observer_payloads'] = []
        with self.assertRaisesRegex(ValueError, 'observer payloads'):
            self.check()

    def test_wrong_name_reference_cannot_supply_unused_v(self):
        self.proposal['representation_change']['cases'][1]['insert_record']['param'] = 3
        with self.assertRaisesRegex(ValueError, 'transition or model status'):
            self.check()
