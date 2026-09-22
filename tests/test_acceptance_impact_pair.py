"""Adversarial tests for the frozen acceptance-impact pair audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib import acceptance_impact_pair as audit


def binding(root: Path, path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


class AcceptanceImpactPairTests(unittest.TestCase):
    def test_generated_audit_is_current_and_nonexecuting(self):
        result = audit.build()
        self.assertEqual(audit.canonical_bytes(result), (audit.ROOT / audit.OUTPUT).read_bytes())
        self.assertEqual(audit.check()["status"], "PASS")
        self.assertFalse(result["current_checker_execution"])
        self.assertEqual(result["pair"]["scalar_differences"], [audit.EXPECTED_DIFFERENCE])
        self.assertEqual(result["pair"]["changed_declaration"]["name"], "LALNest.rec_1")

    def test_bound_byte_tamper_is_rejected_before_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / audit.CANDIDATE["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes((audit.ROOT / audit.CANDIDATE["path"]).read_bytes() + b" ")
            with self.assertRaisesRegex(audit.PairAuditError, "file binding mismatch"):
                audit.verify_binding(root, audit.CANDIDATE)

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.ndjson"
            control = root / "control.ndjson"
            raw = (audit.ROOT / audit.CANDIDATE["path"]).read_bytes()
            candidate.write_bytes(raw.replace(b'{"meta":', b'{"meta":{},"meta":', 1))
            control.write_bytes((audit.ROOT / audit.CONTROL["path"]).read_bytes())
            with self.assertRaisesRegex(audit.PairAuditError, "duplicate JSON key"):
                audit.audit_pair(root, binding(root, candidate), binding(root, control))

    def test_second_scalar_difference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.ndjson"
            control = root / "control.ndjson"
            rows = [json.loads(line) for line in
                    (audit.ROOT / audit.CANDIDATE["path"]).read_text().splitlines()]
            rows[104]["inductive"]["recs"][0]["k"] = True
            candidate.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows))
            control.write_bytes((audit.ROOT / audit.CONTROL["path"]).read_bytes())
            with self.assertRaisesRegex(audit.PairAuditError, "scalar difference changed"):
                audit.audit_pair(root, binding(root, candidate), binding(root, control))

    def test_shared_expression_table_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for source, name in ((audit.CANDIDATE, "candidate.ndjson"),
                                 (audit.CONTROL, "control.ndjson")):
                rows = [json.loads(line) for line in
                        (audit.ROOT / source["path"]).read_text().splitlines()]
                rows[4]["sort"] = 0
                path = root / name
                path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows))
                paths.append(path)
            with self.assertRaisesRegex(audit.PairAuditError, "name or expression table changed"):
                audit.audit_pair(root, binding(root, paths[0]), binding(root, paths[1]))

    def test_reversed_pointer_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.ndjson"
            control = root / "control.ndjson"
            for source, path, value in ((audit.CANDIDATE, candidate, 49),
                                        (audit.CONTROL, control, 68)):
                rows = [json.loads(line) for line in
                        (audit.ROOT / source["path"]).read_text().splitlines()]
                rows[104]["inductive"]["recs"][0]["type"] = value
                path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows))
            with self.assertRaisesRegex(audit.PairAuditError, "scalar difference changed"):
                audit.audit_pair(root, binding(root, candidate), binding(root, control))

    def test_declaration_identity_and_reference_set_are_enforced(self):
        original = audit._declarations

        def renamed(records, names):
            rows = original(records, names)
            for row in rows:
                if row["pointer"] == "/104/inductive/recs/0":
                    row["name"] = "Unexpected.rec"
            return rows

        with patch.object(audit, "_declarations", side_effect=renamed), \
             self.assertRaisesRegex(audit.PairAuditError, "declaration identity"):
            audit.audit_pair(audit.ROOT)

        def extra_reference(records, names):
            rows = original(records, names)
            rows.append({"pointer": "/synthetic", "kind": "recs",
                         "name": "Unexpected.rec", "type_id": 49})
            return rows

        with patch.object(audit, "_declarations", side_effect=extra_reference), \
             self.assertRaisesRegex(audit.PairAuditError, "type-reference set"):
            audit.audit_pair(audit.ROOT)

    def test_historical_binding_tamper_and_stale_output_are_rejected(self):
        original = Path.read_bytes
        historical = audit.ROOT / audit.HISTORICAL["path"]
        output = audit.ROOT / audit.OUTPUT

        def tampered_history(path: Path) -> bytes:
            raw = original(path)
            return raw + b" " if path == historical else raw

        with patch.object(Path, "read_bytes", tampered_history), \
             self.assertRaisesRegex(audit.PairAuditError, "file binding mismatch"):
            audit.build()

        def stale_output(path: Path) -> bytes:
            raw = original(path)
            return raw + b" " if path == output else raw

        with patch.object(Path, "read_bytes", stale_output), \
             self.assertRaisesRegex(audit.PairAuditError, "stale generated pair audit"):
            audit.check()


if __name__ == "__main__":
    unittest.main()
