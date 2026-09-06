"""Pure regression checks for successor closure accounting; no process fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('cvc_prep2_evidence', ROOT / 'results/research/conditional-validation-contracts/cvc-prep-2/validate-evidence.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class ClosureAccountingTests(unittest.TestCase):
    def fixture(self, rows):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ledger'
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            return v.fixture_costs(path)

    def test_fixture_costs_require_paired_bounded_finite_attempts(self):
        reserved = {'kind': 'RESERVED', 'test': 'inert', 'reserved_launches': 2, 'reserved_seconds': 10}
        terminal = {'kind': 'TERMINAL', 'test': 'inert', 'charged_seconds': .5}
        self.assertEqual(self.fixture([reserved, terminal]), (2, .5))
        for rows in [[reserved], [terminal], [reserved, reserved, terminal, terminal],
                     [reserved, {**terminal, 'test': 'wrong'}],
                     [reserved, {**terminal, 'charged_seconds': 11}],
                     [reserved, {**terminal, 'charged_seconds': float('nan')}],
                     [{**reserved, 'reserved_launches': True}, terminal]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError): self.fixture(rows)

    def work(self):
        initial = {'started_at': '2026-09-06T20:00:00+00:00', 'limits': {'max_sessions': 2}, 'inputs': ['bound'],
                   'sessions': [{'number': 1, 'started_at': '2026-09-06T20:00:00+00:00', 'ended_at': None}]}
        closed = copy.deepcopy(initial)
        closed.update(ended_at='2026-09-06T20:01:00+00:00', execution_stopped_at='2026-09-06T20:00:50+00:00', active_seconds=60)
        closed['sessions'][0]['ended_at'] = closed['ended_at']
        return initial, closed

    def test_closed_work_preserves_input_and_time_accounting(self):
        initial, closed = self.work()
        self.assertEqual(v.closed_sessions(closed, initial), 60)
        mutations = [lambda w: w.__setitem__('inputs', ['changed']),
                     lambda w: w.__setitem__('active_seconds', 59),
                     lambda w: w.__setitem__('execution_stopped_at', '2026-09-06T20:02:00+00:00'),
                     lambda w: w.__setitem__('ended_at', '2026-09-06T20:00:59+00:00'),
                     lambda w: w['sessions'][0].__setitem__('started_at', '2026-09-06T20:00:01+00:00')]
        for mutate in mutations:
            changed = copy.deepcopy(closed); mutate(changed)
            with self.assertRaises(ValueError): v.closed_sessions(changed, initial)

    def test_closed_work_rejects_overlapping_sessions(self):
        initial, closed = self.work()
        closed['sessions'].append({'number': 2, 'started_at': '2026-09-06T20:00:30+00:00', 'ended_at': '2026-09-06T20:02:00+00:00'})
        with self.assertRaisesRegex(ValueError, 'overlapping'): v.closed_sessions(closed, initial)

    def test_prelaunch_counts_come_from_raw_logs(self):
        raw = b'\nRan 29 tests in 5.000s\n\nOK\n'
        receipt = {'test_count': 29, 'checks': [{'log': 'inert.log', 'log_sha256': v.digest(raw),
                   'returncode': 0, 'status': 'PASS', 'test_count': 29}]}
        with patch.object(v, 'committed', return_value=raw):
            self.assertEqual(v.test_counts('checkpoint', receipt), [29])
            receipt['checks'][0]['test_count'] = 30
            with self.assertRaisesRegex(ValueError, 'per-check test count'): v.test_counts('checkpoint', receipt)


if __name__ == '__main__':
    unittest.main()
