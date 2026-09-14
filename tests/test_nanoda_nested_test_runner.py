"""Administrative launch-gate regressions; every subprocess/launch API is mocked."""
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'results/research/nanoda-nested-test-1/run-cell.py'
spec = importlib.util.spec_from_file_location('nested_test_run_cell_tests', RUNNER)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class LaunchGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / 'results/research/nanoda-nested-test-1'
        self.execution = self.base / 'execution'
        self.execution.mkdir(parents=True)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.input = self.root / 'input.txt'
        self.input.write_bytes(b'frozen input')
        self.cell = '001-focused'
        self.manifest = {
            'item_id': p.ITEM, 'cell_id': self.cell,
            'bindings': [{'path': str(self.input), 'sha256': p.digest(self.input.read_bytes())}],
            'cwd': str(self.source), 'source_revision': 'a' * 40,
            'patch_sha256': p.digest(b'frozen patch'), 'timeout_seconds': 120,
            'argv': ['never-executed'], 'environment': {},
        }
        self.path = self.execution / (self.cell + '-manifest.json')
        self.save_manifest()
        self.write(self.base / 'work-record.json', {'start_monotonic': 1000.0, 'started_at': '2026-09-13T00:00:00+00:00'})
        self.write(self.base / 'dependency-lock.json', {'files': [], 'packages': []})
        self.source_patch = b'frozen patch'
        self.untracked = b''
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(p, 'ROOT', self.root))
        stack.enter_context(patch.object(p, 'BASE', self.base))
        stack.enter_context(patch.object(p.sys, 'argv', ['run-cell.py', self.cell]))
        stack.enter_context(patch.object(p.time, 'monotonic', return_value=1100.0))
        self.clock = stack.enter_context(patch.object(p, 'datetime', wraps=datetime))
        self.clock.now.side_effect = lambda tz: datetime(2026, 9, 13, tzinfo=timezone.utc) + timedelta(seconds=p.time.monotonic() - 1000.0)
        self.git = stack.enter_context(patch.object(p.subprocess, 'check_output', side_effect=self.git_output))
        self.launch = stack.enter_context(patch.object(p, 'run_process', side_effect=AssertionError('unexpected scientific launch')))

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value))

    def save_manifest(self):
        self.path.write_text(json.dumps(self.manifest))
        self.committed = self.path.read_bytes()

    def git_output(self, argv, **kwargs):
        if argv[:2] == ['git', 'show']:
            return self.committed
        if argv == ['git', 'rev-parse', 'HEAD']:
            return (self.manifest['source_revision'] + '\n').encode()
        if argv == ['git', 'diff', '--binary', 'HEAD']:
            return self.source_patch
        if argv == ['git', 'ls-files', '--others', '--exclude-standard']:
            return self.untracked
        raise AssertionError('Unexpected subprocess request: ' + repr(argv))

    def refuse(self, message):
        with self.assertRaisesRegex((ValueError, FileExistsError), message):
            p.main()
        self.launch.assert_not_called()
        self.assertFalse((self.execution / self.cell).exists())

    def account(self, builds=0, tests=0, pending=None, reservations=None):
        self.write(self.execution / 'accounting.json', {
            'builds': builds, 'test_processes': tests, 'pending': pending,
            'reservations': reservations or [],
        })

    def test_uncommitted_manifest_refuses_before_spawn(self):
        self.committed = b'different committed manifest'
        self.refuse('manifest must be committed')

    def test_changed_input_refuses_before_spawn(self):
        self.input.write_bytes(b'changed after freeze')
        self.refuse('binding mismatch')

    def test_changed_source_patch_refuses_before_spawn(self):
        self.source_patch = b'changed patch'
        self.refuse('exact source patch')

    def test_untracked_source_refuses_before_spawn(self):
        self.untracked = b'unbound.rs\n'
        self.refuse('unexpected untracked source')

    def test_wrong_cell_identity_refuses_before_spawn(self):
        self.manifest['cell_id'] = '002-full'
        self.save_manifest()
        self.refuse('wrong cell identity')

    def test_full_reservation_must_fit_remaining_time(self):
        with patch.object(p.time, 'monotonic', return_value=6281.0):
            self.refuse('remaining active time')

    def test_process_ceiling_cannot_be_enlarged(self):
        self.manifest['timeout_seconds'] = 121
        self.save_manifest()
        self.refuse('remaining active time|process ceiling')

    def test_build_cap_refuses_before_spawn(self):
        self.account(builds=3, tests=3, reservations=[
            {'cell_id': str(n) + '-full', 'build_number': n, 'test_number': n, 'status': 'FAILED'}
            for n in range(1, 4)
        ])
        self.refuse('budget|cap|account|reservation')

    def test_test_cap_refuses_before_spawn(self):
        self.account(builds=3, tests=4, reservations=[
            {'cell_id': str(n) + '-full', 'build_number': n, 'test_number': n, 'status': 'FAILED'}
            for n in range(1, 5)
        ])
        self.refuse('budget|cap|account|reservation')

    def test_pending_reservation_refuses_before_spawn(self):
        self.account(builds=1, tests=1, pending='002-full', reservations=[
            {'cell_id': '002-full', 'build_number': 1, 'test_number': 1, 'status': 'RESERVED'}
        ])
        self.refuse('unreconciled|pending|account|reservation')

    def test_completed_reservation_cannot_be_reused(self):
        self.account(builds=1, tests=1, reservations=[
            {'cell_id': self.cell, 'build_number': 1, 'test_number': 1, 'status': 'FAILED'}
        ])
        self.refuse('reuse|account|reservation')

    def test_clock_rollback_refuses_before_spawn(self):
        with patch.object(p.time, 'monotonic', return_value=999.0):
            self.refuse('paired item clock disagreement')

    def test_disagreeing_clocks_refuse_before_spawn(self):
        self.clock.now.side_effect = lambda tz: datetime(2026, 9, 13, tzinfo=timezone.utc)
        self.refuse('paired item clock disagreement')

    def test_missing_account_with_prior_directory_refuses_before_spawn(self):
        (self.execution / '002-full').mkdir()
        self.refuse('missing accounting after reservation')

    def test_inconsistent_counts_refuse_before_spawn(self):
        self.account(builds=0, tests=0, reservations=[{'cell_id': '002-full'}])
        self.refuse('reservation count mismatch')

    def dependency(self):
        directory = self.root / 'dependency'
        directory.mkdir()
        source = directory / 'lib.rs'
        source.write_bytes(b'bound dependency')
        self.write(self.base / 'dependency-lock.json', {'packages': [{
            'source_root': str(directory),
            'files': [{'path': str(source), 'sha256': p.digest(source.read_bytes())}],
        }]})
        return source

    def test_changed_dependency_source_refuses_before_spawn(self):
        source = self.dependency()
        source.write_bytes(b'changed dependency')
        self.refuse('dependency source mismatch')

    def test_unbound_dependency_file_refuses_before_spawn(self):
        source = self.dependency()
        source.with_name('extra.rs').write_bytes(b'unbound dependency')
        self.refuse('dependency inventory mismatch')

    def test_durable_reservation_precedes_mock_launch(self):
        def observe(*args, **kwargs):
            account = json.loads((self.execution / 'accounting.json').read_text())
            self.assertEqual((account['builds'], account['test_processes'], account['pending']), (1, 1, self.cell))
            self.assertEqual(account['reservations'][0]['status'], 'RESERVED')
            raise RuntimeError('mock supervisor loss')
        self.launch.side_effect = observe
        with self.assertRaisesRegex(RuntimeError, 'mock supervisor loss'):
            p.main()
        self.launch.assert_called_once()
        account = json.loads((self.execution / 'accounting.json').read_text())
        self.assertEqual(account['pending'], self.cell)
        self.assertEqual(account['builds'], 1)

    def test_unbound_cargo_configuration_refuses_before_spawn(self):
        config = self.root / 'cargo-config.toml'
        config.write_text('[build]\n')
        self.manifest['absent_paths'] = [str(config)]
        self.save_manifest()
        self.refuse('unbound Cargo configuration')

    def test_cleanup_failure_keeps_reservation_pending(self):
        self.launch.side_effect = None
        self.launch.return_value = {'status': 'INTERRUPTED', 'returncode': 1,
                                    'cleanup_completed': False, 'deadline_exceeded': False}
        self.assertEqual(p.main(), 1)
        account = json.loads((self.execution / 'accounting.json').read_text())
        self.assertEqual(account['pending'], self.cell)
        self.assertEqual(account['builds'], 1)

    def test_deadline_failure_keeps_reservation_pending(self):
        self.launch.side_effect = None
        self.launch.return_value = {'status': 'TIMED_OUT', 'returncode': -9,
                                    'cleanup_completed': True, 'deadline_exceeded': True}
        self.assertEqual(p.main(), 1)
        account = json.loads((self.execution / 'accounting.json').read_text())
        self.assertEqual(account['pending'], self.cell)

    def test_ordinary_failed_build_stays_charged_and_allows_repair(self):
        self.launch.side_effect = None
        self.launch.return_value = {'status': 'FAILED', 'returncode': 101,
                                    'cleanup_completed': True, 'deadline_exceeded': False}
        self.assertEqual(p.main(), 1)
        account = json.loads((self.execution / 'accounting.json').read_text())
        self.assertIsNone(account['pending'])
        self.assertEqual((account['builds'], account['test_processes']), (1, 1))
        self.assertEqual(account['reservations'][0]['status'], 'FAILED')


if __name__ == '__main__':
    unittest.main()
