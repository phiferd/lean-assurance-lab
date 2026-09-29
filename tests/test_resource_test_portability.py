"""Regression checks for current-runner fixtures; frozen evidence stays intact."""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from lib import resource_envelope_control as control
from lib import resource_envelope_supervisor as supervisor
from lib import resource_test_portability as portable


class ResourceTestPortabilityTests(unittest.TestCase):
    def test_sources_match_original_bindings_and_restore_paths(self):
        original = control.OPTION_TRANSPORT_SOURCES
        with portable.fixtures_for(portable.SOURCE_TEST):
            self.assertEqual(len(control.OPTION_TRANSPORT_SOURCES), 8)
            self.assertTrue(all(p.is_file() for p in control.OPTION_TRANSPORT_SOURCES))
            self.assertNotEqual(control.OPTION_TRANSPORT_SOURCES, original)
        self.assertIs(control.OPTION_TRANSPORT_SOURCES, original)

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "sources"
            shutil.copytree(portable.SOURCES, root)
            (root / "lean/Init/Prelude.lean").write_text("changed")
            with self.assertRaisesRegex(ValueError, "pinned option source changed"):
                portable.pinned_sources(root)

    def test_high_host_rss_is_isolated_only_for_two_timing_tests(self):
        usage = SimpleNamespace(ru_maxrss=10**9, ru_utime=0.1, ru_stime=0.2)
        with patch.object(supervisor.os, "wait4", return_value=(123, 0, usage)) as real:
            for test_id in portable.TIMING_TESTS:
                with portable.fixtures_for(test_id):
                    child, status, observed = supervisor.os.wait4(123, 0)
                    self.assertEqual((child, status), (123, 0))
                    self.assertEqual(observed.ru_maxrss, 1)
                    self.assertEqual((observed.ru_utime, observed.ru_stime), (0.1, 0.2))
                self.assertIs(supervisor.os.wait4, real)
            with portable.fixtures_for("test_resource_envelope_supervisor.ResourceSupervisorTests.test_sampled_memory_limit"):
                self.assertIs(supervisor.os.wait4(123, 0)[2], usage)
            with self.assertRaisesRegex(RuntimeError, "failure"):
                with portable.fixtures_for(next(iter(portable.TIMING_TESTS))):
                    raise RuntimeError("failure")
            self.assertIs(supervisor.os.wait4, real)

    def test_frozen_execution_inputs_unchanged(self):
        manifest = json.loads((portable.ROOT / "results/research/resource-envelope-pilot-1/execution-manifest-r2.json").read_text())
        for row in manifest["execution_inputs"]:
            data = (portable.ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"], row["path"])

    def test_original_three_test_bodies_pass_through_adapter(self):
        suite = unittest.TestSuite()
        for name in (portable.SOURCE_TEST, *sorted(portable.TIMING_TESTS)):
            # unittest discovery has already made the tests directory importable.
            suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
        result = unittest.TestResult()
        portable.portable_suite(suite).run(result)
        self.assertEqual(result.testsRun, 3)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
