"""Reuse existing supervisor controls against the optional-deadline local copy."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import local_supervisor as local
sys.path.insert(0, str(ROOT / 'tests'))
import test_resource_envelope_supervisor as retained
retained.supervisor = local

class NoDeadlineControls(unittest.TestCase):
    def test_healthy_silent_completion(self):
        with patch.object(local, '_group_snapshot', side_effect=retained.synthetic_snapshot):
            result = retained.run(['/bin/sh', '-c', 'sleep 0.12; printf finished'], timeout_seconds=None)
        self.assertEqual(result.stdout, b'finished')
        self.assertEqual(result.receipt['exit_code'], 0)
        self.assertIsNone(result.receipt['stop_reason'])
        self.assertIsNone(result.receipt['limits']['timeout_seconds'])
        self.assertTrue(result.receipt['reap_complete'])
        self.assertTrue(result.receipt['cleanup_complete'])

    def test_memory_control_still_stops(self):
        with patch.object(local, '_group_snapshot', side_effect=retained.synthetic_snapshot):
            result = retained.run(['/bin/sh', '-c', 'sleep 2'], timeout_seconds=None, memory_ceiling_bytes=500000)
        self.assertEqual(result.receipt['stop_reason'], 'OBSERVED_MEMORY_LIMIT')
        self.assertTrue(result.receipt['cleanup_complete'])

    def test_monitor_fault_still_stops(self):
        with patch.object(local, '_group_snapshot', side_effect=PermissionError('synthetic monitor failure')):
            result = retained.run(['/bin/sh', '-c', 'sleep 2'], timeout_seconds=None)
        self.assertEqual(result.receipt['stop_reason'], 'MONITOR_FAULT')
        self.assertTrue(result.receipt['reap_complete'])

    def test_output_cap_still_stops(self):
        with patch.object(local, '_group_snapshot', side_effect=retained.synthetic_snapshot):
            result = retained.run(['/bin/sh', '-c', 'yes x'], timeout_seconds=None, output_cap_bytes=100000)
        self.assertEqual(result.receipt['stop_reason'], 'OUTPUT_CAP')
        self.assertTrue(result.receipt['cleanup_complete'])

suite = unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromTestCase(retained.ResourceSupervisorTests),
    unittest.defaultTestLoader.loadTestsFromTestCase(NoDeadlineControls),
])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
