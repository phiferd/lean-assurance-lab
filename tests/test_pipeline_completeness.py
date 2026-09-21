from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

from lib.pipeline_completeness import (
    SentinelError, expected_matrix, inventory, omission_fault,
    parse_artifact, process_classification, sentinel, truncation_fault,
    workspace_control_files,
)


def synthetic_export() -> bytes:
    rows = [{"meta": {"exporter": {"name": "lean4export", "version": "3.1.0"},
                      "format": {"version": "3.1.0"},
                      "lean": {"githash": "fixture", "version": "4.29.1"}}}]
    rows.extend([
        {"in": 1, "str": {"pre": 0, "str": "True"}},
        {"in": 2, "str": {"pre": 1, "str": "intro"}},
        {"in": 3, "str": {"pre": 0, "str": "PipelineCompleteness"}},
    ])
    for ordinal in range(1, 13):
        rows.append({"in": ordinal + 3,
                     "str": {"pre": 3, "str": f"d{ordinal:02d}"}})
    rows.append({"ie": 0, "const": {"name": 1, "us": []}})
    rows.append({"ie": 1, "const": {"name": 2, "us": []}})
    for ordinal in range(1, 12):
        rows.append({"ie": ordinal + 1, "const": {"name": ordinal + 3, "us": []}})
    for ordinal in range(1, 13):
        name_id = ordinal + 3
        value_id = 1 if ordinal == 1 else ordinal
        rows.append({"thm": {"all": [name_id], "levelParams": [], "name": name_id,
                             "type": 0, "value": value_id}})
    return b"".join(json.dumps(row, separators=(",", ":")).encode() + b"\n" for row in rows)


def receipt(code: int) -> dict:
    return {"exit_code": code, "memory_monitor_error": None,
            "memory_monitor_samples": 1, "maximum_observed_rss_bytes": 1,
            "memory_exceeded": False, "timed_out": False, "cleanup_complete": True}


class PipelineCompletenessTests(unittest.TestCase):
    def test_exact_inventory_and_dependency_closure(self):
        result = inventory(synthetic_export())
        self.assertEqual(result["root_target"], "PipelineCompleteness.d12")
        self.assertEqual(len(result["ordered_declarations"]), 12)
        self.assertEqual(result["transitive_value_dependency_closure"],
                         [f"PipelineCompleteness.d{n:02d}" for n in range(1, 13)])

    def test_closure_rejects_a_disconnected_expected_declaration(self):
        rows = [json.loads(line) for line in synthetic_export().splitlines()]
        final = next(row for row in rows if row.get("thm", {}).get("name") == 15)
        final["thm"]["value"] = 1
        data = b"".join(json.dumps(row, separators=(",", ":")).encode() + b"\n"
                        for row in rows)
        with self.assertRaisesRegex(SentinelError, "direct dependency differs"):
            inventory(data)

    def test_fixed_faults_fail_for_distinct_reasons(self):
        baseline = synthetic_export()
        import hashlib
        digest = hashlib.sha256(baseline).hexdigest()
        substitution = b'{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},"format":{"version":"3.1.0"},"lean":{"githash":"fixture","version":"4.29.1"}}}\n'
        self.assertEqual(sentinel(baseline, digest)["classification"], "PASS")
        self.assertEqual(sentinel(omission_fault(baseline), digest)["classification"],
                         "FAIL_MISSING_TARGET")
        self.assertEqual(sentinel(substitution, digest)["classification"],
                         "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY")
        self.assertEqual(sentinel(truncation_fault(baseline), digest)["classification"],
                         "FAIL_PARSE_OR_DEPENDENCY_CLOSURE")

    def test_duplicate_keys_and_non_lf_fail_closed(self):
        with self.assertRaises(SentinelError):
            parse_artifact(b'{"meta":{},"meta":{}}\n')
        with self.assertRaises(SentinelError):
            parse_artifact(synthetic_export().rstrip(b"\n"))

    def test_matrix_is_controls_then_faults(self):
        matrix = expected_matrix()
        self.assertEqual(matrix[:2], [("baseline", "official", "PASS"),
                                      ("baseline", "lean4lean", "PASS")])
        self.assertEqual(len(matrix), 8)

    def test_process_outcomes_preserve_rejection_and_infrastructure(self):
        self.assertEqual(process_classification(receipt(0)), "ACCEPT")
        self.assertEqual(process_classification(receipt(1)), "REJECT")
        bad = receipt(0)
        bad["memory_monitor_samples"] = 0
        self.assertEqual(process_classification(bad), "INFRASTRUCTURE_FAILURE")

    def test_minimal_lake_workspace_does_not_preempt_lake_manifest_generation(self):
        controls = workspace_control_files()
        self.assertEqual(set(controls), {"lean-toolchain", "lakefile.toml"})
        self.assertNotIn("lake-manifest.json", controls)
        self.assertIn(b'[[lean_lib]]', controls["lakefile.toml"])


if __name__ == "__main__":
    unittest.main()
