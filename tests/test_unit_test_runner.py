import contextlib
import importlib.machinery
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('unit_runner', str(ROOT / 'scripts/run-unit-tests'))
spec = importlib.util.spec_from_loader(loader.name, loader)
runner = importlib.util.module_from_spec(spec)
loader.exec_module(runner)


class UnitRunnerBoundaryTests(unittest.TestCase):
    def test_only_exact_payload_test_is_skipped(self):
        target = unittest.FunctionTestCase(lambda: self.fail('must be skipped'))
        target.id = lambda: runner.GATE8_TEST_ID
        unrelated = unittest.FunctionTestCase(lambda: None)
        suite = runner._rewrite_suite(unittest.TestSuite([target, unrelated]), True)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(result.skipped[0][0].id(), runner.GATE8_TEST_ID)
        self.assertTrue(result.wasSuccessful())

    def test_present_payload_retains_original_failures(self):
        target = unittest.FunctionTestCase(lambda: self.fail('hash mismatch remains a failure'))
        target.id = lambda: runner.GATE8_TEST_ID
        suite = runner._rewrite_suite(unittest.TestSuite([target]), False)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.skipped, [])

    def test_missing_tracked_input_is_not_an_integration_skip(self):
        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [ROOT / 'corpus/missing.ndjson'])), \
             patch.object(runner.unittest.defaultTestLoader, 'discover') as discover, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 2)
        discover.assert_not_called()

    def test_required_payload_fails_before_discovery(self):
        with patch('sys.argv', ['run-unit-tests', '--require-full-payload']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [ROOT / 'external/missing'])), \
             patch.object(runner.unittest.defaultTestLoader, 'discover') as discover, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 2)
        discover.assert_not_called()


if __name__ == '__main__':
    unittest.main()
