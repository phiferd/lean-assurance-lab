from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MutationModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "mutation-model" / "catalog.json").read_text())
        cls.batch = json.loads((ROOT / "results" / "mutation-batches" / "nanoda-semantic-0001.json").read_text())

    def test_manual_catalog_binds_specs(self) -> None:
        self.assertEqual(len(self.catalog["manual_mutants"]), 6)
        for row in self.catalog["manual_mutants"]:
            digest = hashlib.sha256((ROOT / row["spec"]).read_bytes()).hexdigest()
            self.assertEqual(digest, row["spec_sha256"])

    def test_generated_ids_are_content_deterministic(self) -> None:
        for spec in self.batch["mutants"]:
            payload = "\0".join(
                [
                    spec["source_file"], spec["source_span"].split("-")[0],
                    str(spec["source_column"]), spec["mutation_operator"],
                    spec["original"], spec["mutated"],
                ]
            ).encode()
            digest = hashlib.sha256(payload).hexdigest()
            self.assertEqual(spec["identity"]["sha256"], digest)
            self.assertEqual(spec["id"], f"nanoda-gen-{digest[:12]}")

    def test_attempts_have_final_classifications(self) -> None:
        allowed = {
            "COMPILING_SEMANTIC_MUTANT", "BUILD_FAILURE", "DUPLICATE",
            "UNSUPPORTED_MUTATION_SITE", "REJECTED_NON_SEMANTIC",
        }
        self.assertEqual(set(self.batch["attempt_summary"]), allowed)
        for status in allowed:
            count = sum(row["attempt_status"] == status for row in self.batch["attempts"])
            self.assertEqual(self.batch["attempt_summary"][status], count)

    def test_population_is_bounded_and_multi_family(self) -> None:
        self.assertGreaterEqual(self.batch["generated_count"], 10)
        self.assertLessEqual(self.batch["generated_count"], 25)
        self.assertGreaterEqual(len({row["operator_family"] for row in self.batch["mutants"]}), 3)


if __name__ == "__main__":
    unittest.main()
