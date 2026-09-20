from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from lib.metamorphic_ndjson_audit import AuditError, audit_bytes, decode
from lib.metamorphic_ndjson_transform import TransformError, identity_roundtrip_bytes, transform_bytes
from lib.metamorphic_pilot_runner import run_supervised


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = [
    ROOT / "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson",
    ROOT / "corpus/controls/nanoda-gen-f19ffc8a2e9b-matching-imax-control.ndjson",
]
ALGORITHMS = ["reverse-ready-v1", "kind-round-robin-v1"]


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode().splitlines()]


def encoded(values: list[dict]) -> bytes:
    return ("\n".join(json.dumps(value, separators=(",", ":")) for value in values) + "\n").encode()


class TransformationTests(unittest.TestCase):
    def test_reverse_ready_pairs_are_nonidentity_and_preserved(self):
        for path in ORIGINALS:
            source = path.read_bytes()
            variant, transform = transform_bytes(source, "reverse-ready-v1")
            audit = audit_bytes(source, variant)
            self.assertTrue(transform["nonidentity"])
            self.assertTrue(audit["equivalent"])
            self.assertTrue(audit["eligible"])
            self.assertGreaterEqual(audit["position_changes"], 2)
            self.assertGreaterEqual(audit["identifier_changes"], 1)

    def test_round_robin_is_preserved_but_ineligible_under_frozen_delta(self):
        for path in ORIGINALS:
            source = path.read_bytes()
            variant, transform = transform_bytes(source, "kind-round-robin-v1")
            audit = audit_bytes(source, variant)
            self.assertTrue(audit["equivalent"])
            self.assertGreaterEqual(audit["position_changes"], 2)
            self.assertEqual(audit["identifier_changes"], 0)
            self.assertFalse(transform["nonidentity"])
            self.assertFalse(audit["eligible"])

    def test_generation_is_byte_deterministic(self):
        for path in ORIGINALS:
            source = path.read_bytes()
            for algorithm in ALGORITHMS:
                first, first_report = transform_bytes(source, algorithm)
                second, second_report = transform_bytes(source, algorithm)
                self.assertEqual(first, second)
                self.assertEqual(first_report, second_report)

    def test_identity_decode_encode_roundtrip(self):
        for path in ORIGINALS:
            source = path.read_bytes()
            roundtrip = identity_roundtrip_bytes(source)
            self.assertEqual(decode(source).canonical(), decode(roundtrip).canonical())
            self.assertTrue(audit_bytes(source, roundtrip, require_nonidentity=False)["eligible"])

    def test_unknown_algorithm_fails(self):
        with self.assertRaisesRegex(TransformError, "unknown algorithm"):
            transform_bytes(ORIGINALS[0].read_bytes(), "unknown")


class AdversarialAuditTests(unittest.TestCase):
    def test_changed_let_value_fails_preservation(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        changed[-2]["letE"]["value"] = 1
        self.assertFalse(audit_bytes(source, encoded(changed))["equivalent"])

    def test_changed_imax_constructor_fails_preservation(self):
        source = ORIGINALS[1].read_bytes()
        changed = rows(source)
        changed[8]["max"] = changed[8].pop("imax")
        self.assertFalse(audit_bytes(source, encoded(changed))["equivalent"])

    def test_missing_record_fails_closed(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        del changed[8]
        with self.assertRaises(AuditError): audit_bytes(source, encoded(changed))

    def test_duplicate_index_fails_closed(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        changed[4]["in"] = 3
        with self.assertRaisesRegex(AuditError, "non-contiguous"):
            audit_bytes(source, encoded(changed))

    def test_invalid_reference_fails_closed(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        changed[8]["sort"] = 99
        with self.assertRaisesRegex(AuditError, "unresolved"):
            audit_bytes(source, encoded(changed))

    def test_unknown_tag_fails_closed(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        changed[8]["bogus"] = changed[8].pop("sort")
        with self.assertRaisesRegex(AuditError, "known tag"):
            audit_bytes(source, encoded(changed))

    def test_extra_field_fails_closed(self):
        source = ORIGINALS[0].read_bytes()
        changed = rows(source)
        changed[8]["extra"] = 0
        with self.assertRaisesRegex(AuditError, "fields differ"):
            audit_bytes(source, encoded(changed))


class SupervisorTests(unittest.TestCase):
    def test_memory_limit_is_enforced(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            prefix = Path(directory) / "memory"
            script = "import time; x=bytearray(128*1024*1024); time.sleep(30)"
            receipt = run_supervised(argv=[sys.executable, "-c", script], cwd=ROOT, stdin=None,
                                     env=os.environ.copy(), timeout_seconds=10,
                                     memory_bytes=64 * 1024 * 1024, raw_prefix=prefix)
            self.assertTrue(receipt["memory_exceeded"])
            self.assertIsNone(receipt["memory_monitor_error"])
            self.assertGreater(receipt["memory_monitor_samples"], 0)
            self.assertGreater(receipt["maximum_observed_rss_bytes"], receipt["memory_limit_bytes"])
            self.assertTrue(receipt["cleanup_complete"])
            self.assertIn("peak_rss_bytes", receipt["metrics"])

    def test_timeout_kills_process_group(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            prefix = Path(directory) / "timeout"
            script = ("import subprocess,sys,time; "
                      "subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); time.sleep(30)")
            receipt = run_supervised(argv=[sys.executable, "-c", script], cwd=ROOT, stdin=None,
                                     env=os.environ.copy(), timeout_seconds=1,
                                     memory_bytes=2 * 1024 * 1024 * 1024, raw_prefix=prefix)
            self.assertTrue(receipt["timed_out"])
            self.assertTrue(receipt["cleanup_complete"])


if __name__ == "__main__":
    unittest.main()
