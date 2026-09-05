import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('refresh_current', str(ROOT / 'scripts/refresh-current-state'))
spec = importlib.util.spec_from_loader(loader.name, loader)
refresh = importlib.util.module_from_spec(spec)
loader.exec_module(refresh)


class RefreshCurrentStateTests(unittest.TestCase):
    def test_failure_stops_before_downstream_generation_and_preserves_log(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def runner(command, **kwargs):
                calls.append(command)
                kwargs['stdout'].write(b'mechanical diagnostic')
                return SimpleNamespace(returncode=7 if len(calls) == 2 else 0)
            log_dir = Path(directory) / 'attempt'
            self.assertEqual(refresh.refresh(log_dir, runner), 7)
            self.assertEqual(len(calls), 2)
            self.assertIn('FAILED', (log_dir / 'result.json').read_text())
            self.assertEqual((log_dir / '02-current-assurance-snapshot.log').read_bytes(), b'mechanical diagnostic')
            with self.assertRaises(FileExistsError):
                refresh.refresh(log_dir, runner)

    def test_refresh_order_attests_changed_producers_before_dependents(self):
        expected = ['build-artifact-graph', 'current-assurance-snapshot', 'build-artifact-graph',
                    'milestone-8-assurance', 'build-artifact-graph', 'render-public-status',
                    'build-artifact-graph', 'milestone-9-assurance', 'build-artifact-graph', 'artifact-status']
        self.assertEqual([Path(c[0]).name for c in refresh.COMMANDS], expected)
        self.assertEqual(refresh.COMMANDS[-1][1:], ['--require-current'])
        self.assertFalse(any('run-campaign' in c[0] or 'run-mutant' in c[0] for c in refresh.COMMANDS))
