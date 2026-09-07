"""Pure adversarial CVC-3 protocol tests. Every compiler invocation is mocked."""
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
from lib import cvc_runner2 as p
from lib import cvc_runner_audit as a
from lib.cvc_process import atomic
from lib import cvc_fixture_budget as f
REAL_GATE = p.gate


def at(seconds):
    from datetime import datetime, timezone, timedelta
    return {'at': (datetime(2026, 9, 6, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
            'monotonic': 1000 + seconds}


def identity():
    return {'kind': 'START', 'run_id': p.RUN, 'manifest_sha256': 'a'*64, 'time': at(0)}


def start():
    return [identity(), {'kind': 'SESSION_START', 'number': 1, 'time': at(0)}]


def reservation(n=1, seconds=300, when=1):
    return {'kind': 'RESERVED', 'number': n, 'phase': 'signature' if n == 1 else 'proof',
            'session': 1, 'mode': 'proof', 'time': at(when), 'reserved_seconds': seconds}


def terminal(n=1, status='COMPLETE', **extra):
    return {'kind': 'TERMINAL', 'number': n, 'status': status, 'charged_seconds': 1,
            'returncode': 0 if status == 'COMPLETE' else 1, 'time': at(2),
            'outputs': [{'path': 'fixture.olean'}] if status == 'COMPLETE' else [], **extra}


def proof(mode='proof'):
    return 'import Contract\n\n' + '\n\n'.join(f'theorem {n} : {t} := by\n  exact True.intro' for n, t in a.targets(mode)) + '\n'


def stdout(mode='proof', axioms='[propext, Classical.choice, Quot.sound]'):
    return '\n'.join(f"'{n}' depends on axioms: {axioms}" for n in [n for n, _ in a.targets(mode)] + a.COMPARATORS) + '\n'


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = p.load(ROOT / p.ASSUMPTIONS)

    def test_fixed_types_and_generated_suffix_for_both_outcomes(self):
        for mode in ('proof', 'counterexample'):
            generated = a.generate(proof(mode), mode).decode()
            self.assertTrue(generated.endswith(a.suffix(mode)))
            result = a.audit(stdout(mode), '', self.assumptions, mode)
            self.assertEqual(len(result['transitive_axioms']), 6 if mode == 'proof' else 3)

    def test_missing_wrong_type_and_comment_spoof_rejected(self):
        data = proof()
        for bad in [data.replace(a.TARGETS[0][1], 'True'), data.replace(a.TARGETS[0][0], 'Lab.Other'),
                    'import Contract\n/- ' + data + ' -/\n',
                    data.replace('import Contract', '-- import Contract'), data + '\nimport Lean\n']:
            with self.subTest(bad=bad), self.assertRaises(ValueError): a.generate(bad)

    def test_new_axioms_native_trust_and_forged_printouts_rejected(self):
        for suffix in ['\naxiom wrong : False', '\n#eval IO.println "fake"', '\nrun_elab do pure ()',
                       '\nset_option debug.skipKernelTC true', '\nunsafe def x := 0', '\nattribute [implemented_by x] y']:
            with self.subTest(suffix=suffix), self.assertRaises(ValueError): a.generate(proof() + suffix)
        for body in ('sorry', 'admit', 'by native_decide', 'Lean.ofReduceBool true'):
            with self.subTest(body=body), self.assertRaises(ValueError): a.generate(proof().replace('True.intro', body))

    def test_nested_comments_do_not_create_false_declarations(self):
        self.assertEqual(a.strip_comments('/- a /- b -/ c -/\nX').strip(), 'X')
        with self.assertRaises(ValueError): a.strip_comments('/- unfinished')

    def test_empty_and_multiline_actual_transitive_subsets(self):
        names = [n for n, _ in a.TARGETS] + a.COMPARATORS
        result = a.audit('\n'.join(f"'{n}' does not depend on any axioms" for n in names), '', self.assumptions)
        self.assertTrue(all(not x for x in result['transitive_axioms'].values()))
        a.audit(stdout(axioms='[propext,\n Std.TreeMap.all_eq_all_toList, Lean.Level.normalize_eq]'), '', self.assumptions)

    def test_missing_duplicate_malformed_and_extra_reports_rejected(self):
        data = stdout()
        for bad in ['\n'.join(data.splitlines()[:-1]), data + data.splitlines()[0],
                    data.replace('Quot.sound]', 'Quot.sound'), data + "'Other' depends on axioms: []\n",
                    data.replace('[propext,', '[propext propext,'), data.replace('Classical.choice', 'propext')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): a.audit(bad, '', self.assumptions)

    def test_unlisted_single_and_dotted_axioms_and_sorry_rejected(self):
        for bad in ('extra', 'Lean.Level.mkData_eq', 'sorryAx', 'Lab.assumedTarget'):
            with self.subTest(axiom=bad), self.assertRaises(ValueError): a.audit(stdout(axioms='[' + bad + ']'), '', self.assumptions)
        with self.assertRaises(ValueError): a.audit(stdout(), "warning: declaration uses 'sorry'", self.assumptions)


class AccountingTests(unittest.TestCase):
    def test_thirteenth_attempt_is_rejected(self):
        rows = start()
        for n in range(1, 13): rows += [reservation(n), terminal(n, 'COMPLETE' if n == 1 else 'FAILED')]
        self.assertEqual(len(p.derive(rows)['attempts']), 12)
        with self.assertRaises(ValueError): p.derive(rows + [reservation(13)])

    def test_signature_failure_stops_but_proof_failure_allows_counted_repair(self):
        with self.assertRaises(ValueError): p.derive(start() + [reservation(), terminal(status='FAILED'), reservation(2)])
        state = p.derive(start() + [reservation(), terminal(), reservation(2), terminal(2, 'FAILED'), reservation(3)])
        self.assertEqual(len(state['attempts']), 3)

    def test_duplicate_or_out_of_order_reservation_and_terminal_rejected(self):
        for rows in [start()+[reservation(2)], start()+[reservation(), reservation()],
                     start()+[reservation(), terminal(), terminal()], start()+[terminal()],
                     start()+[reservation(seconds=301)], start()+[reservation(), terminal(charged_seconds=float('nan'))]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError): p.derive(rows)

    def test_orphan_cannot_be_undercharged_or_succeeded(self):
        for term in [terminal(status='INTERRUPTED', orphan=True), terminal(orphan=True, charged_seconds=300)]:
            with self.assertRaises(ValueError): p.derive(start()+[reservation(), term])
        state = p.derive(start()+[reservation(), terminal(status='INTERRUPTED', orphan=True, charged_seconds=300)])
        self.assertEqual(state['outcome'], 'BOUNDED_UNRESOLVED')

    def test_session_deadline_counts_design_time_and_clock_rollback(self):
        state = p.derive(start())
        self.assertEqual(p.budget(state, at(5399)), 1)
        for current in (at(5400), at(-1), {'at': at(1)['at'], 'monotonic': 0}):
            with self.subTest(current=current), self.assertRaises(ValueError): p.budget(state, current)

    def test_successful_terminal_after_session_budget_is_unresolved(self):
        rows = start() + [reservation(), terminal(), reservation(2, seconds=1, when=5399),
                         terminal(2, result='SUCCESS', axiom_audit={'checked': True}, time=at(5401))]
        state = p.derive(rows)
        self.assertEqual(state['outcome'], 'BOUNDED_UNRESOLVED')
        self.assertIn('active design budget', state['control_stop'])
        self.assertTrue(state['attempts'][-1]['terminal']['axiom_audit'])
        with self.assertRaises(ValueError): p.derive(rows+[reservation(3)])

    def test_terminal_audit_crossing_total_budget_persists_stop(self):
        rows = [identity()]
        for n in range(1, 4):
            rows += [{'kind': 'SESSION_START', 'number': n, 'time': at((n-1)*5400)},
                     {'kind': 'SESSION_END', 'number': n, 'time': at(n*5400), 'charged_seconds': 5400}]
        rows += [{'kind': 'SESSION_START', 'number': 4, 'time': at(16200)},
                 {**reservation(when=16201), 'session': 4}, terminal(time=at(16202)),
                 {**reservation(2, seconds=1, when=21599), 'session': 4},
                 terminal(2, result='SUCCESS', axiom_audit={'checked': True}, time=at(21601))]
        state = p.derive(rows)
        self.assertEqual(state['outcome'], 'BOUNDED_UNRESOLVED')
        self.assertIsNotNone(state['control_stop'])

    def test_four_sessions_total_and_fifth_start_rejected(self):
        rows = [identity()]
        for n in range(1, 5):
            rows += [{'kind': 'SESSION_START', 'number': n, 'time': at((n-1)*5400)},
                     {'kind': 'SESSION_END', 'number': n, 'time': at(n*5400), 'charged_seconds': 5400}]
        self.assertEqual(p.active_seconds(p.derive(rows), at(21600)), 21600)
        with self.assertRaises(ValueError): p.derive(rows + [{'kind': 'SESSION_START', 'number': 5, 'time': at(21600)}])

    def test_proof_success_prevents_another_attempt(self):
        rows = start()+[reservation(), terminal(), reservation(2), terminal(2, result='SUCCESS', axiom_audit={'checked': True})]
        self.assertEqual(p.derive(rows)['outcome'], 'SUCCESS')
        with self.assertRaises(ValueError): p.derive(rows+[reservation(3)])

    def test_wal_recovers_only_a_valid_suffix_and_refuses_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = p.Ledger(Path(temp)); ledger.initialize({k:v for k,v in identity().items() if k!='kind'})
            p.append(ledger.path, {'kind': 'SESSION_START', 'number': 1, 'time': at(0)})
            events, state = ledger.read()
            self.assertEqual(len(state['sessions']), 1)
            self.assertEqual(p.load(ledger.snapshot)['count'], 2)
            original = ledger.path.read_bytes()
            for changed in [original[:-1], original.splitlines(keepends=True)[0], original.replace(b'SESSION_START', b'SESSION_ENDED')]:
                ledger.path.write_bytes(changed)
                with self.assertRaises(ValueError): ledger.read()
            ledger.path.write_bytes(original)
            ledger.snapshot.unlink()
            with self.assertRaises(ValueError): ledger.read()


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for rel in set(p.FIXED) | set(p.CODE):
            dest = self.root / rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / rel, dest)
        self.m = p.build_manifest(self.root)
        atomic(self.root / p.MANIFEST, self.m)
        stack = contextlib.ExitStack(); self.addCleanup(stack.close)
        self.gate = stack.enter_context(patch.object(p, 'gate'))
        stack.enter_context(patch.object(p, 'committed'))
        self.runtime = stack.enter_context(patch.object(p, 'verify_payloads'))
        stack.enter_context(patch.object(p.subprocess, 'check_output', return_value='a'*40+'\n'))
        self.launch = stack.enter_context(patch.object(p, 'run_process', side_effect=self.fake))
        p.session(self.root)

    def fake(self, argv, cwd, env, directory, seconds, **kwargs):
        state = self.state()
        row = state['attempts'][-1]
        self.assertNotIn('terminal', row)
        self.assertEqual(row['reservation']['argv'], argv)
        self.assertEqual(row['reservation']['env'], env)
        self.assertEqual(kwargs['deadline_monotonic'], row['reservation']['time']['monotonic'] + seconds)
        self.assertEqual(p.sha(Path(cwd) / argv[3]), row['reservation']['input_sha256'])
        Path(argv[2]).write_bytes(b'compiled fixture')
        Path(argv[2]).with_suffix('.ir').write_bytes(b'fixture IR')
        (directory / 'stdout').write_text('' if len(state['attempts'])==1 else stdout(row['reservation']['mode']))
        (directory / 'stderr').write_text('')
        request = {'argv': argv, 'cwd': str(cwd), 'env': env, 'seconds': seconds,
                   'monotonic_started': row['reservation']['time']['monotonic'],
                   'started_at': row['reservation']['time']['at'], 'deadline_monotonic': kwargs['deadline_monotonic']}
        request['request_sha256'] = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        atomic(directory / 'request.json', request)
        term = {'status': 'COMPLETE', 'charged_seconds': .01, 'returncode': 0, 'cleanup_completed': True,
                'request_sha256': request['request_sha256'], 'stdout_sha256': p.sha(directory / 'stdout'),
                'stderr_sha256': p.sha(directory / 'stderr')}
        atomic(directory / 'supervisor.json', term)
        return term

    def state(self):
        return p.Ledger(self.root / p.OUT / 'execution').read()[1]

    def signature(self):
        return p.execute(self.root)

    def implementation(self, mode='proof'):
        (self.root / p.BASE / 'proof-input.lean').write_text(proof(mode))

    def test_signature_then_proof_success_and_no_completed_replay(self):
        self.assertEqual(len(self.signature()['attempts']), 1)
        self.implementation()
        result = p.execute(self.root, resume=True)
        self.assertEqual(result['outcome'], 'SUCCESS')
        self.assertEqual(p.execute(self.root, resume=True), result)
        self.assertEqual(self.launch.call_count, 2)

    def test_signature_failure_consumed_once_and_never_retried(self):
        def fail(*args, **kwargs):
            term = self.fake(*args, **kwargs); term.update(status='FAILED', returncode=7); return term
        self.launch.side_effect = fail
        self.assertEqual(self.signature()['outcome'], 'BOUNDED_UNRESOLVED')
        p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 1)

    def test_failed_proof_is_repaired_as_next_number(self):
        self.signature(); self.implementation()
        def wrong(*args, **kwargs):
            term = self.fake(*args, **kwargs); (args[3] / 'stdout').write_text(stdout(axioms='[extra]')); return term
        self.launch.side_effect = wrong
        self.assertEqual(p.execute(self.root, resume=True)['attempts'][-1]['terminal']['status'], 'FAILED')
        self.launch.side_effect = self.fake
        self.assertEqual(p.execute(self.root, resume=True)['outcome'], 'SUCCESS')
        self.assertEqual(len(self.state()['attempts']), 3)

    def test_counterexample_retains_negative_outcome(self):
        self.signature(); self.implementation('counterexample')
        self.assertEqual(p.execute(self.root, resume=True, mode='counterexample')['outcome'], 'NEGATIVE')

    def test_runtime_change_missing_promotion_and_concurrent_lock_prevent_launch(self):
        for dependency in (self.runtime, self.gate):
            dependency.side_effect = ValueError('changed')
            with self.assertRaises(ValueError): self.signature()
            dependency.side_effect = None
        owner = p.lock(self.root / p.OUT / 'controller.lock')
        try:
            with self.assertRaises(ValueError): self.signature()
        finally:
            owner.close()
        self.launch.assert_not_called()

    def test_missing_ledger_or_marker_cannot_reset_run(self):
        self.signature()
        (self.root / p.OUT / 'execution/state.json').unlink()
        for action in [lambda: p.session(self.root), lambda: p.execute(self.root, resume=True)]:
            with self.assertRaises(ValueError): action()
        self.assertEqual(self.launch.call_count, 1)

    def test_changed_signature_output_prevents_proof_launch(self):
        self.signature(); self.implementation()
        (self.root / p.BASE / 'Contract.olean').write_bytes(b'changed')
        with self.assertRaises(ValueError): p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 1)

    def test_changed_signature_source_and_dependency_argv_manifest_refused(self):
        self.signature(); self.implementation()
        (self.root / p.BASE / 'Contract.lean').write_bytes(b'changed')
        with self.assertRaises(ValueError): p.execute(self.root, resume=True)
        self.assertEqual(self.launch.call_count, 1)
        for mutate in [lambda m:m.update(run_id='OLD-RUN'), lambda m:m['limits'].update(attempts=13),
                       lambda m:m['environment'].update(LEAN_PATH='/extra'),
                       lambda m:m['commands'][1].append('--run'), lambda m:m.update(preparation_costs={}),
                       lambda m:m.update(controller_inputs=[]), lambda m:m['fixed_inputs'][0].update(sha256='0'*64)]:
            value = copy.deepcopy(self.m); mutate(value); atomic(self.root / p.MANIFEST, value)
            with self.assertRaises(ValueError): p.validate_manifest(self.root)

    def test_orphan_reconciliation_charges_once_and_does_not_replay(self):
        self.signature(); self.implementation()
        # Crash after reservation, before any supervisor/request is created.
        self.launch.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt): p.execute(self.root, resume=True)
        state = self.state(); reserved = state['attempts'][-1]['reservation']['reserved_seconds']
        self.assertNotIn('terminal', state['attempts'][-1])
        self.launch.side_effect = self.fake
        result = p.execute(self.root, resume=True)
        self.assertEqual(result['attempts'][1]['terminal']['status'], 'INTERRUPTED')
        self.assertEqual(result['attempts'][1]['terminal']['charged_seconds'], reserved)
        self.assertEqual(len(result['attempts']), 3)

    def test_orphan_guard_receipt_is_reconciled_with_full_charge(self):
        self.signature(); self.implementation()
        def crash(*args, **kwargs):
            self.fake(*args, **kwargs)
            raise KeyboardInterrupt
        self.launch.side_effect = crash
        with self.assertRaises(KeyboardInterrupt): p.execute(self.root, resume=True)
        self.launch.side_effect = self.fake
        result = p.execute(self.root, resume=True)
        orphan = result['attempts'][1]
        self.assertTrue(orphan['terminal']['orphan'])
        self.assertEqual(orphan['terminal']['charged_seconds'], orphan['reservation']['reserved_seconds'])
        self.assertTrue(orphan['terminal']['raw_files'])
        self.assertEqual(len(result['attempts']), 3)

    def test_missing_guard_receipt_waits_then_stops_without_new_launch(self):
        self.signature(); self.implementation()
        def crash(*args, **kwargs):
            self.fake(*args, **kwargs); (args[3] / 'supervisor.json').unlink()
            raise KeyboardInterrupt
        self.launch.side_effect = crash
        with self.assertRaises(KeyboardInterrupt): p.execute(self.root, resume=True)
        ledger = p.Ledger(self.root / p.OUT / 'execution'); state = self.state()
        with self.assertRaises(ValueError): p.recover(self.root, ledger, state)
        row = state['attempts'][-1]['reservation']
        with patch.object(p.time, 'monotonic', return_value=row['time']['monotonic']+row['reserved_seconds']+2):
            result = p.recover(self.root, ledger, state)
        self.assertIsNotNone(result['control_stop'])
        self.assertEqual(result['attempts'][-1]['terminal']['charged_seconds'], row['reserved_seconds'])
        self.assertEqual(self.launch.call_count, 2)

    def test_missing_olean_or_stdout_audit_cannot_pass(self):
        self.signature(); self.implementation()
        def missing(*args, **kwargs):
            result = self.fake(*args, **kwargs); Path(args[0][2]).unlink(); return result
        self.launch.side_effect = missing
        self.assertEqual(p.execute(self.root, resume=True)['attempts'][-1]['terminal']['status'], 'FAILED')

    def test_begin_end_sessions_use_append_only_design_accounting(self):
        p.session(self.root, end=True); p.session(self.root)
        state = self.state()
        self.assertEqual(len(state['sessions']), 2)
        self.assertIn('charged_seconds', state['sessions'][0])
        with self.assertRaises(ValueError): p.session(self.root)

    def test_immutable_change_during_launch_is_persistent_control_stop(self):
        self.signature(); self.implementation()
        target = self.root / p.SIGNATURE
        def changed(*args, **kwargs):
            result = self.fake(*args, **kwargs); target.write_bytes(b'changed'); return result
        self.launch.side_effect = changed
        result = p.execute(self.root, resume=True)
        self.assertIsNotNone(result['control_stop'])


