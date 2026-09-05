import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import publication_study_closure as closure


class PublicationStudyClosureTests(unittest.TestCase):
    def test_registered_strong_positive_has_priority_over_specification_gap(self):
        decision = closure.derive_decision()
        self.assertEqual(decision['outcome_class'], 'STRONG_POSITIVE')
        self.assertEqual(decision['claim_tier'], 'BOUNDED_PILOT')
        self.assertEqual(decision['publication_decision'], 'PUBLISH_BOUNDED')
        self.assertTrue(decision['outcome_triggers']['SPECIFICATION_RESULT'])
        self.assertEqual(decision['publication_execution'], 'NOT_AUTHORIZED')

    def test_literal_rules_preserve_null_specification_and_inconclusive_results(self):
        decision = closure.derive_decision()
        facts = copy.deepcopy(decision['facts'])
        facts.update(coarse_positive_newly_isolated=0, synthesis_isolated_successes=0,
                     schema_valid_corpus_recommendations=0, external_actions_recommended=0)
        self.assertEqual(closure.classify(facts, decision['classification_priority'])[0], 'SPECIFICATION_RESULT')
        facts.update(qualification_gap_candidates=0, coarse_positive_but_not_isolated=0)
        self.assertEqual(closure.classify(facts, decision['classification_priority'])[0], 'NEGATIVE_METHOD_RESULT')
        facts.update(existing_isolated_covered=1)
        self.assertEqual(closure.classify(facts, decision['classification_priority'])[0], 'MODERATE_POSITIVE')
        facts.update(discovery_closed=False)
        self.assertEqual(closure.classify(facts, decision['classification_priority'])[0], 'INCONCLUSIVE')

    def test_decision_and_report_cannot_be_relabelled_after_results(self):
        original = closure.load
        def tampered(path):
            value = original(path)
            if path == closure.DECISION:
                value['outcome_class'] = 'SPECIFICATION_RESULT'
            return value
        with patch.object(closure, 'load', side_effect=tampered):
            errors = closure.validate_content(check_manifest=False)
        self.assertTrue(any('decision differs' in e for e in errors), errors)

    def test_content_inventory_excludes_its_own_and_attestation_bytes(self):
        paths = closure.content_paths()
        self.assertNotIn(closure.MANIFEST, paths)
        self.assertNotIn(closure.HISTORICAL, paths)
        for required in [closure.DECISION, closure.REPORT, closure.ENTRYPOINT,
                         'scripts/publication_study_history.py', closure.g10.RESULT]:
            self.assertIn(required, paths)

    def test_phase_appropriate_study_validates(self):
        if (ROOT / closure.HISTORICAL).exists():
            errors = closure.history.validate_historical(ROOT, closure.load(closure.HISTORICAL),
                closure.MANIFEST, closure.ENTRYPOINT, ['validate', '--content-only'])
        else:
            errors = closure.validate_content(check_manifest=False)
        self.assertEqual(errors, [])

    def test_real_study_transition_uses_old_validator_and_facts(self):
        # Phase A exercises the generic committed-snapshot transition suite;
        # Phase B additionally checks this exact completed study history.
        if not (ROOT / closure.HISTORICAL).exists():
            self.assertEqual(closure.load(closure.DECISION)['status'], 'GATE_11_COMPLETE')
            return
        with tempfile.TemporaryDirectory(prefix='publication-transition-') as directory:
            destination = Path(directory) / 'repo'
            subprocess.run(['git', 'clone', '--local', '--no-hardlinks', str(ROOT), str(destination)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for path in [closure.DECISION, closure.SCHEMA, 'scripts/publication_study_closure.py',
                         'scripts/publication_study_gate10.py', closure.g10.RUN + '/control.ndjson']:
                (destination / path).write_text('later mutable successor bytes\n')
            subprocess.run(['git', 'add', '.'], cwd=destination, check=True)
            subprocess.run(['git', '-c', 'user.name=Transition Test', '-c', 'user.email=test@example.invalid',
                            'commit', '-qm', 'Synthetic later successor'], cwd=destination, check=True)
            errors = closure.history.validate_historical(destination, closure.load(closure.HISTORICAL),
                closure.MANIFEST, closure.ENTRYPOINT, ['validate', '--content-only'])
            self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
