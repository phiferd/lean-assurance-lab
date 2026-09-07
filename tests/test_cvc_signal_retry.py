"""Pure mocked Darwin signal regressions; no fixture, fork or signal launch."""
import errno
from pathlib import Path
import runpy
import signal
import sys
import unittest
from unittest.mock import Mock, patch

from lib import cvc_signal_retry as adapter

ROOT = Path(__file__).resolve().parents[1]


class SignalRetryTests(unittest.TestCase):
    def setUp(self):
        self.current = 100.
        self.clock = patch.object(adapter.time, 'monotonic', side_effect=lambda: self.current)
        self.sleep = patch.object(adapter.time, 'sleep', side_effect=self.advance)
        self.clock.start(); self.sleep.start()
        self.addCleanup(self.clock.stop); self.addCleanup(self.sleep.stop)

    def advance(self, seconds):
        self.assertGreater(seconds, 0)
        self.assertLessEqual(seconds, .001)
        self.current += seconds

    def denied(self):
        return PermissionError(errno.EPERM, 'Operation not permitted')

    def missing(self):
        return ProcessLookupError(errno.ESRCH, 'No such process')

    def test_success_passes_through_without_inspecting_process(self):
        kernel = Mock(return_value=None)
        with patch.object(adapter.os, 'getpgid') as inspect:
            self.assertIsNone(adapter._killpg_with_retry(kernel, 123, signal.SIGKILL))
        kernel.assert_called_once_with(123, signal.SIGKILL); inspect.assert_not_called()

    def test_transient_denial_retries_identical_signal_and_preserves_esrch(self):
        gone = self.missing()
        kernel = Mock(side_effect=[self.denied(), self.denied(), gone])
        with patch.object(adapter.os, 'getpgid', side_effect=self.missing()) as inspect:
            with self.assertRaises(ProcessLookupError) as result:
                adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertIs(result.exception, gone)
        self.assertEqual(kernel.call_count, 3)
        self.assertTrue(all(call.args == (123, signal.SIGKILL) for call in kernel.call_args_list))
        self.assertEqual(inspect.call_count, 4)

    def test_transient_denial_can_return_real_kernel_success(self):
        kernel = Mock(side_effect=[self.denied(), None])
        with patch.object(adapter.os, 'getpgid', side_effect=self.missing()):
            self.assertIsNone(adapter._killpg_with_retry(kernel, 123, signal.SIGTERM))
        self.assertEqual(kernel.call_count, 2)

    def test_existing_or_reused_leader_propagates_original_denial(self):
        denial = self.denied(); kernel = Mock(side_effect=denial)
        with patch.object(adapter.os, 'getpgid', return_value=123):
            with self.assertRaises(PermissionError) as result:
                adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertIs(result.exception, denial); self.assertEqual(kernel.call_count, 1)

    def test_unknown_leader_inspection_does_not_authorize_retry(self):
        denial = self.denied(); kernel = Mock(side_effect=denial)
        with patch.object(adapter.os, 'getpgid', side_effect=PermissionError(errno.EPERM, 'inspection denied')):
            with self.assertRaises(PermissionError) as result:
                adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertIs(result.exception, denial); self.assertEqual(kernel.call_count, 1)

    def test_leader_reappearance_stops_further_retries(self):
        denial = self.denied(); kernel = Mock(side_effect=denial)
        with patch.object(adapter.os, 'getpgid', side_effect=[self.missing(), 123]):
            with self.assertRaises(PermissionError) as result:
                adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertIs(result.exception, denial); self.assertEqual(kernel.call_count, 1)

    def test_other_errors_pass_through_without_retry_or_inspection(self):
        for error in (self.missing(), OSError(errno.EINVAL, 'invalid signal')):
            with self.subTest(error=error):
                kernel = Mock(side_effect=error)
                with patch.object(adapter.os, 'getpgid') as inspect:
                    with self.assertRaises(OSError) as result:
                        adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
                self.assertIs(result.exception, error)
                self.assertEqual(kernel.call_count, 1); inspect.assert_not_called()

    def test_persistent_denial_propagates_within_fixed_retry_bound(self):
        denial = self.denied(); times = []
        def kernel(group, sig):
            times.append(self.current)
            raise denial
        with patch.object(adapter.os, 'getpgid', side_effect=self.missing()):
            with self.assertRaises(PermissionError) as result:
                adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertIs(result.exception, denial)
        self.assertLessEqual(len(times), adapter.MAX_RETRIES + 1)
        self.assertTrue(all(t < 100. + adapter.RETRY_SECONDS for t in times))
        self.assertLessEqual(adapter.RETRY_SECONDS, .05)

    def test_nonadvancing_clock_still_has_finite_retry_count(self):
        kernel = Mock(side_effect=self.denied())
        with patch.object(adapter.time, 'sleep'):
            with patch.object(adapter.os, 'getpgid', side_effect=self.missing()):
                with self.assertRaises(PermissionError):
                    adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertEqual(kernel.call_count, adapter.MAX_RETRIES + 1)

    def test_scheduling_delay_cannot_launch_signal_after_deadline(self):
        kernel = Mock(side_effect=self.denied())
        with patch.object(adapter.time, 'sleep', side_effect=lambda _: setattr(self, 'current', 101.)):
            with patch.object(adapter.os, 'getpgid', side_effect=self.missing()):
                with self.assertRaises(PermissionError):
                    adapter._killpg_with_retry(kernel, 123, signal.SIGKILL)
        self.assertEqual(kernel.call_count, 1)

    def test_darwin_context_restores_original_even_on_exception(self):
        kernel = Mock(return_value=None)
        with patch.object(adapter.sys, 'platform', 'darwin'), patch.object(adapter.os, 'killpg', kernel):
            with self.assertRaisesRegex(RuntimeError, 'test exit'):
                with adapter.signal_retry():
                    self.assertIsNot(adapter.os.killpg, kernel)
                    adapter.os.killpg(123, signal.SIGKILL)
                    raise RuntimeError('test exit')
            self.assertIs(adapter.os.killpg, kernel)
        kernel.assert_called_once_with(123, signal.SIGKILL)

    def test_non_darwin_context_leaves_runtime_untouched(self):
        for platform in ('linux', 'win32'):
            with self.subTest(platform=platform), patch.object(adapter.sys, 'platform', platform):
                with patch.object(adapter.os, 'killpg') as kernel:
                    with adapter.signal_retry():
                        self.assertIs(adapter.os.killpg, kernel)
                    self.assertIs(adapter.os.killpg, kernel)
                    kernel.assert_not_called()

    def test_nested_context_restores_each_original_binding(self):
        with patch.object(adapter.sys, 'platform', 'darwin'), patch.object(adapter.os, 'killpg') as kernel:
            with adapter.signal_retry():
                outer = adapter.os.killpg
                with adapter.signal_retry():
                    self.assertIs(adapter.os.killpg, outer)
                self.assertIs(adapter.os.killpg, outer)
            self.assertIs(adapter.os.killpg, kernel)

    def test_driver_runs_exact_original_script_forwards_flags_and_restores(self):
        driver_path = ROOT / 'scripts/run-unit-tests-with-signal-retry'
        driver = runpy.run_path(str(driver_path), run_name='signal_retry_driver_test')
        kernel = Mock()
        def original_driver(path, *, run_name):
            self.assertEqual(path, str(ROOT / 'scripts/run-unit-tests'))
            self.assertEqual(run_name, '__main__')
            self.assertEqual(sys.argv[1:], ['--require-full-payload'])
            self.assertIsNot(adapter.os.killpg, kernel)
            raise SystemExit(7)
        with patch.object(adapter.sys, 'platform', 'darwin'), patch.object(adapter.os, 'killpg', kernel):
            with patch.object(sys, 'argv', [str(driver_path), '--require-full-payload']):
                with patch.object(runpy, 'run_path', side_effect=original_driver) as run:
                    with self.assertRaises(SystemExit) as result:
                        driver['main']()
                self.assertEqual(result.exception.code, 7); self.assertEqual(run.call_count, 1)
                self.assertIs(adapter.os.killpg, kernel)
        kernel.assert_not_called()


if __name__ == '__main__':
    unittest.main()
