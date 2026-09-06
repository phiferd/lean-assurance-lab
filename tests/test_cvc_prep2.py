"""Adversarial CVC preparation tests. Real fixtures are Python only, at most .5s."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc_prep2 as p


def start():
    return [{'kind': 'RESERVED', 'number': 0, 'module': 'START', 'reserved_seconds': 0},
            {'kind': 'TERMINAL', 'number': 0, 'status': 'COMPLETE', 'charged_seconds': 0}]


def reservation(n=1, seconds=300):
    return {'kind': 'RESERVED', 'number': n, 'module': 'Batteries.M' + str(n), 'reserved_seconds': seconds}


def terminal(n=1, status='COMPLETE', seconds=1):
    return {'kind': 'TERMINAL', 'number': n, 'status': status, 'charged_seconds': seconds}


class LedgerTests(unittest.TestCase):
    def test_hash_chain_rejects_tampering_and_truncation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'events'
            for row in start() + [reservation(), terminal()]:
                p.append(path, row)
            data = path.read_bytes()
            self.assertEqual(p.derive(p.read_events(path))[1]['terminal']['status'], 'COMPLETE')
            for changed in [data.replace(b'COMPLETE', b'FAILED'), data[:-1], b'{}\n']:
                path.write_bytes(changed)
                with self.assertRaises(ValueError):
                    p.read_events(path)

    def test_duplicate_reservation_terminal_and_order_rejected(self):
        cases = [start() + [reservation(), reservation()], start() + [reservation(2)],
                 start() + [reservation(), terminal(), terminal()],
                 start() + [reservation(), terminal(status='FAILED'), reservation(2)],
                 start() + [reservation(), reservation(2)], [reservation()],
                 start() + [reservation(seconds=301)], start() + [reservation(), terminal(seconds=math.inf)]]
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                p.derive(rows)

    def test_orphan_preserves_reservation(self):
        state = p.derive(start() + [reservation(seconds=13)])
        self.assertNotIn('terminal', state[1])
        self.assertEqual(state[1]['reserved_seconds'], 13)

    def test_lock_rejects_concurrent_owner(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'owner.lock'
            one = p.lock(path)
            try:
                with self.assertRaisesRegex(ValueError, 'concurrent'):
                    p.lock(path)
            finally:
                one.close()


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 6, tzinfo=timezone.utc)
        self.work = {'sessions': [{'started_at': self.now.isoformat(), 'ended_at': None}]}

    def budget(self, state=None, work=None):
        return p.attempt_budget(work or self.work, state or {}, self.now)

    def test_deadlines_include_session_and_compilation_subcaps(self):
        self.assertEqual(self.budget(), 300)
        state = {n: {'reserved_seconds': 300, 'terminal': {'charged_seconds': 300}} for n in range(1, 9)}
        state[9] = {'reserved_seconds': 300, 'terminal': {'charged_seconds': 500}}
        self.assertEqual(self.budget(state), 100)
        self.work['sessions'][0]['started_at'] = (self.now - timedelta(seconds=5399)).isoformat()
        self.assertEqual(self.budget(state), 1)

    def test_attempt_11_and_exhausted_compile_rejected(self):
        for state in [{n: {'reserved_seconds': 0} for n in range(1, 11)},
                      {n: {'reserved_seconds': 300} for n in range(1, 11)},
                      {1: {'reserved_seconds': math.inf}}]:
            with self.assertRaises(ValueError):
                self.budget(state)

    def test_two_session_total_and_third_session_rejection(self):
        old = self.now - timedelta(seconds=10800)
        work = {'sessions': [{'started_at': old.isoformat(), 'ended_at': (old + timedelta(seconds=5400)).isoformat()},
                             {'started_at': (old + timedelta(seconds=5400)).isoformat(), 'ended_at': None}]}
        with self.assertRaises(ValueError):
            self.budget(work=work)
        work['sessions'][1]['started_at'] = (self.now - timedelta(seconds=5399)).isoformat()
        self.assertEqual(self.budget(work=work), 1)
        work['sessions'].append({'started_at': self.now.isoformat(), 'ended_at': None})
        with self.assertRaises(ValueError):
            self.budget(work=work)

    def test_reversed_overlong_and_closed_sessions_rejected(self):
        for session in [{'started_at': (self.now + timedelta(seconds=1)).isoformat(), 'ended_at': None},
                        {'started_at': (self.now - timedelta(seconds=5401)).isoformat(), 'ended_at': None},
                        {'started_at': self.now.isoformat(), 'ended_at': self.now.isoformat()}]:
            with self.assertRaises(ValueError):
                self.budget(work={'sessions': [session]})


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / p.MANIFEST
        self.mods, self.order, donors = {}, [], []
        for kind, prefix, count in [('batteries', 'Batteries', 25), ('lean4lean', 'Lean4Lean', 12)]:
            donor = self.root / ('donor-' + kind)
            files = []
            for n in range(count):
                module = prefix + '.M' + str(n)
                if prefix == 'Batteries' and n == 1:
                    module = 'Batteries.M0.Nested'
                rel = module.replace('.', '/') + '.lean'
                source = donor / rel
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text('def value' + str(n) + ' := ' + str(n) + '\n')
                row = {'path': str(source), 'bytes': source.stat().st_size, 'sha256': p.sha(source)}
                self.mods[module] = {'module': module, 'kind': kind, 'imports': [], 'source': row}
                self.order.append(module)
                files.append({'module': module, 'path': rel, 'bytes': row['bytes'], 'sha256': row['sha256']})
            donors.append({'root': str(donor), 'files': files})
        runtime = self.root / 'runtime'
        (runtime / 'bin').mkdir(parents=True)
        (runtime / 'bin/lean').write_text('inert binary identity; never executed')
        self.write(p.PROPOSAL, {'runtime': {'path': str(runtime), 'lean_binary': {'sha256': p.sha(runtime / 'bin/lean')}}})
        self.write(p.CLOSURE, {'closure': {'modules': list(self.mods.values()), 'topological_noncore_order': self.order}})
        self.write(p.PRIOR + '/runtime-manifest.json', {'runtime_root': str(runtime)})
        self.write(p.OUT + '/initial-work-record.json', {'sessions': [{'started_at': p.now(), 'ended_at': None}]})
        for rel in ['lib/cvc_prep2.py', 'tests/test_cvc_prep2.py', 'lib/cvc_prep_binding.py', 'lib/research_queue.py',
                    'scripts/bind-cvc-u1-successor', 'scripts/prepare-cvc-u1-successor', p.OUT + '/inert-test-receipt.json']:
            self.write(rel, {})
        b = lambda rel: {'path': rel, 'sha256': p.sha(self.root / rel)}
        self.m = {'schema_version': 1, 'item_id': p.ITEM, 'run_id': p.RUN,
                  'source_closure': b(p.CLOSURE), 'runtime_manifest': b(p.PRIOR + '/runtime-manifest.json'),
                  'work_record': b(p.OUT + '/initial-work-record.json'), 'controller': b('lib/cvc_prep2.py'),
                  'tests': b('tests/test_cvc_prep2.py'), 'limits': p.LIMITS,
                  'immutable_bindings': [b(rel) for rel in ['lib/cvc_prep_binding.py', 'lib/research_queue.py', 'scripts/bind-cvc-u1-successor',
                    'scripts/prepare-cvc-u1-successor', p.PROPOSAL, p.OUT + '/inert-test-receipt.json']],
                  'materialization': {'root': p.BASE, 'source_root': p.BASE + '/src', 'build_root': p.BASE + '/build/lib/lean',
                                      'tmp_root': p.BASE + '/tmp', 'donors': donors},
                  'ledger_root': p.OUT + '/execution',
                  'compiler': {'path': str(runtime / 'bin/lean'), 'sha256': p.sha(runtime / 'bin/lean'), 'argv_prefix': ['-o'],
                    'env': {'LEAN_SYSROOT': str(runtime), 'LEAN_PATH': str(self.root / p.BASE / 'build/lib/lean') + ':' + str(runtime / 'lib/lean'),
                            'PATH': str(runtime / 'bin') + ':/usr/bin:/bin', 'TMPDIR': str(self.root / p.BASE / 'tmp'), 'LANG': 'C.UTF-8'}}}
        prior_outputs = []
        for n, module in enumerate(self.order[:27]):
            for suffix in ['.olean', '.ir', '.olean.server', '.olean.private'] + (['.extra'] if n < 11 else []):
                dest = self.root / p.PRIOR_BASE / (module.replace('.', '/') + suffix)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(b'olean' if suffix == '.olean' else suffix.encode())
                prior_outputs.append({'path': str(dest.relative_to(self.root)), 'bytes': dest.stat().st_size,
                                      'sha256': p.sha(dest)})
        self.write(p.PRIOR + '/result.json', {'item_id': 'CVC-PREP-1', 'outcome': 'BOUNDED_UNRESOLVED',
                   'completed_modules': 27, 'compilation_attempts': 27,
                   'attempts': [{'module': module, 'status': 'COMPLETE'} for module in self.order[:27]],
                   'outputs': prior_outputs})
        self.write(p.SUCCESSOR, {'remaining_order': self.order[27:]})
        self.m['immutable_bindings'].append(b(p.SUCCESSOR))
        self.m['predecessor'] = b(p.PRIOR + '/result.json')
        self.m['seed_outputs'] = p.relocated_outputs(prior_outputs)
        self.write(p.OUT + '/command-manifest.json', p.commands(self.root, self.m, self.order[27:]))
        self.m['commands'] = b(p.OUT + '/command-manifest.json')
        self.save()

    def write(self, rel, obj):
        dest = self.root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(obj))

    def save(self):
        self.write(p.MANIFEST, self.m)

    def fake(self, argv, cwd, env, stdout, stderr, deadline):
        state = p.derive(p.read_events(self.root / self.m['ledger_root'] / 'events.jsonl'))
        row = state[max(state)]
        self.assertNotIn('terminal', row)  # Reservation is durable before this call.
        self.assertEqual(row['argv'], argv)
        self.assertEqual(row['cwd'], str(cwd))
        self.assertIn('source_sha256', row)
        out = Path(argv[2])
        out.write_bytes(b'olean')
        out.with_suffix('.ir').write_bytes(b'ir')
        Path(str(out) + '.server').write_bytes(b'server')
        stdout.write_bytes(b'ok')
        stderr.write_bytes(b'')
        return {'status': 'COMPLETE', 'returncode': 0, 'charged_seconds': .01,
                'started_at': p.now(), 'ended_at': p.now(), **p.log_receipt(stdout, stderr)}

    def run_fake(self, resume=False, side_effect=None):
        with patch.object(p, 'runtime'), patch.object(p, 'committed'), patch.object(p, 'gate'), \
             patch.object(p.subprocess, 'check_output', return_value='a' * 40 + '\n'), \
             patch.object(p, 'run_process', side_effect=side_effect or self.fake) as launched:
            result = p.execute(self.root, self.path, resume)
        return result, launched.call_count

    def test_full_order_sidecars_once_and_successful_resume_no_replay(self):
        self.assertEqual(self.run_fake(), (0, 10))
        self.assertEqual(self.run_fake(resume=True), (0, 0))
        state = p.derive(p.read_events(self.root / self.m['ledger_root'] / 'events.jsonl'))
        self.assertEqual(sum(len(r['terminal'].get('outputs', [])) for r in state.values()), 30)
        self.assertAlmostEqual(sum(r['terminal']['charged_seconds'] for r in state.values()), .10)

    def test_failure_stops_and_cannot_retry(self):
        def failed(*args):
            result = self.fake(*args)
            result['status'], result['returncode'] = 'FAILED', 7
            return result
        self.assertEqual(self.run_fake(side_effect=failed), (1, 1))
        self.assertEqual(self.run_fake(resume=True), (1, 0))

    def test_later_failure_preserves_successes_and_never_replays(self):
        calls = []
        def fail_third(*args):
            calls.append(args[0])
            result = self.fake(*args)
            if len(calls) == 3:
                result['status'], result['returncode'] = 'FAILED', 7
            return result
        self.assertEqual(self.run_fake(side_effect=fail_third), (1, 3))
        self.assertEqual(self.run_fake(resume=True), (1, 0))
        state = p.derive(p.read_events(self.root / self.m['ledger_root'] / 'events.jsonl'))
        self.assertEqual(list(state), [0, 1, 2, 3])
        expected = p.verify_prior_outputs(self.root, state, seed=self.m['seed_outputs'])
        self.assertEqual(len(expected), 125)
        self.assertEqual([state[n]['terminal']['status'] for n in [1, 2, 3]], ['COMPLETE', 'COMPLETE', 'FAILED'])

    def test_control_failure_is_terminal_after_inputs_restored(self):
        source = Path(self.mods[self.order[-1]]['source']['path'])
        original = source.read_bytes(); source.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'donor mismatch'): self.run_fake()
        source.write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'recorded first control stop'): self.run_fake()
        self.assertFalse((self.root / p.BASE).exists())
        self.assertEqual(p.js(self.root / p.OUT / 'execution/stop.json')['status'], 'CONTROL_STOP')
        with self.assertRaisesRegex(ValueError, 'recorded first control stop'):
            p.preflight(self.root, self.path)

    def test_changed_dependency_and_unrecorded_output_rejected(self):
        self.run_fake()
        dest = self.root / p.BASE / 'build/lib/lean/Batteries/M0.olean'
        dest.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'output changed'):
            self.run_fake(resume=True)
        dest.write_bytes(b'olean')
        (dest.parent / 'unrecorded.ir').write_bytes(b'unknown')
        with self.assertRaisesRegex(ValueError, 'recorded first control stop'):
            self.run_fake(resume=True)
        with self.assertRaisesRegex(ValueError, 'unrecorded'):
            p.verify_output_set(self.root, self.root / self.m['materialization']['build_root'],
                                self.m['seed_outputs'] + [o for r in p.derive(p.read_events(self.root / self.m['ledger_root'] / 'events.jsonl')).values()
                                for o in r.get('terminal', {}).get('outputs', [])])

    def test_changed_source_and_runtime_stop_before_spawn(self):
        self.run_fake()
        source = self.root / p.BASE / 'src/Batteries/M0.lean'
        source.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            self.run_fake(resume=True)
        (self.root / p.OUT / 'execution/stop.json').unlink()
        with patch.object(p, 'runtime', side_effect=ValueError('runtime changed')), patch.object(p, 'gate'):
            with self.assertRaisesRegex(ValueError, 'runtime changed'):
                p.preflight(self.root, self.path)

    def test_orphan_conservatively_charged_and_no_replay(self):
        self.run_fake()
        ep = self.root / self.m['ledger_root'] / 'events.jsonl'
        rows = ep.read_bytes().splitlines(keepends=True)
        ep.write_bytes(b''.join(rows[:3]))  # START pair and attempt1 reservation.
        self.assertEqual(self.run_fake(resume=True), (1, 0))
        state = p.derive(p.read_events(ep))
        self.assertEqual(state[1]['terminal']['status'], 'INTERRUPTED')
        self.assertEqual(state[1]['terminal']['charged_seconds'], state[1]['reserved_seconds'])

    def test_missing_marker_or_ledger_cannot_reset(self):
        self.run_fake()
        (self.root / self.m['ledger_root'] / 'events.jsonl').unlink()
        for resume in [False, True]:
            with self.assertRaises(ValueError):
                self.run_fake(resume=resume)

    def test_extra_args_network_compiler_paths_and_modules_rejected(self):
        original = copy.deepcopy(self.m)
        mutations = [lambda: self.m['compiler']['argv_prefix'].append('--run'),
                     lambda: self.m['compiler'].__setitem__('path', '/usr/bin/curl'),
                     lambda: self.m['compiler']['env'].__setitem__('LEAN_PATH', '/arbitrary'),
                     lambda: self.m['materialization'].__setitem__('source_root', 'research/Lab'),
                     lambda: self.m['limits'].__setitem__('max_compilation_attempts', 11)]
        for mutate in mutations:
            self.m = copy.deepcopy(original)
            mutate(); self.save()
            with self.assertRaises(ValueError):
                p.validate_manifest(self.root, self.path)
        self.m = copy.deepcopy(original)
        closure = p.js(self.root / p.CLOSURE)
        closure['closure']['modules'][0]['module'] = 'Lab.Proof'
        closure['closure']['topological_noncore_order'][0] = 'Lab.Proof'
        self.write(p.CLOSURE, closure)
        self.m['source_closure']['sha256'] = p.sha(self.root / p.CLOSURE)
        self.save()
        with self.assertRaisesRegex(ValueError, 'Lab or unknown'):
            p.validate_manifest(self.root, self.path)

    def test_uncommitted_input_and_nonselected_item_rejected(self):
        with patch.object(p, 'gate'), patch.object(p, 'committed', side_effect=ValueError('uncommitted')):
            with self.assertRaisesRegex(ValueError, 'uncommitted'):
                p.validate_manifest(self.root, self.path, True)
        with patch('lib.research_queue.load_queue', return_value={'frontier_id': 'F-CONDITIONAL-VALIDATION-CONTRACTS',
                                                                'selected_item': 'CVC-3', 'items': []}):
            with self.assertRaisesRegex(ValueError, 'not selected'):
                p.gate(self.root)

    def test_preflight_never_materializes(self):
        with patch.object(p, 'runtime'), patch.object(p, 'gate'):
            self.assertEqual(p.preflight(self.root, self.path)['compiler_launches'], 0)
        self.assertFalse((self.root / p.BASE).exists())

    def test_exact_seed_mapping_and_only_remaining_launches(self):
        result, count = self.run_fake()
        self.assertEqual((result, count), (0, 10))
        state = p.derive(p.read_events(self.root / self.m['ledger_root'] / 'events.jsonl'))
        self.assertEqual([r['module'] for n, r in state.items() if n], self.order[27:])
        self.assertEqual(state[1]['prior_outputs'], self.m['seed_outputs'])
        self.assertEqual(len(state[1]['prior_outputs']), 119)
        self.assertEqual(len(p.verify_prior_outputs(self.root, state,
                         self.root / self.m['materialization']['build_root'], self.m['seed_outputs'])), 149)
        self.assertEqual(p.seed_inputs(self.root, self.m), p.js(self.root / p.PRIOR / 'result.json')['outputs'])

    def test_seed_invalid_before_any_destination_or_launch(self):
        original = p.js(self.root / p.PRIOR / 'result.json')['outputs'][0]
        path = self.root / original['path']
        data = path.read_bytes()
        extra = path.parent / 'unexpected.ir'
        for mutation in ['changed', 'missing', 'extra', 'symlink', 'extra_directory']:
            with self.subTest(mutation=mutation):
                if mutation == 'changed': path.write_bytes(b'changed')
                elif mutation == 'missing': path.unlink()
                elif mutation == 'extra': extra.write_bytes(b'unknown')
                elif mutation == 'extra_directory': extra.mkdir()
                else:
                    path.unlink(); path.symlink_to(extra)
                with patch.object(p, 'materialize') as copied, patch.object(p, 'run_process') as launched:
                    with self.assertRaises(ValueError): self.run_fake()
                    copied.assert_not_called(); launched.assert_not_called()
                self.assertFalse((self.root / p.BASE).exists())
                (self.root / p.OUT / 'execution/stop.json').unlink()
                if path.is_symlink(): path.unlink()
                path.write_bytes(data)
                if extra.is_dir(): extra.rmdir()
                elif extra.exists(): extra.unlink()

    def test_direct_materialization_rechecks_all_sources_runtime_and_seeds(self):
        with patch.object(p, 'runtime', side_effect=ValueError('changed runtime')):
            with self.assertRaisesRegex(ValueError, 'changed runtime'):
                p.materialize(self.root, self.m, self.mods)
        self.assertFalse((self.root / p.BASE).exists())
        source = Path(self.mods[self.order[-1]]['source']['path'])
        data = source.read_bytes(); source.write_bytes(b'changed')
        with patch.object(p, 'runtime'):
            with self.assertRaisesRegex(ValueError, 'donor mismatch'):
                p.materialize(self.root, self.m, self.mods)
        self.assertFalse((self.root / p.BASE).exists())
        source.write_bytes(data)

    def test_changed_predecessor_or_commands_cannot_be_rebound_to_new_scope(self):
        self.m['seed_outputs'].reverse(); self.save()
        with self.assertRaisesRegex(ValueError, 'seed output binding'):
            p.validate_manifest(self.root, self.path)
        self.m['seed_outputs'].reverse()
        cmd = p.js(self.root / self.m['commands']['path'])
        cmd['commands'][0]['module'] = self.order[0]
        self.write(self.m['commands']['path'], cmd)
        self.m['commands']['sha256'] = p.sha(self.root / self.m['commands']['path']); self.save()
        with self.assertRaisesRegex(ValueError, 'command manifest'):
            p.validate_manifest(self.root, self.path)


class OutputIdentityTests(unittest.TestCase):
    def test_mixed_namespace_and_module_order_is_irrelevant_but_bytes_are_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); build = root / 'build'; rows = []
            for rel in ['Pkg/Thing/A.olean', 'Pkg/Thing.olean', 'Pkg/Thing.olean.server']:
                path = build / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(rel.encode())
                rows.append({'path': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': p.sha(path)})
            self.assertNotEqual(p.inventory(root, build), sorted(rows, key=lambda r: r['path']))
            p.verify_output_set(root, build, list(reversed(rows)))
            for changed in [rows + [rows[0]], rows[:-1], [{**r, 'sha256': '0'*64} for r in rows]]:
                with self.assertRaises(ValueError): p.verify_output_set(root, build, changed)
            alias = build / 'alias'; alias.symlink_to(build / 'Pkg')
            with self.assertRaisesRegex(ValueError, 'symlink'): p.verify_output_set(root, build, rows)

    def test_relocation_rejects_escape_and_duplicate_paths(self):
        row = {'path': p.PRIOR_BASE + '/Pkg/M.olean', 'bytes': 1, 'sha256': 'a'*64}
        for rows in [[row, row], [{**row, 'path': '/absolute'}],
                     [{**row, 'path': p.PRIOR_BASE + '/../escape'}], [{**row, 'path': 'other/output'}]]:
            with self.assertRaises(ValueError): p.relocated_outputs(rows)


class BinderTests(unittest.TestCase):
    def test_binder_refuses_any_started_or_stopped_state(self):
        import runpy
        binder = runpy.run_path(str(ROOT / 'scripts/bind-cvc-u1-successor'))['main']
        for state_path in [p.OUT + '/execution/start.json', p.OUT + '/execution/stop.json',
                           p.OUT + '/execution/events.jsonl', p.BASE]:
            with self.subTest(state_path=state_path), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path = root / state_path; path.parent.mkdir(parents=True, exist_ok=True); path.touch()
                with patch.dict(binder.__globals__, ROOT=root):
                    with self.assertRaisesRegex(ValueError, 'cannot rebind'):
                        binder()


class ProcessTests(unittest.TestCase):
    """4 reserved fixture attempts per suite, including one child and a failed start."""
    def run_fixture(self, code=None, missing=False, timeout=.5, children=0):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            argv = ['/definitely/absent/cvc-fixture'] if missing else [sys.executable, '-c', code]
            ledger = os.environ.get('CVC_PREP_FIXTURE_LEDGER')
            if ledger:
                path = Path(ledger).resolve()
                rows = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
                used = sum(r.get('reserved_launches', 0) for r in rows)
                charged = sum(r.get('charged_seconds', 0) for r in rows)
                if charged + 5 * (1 + children) > 400 or timeout > 5:
                    raise AssertionError('CVC fixture process-time budget exhausted')
                require_count = 1 + children
                if used + require_count > 80:
                    raise AssertionError('CVC fixture launch budget exhausted')
                with path.open('a') as f:
                    f.write(json.dumps({'kind': 'RESERVED', 'reserved_launches': require_count,
                                        'reserved_seconds': 5 * require_count, 'at': p.now(), 'test': self.id()}) + '\n')
                    f.flush(); os.fsync(f.fileno())
            result = p.run_process(argv, root, {'PATH': '/usr/bin:/bin'}, root / 'stdout', root / 'stderr', timeout)
            text = (root / 'stdout').read_text()
            if ledger:
                with path.open('a') as f:
                    f.write(json.dumps({'kind': 'TERMINAL', 'charged_seconds': result['charged_seconds'],
                                        'status': result['status'], 'at': p.now(), 'test': self.id()}) + '\n')
            return result, text

    def test_real_success_and_failed_spawn_preserve_logs(self):
        result, text = self.run_fixture('print("fixture")')
        self.assertEqual((result['status'], text.strip()), ('COMPLETE', 'fixture'))
        result, _ = self.run_fixture(missing=True)
        self.assertEqual(result['status'], 'FAILED')
        self.assertIsNotNone(result['stdout_sha256'])

    def test_real_timeout_kills_process_group(self):
        # EOF on the grandchild's FIFO proves its descriptor was closed;
        # this needs neither network/ps access nor a process-table race.
        with tempfile.TemporaryDirectory() as temp:
            address = str(Path(temp) / 'child.fifo')
            os.mkfifo(address)
            reader = os.open(address, os.O_RDONLY | os.O_NONBLOCK)
            child_code = 'import os,time; fd=os.open(' + repr(address) + ',os.O_WRONLY); os.write(fd,b"ready"); time.sleep(4)'
            code = 'import subprocess,sys,time; child=subprocess.Popen([sys.executable,"-c",' + repr(child_code) + ']); print(child.pid,flush=True); time.sleep(4)'
            try:
                result, _ = self.run_fixture(code, children=1)
                self.assertEqual(result['status'], 'TIMED_OUT')
                self.assertEqual(os.read(reader, 5), b'ready')
                self.assertEqual(os.read(reader, 1), b'')
            finally:
                os.close(reader)

    def test_interruption_kills_group_and_preserves_charge(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            class Interrupted:
                pid, returncode = 12345, -2
                def wait(self, timeout=None):
                    raise KeyboardInterrupt
            with patch.object(p.subprocess, 'Popen', return_value=Interrupted()), patch.object(p, 'kill') as killed:
                result = p.run_process(['inert'], root, {}, root / 'stdout', root / 'stderr', 1)
            self.assertEqual(result['status'], 'INTERRUPTED')
            killed.assert_called_once()
            self.assertGreaterEqual(result['charged_seconds'], 0)


if __name__ == '__main__':
    unittest.main()
