"""Pure ownership-controller regressions; no observer process is launched."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from lib import cvc4_ownership_runner as runner


def clock(value):
    return {'at': '2026-09-08T00:00:%02d+00:00' % value, 'monotonic': float(value)}


def cell(role, implementation):
    return {'id': 'E-' + implementation.upper() + '-' + role.upper() + '-PARAM-RECORD',
            'pair_id': 'ownership', 'role': role, 'implementation': implementation,
            'argv': ['observer'], 'cwd': '/tmp', 'env': {},
            'expected': {'returncode': 0, 'stdout_pattern': 'accepted\\n', 'stderr_pattern': ''}}


def start():
    return {'kind': 'START', 'run_id': runner.RUN, 'time': clock(0),
            'manifest_sha256': 'x', 'checkpoint': 'y',
            'work': {'intervals': [{'number': 1, 'start': clock(0), 'end': None}]},
            'predecessor': {'run_id': runner.predecessor.RUN, 'launches': runner.INHERITED_LAUNCHES,
                            'known_process_seconds': runner.INHERITED_PROCESS_SECONDS,
                            'work': {'intervals': [{'number': 1, 'start': clock(0), 'end': None}]},
                            'accounted_at': clock(0)}}


def reserve(number, target, event_time):
    state = runner.derive(EVENTS + [{'kind': 'RESERVED', 'number': n + 1, 'cell': c,
        'time': clock(n + 1), 'work': start()['work'], 'reserved_seconds': 30,
        'manifest_sha256': 'x', 'checkpoint': 'y'} for n, c in enumerate(CELLS[:number - 1])])
    return {'kind': 'RESERVED', 'number': number, 'cell': target, 'time': event_time,
            'work': start()['work'], 'reserved_seconds': runner.budget(state, event_time),
            'manifest_sha256': 'x', 'checkpoint': 'y'}


CELLS = [cell('control', 'official'), cell('control', 'nanoda'),
         cell('candidate', 'official'), cell('candidate', 'nanoda')]
EVENTS = [start()]


class OwnershipOrderTests(unittest.TestCase):
    def accepted(self, number, target):
        return {'kind': 'TERMINAL', 'number': number, 'time': clock(number + 1),
                'work': start()['work'], 'hypothesis_matched': True, 'charged_seconds': .1,
                'process_status': 'COMPLETE', 'returncode': 0, 'receipts': []}

    def test_both_fresh_controls_are_required_before_any_candidate(self):
        first = reserve(1, CELLS[0], clock(1))
        events = EVENTS + [first, self.accepted(1, CELLS[0])]
        candidate = {'kind': 'RESERVED', 'number': 2, 'cell': CELLS[2], 'time': clock(3),
                     'work': start()['work'], 'reserved_seconds': 30, 'manifest_sha256': 'x', 'checkpoint': 'y'}
        with self.assertRaisesRegex(ValueError, 'both fresh controls'):
            runner.derive(events + [candidate])
        second = {'kind': 'RESERVED', 'number': 2, 'cell': CELLS[1], 'time': clock(3),
                  'work': start()['work'], 'reserved_seconds': 30, 'manifest_sha256': 'x', 'checkpoint': 'y'}
        events += [second, self.accepted(2, CELLS[1])]
        third = {'kind': 'RESERVED', 'number': 3, 'cell': CELLS[2], 'time': clock(5),
                 'work': start()['work'], 'reserved_seconds': 30, 'manifest_sha256': 'x', 'checkpoint': 'y'}
        self.assertEqual(runner.derive(events + [third])['attempts'][-1]['reservation']['cell']['role'], 'candidate')

    def test_missing_or_malformed_output_remains_a_pause_not_an_outcome(self):
        reservation = reserve(1, CELLS[0], clock(1))
        terminal = {'kind': 'TERMINAL', 'number': 1, 'time': clock(2), 'work': start()['work'],
                    'hypothesis_matched': None, 'charged_seconds': .1, 'control_error': 'missing or malformed output',
                    'receipts': []}
        state = runner.derive(EVENTS + [reservation, terminal])
        self.assertEqual(state['control_stop'], 'missing or malformed output')
        malformed = deepcopy(terminal); malformed['hypothesis_matched'] = False
        with self.assertRaisesRegex(ValueError, 'control error cannot'):
            runner.derive(EVENTS + [reservation, malformed])

    def test_new_and_combined_launch_caps_are_cumulative(self):
        state = {'attempts': [{'terminal': {}} for _ in range(4)], 'control_stop': None, 'hypothesis_mismatch': False,
                 'work': {'intervals': [{'number': 1, 'start': clock(0), 'end': None}]}}
        with self.assertRaisesRegex(ValueError, 'combined validator launch cap'):
            runner.budget(state, clock(1))
        self.assertEqual(runner.INHERITED_LAUNCHES + runner.LIMITS['validator_launches'], 16)


class ReceiptAndClockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.directory = self.root / runner.OUT / 'attempts/01'; self.directory.mkdir(parents=True)
        self.reservation = {'number': 1, 'time': clock(1), 'reserved_seconds': 30, 'checkpoint': 'fixed',
                            'cell': {**cell('control', 'official'), 'argv': ['observer', 'input'],
                                     'cwd': '/tmp/exact', 'env': {'LANG': 'C'}}}

    def write_receipts(self, stdout=b'accepted\n', stderr=b''):
        for name, data in (('stdout', stdout), ('stderr', stderr)):
            (self.directory / name).write_bytes(data)
        request = {'argv': self.reservation['cell']['argv'], 'cwd': self.reservation['cell']['cwd'],
                   'env': self.reservation['cell']['env'], 'seconds': 30, 'started_at': clock(1)['at'],
                   'monotonic_started': 1.1, 'deadline_monotonic': 31.}
        request['request_sha256'] = runner.digest(request)
        (self.directory / 'request.json').write_text(json.dumps(request))
        result = {'status': 'COMPLETE', 'returncode': 0, 'charged_seconds': .1,
                  'monotonic_started': 1.1, 'monotonic_ended': 1.21,
                  'request_sha256': request['request_sha256'], 'stdout_sha256': runner.sha(self.directory / 'stdout'),
                  'stderr_sha256': runner.sha(self.directory / 'stderr'), 'cleanup_completed': True,
                  'deadline_exceeded': False}
        (self.directory / 'supervisor.json').write_text(json.dumps(result))
        return result

    def test_supervisor_rejects_bound_request_tampering_and_process_hash_tampering(self):
        self.write_receipts(); runner.supervisor(self.root, self.reservation)
        request = json.loads((self.directory / 'request.json').read_text()); request['cwd'] = '/wrong'
        (self.directory / 'request.json').write_text(json.dumps(request))
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            runner.supervisor(self.root, self.reservation)
        self.write_receipts(); request = json.loads((self.directory / 'request.json').read_text())
        (self.directory / 'process.json').write_text(json.dumps({'pid': 3, 'supervisor_pid': 2,
            'request_sha256': '0' * 64, 'started_at': clock(1)['at']}))
        with self.assertRaisesRegex(ValueError, 'process receipt'):
            runner.supervisor(self.root, self.reservation)

    def test_compare_rejects_missing_utf8_and_empty_acceptance_output(self):
        result = self.write_receipts(); (self.directory / 'stdout').unlink()
        with self.assertRaises(FileNotFoundError): runner.compare(self.root, self.reservation, result)
        self.write_receipts(stdout=b'\xff')
        with self.assertRaises(UnicodeDecodeError): runner.compare(self.root, self.reservation, result)
        self.write_receipts(stdout=b'')
        with self.assertRaisesRegex(ValueError, 'missing or malformed'):
            runner.compare(self.root, self.reservation, result)

    def test_terminal_cannot_forge_raw_supervisor_status_or_returncode(self):
        result = self.write_receipts(); _, receipts = runner.supervisor(self.root, self.reservation)
        terminal = {'receipts': receipts, 'charged_seconds': .1, 'process_status': 'FAILED',
                    'returncode': 101, 'hypothesis_matched': None}
        state = {'attempts': [{'reservation': self.reservation, 'terminal': terminal}], 'reconciliations': []}
        identity = {'manifest': {'cells': [self.reservation['cell']]}, 'checkpoint': 'fixed'}
        with self.assertRaisesRegex(ValueError, 'terminal receipt differs'):
            runner.verify_attempts(self.root, state, identity)

    def test_unknown_candidate_output_pauses_but_exact_acceptance_is_observed(self):
        self.reservation['cell']['role'] = 'candidate'
        self.reservation['cell']['expected'] = {'returncode': 1, 'stdout_pattern': '', 'stderr_pattern': 'ownership refusal\\n'}
        result = self.write_receipts(stdout=b'', stderr=b'some unrelated panic\n')
        result['returncode'] = 101
        with self.assertRaisesRegex(ValueError, 'unrecognized output'):
            runner.compare(self.root, self.reservation, result)
        result = self.write_receipts(stdout=b'Accepted 1 declarations.\n')
        self.assertIs(runner.compare(self.root, self.reservation, result), False)

    def test_empty_receipts_cannot_establish_a_control_acceptance(self):
        terminal = {'receipts': [], 'hypothesis_matched': True}
        state = {'attempts': [{'reservation': self.reservation, 'terminal': terminal}], 'reconciliations': []}
        with self.assertRaisesRegex(ValueError, 'requires raw receipts'):
            runner.verify_attempts(self.root, state, {'manifest': {'cells': [self.reservation['cell']]}, 'checkpoint': 'fixed'})

    def test_wall_and_monotonic_rollbacks_and_distinct_work_are_rejected_or_allowed(self):
        backward_wall = {'at': '2026-09-07T23:59:59+00:00', 'monotonic': 2.}
        with self.assertRaisesRegex(ValueError, 'rollback'):
            runner.elapsed(clock(1), backward_wall)
        backward_mono = {'at': '2026-09-08T00:00:02+00:00', 'monotonic': .5}
        with self.assertRaisesRegex(ValueError, 'rollback'):
            runner.elapsed(clock(1), backward_mono)
        # A new item's first interval is not required to reproduce predecessor intervals.
        runner.elapsed(clock(1), clock(2))


if __name__ == '__main__':
    unittest.main()
