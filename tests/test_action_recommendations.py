import copy
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-action-recommendations"
loader = importlib.machinery.SourceFileLoader("action_recommendations", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class ActionRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "schemas" / "investigation-action-recommendations.schema.json").read_text()
        )
        cls.report = json.loads(
            (ROOT / "results" / "action-recommendations" / "current.json").read_text()
        )

    def test_current_recommendations_conform_to_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.report)

    def test_external_actions_are_human_gated(self):
        external = [
            recommendation
            for finding in self.report["findings"]
            for recommendation in finding["recommendations"]
            if recommendation["external_action"]
        ]
        self.assertTrue(external)
        self.assertTrue(all(row["human_gate"]["required"] for row in external))
        self.assertTrue(all(row["human_gate"]["status"] == "REVIEW_REQUIRED" for row in external))

    def test_every_finding_has_a_concrete_action(self):
        for finding in self.report["findings"]:
            self.assertTrue(finding["recommendations"])
            self.assertTrue(all(row["target"] and row["rationale"] for row in finding["recommendations"]))

    def test_schema_rejects_ungated_external_action(self):
        report = copy.deepcopy(self.report)
        recommendation = report["findings"][0]["recommendations"][1]
        recommendation["human_gate"] = {"required": False, "status": "NOT_REQUIRED"}
        errors = list(jsonschema.Draft202012Validator(self.schema).iter_errors(report))
        self.assertTrue(errors)

    def test_bound_evidence_hashes_match(self):
        for finding in self.report["findings"]:
            for evidence in finding["evidence"]:
                self.assertEqual(module.sha256_file(ROOT / evidence["path"]), evidence["sha256"])


if __name__ == "__main__":
    unittest.main()
