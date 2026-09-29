"""Portable fixtures for three exact frozen resource unit tests, not experiments."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "tests/fixtures/resource-option-sources"
SOURCE_TEST = "test_resource_envelope_control.ResourceEnvelopeControlTests.test_pinned_lake_option_transport_chain"
TIMING_TESTS = frozenset(
    "test_resource_envelope_supervisor.ResourceSupervisorTests." + name
    for name in ("test_late_snapshot_after_exit_is_discarded",
                 "test_healthy_fast_exit_can_have_zero_group_samples")
)


def pinned_sources(root=SOURCES):
    manifest = json.loads((ROOT / "results/research/resource-envelope-pilot-1/execution-manifest-r2.json").read_text())
    paths = []
    for row in manifest["option_transport_sources"]:
        relative = row["path"].split("/src/", 1)[1]
        path = root / relative
        data = path.read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError(f"pinned option source changed: {relative}")
        paths.append(path)
    return tuple(paths)


@contextmanager
def fixtures_for(test_id):
    if test_id == SOURCE_TEST:
        from lib import resource_envelope_control as control
        with patch.object(control, "OPTION_TRANSPORT_SOURCES", pinned_sources()):
            yield
    elif test_id in TIMING_TESTS:
        from lib import resource_envelope_supervisor as supervisor
        original = supervisor.os.wait4

        def wait4(pid, options):
            # Preserve real process/reaping behavior. These two tests exercise
            # sampling timing, so supply a known below-ceiling RSS precondition.
            child, status, usage = original(pid, options)
            if usage is not None:
                usage = SimpleNamespace(ru_maxrss=1, ru_utime=usage.ru_utime,
                                        ru_stime=usage.ru_stime)
            return child, status, usage

        with patch.object(supervisor.os, "wait4", side_effect=wait4):
            yield
    else:
        yield


class _PortableTest(unittest.TestSuite):
    def run(self, result, debug=False):
        with fixtures_for(next(iter(self)).id()):
            return super().run(result, debug)


def portable_suite(suite):
    """Keep original test bodies/IDs and all other tests unchanged."""
    adapted = unittest.TestSuite()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            adapted.addTest(portable_suite(test))
        elif test.id() == SOURCE_TEST or test.id() in TIMING_TESTS:
            adapted.addTest(_PortableTest([test]))
        else:
            adapted.addTest(test)
    return adapted