class FixtureAccountingTests(unittest.TestCase):
    def rows(self):
        return [{'kind': 'RESERVED', 'number': 1, 'test': 'ProcessTests.test_failed_start_is_receipted',
                 'processes': 2, 'seconds_per_process': 5},
                {'kind': 'TERMINAL', 'number': 1, 'charged_seconds': 1, 'source_bindings_unchanged': True}]

    def test_source_change_or_nonfinite_charge_blocks_later_reservation(self):
        for field, value in [('source_bindings_unchanged', False), ('charged_seconds', float('nan')),
                             ('charged_seconds', 11)]:
            rows = self.rows(); rows[-1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): f.totals(rows)
        rows = self.rows(); rows[0]['processes'] = 1
        with self.assertRaises(ValueError): f.totals(rows)
        with self.assertRaises(ValueError): f.totals(self.rows()[:1])

    def test_fixture_identity_and_snapshot_reject_deletion_or_truncation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture-ledger.jsonl'
            f.read_accounting(path)
            for row in self.rows(): p.append(path, row)
            f.checkpoint(path, p.read_events(path))
            original = path.read_bytes()
            self.assertEqual(f.totals(f.read_accounting(path)), (2, 1))
            path.write_bytes(b'')
            with self.assertRaises(ValueError): f.read_accounting(path)
            path.write_bytes(original); path.unlink()
            with self.assertRaises(ValueError): f.read_accounting(path)


