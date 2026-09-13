"""Dated upstream observations must not turn submission into acceptance."""
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBSERVE = runpy.run_path(str(ROOT / 'scripts/build-project-review'))['contribution_observations']


class ContributionObservationTests(unittest.TestCase):
    def test_preserves_distinct_states_and_observation_dates(self):
        arena_pr = dict(url='https://example.test/181', state='MERGED',
                        merged_at='2026-09-06T00:00:00Z', head_revision='a' * 40,
                        observed_on='2026-09-13', review_state='COMPLETED', checks_state='PASS')
        nanoda_pr = dict(url='https://example.test/32', state='OPEN',
                         merged_at=None, head_revision='b' * 40,
                         observed_on='2026-09-13', review_state='NO_ACTIVITY',
                         checks_state='NOT_REPORTED')
        rows = OBSERVE({'contributions': [
            {'id': 'ARENA-PR-181', 'title': 'Arena', 'target_repository': 'owner/arena',
             'upstream': arena_pr},
            {'id': 'NANODA-PR-32', 'title': 'Nanoda', 'target_repository': 'owner/nanoda',
             'upstream': nanoda_pr},
            {'id': 'LOCAL-DRAFT', 'title': 'Draft', 'target_repository': 'owner/nanoda',
             'upstream': None},
        ]})
        self.assertEqual(rows[0]['merged_at'], arena_pr['merged_at'])
        self.assertTrue(rows[0]['merged'])
        self.assertEqual(rows[0]['observed_at'], '2026-09-13')
        self.assertEqual(rows[1]['state'], 'open')
        self.assertFalse(rows[1]['merged'])
        self.assertIsNone(rows[1]['merged_at'])
        self.assertEqual(rows[1]['head_sha'], 'b' * 40)
        self.assertEqual(rows[1]['observed_at'], '2026-09-13')
        self.assertEqual(len(rows), 2)

    def test_missing_merge_evidence_is_not_guessed(self):
        with self.assertRaises(KeyError):
            OBSERVE({'contributions': [{
                'id': 'BROKEN', 'title': 'Broken', 'target_repository': 'owner/repo',
                'upstream': {'url': 'x', 'state': 'OPEN'},
            }]})
