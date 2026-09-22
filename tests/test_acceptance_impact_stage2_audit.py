"""Adversarial tests for the independent acceptance-impact Stage-2 audit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from lib import acceptance_impact_stage2_audit as audit


def compact(rows: list[dict]) -> bytes:
    return b"".join((json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
                    for row in rows)


class AcceptanceImpactStage2AuditTests(unittest.TestCase):
    def make_pair(self, root: Path) -> tuple[dict, dict]:
        bindings = {}
        for role in ("candidate_use", "control_use"):
            base = (audit.ROOT / audit.BASES[role]["path"]).read_bytes()
            base_copy = root / audit.BASES[role]["path"]
            base_copy.parent.mkdir(parents=True, exist_ok=True)
            base_copy.write_bytes(base)
            path = root / f"{role}.ndjson"
            path.write_bytes(base + compact(audit.EXPECTED_SUFFIXES[role]))
            bindings[role] = audit.binding(path, root)
        return bindings["candidate_use"], bindings["control_use"]

    def test_exact_pair_passes_and_report_is_deterministic_and_nonexecuting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / audit.CONTRACT["path"]).parent.mkdir(parents=True)
            (root / audit.CONTRACT["path"]).write_bytes(
                (audit.ROOT / audit.CONTRACT["path"]).read_bytes())
            candidate, control = self.make_pair(root)
            bindings = {"candidate_use": candidate, "control_use": control}
            result = audit.build(root, bindings)
            self.assertFalse(result["current_checker_execution"])
            structural = result["structural_audit"]
            self.assertEqual(structural["scalar_differences_control_to_candidate"],
                             audit.EXPECTED_DIFFERENCES)
            self.assertEqual(
                structural["artifacts"]["candidate_use"]["spine"]["application_count"], 5)
            self.assertTrue(structural["cross_domain_distinction"]
                            ["syntactically_distinct_rigid_heads"])
            output = "audit.json"
            self.assertEqual(audit.write(root, output, bindings)["status"], "PASS")
            self.assertEqual((root / output).read_bytes(), audit.canonical_bytes(result))
            self.assertEqual(audit.check(root, output, bindings)["status"], "PASS")

    def test_duplicate_key_and_missing_terminal_newline_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, control = self.make_pair(root)
            path = root / candidate["path"]
            raw = path.read_bytes().replace(b'{"meta":', b'{"meta":{},"meta":', 1)
            path.write_bytes(raw)
            candidate = audit.binding(path, root)
            with self.assertRaisesRegex(audit.Stage2AuditError, "duplicate JSON key"):
                audit.audit_artifacts(root, {"candidate_use": candidate, "control_use": control})
            path.write_bytes(raw.rstrip(b"\n"))
            candidate = audit.binding(path, root)
            with self.assertRaisesRegex(audit.Stage2AuditError, "end with one newline"):
                audit.audit_artifacts(root, {"candidate_use": candidate, "control_use": control})

    def test_changed_base_prefix_is_rejected_even_with_fresh_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, control = self.make_pair(root)
            path = root / candidate["path"]
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            rows[104]["inductive"]["recs"][0]["type"] = 49
            path.write_bytes(compact(rows))
            candidate = audit.binding(path, root)
            with self.assertRaisesRegex(audit.Stage2AuditError, "exact 105-record base prefix"):
                audit.audit_artifacts(root, {"candidate_use": candidate, "control_use": control})

    def test_spine_or_added_declaration_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, control = self.make_pair(root)
            path = root / candidate["path"]
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            rows[117]["app"]["fn"] = 90
            path.write_bytes(compact(rows))
            candidate = audit.binding(path, root)
            with self.assertRaisesRegex(audit.Stage2AuditError, "appended records"):
                audit.audit_artifacts(root, {"candidate_use": candidate, "control_use": control})

            candidate, control = self.make_pair(root)
            path = root / control["path"]
            path.write_bytes(path.read_bytes() + b'{"axiom":{}}\n')
            control = audit.binding(path, root)
            with self.assertRaisesRegex(audit.Stage2AuditError, "exactly 121 records"):
                audit.audit_artifacts(root, {"candidate_use": candidate, "control_use": control})

    def test_closure_analysis_distinguishes_open_spine_from_closed_value(self):
        rows = ([json.loads(line) for line in
                 (audit.ROOT / audit.BASES["candidate_use"]["path"]).read_text().splitlines()]
                + audit.EXPECTED_SUFFIXES["candidate_use"])
        expressions, _, _ = audit._indexes(rows)
        self.assertEqual(audit._loose_bvars(92, expressions), {0})
        self.assertEqual(audit._loose_bvars(93, expressions), set())
        self.assertEqual(audit._loose_bvars(94, expressions), set())

    def test_domain_and_pair_difference_checks_are_directional(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, control = self.make_pair(root)
            with self.assertRaisesRegex(audit.Stage2AuditError,
                                        "base prefix|scalar differences changed"):
                audit.audit_artifacts(
                    root, {"candidate_use": control, "control_use": candidate})


if __name__ == "__main__":
    unittest.main()
