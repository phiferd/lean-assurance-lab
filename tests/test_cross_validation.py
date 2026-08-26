import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from cross_validation import (  # noqa: E402
    aggregate_classification,
    inspect_export,
    load_catalog,
    normalize_process,
    profiles_by_id,
    result_classification,
    run_validator,
    static_compatibility,
)


class CrossValidationTests(unittest.TestCase):
    def test_catalog_conforms_to_schema_and_disables_majority_vote(self):
        catalog = load_catalog()
        schema = json.loads((ROOT / "schemas" / "validator-catalog.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(catalog)
        self.assertFalse(catalog["policy"]["majority_vote"])
        self.assertGreaterEqual(len(catalog["validators"]), 2)

    def test_witness_is_statically_compatible_with_built_profiles(self):
        arena_root = ROOT / "external" / "lean-kernel-arena"
        if not (arena_root / ".git").exists():
            self.skipTest("requires materialized Lean Kernel Arena checker profiles")
        metadata = inspect_export(ROOT / "corpus" / "generated" / "nanoda-0003-auto-universe.ndjson")
        for profile in load_catalog()["validators"]:
            with self.subTest(profile=profile["id"]):
                self.assertEqual(static_compatibility(profile, metadata)["status"], "COMPATIBLE")

    def test_normalization_preserves_all_exceptional_outcomes(self):
        self.assertEqual(normalize_process("kiota", 0, b"", b"")[0], "ACCEPT")
        self.assertEqual(normalize_process("kiota", 1, b"", b"type mismatch")[0], "REJECT")
        self.assertEqual(normalize_process("kiota", 2, b"", b"")[0], "DECLINE")
        self.assertEqual(normalize_process("kiota", -9, b"", b"")[0], "CRASH")
        self.assertEqual(normalize_process("kiota", 1, b"", b"ERROR: json parse: bad")[0], "PARSE_ERROR")
        self.assertEqual(normalize_process("kiota", 17, b"", b"")[0], "UNKNOWN")

    def test_expected_outcome_classifications_are_explicit(self):
        expected = {
            "ACCEPT": "CHECKER_DISAGREEMENT", "REJECT": "CONFIRMED",
            "DECLINE": "DECLINED", "CRASH": "CRASHED", "TIMEOUT": "TIMED_OUT",
            "PARSE_ERROR": "PARSE_ERROR", "UNKNOWN": "UNRESOLVED",
        }
        for outcome, classification in expected.items():
            self.assertEqual(result_classification(outcome, "REJECT"), classification)

    def test_aggregate_never_majority_votes_away_disagreement(self):
        rows = [
            {
                "classification": "CONFIRMED",
                "compatibility": {"status": "COMPATIBLE"},
                "result": {"normalized_outcome": "REJECT"},
            },
            {
                "classification": "CONFIRMED",
                "compatibility": {"status": "COMPATIBLE"},
                "result": {"normalized_outcome": "REJECT"},
            },
            {
                "classification": "CHECKER_DISAGREEMENT",
                "compatibility": {"status": "COMPATIBLE"},
                "result": {"normalized_outcome": "ACCEPT"},
            },
        ]
        self.assertEqual(aggregate_classification(rows, "REJECT"), "CHECKER_DISAGREEMENT")

    def test_exceptional_outcome_is_not_hidden_by_confirmation(self):
        rows = [
            {
                "classification": "CONFIRMED",
                "compatibility": {"status": "COMPATIBLE"},
                "result": {"normalized_outcome": "REJECT"},
            },
            {
                "classification": "TIMED_OUT",
                "compatibility": {"status": "COMPATIBLE"},
                "result": {"normalized_outcome": "TIMEOUT"},
            },
        ]
        self.assertEqual(aggregate_classification(rows, "REJECT"), "TIMED_OUT")

    def test_direct_runner_records_decline_crash_and_timeout(self):
        artifact = ROOT / "corpus" / "probes" / "malformed-object.ndjson"
        base = {"binary": "/bin/sh", "adapter": "test"}
        decline = run_validator({**base, "command": ["{binary}", "-c", "exit 2"]}, artifact, 1)
        crash = run_validator({**base, "command": ["{binary}", "-c", "kill -9 $$"]}, artifact, 1)
        timeout = run_validator({**base, "command": ["{binary}", "-c", "sleep 1"]}, artifact, 0.01)
        self.assertEqual(decline["normalized_outcome"], "DECLINE")
        self.assertEqual(crash["normalized_outcome"], "CRASH")
        self.assertEqual(timeout["normalized_outcome"], "TIMEOUT")
        self.assertEqual(decline["command"], ["/bin/sh", "-c", "exit 2"])


if __name__ == "__main__":
    unittest.main()
