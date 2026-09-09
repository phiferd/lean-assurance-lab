"""Dated upstream observations must not turn submission into acceptance."""
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBSERVE = runpy.run_path(str(ROOT / 'scripts/build-project-review'))['contribution_observations']


class ContributionObservationTests(unittest.TestCase):
    def test_preserves_distinct_states_and_observation_dates(self):
        arena_pr = dict(url='https://example.test/181', state='closed',
                        merged=True, merged_at='2026-09-06T00:00:00Z', head_sha='a' * 40)
        nanoda_pr = dict(url='https://example.test/32', state='open',
                         merged=False, merged_at=None, head_sha='b' * 40)
        rows = OBSERVE({'reviewed_on': '2026-09-09',
                        'upstream_observations': {'pull_requests': [arena_pr]}},
                       {'retrieved_at': '2026-09-09 12:59:16 UTC', 'observation': nanoda_pr})
        self.assertEqual(rows[0]['merged_at'], arena_pr['merged_at'])
        self.assertTrue(rows[0]['merged'])
        self.assertEqual(rows[0]['observed_at'], '2026-09-09')
        self.assertEqual(rows[1]['state'], 'open')
        self.assertFalse(rows[1]['merged'])
        self.assertIsNone(rows[1]['merged_at'])
        self.assertEqual(rows[1]['head_sha'], 'b' * 40)
        self.assertEqual(rows[1]['observed_at'], '2026-09-09 12:59:16 UTC')

    def test_missing_merge_evidence_is_not_guessed(self):
        with self.assertRaises(KeyError):
            OBSERVE({'reviewed_on': '2026-09-09',
                     'upstream_observations': {'pull_requests': []}},
                    {'retrieved_at': '2026-09-09', 'observation': {'url': 'x', 'state': 'open'}})
