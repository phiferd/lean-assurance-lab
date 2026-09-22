"""Adversarial tests for the frozen acceptance-impact Stage-2 producer."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib import acceptance_impact_stage2_producer as producer


class AcceptanceImpactStage2ProducerTests(unittest.TestCase):
    def test_render_is_exact_and_preserves_each_base_byte_for_byte(self):
        rendered = producer.render_artifacts()
        contract = json.loads((producer.ROOT / producer.CONTRACT).read_text())
        for artifact_id, tail_key in (("candidate_use", "candidate_tail"),
                                      ("control_use", "control_tail")):
            base = (producer.ROOT
                    / contract["base_bindings"][artifact_id]["path"]).read_bytes()
            raw = rendered[artifact_id]
            self.assertTrue(raw.startswith(base))
            self.assertTrue(raw.endswith(b"\n"))
            self.assertFalse(raw.endswith(b"\n\n"))
            records = [json.loads(line) for line in raw.splitlines()]
            self.assertEqual(len(records), 121)
            self.assertEqual(records[:105], [json.loads(line) for line in base.splitlines()])
            self.assertEqual(records[105:], contract["fixed_append_records_common"]
                             + contract[tail_key])
            self.assertEqual(records[120]["def"]["value"], 93)

    def test_fixed_five_application_spine_and_domains_are_emitted(self):
        rendered = producer.render_artifacts()
        records = {key: [json.loads(line) for line in raw.splitlines()]
                   for key, raw in rendered.items()}
        for rows in records.values():
            expressions = {row["ie"]: row for row in rows if "ie" in row}
            self.assertEqual(expressions[88]["app"], {"arg": 81, "fn": 87})
            self.assertEqual(expressions[89]["app"], {"arg": 82, "fn": 88})
            self.assertEqual(expressions[90]["app"], {"arg": 84, "fn": 89})
            self.assertEqual(expressions[91]["app"], {"arg": 86, "fn": 90})
            self.assertEqual(expressions[92]["app"], {"arg": 2, "fn": 91})
            self.assertEqual(expressions[87]["const"], {"name": 13, "us": [1]})
        candidate = {row["ie"]: row for row in records["candidate_use"] if "ie" in row}
        control = {row["ie"]: row for row in records["control_use"] if "ie" in row}
        self.assertEqual(candidate[93]["lam"]["type"], 28)
        self.assertEqual(candidate[94]["forallE"]["type"], 28)
        self.assertEqual(control[93]["lam"]["type"], 29)
        self.assertEqual(control[94]["forallE"]["type"], 29)

    def test_produce_writes_only_the_two_temp_outputs_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = producer.produce(output_directory=output)
            expected = {"five-app-candidate.ndjson", "five-app-control.ndjson"}
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            before = {path.name: path.read_bytes() for path in output.iterdir()}
            self.assertEqual({row["records"] for row in result.values()}, {121})
            with self.assertRaisesRegex(producer.ProducerError, "output already exists"):
                producer.produce(output_directory=output)
            self.assertEqual({path.name: path.read_bytes() for path in output.iterdir()}, before)

    def test_existing_second_destination_prevents_partial_first_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            control = output / "five-app-control.ndjson"
            control.write_bytes(b"owned\n")
            with self.assertRaisesRegex(producer.ProducerError, "output already exists"):
                producer.produce(output_directory=output)
            self.assertFalse((output / "five-app-candidate.ndjson").exists())
            self.assertEqual(control.read_bytes(), b"owned\n")

    def test_uncommitted_contract_is_refused_before_rendering(self):
        with patch.object(producer, "committed", side_effect=ValueError("not at HEAD")), \
             self.assertRaisesRegex(producer.ProducerError,
                                    "committed consequence contract required"):
            producer.render_artifacts()

    def test_bound_base_tamper_is_refused(self):
        original = Path.read_bytes
        candidate = producer.ROOT / producer.EXPECTED_BASE_BINDINGS["candidate_use"]["path"]

        def tampered(path: Path) -> bytes:
            raw = original(path)
            return raw + b" " if path == candidate else raw

        with patch.object(Path, "read_bytes", tampered), \
             self.assertRaisesRegex(producer.ProducerError, "base binding mismatch"):
            producer.render_artifacts()

    def test_changed_committed_suffix_is_refused(self):
        original = Path.read_bytes
        contract_path = producer.ROOT / producer.CONTRACT

        def changed(path: Path) -> bytes:
            raw = original(path)
            if path != contract_path:
                return raw
            value = json.loads(raw)
            value["candidate_tail"][0]["lam"]["type"] = 29
            return (json.dumps(value) + "\n").encode()

        with patch.object(producer, "committed", return_value=None), \
             patch.object(Path, "read_bytes", changed), \
             self.assertRaisesRegex(producer.ProducerError, "artifact tail differs"):
            producer.render_artifacts()


if __name__ == "__main__":
    unittest.main()
