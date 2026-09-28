"""Negative controls for observer output reconciliation, without API launches."""
import json
from pathlib import Path
import tempfile
import unittest

from lib.binder_model_control import (
    GateError, canonical_record_bytes, verify_adopted_record, verify_batch_partition,
)
import hashlib
from lib.binder_model_execute import compare


BASE = Path(__file__).resolve().parents[1] / "results/research/binder-model-pilot-1/smoke"


class OutputReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = (BASE / "inputs.ndjson").read_bytes()
        self.expected = (BASE / "expected.ndjson").read_bytes()

    def test_handwritten_smoke_rows_have_seven_stages(self):
        result = compare(self.inputs, self.expected, expected_bytes=self.expected)
        self.assertEqual((result["status"], result["vectors"], result["stage_outputs"]),
                         ("MATCH", 5, 7))

    def test_rejects_missing_extra_duplicate_or_reordered_rows(self):
        rows = self.expected.splitlines(keepends=True)
        for bad in (b"".join(rows[:-1]), b"".join(rows + rows[-1:]),
                    b"".join(rows[:1] + rows[:1] + rows[2:]),
                    b"".join(rows[1:2] + rows[:1] + rows[2:])):
            with self.subTest(bad=bad[:35]), self.assertRaises(GateError):
                compare(self.inputs, bad, expected_bytes=self.expected)

    def test_rejects_bool_index_duplicate_json_key_and_extra_field(self):
        rows = [json.loads(x) for x in self.expected.splitlines()]
        rows[0]["outputs"][0][2][1][1] = True
        bad = b"".join(json.dumps(x).encode() + b"\n" for x in rows)
        with self.assertRaises(GateError):
            compare(self.inputs, bad, expected_bytes=self.expected)
        duplicate = self.expected.replace(b'"id":', b'"id":"extra","id":', 1)
        with self.assertRaises(GateError):
            compare(self.inputs, duplicate, expected_bytes=self.expected)
        extra = self.expected.replace(b'"outputs":', b'"extra":0,"outputs":', 1)
        with self.assertRaises(GateError):
            compare(self.inputs, extra, expected_bytes=self.expected)

    def test_semantic_difference_is_preserved_as_distinguishing(self):
        rows = [json.loads(x) for x in self.expected.splitlines()]
        rows[3]["outputs"][1][2][1] = 4
        bad = b"".join(json.dumps(x).encode() + b"\n" for x in rows)
        result = compare(self.inputs, bad, expected_bytes=self.expected)
        self.assertEqual(result["status"], "DISTINGUISHING")
        self.assertEqual(len(result["mismatches"]), 1)

    def test_malformed_json_is_gate_error(self):
        rows = self.expected.splitlines(keepends=True)
        with self.assertRaises(GateError):
            compare(self.inputs, b"".join([b'{"id":\n', *rows[1:]]), expected_bytes=self.expected)
        with self.assertRaises(GateError):
            compare(b'{"id":\n', self.expected, expected_bytes=self.expected)

    def test_large_valid_index_is_distinguishing_not_format_pause(self):
        rows = [json.loads(x) for x in self.expected.splitlines()]
        rows[0]["outputs"][0][2][1][1] = 33
        observed = b"".join(json.dumps(x).encode() + b"\n" for x in rows)
        result = compare(self.inputs, observed, expected_bytes=self.expected)
        self.assertEqual(result["status"], "DISTINGUISHING")

    def test_partition_rejects_altered_or_duplicate_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            full = root / "all.ndjson"
            one, two = root / "one.ndjson", root / "two.ndjson"
            full.write_bytes(b'{"ordinal":0}\n{"ordinal":1}\n{"ordinal":2}\n{"ordinal":3}\n')
            one.write_bytes(b'{"ordinal":0}\n{"ordinal":1}\n')
            two.write_bytes(b'{"ordinal":2}\n{"ordinal":3}\n')
            verify_batch_partition(full, [one, two], batch_size=2, count=4)
            two.write_bytes(one.read_bytes())
            with self.assertRaises(GateError):
                verify_batch_partition(full, [one, two], batch_size=2, count=4)
            two.write_bytes(b'{"ordinal":2}\n{"ordinal":4}\n')
            with self.assertRaises(GateError):
                verify_batch_partition(full, [one, two], batch_size=2, count=4)

    def test_adoption_replay_rejects_bool_equal_to_integer(self):
        retained = {"index": 1, "term": ["b", 0]}
        expected_hash = hashlib.sha256(canonical_record_bytes(retained)).hexdigest()
        verify_adopted_record(dict(retained), retained, expected_hash)
        with self.assertRaises(GateError):
            verify_adopted_record({"index": True, "term": ["b", 0]}, retained,
                                  expected_hash)


if __name__ == "__main__":
    unittest.main()
