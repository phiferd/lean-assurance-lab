"""Negative controls for independently audited export selection and closure."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import real_proof_slices_audit as audit


def enc(row):
    return json.dumps(row, separators=(",", ":")).encode() + b"\n"


class SliceAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rows = [
            {"meta": {"exporter": {"name": "lean4export", "version": "3.1.0"},
                      "format": {"version": "3.1.0"},
                      "lean": {"version": "4.29.1", "githash": "f72c35b3f637c8c6571d353742168ab66cc22c00"}}},
            {"in": 1, "str": {"pre": 0, "str": "Nat"}},
            {"in": 2, "str": {"pre": 0, "str": "p"}},
            {"in": 3, "str": {"pre": 1, "str": "a"}},
            {"in": 4, "str": {"pre": 1, "str": "b"}},
            {"in": 5, "str": {"pre": 1, "str": "c"}},
            {"in": 6, "str": {"pre": 1, "str": "d"}},
            {"ie": 0, "sort": 0},
            {"ie": 1, "forallE": {"binderInfo": "default", "body": 0, "name": 2, "type": 0}},
            {"ie": 2, "lam": {"binderInfo": "default", "body": 0, "name": 2, "type": 0}},
            *[{"thm": {"all": [name], "levelParams": [], "name": name, "type": 1, "value": 2}}
              for name in (3, 4, 5, 6)],
        ]
        self.protocol = {
            "schema": "real-proof-slices-protocol-v1", "source_contract": {"sources": []},
            "selection": {"order": ["init", "std", "cedar"], "per_source": 4,
                          "skip_first_theorem_records": {"init": 0, "std": 0, "cedar": 0},
                          "name_prefix": {"init": "Nat.", "std": "Std.", "cedar": "Cedar."},
                          "freeze_before_observation": True, "replacement_after_outcome": False},
        }
        self.receipt_path = self.root / "receipt.json"
        self.patch_root = patch.object(audit, "ROOT", self.root)
        self.patch_specs = patch.dict(audit.SOURCE_SPECS)
        self.patch_root.start(); self.patch_specs.start()
        self.addCleanup(self.patch_root.stop); self.addCleanup(self.patch_specs.stop)
        self.rebind()

    def rebind(self):
        lines = [enc(row) for row in self.rows]
        original = b"".join(lines)
        source = self.root / "external/lean-kernel-arena/_build/tests/init.ndjson"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(original)
        source_hash = hashlib.sha256(original).hexdigest()
        audit.SOURCE_SPECS["init"] = (len(original), source_hash)
        self.protocol["source_contract"]["sources"] = [
            {"id": name, "path": f"external/lean-kernel-arena/_build/tests/{name}.ndjson",
             "bytes": spec[0], "sha256": spec[1]} for name, spec in audit.SOURCE_SPECS.items()]
        base = self.root / "results/research/real-proof-slices-pilot-1"
        base.mkdir(parents=True, exist_ok=True)
        protocol_bytes = json.dumps(self.protocol).encode()
        (base / "protocol.json").write_bytes(protocol_bytes)
        names = {3: "Nat.a", 4: "Nat.b", 5: "Nat.c", 6: "Nat.d"}
        selected = []; offset = 0
        for line_no, (row, raw) in enumerate(zip(self.rows, lines), 1):
            if "thm" in row:
                ident = row["thm"]["name"]
                selected.append({"slot": len(selected) + 1, "theorem_ordinal": len(selected) + 1,
                                 "source_line": line_no, "source_offset": offset,
                                 "name_id": ident, "name": names[ident],
                                 "source_row_sha256": hashlib.sha256(raw).hexdigest()})
            offset += len(raw)
        science = {
            "schema": "real-proof-slices-scientific-manifest-v1",
            "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
            "selection_rule": self.protocol["selection"],
            "sources": [{"source": name, "source_path": f"external/lean-kernel-arena/_build/tests/{name}.ndjson",
                         "source_bytes": spec[0], "source_sha256": spec[1],
                         "selected": selected if name == "init" else [None] * 4}
                        for name, spec in audit.SOURCE_SPECS.items()],
        }
        (base / "scientific-manifest.json").write_text(json.dumps(science))
        included_lines = [1, 2, 3, 4, 8, 9, 10, 11]
        included = []; offset = 0
        for line_no, raw in enumerate(lines, 1):
            if line_no in included_lines:
                included.append({"source_line": line_no, "offset": offset, "bytes": len(raw),
                                 "sha256": hashlib.sha256(raw).hexdigest()})
            offset += len(raw)
        expected = b"".join(lines[i - 1] for i in included_lines)
        output_path = "corpus/real-proof-slices-pilot-1/init-01.ndjson"
        output = self.root / output_path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(expected)
        self.receipt = {
            "schema": "real-proof-slice-receipt-v1", "case": "init-01", "source": "init",
            "source_path": "external/lean-kernel-arena/_build/tests/init.ndjson",
            "source_sha256": source_hash, "source_bytes": len(original),
            "selected_source_line": selected[0]["source_line"], "selected_name_id": 3,
            "disposition": "READY", "size_ceiling_bytes": 8_000_000,
            "record_ceiling": 120_000, "would_be_bytes": len(expected),
            "record_count": len(included), "output_path": output_path,
            "output_sha256": hashlib.sha256(expected).hexdigest(), "included_rows": included,
        }

    def check(self):
        self.receipt_path.write_text(json.dumps(self.receipt))
        return audit.audit_case(self.receipt_path)

    def test_exact_slice_passes(self):
        self.assertEqual(self.check()["status"], "PASS")

    def test_missing_dependency_row_rejected(self):
        self.receipt["included_rows"].pop(3)
        with self.assertRaisesRegex(audit.AuditError, "closure mismatch"): self.check()

    def test_extra_declaration_rejected(self):
        self.receipt["included_rows"].insert(4, {"source_line": 5, "offset": 0, "bytes": 0, "sha256": "0" * 64})
        with self.assertRaisesRegex(audit.AuditError, "closure mismatch"): self.check()

    def test_reordered_rows_rejected(self):
        self.receipt["included_rows"][2], self.receipt["included_rows"][3] = (
            self.receipt["included_rows"][3], self.receipt["included_rows"][2])
        with self.assertRaisesRegex(audit.AuditError, "closure mismatch"): self.check()

    def test_modified_output_rejected(self):
        (self.root / self.receipt["output_path"]).write_bytes(b"{}\n")
        with self.assertRaisesRegex(audit.AuditError, "slice bytes differ"): self.check()

    def test_bad_source_binding_rejected(self):
        self.receipt["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(audit.AuditError, "source binding mismatch"): self.check()

    def test_wrong_selection_under_same_root_tags_rejected(self):
        self.receipt["selected_source_line"] = 12
        self.receipt["selected_name_id"] = 4
        with self.assertRaisesRegex(audit.AuditError, "selected theorem changed"): self.check()

    def test_changed_scientific_manifest_rejected(self):
        path = self.root / "results/research/real-proof-slices-pilot-1/scientific-manifest.json"
        science = json.loads(path.read_text())
        science["sources"][0]["selected"][0]["name"] = "Nat.b"
        path.write_text(json.dumps(science))
        with self.assertRaisesRegex(audit.AuditError, "frozen scientific manifest"): self.check()

    def test_missing_environment_owner_rejected(self):
        self.rows[10]["thm"]["all"] = [2]
        self.rebind()
        with self.assertRaisesRegex(audit.AuditError, "unresolved declaration owner"): self.check()

    def test_independently_reproduced_extraction_failure(self):
        self.rows[10]["thm"]["all"] = [2]
        self.rebind()
        self.receipt.update(disposition="EXTRACTION_FAILURE", error_type="SliceError",
                            error="unresolved environment constant 2", output_path=None,
                            output_sha256=None, would_be_bytes=None, included_rows=[], record_count=0)
        self.assertEqual(self.check()["status"], "PASS_EXTRACTION_FAILURE")

    def test_unreproduced_extraction_failure_rejected(self):
        self.receipt.update(disposition="EXTRACTION_FAILURE", error_type="SliceError",
                            error="unresolved environment constant 2", output_path=None,
                            output_sha256=None, would_be_bytes=None, included_rows=[], record_count=0)
        with self.assertRaises(audit.AuditError): self.check()

    def test_incomplete_quotient_package_rejected(self):
        self.rows.insert(7, {"in": 7, "str": {"pre": 1, "str": "q"}})
        self.rows.insert(10, {"quot": {"kind": "type", "name": 7, "levelParams": [], "type": 0}})
        self.rows.insert(11, {"ie": 3, "const": {"name": 7, "us": []}})
        self.rows[12]["lam"]["body"] = 3
        self.rebind()
        with self.assertRaisesRegex(audit.AuditError, "incomplete quotient package"): self.check()

    def test_wrong_four_quotient_kinds_rejected(self):
        for index in range(7, 11):
            self.rows.insert(index, {"in": index, "str": {"pre": 1, "str": f"q{index}"}})
        for offset, name in enumerate(range(7, 11)):
            self.rows.insert(13 + offset, {"quot": {"kind": "type", "name": name,
                                                    "levelParams": [], "type": 0}})
        self.rows.insert(17, {"ie": 3, "const": {"name": 7, "us": []}})
        self.rows[18]["lam"]["body"] = 3
        self.rebind()
        with self.assertRaisesRegex(audit.AuditError, "incomplete quotient package"): self.check()

    def test_inductive_member_requires_whole_group(self):
        for index, child in enumerate(("I", "mk", "rec"), 7):
            self.rows.insert(index, {"in": index, "str": {"pre": 1, "str": child}})
        group = {"inductive": {
            "types": [{"name": 7, "levelParams": [], "type": 0, "all": [7], "ctors": [8]}],
            "ctors": [{"name": 8, "levelParams": [], "type": 0, "induct": 7}],
            "recs": [{"name": 9, "levelParams": [], "type": 0, "all": [7],
                      "rules": [{"ctor": 8, "rhs": 0}]}]}}
        self.assertEqual(audit._names(group, "inductive"), [7, 8, 9])
        self.rows.insert(12, group)
        self.rows.insert(13, {"ie": 3, "const": {"name": 9, "us": []}})
        self.rows[14]["lam"]["body"] = 3
        self.rebind()
        with self.assertRaisesRegex(audit.AuditError, "closure mismatch"): self.check()


if __name__ == "__main__": unittest.main()
