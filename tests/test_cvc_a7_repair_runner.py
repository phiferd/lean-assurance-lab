"""Pure state and fully mocked runner tests; never launches Lean or a fixture."""
import contextlib
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lib import cvc_a7_repair_runner as p
from lib.cvc_process import atomic
from lib.cvc_runner_audit import TARGETS

ROOT = Path(__file__).resolve().parents[1]


def at(seconds):
    from datetime import datetime, timedelta, timezone
    return {'at': (datetime(2026, 9, 7, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
            'monotonic': 1000 + seconds}


def work():
    return {'intervals': [{'number': 1, 'start': at(0)}]}


def inputs(digest='a'):
    return [{'path': path, 'sha256': digest * 64} for path in p.CODE]


def start():
    return [{'kind': 'START', 'run_id': p.RUN, 'time': at(1), 'work': work()},
            {'kind': 'TOOLING_REVISION', 'number': 1, 'time': at(1), 'work': work(), 'inputs': inputs()}]


def reserve(number, phase, revision=1, when=None):
    when = number * 2 if when is None else when
    return {'kind': 'RESERVED', 'number': number, 'phase': phase, 'tooling_revision': revision,
            'time': at(when), 'work': work(), 'mode': 'proof', 'reserved_seconds': 300}


def terminal(number, status='COMPLETE', **kw):
    return {'kind': 'TERMINAL', 'number': number, 'status': status, 'charged_seconds': 1,
            'returncode': 0 if status == 'COMPLETE' else 1, 'time': at(number * 2 + 1),
            'outputs': [{'path': 'test.olean'}] if status == 'COMPLETE' else [], **kw}


class AccountingTests(unittest.TestCase):
    def test_clean_counted_baseline_required_before_proof(self):
        rows = start() + [reserve(1, 'signature'), terminal(1)]
        with self.assertRaises(ValueError):
            p.derive(rows + [reserve(2, 'proof')])
        with self.assertRaises(ValueError):
            p.derive(rows + [reserve(2, 'baseline'), terminal(2)])
        rows += [reserve(2, 'baseline'), terminal(2, baseline_audit={'ok': True})]
        self.assertEqual(p.phase(p.derive(rows)), 'proof')

    def test_parser_failure_pauses_until_changed_tooling_without_reset(self):
        rows = start() + [reserve(1, 'signature'), terminal(1), reserve(2, 'baseline'),
                          terminal(2, 'FAILED', repair_pause='parser format')]
        state = p.derive(rows)
        self.assertIsNone(state['outcome'])
        self.assertTrue(state['repair_pause'])
        with self.assertRaises(ValueError):
            p.derive(rows + [reserve(3, 'baseline')])
        revision = {'kind': 'TOOLING_REVISION', 'number': 2, 'time': at(6), 'work': work(), 'inputs': inputs('b')}
        state = p.derive(rows + [revision, reserve(3, 'baseline', revision=2, when=7)])
        self.assertEqual(len(state['attempts']), 3)
        self.assertIsNone(state['repair_pause'])
        with self.assertRaises(ValueError):
            p.derive(rows + [{**revision, 'inputs': inputs()}])

    def test_proof_compile_failure_allows_source_repair_same_tooling(self):
        rows = start() + [reserve(1, 'signature'), terminal(1), reserve(2, 'baseline'),
                          terminal(2, baseline_audit={'ok': True}), reserve(3, 'proof'), terminal(3, 'FAILED'),
                          reserve(4, 'proof')]
        self.assertEqual(len(p.derive(rows)['attempts']), 4)
        with self.assertRaises(ValueError):
            p.derive(rows + [terminal(4, 'FAILED'), reserve(5, 'proof')])

    def test_signature_compile_error_is_repair_pause_not_scientific_result(self):
        state = p.derive(start() + [reserve(1, 'signature'), terminal(1, 'FAILED', repair_pause='compile')])
        self.assertIsNone(state['outcome'])
        self.assertEqual(p.phase(state), 'signature')

    def test_semantic_mismatch_and_control_pause_are_distinct(self):
        state = p.derive(start() + [reserve(1, 'signature'), terminal(1, 'FAILED', scientific_mismatch=True)])
        self.assertEqual(state['outcome'], 'BOUNDED_UNRESOLVED')
        state = p.derive(start() + [reserve(1, 'signature'), terminal(1, 'TIMED_OUT', charged_seconds=300)])
        self.assertTrue(state['control_stop'])
        self.assertIsNone(state['outcome'])

    def test_unlimited_interval_count_charges_actual_cumulative_time(self):
        record = {'intervals': []}
        for number in range(1, 5):
            record['intervals'].append({'number': number, 'start': at(number*100), 'end': at(number*100+10), 'charged_seconds': 10})
        self.assertEqual(p.work_total(record, at(500), enforce_limits=True), 40)
        record['intervals'].append({'number': 5, 'start': at(600)})
        self.assertEqual(p.work_total(record, at(620), enforce_limits=True), 60)
        with self.assertRaises(ValueError):
            p.work_total(record, at(4300), enforce_limits=True)

    def test_work_start_and_closed_intervals_cannot_be_rewritten(self):
        original = work()
        tampered = work(); tampered['intervals'][0]['start'] = at(1)
        with self.assertRaises(ValueError):
            p.work_continuation(original, tampered)
        original['intervals'][0].update(end=at(10), charged_seconds=10)
        with self.assertRaises(ValueError):
            p.work_continuation(original, work())


    def test_late_closure_cannot_erase_observed_open_interval(self):
        previous = work()
        current = {'intervals': [{'number': 1, 'start': at(0), 'end': at(10), 'charged_seconds': 10},
                                 {'number': 2, 'start': at(220)}]}
        with self.assertRaises(ValueError):
            p.work_continuation(previous, current, at(210), at(230))
        rows = start() + [reserve(1, 'signature', when=200), terminal(1, time=at(210))]
        with self.assertRaises(ValueError):
            p.derive(rows + [{**reserve(2, 'baseline', when=230), 'work': current}])
        current['intervals'][0].update(end=at(215), charged_seconds=215)
        p.work_continuation(previous, current, at(210), at(230))

    def test_orphan_keeps_reservation_and_pauses_control(self):
        state = p.derive(start() + [reserve(1, 'signature'), terminal(1, 'INTERRUPTED', orphan=True, charged_seconds=300)])
        self.assertTrue(state['control_stop'])
        self.assertEqual(len(state['attempts']), 1)
        with self.assertRaises(ValueError):
            p.derive(start() + [reserve(1, 'signature'), terminal(1, 'INTERRUPTED', orphan=True, charged_seconds=1)])


class MockedControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for relative in set(p.FIXED) | set(p.CODE):
            source, dest = ROOT / relative, self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, dest)
        self.m = p.build_manifest(self.root); atomic(self.root / p.MANIFEST, self.m)
        current = p.stamp()
        record = {'item_id': p.ITEM, 'run_id': p.RUN, 'policy': p.POLICY, 'status': 'ACTIVE',
                  'intervals': [{'number': 1, 'start': current}], 'active_seconds_closed': 0}
        (self.root / p.WORK).parent.mkdir(parents=True, exist_ok=True)
        atomic(self.root / p.WORK, record)
        stack = contextlib.ExitStack(); self.addCleanup(stack.close)
        stack.enter_context(patch.object(p, 'gate')); stack.enter_context(patch.object(p, 'committed'))
        stack.enter_context(patch.object(p, 'verify_payloads'))
        self.git_snapshots = {}
        self.git_head = None
        stack.enter_context(patch.object(p.subprocess, 'check_output', side_effect=self.git))
        self.launch = stack.enter_context(patch.object(p, 'run_process', side_effect=self.fake))
        self.baseline = stack.enter_context(patch.object(p, 'audit_baseline', return_value={'baseline': True}))
        self.proof = stack.enter_context(patch.object(p, 'audit', return_value={'proof': True}))
        self.bound_audit = p.bound_audit
        self.original_parser = stack.enter_context(patch.object(p, 'bound_audit'))
        self.original_parser.return_value.baseline_source.side_effect = p.baseline_source
        self.original_parser.return_value.audit_baseline.return_value = {'baseline': True}
        self.original_parser.return_value.audit.return_value = {'proof': True}
        self.write_validation()
        p.adopt_revision(self.root, initial=True)

    def git(self, args, **kw):
        if args[:2] == ['git', 'rev-parse']:
            return self.git_head + '\n'
        if args[:2] == ['git', 'show']:
            checkpoint, path = args[2].split(':', 1)
            return self.git_snapshots[checkpoint][path]
        raise AssertionError('unexpected subprocess')

    def write_validation(self):
        self.git_head = str(len(self.git_snapshots) + 1) * 40
        self.git_snapshots[self.git_head] = {path: (self.root / path).read_bytes() for path in p.CODE}
        log = self.root / Path(p.VALIDATION).parent / 'focused.log'
        log.write_text('mock focused tests passed\n')
        atomic(self.root / p.VALIDATION, {'schema_version': 1, 'status': 'PASS', 'command': ['mocked-tests'],
               'returncode': 0, 'source_bindings': [p.binding(self.root, path) for path in p.CODE],
               'log': p.receipt(self.root, log)})

    def state(self):
        return p.Ledger(self.root / p.OUT / 'execution').read()[1]

    def fake(self, argv, cwd, env, directory, seconds, **kw):
        row = self.state()['attempts'][-1]['reservation']
        self.assertEqual(row['argv'], argv)
        self.assertEqual(kw['deadline_monotonic'], row['time']['monotonic'] + seconds)
        Path(argv[2]).write_bytes(b'compiled mocked product')
        (directory / 'stdout').write_text('mock audit\n'); (directory / 'stderr').write_text('')
        request = {'argv': argv, 'cwd': str(cwd), 'env': env, 'seconds': seconds,
                   'monotonic_started': row['time']['monotonic'], 'started_at': row['time']['at'],
                   'deadline_monotonic': kw['deadline_monotonic']}
        request['request_sha256'] = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        atomic(directory / 'request.json', request)
        result = {'status': 'COMPLETE', 'charged_seconds': .01, 'returncode': 0, 'cleanup_completed': True,
                  'request_sha256': request['request_sha256'], 'stdout_sha256': p.sha(directory / 'stdout'),
                  'stderr_sha256': p.sha(directory / 'stderr')}
        atomic(directory / 'supervisor.json', result)
        return result

    def proof_source(self):
        (self.root / p.BASE / 'proof-input.lean').write_text('import Contract\n' +
            '\n'.join(f'theorem {name} : {typ} := by exact True.intro' for name, typ in TARGETS))

    def test_three_stages_with_bound_signature_copy_and_archived_tooling(self):
        self.assertEqual(p.execute(self.root)['attempts'][-1]['reservation']['phase'], 'signature')
        self.assertTrue((self.root / p.BASE / 'Contract.olean').is_file())
        self.assertIsNone(p.execute(self.root, resume=True)['outcome'])
        self.proof_source()
        self.assertEqual(p.execute(self.root, resume=True)['outcome'], 'SUCCESS')
        self.assertEqual(self.launch.call_count, 3)
        self.assertEqual(len(self.state()['revisions']), 1)

    def test_parser_pause_new_tested_revision_then_counted_baseline(self):
        p.execute(self.root)
        self.baseline.side_effect = ValueError('parser format defect')
        failed = p.execute(self.root, resume=True)
        self.assertIsNone(failed['outcome']); self.assertTrue(failed['repair_pause'])
        p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 2)
        source = self.root / p.AUDIT
        source.write_text(source.read_text() + '\n# tested parser revision\n')
        self.write_validation(); p.adopt_revision(self.root)
        self.baseline.side_effect = None
        result = p.execute(self.root, resume=True)
        self.assertEqual(result['attempts'][-1]['reservation']['number'], 3)
        self.assertEqual(result['attempts'][-1]['reservation']['phase'], 'baseline')
        self.assertEqual(result['attempts'][-1]['reservation']['tooling_revision'], 2)
        self.assertEqual(result['attempts'][1]['terminal']['error'], 'parser format defect')

    def test_scientific_mismatch_does_not_become_parser_repair(self):
        p.execute(self.root); self.baseline.side_effect = p.ScientificMismatch('A7 mismatch')
        result = p.execute(self.root, resume=True)
        self.assertEqual(result['outcome'], 'BOUNDED_UNRESOLVED')
        self.assertIsNone(result['repair_pause'])

    def test_mutated_signature_or_old_archived_tooling_blocks_launch(self):
        p.execute(self.root)
        (self.root / p.BASE / 'Contract.olean').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 1)

    def test_same_revision_cannot_be_relabelled_as_repair(self):
        with self.assertRaises(ValueError):
            p.adopt_revision(self.root)
        self.assertEqual(len(self.state()['revisions']), 1)

    def test_stale_test_binding_and_manifest_limit_change_fail_closed(self):
        source = self.root / p.AUDIT; source.write_text(source.read_text() + '\n# changed\n')
        with self.assertRaises(ValueError):
            p.adopt_revision(self.root)
        changed = copy.deepcopy(self.m); changed['limits']['attempts'] = 5
        atomic(self.root / p.MANIFEST, changed)
        with self.assertRaises(ValueError):
            p.validate_manifest(self.root)

    def test_wal_and_workspace_identity_cannot_reset_counters(self):
        p.execute(self.root)
        ledger = p.Ledger(self.root / p.OUT / 'execution')
        ledger.path.write_bytes(ledger.path.read_bytes()[:-1])
        with self.assertRaises(ValueError):
            ledger.read()
        with self.assertRaises(ValueError):
            p.open_run(self.root, self.m, create=True)


    def test_proof_compile_feedback_retries_changed_source_without_tooling_revision(self):
        p.execute(self.root); p.execute(self.root, resume=True); self.proof_source()
        def failed(*args, **kw):
            result = self.fake(*args, **kw)
            result.update(status='FAILED', returncode=1)
            atomic(args[3] / 'supervisor.json', result)
            return result
        self.launch.side_effect = failed
        result = p.execute(self.root, resume=True)
        self.assertIsNone(result['repair_pause']); self.assertIsNone(result['control_stop'])
        source = self.root / p.BASE / 'proof-input.lean'
        source.write_text(source.read_text() + '\n')
        self.launch.side_effect = self.fake
        result = p.execute(self.root, resume=True)
        self.assertEqual(result['outcome'], 'SUCCESS')
        self.assertEqual(result['attempts'][-1]['reservation']['tooling_revision'], 1)
        self.assertNotEqual(result['attempts'][-1]['reservation']['source_sha256'],
                            result['attempts'][-2]['reservation']['source_sha256'])

    def test_timeout_reconciliation_keeps_failed_build_and_same_item(self):
        p.execute(self.root); p.execute(self.root, resume=True); self.proof_source()
        def timed_out(*args, **kw):
            result = self.fake(*args, **kw)
            result.update(status='TIMED_OUT', returncode=-9, charged_seconds=.01, deadline_exceeded=True)
            atomic(args[3] / 'supervisor.json', result)
            return result
        self.launch.side_effect = timed_out
        state = p.execute(self.root, resume=True)
        self.assertTrue(state['control_stop'])
        before = copy.deepcopy(state['attempts'])
        state = p.reconcile_control(self.root)
        self.assertIsNone(state['control_stop'])
        self.assertEqual(state['attempts'], before)
        self.assertEqual(len(state['reconciliations']), 1)
        self.launch.side_effect = self.fake
        self.assertEqual(p.execute(self.root, resume=True)['attempts'][-1]['reservation']['number'], 4)

    def test_unknown_orphan_cleanup_cannot_be_reconciled(self):
        self.launch.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            p.execute(self.root)
        self.launch.side_effect = self.fake
        p.execute(self.root, resume=True)
        with self.assertRaises(ValueError):
            p.reconcile_control(self.root)

    def test_archived_parser_replay_does_not_read_current_parser_bytes(self):
        revision = self.state()['revisions'][0]
        source = self.root / p.AUDIT
        source.write_text('raise RuntimeError("unbound live parser must not execute")\n')
        original = self.bound_audit(self.root, revision)
        self.assertEqual(original.A7, p.predecessor.audit.__globals__['A7'])
        self.assertTrue(callable(original.audit_baseline))

    def test_orphan_recovery_keeps_failed_slot_and_no_new_launch(self):
        p.execute(self.root)
        self.launch.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            p.execute(self.root, resume=True)
        self.launch.side_effect = self.fake
        state = p.execute(self.root, resume=True)
        self.assertEqual(len(state['attempts']), 2)
        self.assertTrue(state['attempts'][-1]['terminal']['orphan'])
        self.assertTrue(state['control_stop'])
        self.assertEqual(self.launch.call_count, 2)


if __name__ == '__main__':
    unittest.main()
