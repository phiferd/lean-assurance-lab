"""Process tests are isolated from pure controls and use self-expiring fixtures."""
import json
import os
from pathlib import Path
import signal
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.cvc_process import run_process, sha
from lib.cvc_fixture_budget import fixture

FIXTURE = str(ROOT / 'tests/cvc_runner2_fixture.py')


class ProcessTests(unittest.TestCase):
    def invoke(self, directory, mode, seconds=1):
        return run_process([sys.executable, FIXTURE, mode], directory, {'PATH': '/usr/bin:/bin'}, directory, seconds)

    def gone(self, pid):
        for _ in range(25):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(.01)
        self.fail(f'fixture PID {pid} still exists after group cleanup')

    def test_success_retains_raw_logs_and_guard_receipt(self):
        with fixture(self.id(), 2) as (directory, recorded):
            result = self.invoke(directory, 'ok'); recorded.update(status=result['status'])
            self.assertEqual(result['status'], 'COMPLETE')
            self.assertEqual((directory / 'stdout').read_text(), 'inert stdout\n')
            self.assertEqual(result['stderr_sha256'], sha(directory / 'stderr'))
            self.assertTrue(result['cleanup_completed'])
            self.assertEqual(json.loads((directory / 'supervisor.json').read_text()), result)

    def test_failed_start_is_receipted(self):
        with fixture(self.id(), 2) as (directory, recorded):
            result = run_process(['/absent/cvc-fixture'], directory, {}, directory, 1)
            recorded.update(status=result['status'])
            self.assertEqual(result['status'], 'FAILED')
            self.assertIsNone(result['returncode'])
            self.assertTrue((directory / 'stdout').is_file())

    def test_cancellation_reaps_child_without_killing_test_controller(self):
        with fixture(self.id(), 2) as (directory, recorded):
            before = signal.getsignal(signal.SIGTERM)
            result = self.invoke(directory, 'cancel'); recorded.update(status=result['status'])
            self.assertEqual(result['status'], 'INTERRUPTED')
            self.assertEqual(signal.getsignal(signal.SIGTERM), before)
            self.gone(int((directory / 'stdout').read_text().strip()))

    def test_timeout_terminates_descendant_group(self):
        with fixture(self.id(), 3) as (directory, recorded):
            result = run_process([sys.executable, FIXTURE, 'descendant'], directory, {'PATH': '/usr/bin:/bin'},
                                 directory, 4, deadline_monotonic=time.monotonic() + .8)
            recorded.update(status=result['status'])
            self.assertEqual(result['status'], 'TIMED_OUT')
            self.assertLess(result['charged_seconds'], 1.5)
            for pid in (directory / 'stdout').read_text().split():
                self.gone(int(pid))

    def test_leaf_deadline_is_independent_of_supervisor_timeout(self):
        with fixture(self.id(), 2) as (directory, recorded):
            result = self.invoke(directory, 'sleep', 4); recorded.update(status=result['status'])
            self.assertEqual(result['returncode'], 124)
            self.assertLess(result['charged_seconds'], 3)

    def test_controller_sigkill_leaves_supervisor_cleanup_receipt(self):
        with fixture(self.id(), 4) as (directory, recorded):
            inner = directory / 'inner'
            result = run_process([sys.executable, FIXTURE, 'controller', str(inner)], directory,
                                 {'PATH': '/usr/bin:/bin'}, directory, 4)
            recorded.update(status=result['status'])
            self.assertEqual(result['returncode'], -signal.SIGKILL)
            for _ in range(50):
                if (inner / 'supervisor.json').exists():
                    break
                time.sleep(.01)
            child = json.loads((inner / 'supervisor.json').read_text())
            self.assertEqual(child['status'], 'INTERRUPTED')
            self.assertTrue(child['cleanup_completed'])
            self.gone(int((inner / 'stdout').read_text().strip()))


if __name__ == '__main__':
    unittest.main()
