"""Pure accounting regressions preserve failure and uncertainty at closure."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/research/conditional-validation-contracts/cvc-runner-1'
SPEC = importlib.util.spec_from_file_location('cvc_runner_closure', OUT / 'validate-evidence.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class ClosureTests(unittest.TestCase):
    def test_orphan_is_preserved_and_never_labeled_measured(self):
        rows = [{'kind': 'RESERVED', 'test': 'fixture', 'reserved_launches': 1, 'reserved_seconds': 5}]
        result = v.fixture_costs(rows, allow_orphan=True)
        self.assertEqual(result['orphan_count'], 1)
        self.assertEqual(result['orphan_reserved_seconds'], 5)
        self.assertEqual(result['measured_seconds'], 0)
        with self.assertRaisesRegex(ValueError, 'orphan'):
            v.fixture_costs(rows)

    def test_malformed_or_nonfinite_validation_receipts_refused(self):
        reserved = {'kind': 'RESERVED', 'test': 'fixture', 'reserved_launches': 1, 'reserved_seconds': 5}
        terminal = {'kind': 'TERMINAL', 'test': 'fixture', 'charged_seconds': .25}
        self.assertEqual(v.fixture_costs([reserved, terminal])['measured_seconds'], .25)
        for rows in [[terminal], [reserved, reserved],
                     [reserved, {**terminal, 'charged_seconds': float('nan')}],
                     [reserved, {**terminal, 'charged_seconds': 6}],
                     [reserved, {**terminal, 'test': 'different'}]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                v.fixture_costs(rows, allow_orphan=True)

    def test_failure_cannot_be_promoted_to_success_or_session_reset(self):
        initial = {'item_id': 'CVC-RUNNER-1', 'started_at': '2026-09-06T20:00:00+00:00',
                   'baseline_commit': 'a'*40, 'limits': {'max_sessions': 2}, 'inputs': ['bound'],
                   'sessions': [{'started_at': '2026-09-06T20:00:00+00:00', 'ended_at': None}]}
        work = copy.deepcopy(initial)
        work.update(status='COMPLETE', outcome='BOUNDED_UNRESOLVED', active_seconds=60,
                    ended_at='2026-09-06T20:01:00+00:00')
        work['sessions'][0]['ended_at'] = work['ended_at']
        self.assertEqual(v.session_seconds(initial, work), 60)
        for mutate in [lambda w: w.update(outcome='SUCCESS'), lambda w: w.update(active_seconds=0),
                       lambda w: w['sessions'][0].update(started_at='2026-09-06T20:00:01+00:00')]:
            changed = copy.deepcopy(work); mutate(changed)
            with self.assertRaises(ValueError):
                v.session_seconds(initial, changed)

    def test_raw_root_failure_and_worker_uncertainty_retained(self):
        stop = json.loads((OUT / 'stop-diagnostic.json').read_text())
        failed = json.loads((ROOT / stop['root_attempt']['record']).read_text())
        self.assertEqual((failed['returncode'], failed['status']), (-15, 'FAIL'))
        self.assertIsNone(stop['root_attempt']['terminal_receipt'])
        worker = json.loads((OUT / 'worker-accounting.json').read_text())
        self.assertIsNone(worker['utc_timestamps'])
        self.assertEqual(sum(row.get('fixture_launches_reported', 0) for row in worker['commands']), 2)


if __name__ == '__main__':
    unittest.main()