class EntryGateTests(unittest.TestCase):
    def test_unpromoted_gate_refuses_before_any_run_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch('lib.research_queue.load_queue', return_value={'frontier_id': 'wrong', 'selected_item': p.ITEM, 'items': []}):
                with self.assertRaises(ValueError): p.session(root)
            self.assertFalse((root / p.OUT).exists())
            self.assertFalse((root / p.BASE).exists())

    def test_promotion_requires_review_and_exact_committed_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rel in [p.MANIFEST, *p.CODE, *p.FIXED]:
                dest = root / rel; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(b'fixed')
            q = {'frontier_id': 'F-CONDITIONAL-VALIDATION-CONTRACTS', 'selected_item': p.ITEM,
                 'items': [{'id': p.ITEM, 'status': 'READY'}] + [
                    {'id': key, 'status': 'COMPLETE', 'closure': {'outcome': 'SUCCESS'}}
                    for key in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2')]}
            with patch('lib.research_queue.load_queue', return_value=q), patch.object(p, 'committed'), \
                    patch.object(p.subprocess, 'check_output', return_value=b'fixed') as git:
                with self.assertRaises(OSError): REAL_GATE(root)
                review = {'item_id': p.ITEM, 'decision': 'PROMOTE', 'run_id': p.RUN,
                          'manifest': p.binding(root, p.MANIFEST), 'implementation_checkpoint': 'a'*40}
                (root / p.ENTRY_REVIEW).parent.mkdir(parents=True, exist_ok=True)
                atomic(root / p.ENTRY_REVIEW, review); REAL_GATE(root)
                git.return_value = b'changed'
                with self.assertRaises(ValueError): REAL_GATE(root)
                git.return_value = b'fixed'; review['run_id'] = 'old'; atomic(root / p.ENTRY_REVIEW, review)
                with self.assertRaises(ValueError): REAL_GATE(root)


if __name__ == '__main__':
    unittest.main()
