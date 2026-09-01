import copy
import hashlib
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

    def test_reviewed_catalog_changes_only_milestone_envelope_when_no_correction_authored(self):
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
        reviewed = copy.deepcopy(self.reviewed)
        reviewed["entries"][0]["characterization"]["authority"]["status"] = "ESTABLISHED"
        errors = validator.review_fact_errors(self.pre, reviewed, self.review)
        self.assertTrue(any("non-provisional" in item for item in errors))

    def test_soundness_overreach_is_rejected(self):
        reviewed = copy.deepcopy(self.reviewed)
        reviewed["entries"][0]["characterization"]["soundness_relevance"]["status"] = (
            "DIRECT_LOGICAL_SOUNDNESS_RELEVANCE_ESTABLISHED"
        )
        errors = validator.review_fact_errors(self.pre, reviewed, self.review)
        self.assertTrue(any("soundness assessment" in item for item in errors))

    def test_missing_authored_attack_or_rationale_fails(self):
        review = copy.deepcopy(self.review)
        review["challenges"][0]["attack"] = ""
        errors = validator.review_fact_errors(self.pre, self.reviewed, review)
        self.assertTrue(any("authored attack" in item for item in errors))

    def test_unrecorded_reviewed_catalog_change_fails(self):
        reviewed = copy.deepcopy(self.reviewed)
        reviewed["entries"][0]["characterization"]["notes"].append("unrecorded mutation")
        errors = validator.correction_errors(self.pre, reviewed, self.review)
        self.assertTrue(any("correction trail disagree" in item for item in errors))

    def test_authored_correction_can_validate_with_matching_catalog_change(self):
        reviewed = copy.deepcopy(self.reviewed)
        index = next(
            index
            for index, row in enumerate(reviewed["entries"])
            if row["characterization"]["id"] == "SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION"
        )
        effect_path = f"/entries/{index}/characterization/layers"
        reviewed["entries"][index]["characterization"]["layers"] = [
            "RECONSTRUCTION",
            "IMPLEMENTATION_POLICY",
        ]
        review = copy.deepcopy(self.review)
        challenge = review["challenges"][2]
        decision_id = "DEC.CATALOG.M9.FIXTURE.LAYER"
        challenge["correction_required"] = True
        challenge["correction_decision_ids"] = [decision_id]
        challenge["statement_hash_after"] = validator.target_hash(
            reviewed, challenge["target"]["catalog_ids"], challenge["target"]["surface_ids"]
        )
        target_ids = ["SCENARIO.REPLAY.ENVIRONMENT_CONSTRUCTION"]
        review["corrections"] = [
            {
                "decision_id": decision_id,
                "challenge_ids": [challenge["id"]],
                "target_ids": target_ids,
                "change_type": "LAYER_CHANGE",
                "previous_interpretation": "The scenario was classified as reconstruction only.",
                "corrected_interpretation": "The scenario also includes implementation policy.",
                "why_previous_failed": "The previous interpretation omitted an authored policy effect.",
                "evidence": [
                    {
                        "artifact": "pre_review_catalog",
                        "locators": ["/entries"],
                        "finding": "Fixture evidence binds the prior layer value.",
                    }
                ],
                "effect_paths": [effect_path],
                "statement_hash_before": validator.target_hash(self.pre, target_ids, []),
                "statement_hash_after": validator.target_hash(reviewed, target_ids, []),
                "catalog_hash_before": validator.projection_sha256(self.pre),
                "catalog_hash_after": validator.projection_sha256(reviewed),
            }
        ]
        review["summary"]["catalog_corrections"] = 1
        review["summary"]["layer_changes"] = 1
        review["status"] = "PASS_WITH_CATALOG_CORRECTIONS"
        review["conclusion"]["catalog_disposition"] = "APPLY_RECORDED_CORRECTIONS"
        review["conclusion"]["reviewed_catalog_sha256"] = hashlib.sha256(
            validator.document_bytes(reviewed)
        ).hexdigest()
        self.assertEqual(validator.correction_errors(self.pre, reviewed, review), [])

    def test_pre_review_generation_is_deterministic(self):
        for path, document in populator.rendered_documents().items():
            self.assertEqual(path.read_bytes(), validator.document_bytes(document))
        rendered_paths = set(populator.rendered_documents())
        self.assertNotIn(validator.REVIEWED_CATALOG_PATH, rendered_paths)
        self.assertNotIn(validator.CATALOG_PATH, rendered_paths)

    def test_renderer_preserves_authored_disposition_and_rationale(self):
        review = copy.deepcopy(self.review)
        review["challenges"][0]["disposition"] = "AUTHORED_FAILED_CHALLENGE_FIXTURE"
        review["challenges"][0]["rationale"] = (
            "An independently authored fixture rationale must survive presentation unchanged."
        )
        report = renderer.render_markdown(review)
        self.assertIn("AUTHORED_FAILED_CHALLENGE_FIXTURE", report)
        self.assertIn(review["challenges"][0]["rationale"], report)
        self.assertEqual(
            review["challenges"][0]["disposition"], "AUTHORED_FAILED_CHALLENGE_FIXTURE"
        )

    def test_renderer_has_no_semantic_decision_constructor(self):
        self.assertEqual(validator.renderer_separation_errors(), [])

    def test_freeze_cycle_is_rejected(self):
        self.assertTrue(
            validator.cycle_errors([{"from": "a", "to": "b"}, {"from": "b", "to": "a"}])
        )


if __name__ == "__main__":
    unittest.main()
