import copy
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


validator = load_module(
    "declaration_m9_validator_tests",
    ROOT / "scripts" / "validate-declaration-validation-milestone-9",
)
renderer = load_module(
    "declaration_m9_renderer_tests",
    ROOT / "scripts" / "render-declaration-validation-milestone-9-review",
)
history = load_module(
    "declaration_m9_history_tests",
    ROOT / "scripts" / "validate-declaration-validation-historical",
)
populator = load_module(
    "declaration_m9_populator_tests",
    ROOT / "scripts" / "populate-declaration-validation-milestone-9",
)


class DeclarationValidationMilestone9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pre = validator.load_json(validator.PRE_CATALOG_PATH)
        cls.reviewed = validator.load_json(validator.REVIEWED_CATALOG_PATH)
        cls.review = validator.load_json(validator.REVIEW_PATH)

    def test_milestone_9_artifacts_pass(self):
        self.assertEqual(validator.validate_document(), [])

    def test_review_schema_and_exact_challenge_set(self):
        schema = validator.load_json(validator.REVIEW_SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(self.review)
        self.assertEqual(len(self.review["challenges"]), 12)
        self.assertEqual(
            [row["challenge"] for row in self.review["challenges"]], renderer.QUESTIONS
        )

    def test_pre_review_inventory_is_exact_immutable_m8_content(self):
        m8, errors = validator.immutable_m8_catalog(history)
        self.assertEqual(errors, [])
        self.assertIsNotNone(m8)
        self.assertEqual(
            validator.inventory_projection(self.pre), validator.inventory_projection(m8)
        )
        self.assertNotEqual(
            populator.document_sha256(self.pre),
            history.load_json(history.M8_ATTESTATION_PATH)["artifacts"]["catalog"]["sha256"],
        )

    def test_reviewed_catalog_changes_only_milestone_envelope(self):
        self.assertEqual(
            validator.inventory_projection(self.pre),
            validator.inventory_projection(self.reviewed),
        )
        self.assertNotEqual(
            populator.document_sha256(self.pre), populator.document_sha256(self.reviewed)
        )
        self.assertEqual(
            validator.document_bytes(self.reviewed), validator.CATALOG_PATH.read_bytes()
        )

    def test_challenge_hash_tampering_fails(self):
        review = copy.deepcopy(self.review)
        review["challenges"][0]["statement_hash_before"] = "0" * 64
        errors = validator.review_fact_errors(self.pre, self.reviewed, review)
        self.assertTrue(any("statement hash" in item for item in errors))

    def test_unbound_review_evidence_fails(self):
        review = copy.deepcopy(self.review)
        review["challenges"][0]["evidence"][0]["artifact"] = "unbound"
        errors = validator.review_fact_errors(self.pre, self.reviewed, review)
        self.assertTrue(any("unbound artifact" in item for item in errors))

    def test_unresolving_review_evidence_locator_fails(self):
        review = copy.deepcopy(self.review)
        review["challenges"][0]["evidence"][0]["locators"] = ["/does/not/exist"]
        catalog_validator = load_module(
            "declaration_m9_catalog_locator_tests",
            ROOT / "scripts" / "validate-declaration-validation-catalog",
        )
        errors = validator.review_evidence_locator_errors(review, catalog_validator)
        self.assertTrue(any("does not resolve" in item for item in errors))

    def test_authority_promotion_is_rejected(self):
        pre = copy.deepcopy(self.pre)
        pre["entries"][0]["characterization"]["authority"]["status"] = "ESTABLISHED"
        errors = validator.review_fact_errors(pre, self.reviewed, self.review)
        self.assertTrue(any("non-provisional" in item for item in errors))

    def test_soundness_overreach_is_rejected(self):
        pre = copy.deepcopy(self.pre)
        pre["entries"][0]["characterization"]["soundness_relevance"]["status"] = (
            "DIRECT_LOGICAL_SOUNDNESS_RELEVANCE_ESTABLISHED"
        )
        errors = validator.review_fact_errors(pre, self.reviewed, self.review)
        self.assertTrue(any("soundness assessment" in item for item in errors))

    def test_duplicate_denotation_is_rejected(self):
        pre = copy.deepcopy(self.pre)
        pre["entries"][1]["semantic_denotation_sha256"] = pre["entries"][0][
            "semantic_denotation_sha256"
        ]
        errors = validator.review_fact_errors(pre, self.reviewed, self.review)
        self.assertTrue(any("duplicate active" in item for item in errors))

    def test_no_correction_status_rejects_correction_trail(self):
        review = copy.deepcopy(self.review)
        review["corrections"] = [
            {
                "decision_id": "DEC.CATALOG.M9.FIXTURE",
                "target_ids": ["DECL.THEOREM.TYPE_PROP"],
                "reason": "mutation fixture",
                "catalog_hash_before": "0" * 64,
                "catalog_hash_after": "1" * 64,
            }
        ]
        errors = validator.review_fact_errors(self.pre, self.reviewed, review)
        self.assertTrue(any("correction trail" in item for item in errors))

    def test_m9_generation_is_deterministic(self):
        for path, document in populator.rendered_documents().items():
            self.assertEqual(path.read_bytes(), validator.document_bytes(document))
        self.assertEqual(validator.REVIEW_PATH.read_bytes(), validator.document_bytes(renderer.render()))

    def test_freeze_cycle_is_rejected(self):
        self.assertTrue(
            validator.cycle_errors([{"from": "a", "to": "b"}, {"from": "b", "to": "a"}])
        )


if __name__ == "__main__":
    unittest.main()
