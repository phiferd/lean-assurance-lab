import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from witness_search import (  # noqa: E402
    canonical_ndjson,
    generate_candidates,
    inductive_metadata_candidates,
    minimize_witness,
    semantic_classification,
    undeclared_universe_template,
)


class FakeSession:
    def evaluate(self, artifact: Path) -> dict:
        records = [json.loads(line) for line in artifact.read_text().splitlines() if line]
        holds = any(row.get("keep") for row in records)
        return {"different": holds}


class WitnessSearchTests(unittest.TestCase):
    def test_inductive_metadata_candidates_target_auxiliary_fields(self):
        records = [
            {"meta": {"format": {"version": "3.1.0"}}},
            {
                "inductive": {
                    "types": [{"numParams": 1, "numIndices": 0, "isRec": True, "all": [1, 2]}],
                    "ctors": [{"cidx": 0, "numFields": 1, "induct": 7}],
                }
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            seed = Path(temp) / "seed.ndjson"
            seed.write_bytes(canonical_ndjson(records))
            candidates = inductive_metadata_candidates(seed)

        transformations = {row["transformation"] for row in candidates}
        self.assertTrue(any(":numParams:increment:" in row for row in transformations))
        self.assertTrue(any(":all:remove-member-0:" in row for row in transformations))
        self.assertTrue(any(":isRec:toggle:" in row for row in transformations))
        self.assertTrue(any(":induct:increment:" in row for row in transformations))

    def test_inductive_metadata_candidates_precede_generic_mutations(self):
        seed = ROOT / "external" / "lean-kernel-arena" / "_build" / "tests" / "nested-nonuniform-param.ndjson"
        if not seed.exists():
            self.skipTest("Arena profiles are not materialized")

        candidates = generate_candidates("inductive-declarations", [seed], 19)

        targeted = [row["strategy"] == "inductive-metadata-mutation" for row in candidates]
        first_generic = targeted.index(False) if False in targeted else len(targeted)
        self.assertTrue(all(targeted[:first_generic]))
        self.assertFalse(any(targeted[first_generic:]))

    def test_universe_template_is_the_confirmed_witness(self):
        payload = canonical_ndjson(undeclared_universe_template())
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            "5f49dd739c4e909a0147b7fc5a8bee4e2eb06ca0f4ad7c87ef20ba871ff7fff3",
        )

    def test_candidate_order_is_deterministic(self):
        seed = ROOT / "corpus" / "controls" / "nanoda-0003-declared-const-universe.ndjson"
        first = generate_candidates("universes", [seed], 41)
        second = generate_candidates("universes", [seed], 41)
        self.assertEqual([row["sha256"] for row in first], [row["sha256"] for row in second])
        self.assertEqual(first[0]["strategy"], "universe-ownership-template")

    def test_minimizer_preserves_predicate(self):
        records = [{"noise": 1}, {"keep": True, "removable": [1, 2]}, {"noise": 2}]
        with tempfile.TemporaryDirectory() as temp:
            result, stats = minimize_witness(records, Path(temp) / "candidate.ndjson", FakeSession())
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["keep"])
        self.assertGreater(stats["predicate_checks"], 0)

    def test_minimizer_preserves_export_metadata(self):
        metadata = {"meta": {"format": {"version": "3.1.0"}}}
        records = [metadata, {"keep": True}, {"noise": 1}]
        with tempfile.TemporaryDirectory() as temp:
            result, _ = minimize_witness(records, Path(temp) / "candidate.ndjson", FakeSession())
        self.assertIn(metadata, result)

    def test_semantic_states_are_distinct(self):
        self.assertEqual(
            semantic_classification("REJECT", "abc", None, None)["status"],
            "AMBIGUOUS_SEMANTICS",
        )
        evidence = {"witness": {"sha256": "abc", "result": {"normalized_outcome": "REJECT"}}}
        self.assertEqual(
            semantic_classification("REJECT", "abc", "REJECT", evidence)["status"],
            "CONFIRMED_EXPECTED_OUTCOME",
        )
        self.assertEqual(
            semantic_classification("ACCEPT", "abc", "REJECT", evidence)["status"],
            "CHECKER_DISAGREEMENT",
        )
        self.assertEqual(
            semantic_classification("REJECT", "other", "REJECT", evidence)["status"],
            "AMBIGUOUS_SEMANTICS",
        )


if __name__ == "__main__":
    unittest.main()
