"""Pure, mocked regressions for the CVC-U1-A7 successor protocol.

No test in this module invokes Lean, a fixture, or the process supervisor.
"""
import contextlib
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import cvc_a7_runner as p
from lib.cvc_process import atomic
from lib.cvc_runner_audit import TARGETS


def at(seconds):
    from datetime import datetime, timedelta, timezone
    return {'at': (datetime(2026, 9, 7, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
            'monotonic': 1000 + seconds}


def identity(run=p.RUN):
    return {'kind': 'START', 'run_id': run, 'manifest_sha256': 'a' * 64, 'time': at(0)}


def start():
    return [identity(), {'kind': 'SESSION_START', 'number': 1, 'time': at(0)}]


def reservation(number, phase, *, seconds=300, when=1, session=1, mode='proof'):
    return {'kind': 'RESERVED', 'number': number, 'phase': phase, 'session': session,
            'mode': mode, 'time': at(when), 'reserved_seconds': seconds}


def terminal(number, status='COMPLETE', **extra):
    return {'kind': 'TERMINAL', 'number': number, 'status': status, 'charged_seconds': 1,
            'returncode': 0 if status == 'COMPLETE' else 1, 'time': at(2),
            'outputs': [{'path': 'fixture.olean'}] if status == 'COMPLETE' else [], **extra}


class StageAccountingTests(unittest.TestCase):
    def test_signature_then_baseline_before_proof(self):
        rows = start() + [reservation(1, 'signature'), terminal(1),
                          reservation(2, 'baseline'), terminal(2, baseline_audit={'ok': True})]
        self.assertEqual(p.phase(p.derive(rows)), 'proof')
        self.assertEqual(len(p.derive(rows + [reservation(3, 'proof')])['attempts']), 3)
        with self.assertRaises(ValueError):
            p.derive(start() + [reservation(1, 'signature'), terminal(1), reservation(2, 'proof')])

    def test_failed_baseline_consumes_its_number_and_retries_as_baseline(self):
        rows = start() + [reservation(1, 'signature'), terminal(1),
                          reservation(2, 'baseline'), terminal(2, 'FAILED')]
        self.assertEqual(p.phase(p.derive(rows)), 'baseline')
        self.assertEqual(len(p.derive(rows + [reservation(3, 'baseline')])['attempts']), 3)
        with self.assertRaises(ValueError):
            p.derive(rows + [reservation(3, 'proof')])

    def test_baseline_success_requires_audit_and_cannot_publish_result(self):
        rows = start() + [reservation(1, 'signature'), terminal(1)]
        with self.assertRaises(ValueError):
            p.derive(rows + [reservation(2, 'baseline'), terminal(2)])
        with self.assertRaises(ValueError):
            p.derive(rows + [reservation(2, 'baseline'),
                             terminal(2, baseline_audit={'ok': True}, result='SUCCESS', axiom_audit={'x': 1})])
        with self.assertRaises(ValueError):
            p.derive(rows + [reservation(2, 'baseline'),
                             terminal(2, 'FAILED', baseline_audit={'ok': True})])

    def test_signature_failure_is_terminal_and_baseline_cannot_precede_it(self):
        with self.assertRaises(ValueError):
            p.derive(start() + [reservation(1, 'baseline')])
        failed = p.derive(start() + [reservation(1, 'signature'), terminal(1, 'FAILED')])
        self.assertEqual(failed['outcome'], 'BOUNDED_UNRESOLVED')
        with self.assertRaises(ValueError):
            p.derive(start() + [reservation(1, 'signature'), terminal(1, 'FAILED'), reservation(2, 'baseline')])

    def test_six_attempt_and_two_session_bounds(self):
        rows = start() + [reservation(1, 'signature'), terminal(1),
                          reservation(2, 'baseline'), terminal(2, baseline_audit={'ok': True})]
        for number in range(3, 7):
            rows += [reservation(number, 'proof'), terminal(number, 'FAILED')]
        self.assertEqual(len(p.derive(rows)['attempts']), 6)
        with self.assertRaises(ValueError):
            p.derive(rows + [reservation(7, 'proof')])
        sessions = [identity()]
        for number in range(1, 3):
            sessions += [{'kind': 'SESSION_START', 'number': number, 'time': at((number - 1) * 3600)},
                         {'kind': 'SESSION_END', 'number': number, 'time': at(number * 3600),
                          'charged_seconds': 3600}]
        self.assertEqual(p.active_seconds(p.derive(sessions), at(7200)), 7200)
        with self.assertRaises(ValueError):
            p.derive(sessions + [{'kind': 'SESSION_START', 'number': 3, 'time': at(7200)}])

    def test_baseline_mismatch_and_orphan_stop_without_free_retry(self):
        rows = start() + [reservation(1, 'signature'), terminal(1), reservation(2, 'baseline'),
                          terminal(2, 'FAILED', baseline_mismatch=True)]
        state = p.derive(rows)
        self.assertEqual(state['outcome'], 'BOUNDED_UNRESOLVED')
        orphan = p.derive(start() + [reservation(1, 'signature'),
                          terminal(1, 'INTERRUPTED', orphan=True, charged_seconds=300)])
        self.assertEqual(orphan['outcome'], 'BOUNDED_UNRESOLVED')


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        # The manifest and controller binding must include every successor-only
        # input, including the immutable Baseline source and expectations.
        required = set(p.FIXED) | set(p.CODE) | {p.BASELINE, p.EXPECTATIONS}
        for rel in required:
            source = ROOT / rel
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        self.m = p.build_manifest(self.root)
        atomic(self.root / p.MANIFEST, self.m)
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        self.gate = stack.enter_context(patch.object(p, 'gate'))
        stack.enter_context(patch.object(p, 'committed'))
        self.payloads = stack.enter_context(patch.object(p, 'verify_payloads'))
        self.launch = stack.enter_context(patch.object(p, 'run_process', side_effect=self.fake))
        self.baseline_audit = stack.enter_context(patch.object(p, 'audit_baseline', return_value={'baseline': True}))
        self.proof_audit = stack.enter_context(patch.object(p, 'audit', return_value={'proof': True}))
        stack.enter_context(patch.object(p.subprocess, 'check_output', return_value='a' * 40 + '\n'))
        p.session(self.root)

    def state(self):
        return p.Ledger(self.root / p.OUT / 'execution').read()[1]

    def fake(self, argv, cwd, env, directory, seconds, **kwargs):
        state = self.state()
        row = state['attempts'][-1]['reservation']
        self.assertEqual(row['argv'], argv)
        self.assertEqual(row['env'], env)
        self.assertEqual(kwargs['deadline_monotonic'], row['time']['monotonic'] + seconds)
        self.assertEqual(Path(argv[3]).name, p.stem_for(row['phase']) + '.lean')
        Path(argv[2]).write_bytes(b'compiled fixture')
        (directory / 'stdout').write_text('mock audit\n')
        (directory / 'stderr').write_text('')
        request = {'argv': argv, 'cwd': str(cwd), 'env': env, 'seconds': seconds,
                   'monotonic_started': row['time']['monotonic'], 'started_at': row['time']['at'],
                   'deadline_monotonic': kwargs['deadline_monotonic']}
        request['request_sha256'] = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        atomic(directory / 'request.json', request)
        result = {'status': 'COMPLETE', 'charged_seconds': .01, 'returncode': 0, 'cleanup_completed': True,
                  'request_sha256': request['request_sha256'], 'stdout_sha256': p.sha(directory / 'stdout'),
                  'stderr_sha256': p.sha(directory / 'stderr')}
        atomic(directory / 'supervisor.json', result)
        return result

    def proof_input(self):
        (self.root / p.BASE / 'proof-input.lean').write_text('import Contract\n' +
            '\n'.join(f'theorem {name} : {typ} := by exact True.intro' for name, typ in TARGETS))

    def test_command_paths_and_counted_stage_sequence(self):
        signature = p.execute(self.root)
        self.assertEqual(signature['attempts'][-1]['reservation']['phase'], 'signature')
        baseline = p.execute(self.root, resume=True)
        self.assertEqual(baseline['attempts'][-1]['reservation']['phase'], 'baseline')
        self.assertIsNone(baseline['outcome'])
        self.proof_input()
        proof = p.execute(self.root, resume=True)
        self.assertEqual(proof['attempts'][-1]['reservation']['phase'], 'proof')
        self.assertEqual(proof['outcome'], 'SUCCESS')
        self.assertEqual(self.launch.call_count, 3)
        self.assertGreaterEqual(self.baseline_audit.call_count, 2)  # audit plus prior-attempt verification

    def test_failed_baseline_is_reserved_then_retried_as_baseline(self):
        p.execute(self.root)
        def fail(*args, **kwargs):
            result = self.fake(*args, **kwargs)
            result.update(status='FAILED', returncode=7)
            return result
        self.launch.side_effect = fail
        failed = p.execute(self.root, resume=True)
        self.assertEqual(failed['attempts'][-1]['reservation']['phase'], 'baseline')
        self.assertIsNone(failed['outcome'])
        self.launch.side_effect = self.fake
        retried = p.execute(self.root, resume=True)
        self.assertEqual(retried['attempts'][-1]['reservation']['phase'], 'baseline')
        self.proof_input()
        self.assertEqual(p.execute(self.root, resume=True)['attempts'][-1]['reservation']['phase'], 'proof')

    def test_signature_output_or_fixed_baseline_tamper_prevents_later_launch(self):
        p.execute(self.root)
        (self.root / p.BASE / 'Contract.olean').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 1)

    def test_manifest_rejects_old_entry_and_stage_command_mutation(self):
        old = copy.deepcopy(self.m)
        old['run_id'] = 'CVC3-U1-PROOF-0001'
        atomic(self.root / p.MANIFEST, old)
        with self.assertRaises(ValueError):
            p.validate_manifest(self.root)

    def test_manifest_binds_fixed_baseline_and_expectations(self):
        fixed = {row['path'] for row in self.m['fixed_inputs']}
        self.assertTrue({p.BASELINE, p.EXPECTATIONS, p.PROTOCOL, p.ASSUMPTIONS} <= fixed)
        atomic(self.root / p.MANIFEST, self.m)
        baseline = self.root / p.BASELINE
        original = baseline.read_bytes()
        baseline.write_bytes(original + b'-- changed\n')
        with self.assertRaises(ValueError):
            p.validate_manifest(self.root)
        atomic(self.root / p.MANIFEST, self.m)
        old = copy.deepcopy(self.m)
        old['commands'][2]['stages']['proof'][-1] = 'Baseline.lean'
        atomic(self.root / p.MANIFEST, old)
        with self.assertRaises(ValueError):
            p.validate_manifest(self.root)

    def test_wal_rejects_reset_and_orphan_is_not_replayed(self):
        p.execute(self.root)
        ledger = p.Ledger(self.root / p.OUT / 'execution')
        original = ledger.path.read_bytes()
        ledger.path.write_bytes(original[:-1])
        with self.assertRaises(ValueError):
            ledger.read()
        ledger.path.write_bytes(original)
        # Crash after the second reservation has durably been recorded.
        self.launch.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            p.execute(self.root, resume=True)
        self.launch.side_effect = self.fake
        recovered = p.execute(self.root, resume=True)
        self.assertTrue(recovered['attempts'][1]['terminal']['orphan'])
        self.assertEqual(recovered['attempts'][1]['terminal']['charged_seconds'],
                         recovered['attempts'][1]['reservation']['reserved_seconds'])
        self.assertEqual(recovered['attempts'][-1]['reservation']['phase'], 'baseline')


if __name__ == '__main__':
    unittest.main()
