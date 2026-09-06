"""Closure regressions: incomplete CVC-RUNNER-1 cannot launch or start CVC-3."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc_runner as runner


class DisabledRunnerTests(unittest.TestCase):
    def test_every_programmatic_entry_refuses_before_any_process_or_file_write(self):
        with tempfile.TemporaryDirectory() as temp, patch('subprocess.Popen') as launch:
            root = Path(temp)
            for entry in [runner.preflight, runner.execute, runner.start_session,
                          runner.end_session, runner.run_process]:
                with self.subTest(entry=entry), self.assertRaisesRegex(ValueError, 'BOUNDED_UNRESOLVED'):
                    entry(root)
            launch.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])

    def test_cli_refuses_all_prior_modes_and_cannot_enable_by_flag(self):
        with patch('subprocess.Popen') as launch:
            for mode in ['--preflight', '--attempt', '--resume', '--start-session', '--end-session', '--force']:
                with self.subTest(mode=mode), contextlib.redirect_stderr(io.StringIO()) as stream:
                    self.assertEqual(runner.main([mode]), 1)
                    self.assertIn('CVC-3 execution is disabled', stream.getvalue())
            launch.assert_not_called()

    def test_diagnostic_and_incomplete_draft_are_durable(self):
        self.assertTrue((ROOT / runner.DIAGNOSTIC).is_file())
        draft = ROOT / 'results/research/conditional-validation-contracts/cvc-runner-1/draft'
        self.assertTrue((draft / 'cvc_runner.py.txt').is_file())
        self.assertTrue((draft / 'test_cvc_runner.py.txt').is_file())


if __name__ == '__main__':
    unittest.main()
