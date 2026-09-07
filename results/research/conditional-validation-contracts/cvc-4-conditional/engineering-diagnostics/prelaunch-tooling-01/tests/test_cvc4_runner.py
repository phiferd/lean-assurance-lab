"""Pure observer-control regressions: every process and Git call is mocked."""
from copy import deepcopy
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lib import cvc4_runner as runner
from lib.cvc_prep import append, read_events


def clock(seconds):
    return {'at': (datetime(2026, 9, 7, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
            'monotonic': 1000. + seconds}


class ObserverRunnerTests(unittest.TestCase):
    def setUp(self):
        self.context = ExitStack()
        self.addCleanup(self.context.close)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.tick = 10
        self.proc_rc, self.proc_stdout, self.proc_stderr = 0, 'accepted\n', ''
        self.proc_overrides = {}
        self.process = self.context.enter_context(patch.object(runner, 'run_process', side_effect=self.fake_process))
        self.context.enter_context(patch.object(runner, 'gate'))
        self.context.enter_context(patch.object(runner, 'committed'))
        self.git = self.context.enter_context(patch.object(runner.subprocess, 'check_output', side_effect=self.fake_git))
        self.context.enter_context(patch.object(runner, 'stamp', side_effect=self.next_stamp))
        self.context.enter_context(patch.object(runner, 'signal_retry'))
        self.context.enter_context(patch('subprocess.Popen', side_effect=AssertionError('unreserved process prohibited in pure tests')))
        for relative in runner.CODE + ['input.txt', 'tooling.log', 'bin/observer']:
            self.write(relative, relative + '\n')
        self.work = {'item_id': runner.ITEM, 'status': 'ACTIVE', 'limits': runner.LIMITS,
                     'active_seconds_closed': 0, 'intervals': [{'number': 1, 'start': clock(0), 'end': None}]}
        self.write_json(runner.WORK, self.work)
        self.write_json('work-baseline.json', self.work)
        self.cells = [self.cell('control'), self.cell('candidate')]
        tooling = [self.binding(p) for p in runner.CODE]
        self.write_json('validation.json', {'status': 'PASS', 'returncode': 0,
                        'source_bindings': tooling, 'log': runner.file_receipt(self.root, self.root / 'tooling.log')})
        self.manifest = {'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.RUN,
                         'run_directory': runner.OUT, 'work_record': runner.WORK, 'limits': runner.LIMITS,
                         'fixed_inputs': [self.binding('input.txt')], 'tooling_inputs': tooling,
                         'payloads': [{'path': str(self.root / 'bin/observer'), 'sha256': runner.sha(self.root / 'bin/observer')}],
                         'work_baseline': self.binding('work-baseline.json'),
                         'validation_record': self.binding('validation.json'), 'cells': self.cells}
        self.save_manifest()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def write_json(self, relative, value):
        return self.write(relative, json.dumps(value, indent=2) + '\n')

    def binding(self, relative):
        return {'path': relative, 'sha256': runner.sha(self.root / relative)}

    def save_manifest(self):
        self.write_json(runner.MANIFEST, self.manifest)

    def cell(self, role, pair='pair1', implementation='one'):
        return {'id': pair + '-' + implementation + '-' + role, 'pair_id': pair,
                'implementation': implementation, 'role': role,
                'argv': [str(self.root / 'bin/observer'), str(self.root / 'input.txt')],
                'cwd': str(self.root), 'env': {'LANG': 'C'},
                'expected': {'returncode': 0, 'stdout_pattern': 'accepted\n', 'stderr_pattern': ''}}

    def fake_git(self, argv, **kwargs):
        if argv == ['git', 'rev-parse', 'HEAD']:
            return 'a' * 40 + '\n'
        self.assertEqual(argv[:2], ['git', 'show'])
        return (self.root / argv[2].split(':', 1)[1]).read_bytes()

    def next_stamp(self):
        value = clock(self.tick)
        self.tick += 1
        return value

    def fake_process(self, argv, cwd, env, directory, seconds, *, deadline_monotonic):
        events = read_events(self.root / runner.OUT / 'events.jsonl')
        reserved = events[-1]
        self.assertEqual(reserved['kind'], 'RESERVED')
        self.assertEqual(reserved['cell']['argv'], argv)
        request = {'argv': argv, 'cwd': str(cwd), 'env': env, 'seconds': seconds,
                   'started_at': reserved['time']['at'],
                   'monotonic_started': reserved['time']['monotonic'] + .01,
                   'deadline_monotonic': deadline_monotonic}
        request['request_sha256'] = runner.digest(request)
        self.write_json(str((directory / 'request.json').relative_to(self.root)), request)
        (directory / 'stdout').write_text(self.proc_stdout)
        (directory / 'stderr').write_text(self.proc_stderr)
        result = {'status': 'COMPLETE' if self.proc_rc == 0 else 'FAILED', 'returncode': self.proc_rc,
                  'charged_seconds': .5, 'started_at': request['started_at'], 'ended_at': clock(self.tick)['at'],
                  'monotonic_started': request['monotonic_started'],
                  'monotonic_ended': request['monotonic_started'] + .501,
                  'request_sha256': request['request_sha256'],
                  'stdout_sha256': runner.sha(directory / 'stdout'), 'stderr_sha256': runner.sha(directory / 'stderr'),
                  'cleanup_completed': True, 'deadline_exceeded': False, **self.proc_overrides}
        self.write_json(str((directory / 'supervisor.json').relative_to(self.root)), result)
        return result

    def begin(self):
        return runner.execute(self.root, 'begin-run')

    def ledger(self):
        return runner.Ledger(self.root / runner.OUT)

    def test_finite_matrix_completes_once_and_binds_prelaunch_reservations(self):
        self.begin()
        state = runner.execute(self.root, 'run')
        self.assertEqual(self.process.call_count, 2)
        self.assertTrue(all(r['terminal']['hypothesis_matched'] for r in state['attempts']))
        self.assertEqual([r['reservation']['number'] for r in state['attempts']], [1, 2])
        for row in state['attempts']:
            self.assertEqual(row['reservation']['reserved_seconds'], 30)
            self.assertEqual(row['reservation']['checkpoint'], 'a' * 40)
            self.assertEqual(row['terminal']['charged_seconds'], .5)
        with self.assertRaisesRegex(ValueError, 'finished'):
            runner.execute(self.root, 'attempt')
        with self.assertRaisesRegex(ValueError, 'cannot reset'):
            self.begin()
        summary = runner.validate_run(self.root)
        self.assertTrue(summary['matrix_complete'] and summary['hypotheses_all_matched'])
        self.assertEqual(summary['known_process_seconds'], 1.)

    def test_expected_nonzero_rejection_is_a_matched_observation(self):
        self.manifest['cells'][1]['expected'] = {'returncode': 101, 'stdout_pattern': '',
                                                'stderr_pattern': r"thread 'main' panicked: exact assertion\n"}
        self.save_manifest()
        self.begin()
        runner.execute(self.root)
        self.proc_rc, self.proc_stdout, self.proc_stderr = 101, '', "thread 'main' panicked: exact assertion\n"
        state = runner.execute(self.root)
        self.assertTrue(state['attempts'][-1]['terminal']['hypothesis_matched'])
        self.assertEqual(state['attempts'][-1]['terminal']['process_status'], 'FAILED')
        self.assertIsNone(state['control_stop'])

    def test_strict_signature_mismatch_stops_sequence(self):
        self.begin()
        self.proc_stdout += 'unexpected extra output\n'
        state = runner.execute(self.root, 'run')
        self.assertEqual(self.process.call_count, 1)
        self.assertTrue(state['hypothesis_mismatch'])
        self.assertIsNone(state['control_stop'])
        with self.assertRaisesRegex(ValueError, 'hypothesis mismatch'):
            runner.execute(self.root)

    def test_failed_control_cannot_authorize_candidate_after_reconciliation(self):
        self.begin()
        self.proc_overrides = {'status': 'TIMED_OUT', 'deadline_exceeded': True}
        state = runner.execute(self.root)
        self.assertIsNotNone(state['control_stop'])
        self.assertIsNone(state['attempts'][0]['terminal']['hypothesis_matched'])
        state = runner.reconcile_control(self.root)
        self.assertIsNone(state['control_stop'])
        with self.assertRaisesRegex(ValueError, 'successfully accepted control'):
            runner.execute(self.root)
        self.assertEqual(self.process.call_count, 1)

    def test_start_error_unknown_cost_stays_paused(self):
        self.begin()
        self.process.side_effect = OSError('fork failure')
        state = runner.execute(self.root)
        self.assertIsNone(state['attempts'][0]['terminal']['charged_seconds'])
        self.assertIn('fork failure', state['control_stop'])
        with self.assertRaisesRegex(ValueError, 'paused'):
            runner.execute(self.root)
        with self.assertRaises(OSError):
            runner.reconcile_control(self.root)
        self.assertIsNone(runner.validate_run(self.root)['known_process_seconds'])

    def test_cleanup_fault_cannot_be_reconciled(self):
        self.begin()
        self.proc_overrides = {'cleanup_completed': False, 'status': 'INTERRUPTED', 'error': 'cleanup failed'}
        state = runner.execute(self.root)
        self.assertEqual(state['attempts'][0]['terminal']['charged_seconds'], .5)
        self.assertIsNone(state['attempts'][0]['terminal']['hypothesis_matched'])
        with self.assertRaisesRegex(ValueError, 'cleanup remains'):
            runner.reconcile_control(self.root)

    def test_parent_loss_retains_pending_reservation_until_explicit_receipt_reconciliation(self):
        self.begin()
        original = self.fake_process
        def interrupted(*args, **kwargs):
            original(*args, **kwargs)
            raise KeyboardInterrupt()
        self.process.side_effect = interrupted
        with self.assertRaises(KeyboardInterrupt):
            runner.execute(self.root)
        self.assertNotIn('terminal', self.ledger().read()[1]['attempts'][0])
        with self.assertRaisesRegex(ValueError, 'pending reservation'):
            runner.execute(self.root)
        state = runner.reconcile_control(self.root)
        self.assertEqual(len(state['attempts']), 1)
        self.assertIsNone(state['attempts'][0]['terminal']['hypothesis_matched'])
        self.assertEqual(len(state['reconciliations']), 1)
        with self.assertRaisesRegex(ValueError, 'successfully accepted control'):
            runner.execute(self.root)

    def test_pending_without_receipts_cannot_be_zero_cost_or_replayed(self):
        self.begin()
        self.process.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            runner.execute(self.root)
        with self.assertRaises(OSError):
            runner.reconcile_control(self.root)
        self.assertTrue(runner.validate_run(self.root)['pending'])

    def test_mutated_supervisor_request_cannot_reconcile(self):
        self.begin()
        self.proc_overrides = {'status': 'TIMED_OUT', 'deadline_exceeded': True}
        runner.execute(self.root)
        request = self.root / runner.OUT / 'attempts/01/request.json'
        data = runner.load(request)
        data['argv'].append('unbound')
        request.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'receipt changed'):
            runner.reconcile_control(self.root)

    def test_runtime_tooling_and_fixed_input_mutations_prevent_launch(self):
        self.begin()
        for path in ('bin/observer', 'lib/cvc4_runner.py', 'input.txt'):
            with self.subTest(path=path):
                original = (self.root / path).read_text()
                (self.root / path).write_text('changed')
                with self.assertRaisesRegex(ValueError, 'changed'):
                    runner.execute(self.root)
                (self.root / path).write_text(original)
        self.process.assert_not_called()

    def test_rebound_manifest_cannot_replace_initial_hypotheses(self):
        self.begin()
        self.manifest['cells'][1]['expected']['stdout_pattern'] = 'different'
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'frozen manifest changed'):
            runner.execute(self.root)
        self.process.assert_not_called()

    def test_finite_matrix_constraints_and_absolute_argument_bindings(self):
        bad = [lambda m: m['limits'].update(validator_launches=17),
               lambda m: m['cells'][0]['argv'].append('/unbound/file'),
               lambda m: m['cells'].reverse(),
               lambda m: m['cells'][0]['expected'].update(returncode=1),
               lambda m: m['cells'].append(deepcopy(m['cells'][0])),
               lambda m: m['cells'].pop(),
               lambda m: m['tooling_inputs'].pop()]
        original = deepcopy(self.manifest)
        for mutate in bad:
            with self.subTest(mutation=mutate):
                self.manifest = deepcopy(original)
                mutate(self.manifest)
                self.save_manifest()
                with self.assertRaises(ValueError):
                    runner.validate_manifest(self.root)
        self.process.assert_not_called()

    def test_sixteen_launch_ceiling_is_enforced(self):
        self.manifest['cells'] = [self.cell(role, 'pair' + str(pair), implementation)
                                  for pair in range(4) for implementation in ('one', 'two')
                                  for role in ('control', 'candidate')]
        self.save_manifest()
        self.begin()
        state = runner.execute(self.root, 'run')
        self.assertEqual(len(state['attempts']), 16)
        with self.assertRaisesRegex(ValueError, 'cap exhausted'):
            runner.budget(state, clock(self.tick))
        with self.assertRaisesRegex(ValueError, 'finished'):
            runner.execute(self.root)
        self.assertEqual(self.process.call_count, 16)

    def test_live_interval_reservation_requires_full_timeout(self):
        self.begin()
        self.tick = 5371
        with self.assertRaisesRegex(ValueError, 'insufficient active budget'):
            runner.execute(self.root)
        self.process.assert_not_called()

    def test_cumulative_engineering_cap_includes_closed_intervals(self):
        self.work['intervals'] = [
            {'number': n + 1, 'start': clock(n * 5500), 'end': clock(n * 5500 + 5400), 'charged_seconds': 5400.}
            for n in range(2)] + [{'number': 3, 'start': clock(11000), 'end': None}]
        self.work['active_seconds_closed'] = 10800.
        self.write_json(runner.WORK, self.work)
        self.write_json('work-baseline.json', self.work)
        self.manifest['work_baseline'] = self.binding('work-baseline.json')
        self.save_manifest()
        self.tick = 16371
        self.begin()
        with self.assertRaisesRegex(ValueError, 'insufficient active budget'):
            runner.execute(self.root)
        self.process.assert_not_called()

    def test_engineering_start_and_observed_time_cannot_be_erased(self):
        self.begin()
        runner.execute(self.root)
        self.work['intervals'][0]['end'] = clock(5)
        self.work['intervals'][0]['charged_seconds'] = 5.
        self.work['intervals'].append({'number': 2, 'start': clock(6), 'end': None})
        self.work['active_seconds_closed'] = 5.
        self.write_json(runner.WORK, self.work)
        with self.assertRaisesRegex(ValueError, 'rollback|erased'):
            runner.execute(self.root)
        self.assertEqual(self.process.call_count, 1)

    def test_closed_intervals_are_immutable_and_utc_mono_both_monotone(self):
        previous = {'intervals': [{'number': 1, 'start': clock(0), 'end': clock(2), 'charged_seconds': 2.},
                                  {'number': 2, 'start': clock(3), 'end': None}]}
        new = deepcopy(previous)
        new['intervals'][0]['end'] = clock(1)
        new['intervals'][0]['charged_seconds'] = 1.
        with self.assertRaisesRegex(ValueError, 'closed engineering interval changed'):
            runner.work_continuation(previous, new, clock(4), clock(5))
        for field in ('at', 'monotonic'):
            backwards = clock(5)
            backwards[field] = clock(3)[field]
            with self.assertRaisesRegex(ValueError, 'rollback'):
                runner.work_continuation(previous, previous, clock(4), backwards)

    def test_accounting_failure_after_process_still_records_failed_terminal(self):
        self.begin()
        def damage(*args, **kwargs):
            result = self.fake_process(*args, **kwargs)
            self.work['intervals'][0]['start'] = clock(10)
            self.write_json(runner.WORK, self.work)
            return result
        self.process.side_effect = damage
        state = runner.execute(self.root)
        self.assertIn('work accounting failure', state['control_stop'])
        self.assertIn('terminal', state['attempts'][0])
        self.assertEqual(state['work']['intervals'][0]['start'], clock(0))
        self.assertIsNone(state['attempts'][0]['terminal']['hypothesis_matched'])

    def test_retained_output_mutation_prevents_next_launch(self):
        self.begin()
        runner.execute(self.root)
        (self.root / runner.OUT / 'attempts/01/stdout').write_text('modified')
        with self.assertRaisesRegex(ValueError, 'receipt changed'):
            runner.execute(self.root)
        self.assertEqual(self.process.call_count, 1)

    def test_ledger_truncation_and_snapshot_mutation_are_refused(self):
        self.begin()
        runner.execute(self.root)
        ledger = self.ledger()
        old = ledger.path.read_bytes()
        ledger.path.write_bytes(old.splitlines(keepends=True)[0])
        with self.assertRaisesRegex(ValueError, 'truncated'):
            ledger.read()
        ledger.path.write_bytes(old)
        snapshot = runner.load(ledger.snapshot)
        snapshot['state']['attempts'][0]['terminal']['charged_seconds'] = 0
        ledger.snapshot.write_text(json.dumps(snapshot))
        with self.assertRaisesRegex(ValueError, 'snapshot or ledger prefix'):
            ledger.read()

    def test_unreserved_duplicate_terminal_is_rejected(self):
        self.begin()
        runner.execute(self.root)
        events, state = self.ledger().read()
        with self.assertRaisesRegex(ValueError, 'duplicate or unreserved'):
            runner.derive(events + [state['attempts'][0]['terminal']])

    def test_clone_safe_read_only_replay_excludes_payload_availability(self):
        self.begin()
        runner.execute(self.root, 'run')
        (self.root / 'bin/observer').unlink()
        self.work['intervals'][0]['end'] = clock(self.tick)
        self.work['intervals'][0]['charged_seconds'] = float(self.tick)
        self.work['status'] = 'COMPLETE'
        self.work['active_seconds_closed'] = float(self.tick)
        self.write_json(runner.WORK, self.work)
        before = {p.name: p.read_bytes() for p in (self.root / runner.OUT).iterdir() if p.is_file()}
        summary = runner.validate_run(self.root, require_payloads=False)
        self.assertTrue(summary['hypotheses_all_matched'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.root / runner.OUT).iterdir() if p.is_file()})
        with self.assertRaises(ValueError):
            runner.validate_run(self.root)

    def test_clone_relocation_preserves_original_absolute_launch_paths(self):
        self.begin()
        runner.execute(self.root, 'run')
        original = self.root
        with tempfile.TemporaryDirectory() as destination:
            clone = Path(destination).resolve() / 'clone'
            shutil.copytree(original, clone)
            self.root = clone
            try:
                summary = runner.validate_run(clone, require_payloads=False)
                self.assertTrue(summary['hypotheses_all_matched'])
                self.assertEqual(summary['manifest']['cells'][0]['cwd'], str(original))
                with self.assertRaisesRegex(ValueError, 'absolute argv file'):
                    runner.validate_manifest(clone, require_payloads=True)
            finally:
                self.root = original


if __name__ == '__main__':
    unittest.main()
