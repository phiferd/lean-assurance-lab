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
    def setUp(self):
        host = patch.object(runner, 'missing_host_payload', return_value=[])
        source = patch.object(runner, 'prepare_test_source', return_value={"status": "PASS"})
        self.host = host.start()
        self.source = source.start()
        self.addCleanup(host.stop)
        self.addCleanup(source.stop)

    def test_only_exact_host_tests_are_skipped(self):
        tests = []
        for test_id in sorted(runner.HOST_PAYLOAD_TEST_IDS):
            test = unittest.FunctionTestCase(lambda: self.fail('missing host test must skip'))
            test.id = lambda test_id=test_id: test_id
            tests.append(test)
        unrelated = unittest.FunctionTestCase(lambda: self.fail('future tests must still run'))
        unrelated.id = lambda: 'test_acceptance_impact_source.AcceptanceImpactSourceTests.future'
        tests.append(unittest.TestSuite([unrelated]))
        result = unittest.TestResult()
        runner._rewrite_suite(unittest.TestSuite(tests), False, True).run(result)
        self.assertEqual({test.id() for test, _ in result.skipped}, runner.HOST_PAYLOAD_TEST_IDS)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 4)

    def test_default_run_keeps_missing_host_tests_visible(self):
        self.host.return_value = [Path('/missing/frozen/cargo')]
        tests = []
        for test_id in sorted(runner.HOST_PAYLOAD_TEST_IDS):
            test = unittest.FunctionTestCase(lambda: self.fail('missing integration must skip'))
            test.id = lambda test_id=test_id: test_id
            tests.append(test)
        output = io.StringIO()
        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner, '_historical_modules', return_value=set()), \
             patch.object(runner, 'portfolio_modules', return_value=set()), \
             patch.object(runner, 'run_portfolio_history', return_value=True), \
             patch.object(runner.unittest.defaultTestLoader, 'discover',
                          return_value=unittest.TestSuite(tests)), \
             contextlib.redirect_stderr(output):
            self.assertEqual(runner.main(), 0)
        self.assertIn('skipped=3', output.getvalue())
        self.source.assert_called_once_with(ROOT)

    def test_present_host_payload_keeps_original_failure(self):
        test = unittest.FunctionTestCase(lambda: self.fail('corruption must fail'))
        test.id = lambda: next(iter(runner.HOST_PAYLOAD_TEST_IDS))
        result = unittest.TestResult()
        runner._rewrite_suite(unittest.TestSuite([test]), False, False).run(result)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.skipped, [])

    def test_required_host_payload_fails_before_discovery_or_source_writes(self):
        self.host.return_value = [Path('/missing/frozen/cargo')]
        with patch('sys.argv', ['run-unit-tests', '--require-full-payload']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner.unittest.defaultTestLoader, 'discover') as discover, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 2)
        discover.assert_not_called()
        self.source.assert_not_called()

    def test_corrupt_present_host_payload_cannot_be_skipped(self):
        self.host.side_effect = ValueError('bound file digest differs')
        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner.unittest.defaultTestLoader, 'discover') as discover, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 2)
        discover.assert_not_called()
        self.source.assert_not_called()

    def test_source_payload_mismatch_fails_before_discovery(self):
        self.source.side_effect = ValueError('materialized source tree manifest differs')
        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner.unittest.defaultTestLoader, 'discover') as discover, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(), 2)
        discover.assert_not_called()

    def test_current_suite_runs_inside_portable_cache_history_context(self):
        entered = []

        @contextlib.contextmanager
        def portable_context():
            entered.append(True)
            yield

        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner, '_historical_modules', return_value=set()), \
             patch.object(runner, 'portfolio_modules', return_value=set()), \
             patch.object(runner, 'run_portfolio_history', return_value=True), \
             patch.object(runner, 'portable_cache_history', portable_context), \
             patch.object(runner.unittest.defaultTestLoader, 'discover',
                          return_value=unittest.TestSuite()), \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 0)
        self.assertEqual(entered, [True])

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

    def test_historical_partition_does_not_hide_future_tests(self):
        old = unittest.FunctionTestCase(lambda: self.fail('must run in historical process'))
        old.id = lambda: 'test_declaration_validation_publication_study.Case.old'
        future = unittest.FunctionTestCase(lambda: None)
        future.id = lambda: 'test_declaration_validation_publication_study_successor.Case.new'
        suite = runner._current_suite(unittest.TestSuite([unittest.TestSuite([old, future])]),
                                      {'test_declaration_validation_publication_study'})
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 1)
        self.assertTrue(result.wasSuccessful())

    def test_historical_failure_fails_complete_run(self):
        from types import SimpleNamespace
        with patch('sys.argv', ['run-unit-tests', '--require-full-payload']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner, '_historical_modules', return_value={'old_module'}), \
             patch.object(runner, 'portfolio_modules', return_value=set()), \
             patch.object(runner, 'run_portfolio_history', return_value=True), \
             patch.object(runner.unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite()), \
             patch.object(runner.subprocess, 'run', return_value=SimpleNamespace(returncode=1)) as run, \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 1)
        self.assertEqual(run.call_args.args[0][1:], ['--tests', '--require-full-payload'])

    def test_checkpoint_failure_fails_complete_run(self):
        with patch('sys.argv', ['run-unit-tests']), \
             patch.object(runner, '_load_payload_status', return_value=(set(), [])), \
             patch.object(runner, '_historical_modules', return_value=set()), \
             patch.object(runner, 'portfolio_modules', return_value={'exact_old_module'}), \
             patch.object(runner, 'run_portfolio_history', return_value=False) as historical, \
             patch.object(runner.unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite()), \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 1)
        historical.assert_called_once_with(ROOT)

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
