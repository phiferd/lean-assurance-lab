"""Adversarial tests for the Kiota recursor-type design package."""
from __future__ import annotations

import copy
import unittest

from lib import kiota_recursor_type_design as design


class KiotaRecursorTypeDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = design.load_json(design.ROOT / design.SOURCE)
        cls.construction = design.load_json(design.ROOT / design.DESIGN)
        cls.fixtures = design.load_json(design.ROOT / design.FIXTURES)
        cls.audit = design.load_json(design.ROOT / design.AUDIT)
        cls.result = design.load_json(design.ROOT / design.RESULT)

    def test_exact_package_passes(self):
        result = design.validate_package(design.ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["outcome"], "VALIDATED_COMPLETE_KIOTA_DESIGN")

    def test_source_hash_or_locator_tampering_fails(self):
        value = copy.deepcopy(self.source)
        value["source_bindings"]["kiota_parser"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(design.DesignError, "binding differs"):
            design.validate_source_value(value)
        value = copy.deepcopy(self.source)
        value["source_findings"][0]["line_ranges"] = [[1, 2]]
        with self.assertRaisesRegex(design.DesignError, "source finding differs"):
            design.validate_source_value(value)

    def test_base_or_nested_stage_omission_fails(self):
        value = copy.deepcopy(self.construction)
        value["base_construction"]["steps"].pop()
        with self.assertRaisesRegex(design.DesignError, "base construction stages"):
            design.validate_design_value(value)
        value = copy.deepcopy(self.construction)
        value["nested_construction"]["steps"].pop(1)
        with self.assertRaisesRegex(design.DesignError, "nested construction stages"):
            design.validate_design_value(value)

    def test_circular_current_rec_environment_fails(self):
        value = copy.deepcopy(self.construction)
        value["input_contract"]["stage"] = "After all supplied recursors are installed"
        with self.assertRaisesRegex(design.DesignError, "circular recursor trust"):
            design.validate_design_value(value)

    def test_weaker_comparison_relation_fails(self):
        value = copy.deepcopy(self.construction)
        value["comparison_adjudication"]["structural_equality"]["selected"] = True
        value["comparison_adjudication"]["definitional_equality_then_replacement"]["selected"] = False
        with self.assertRaisesRegex(design.DesignError, "comparison selection"):
            design.validate_design_value(value)

    def test_fixture_hash_profile_or_outcome_tampering_fails(self):
        value = copy.deepcopy(self.fixtures)
        value["accepted_fixture_bindings"][0]["static_profile"]["blocks"] = 2
        with self.assertRaisesRegex(design.DesignError, "fixture expectation or profile"):
            design.validate_fixtures_value(value)
        value = copy.deepcopy(self.fixtures)
        value["inherited_regression"]["candidate"]["expected_after_repair"] = "ACCEPT"
        with self.assertRaisesRegex(design.DesignError, "inherited regression"):
            design.validate_fixtures_value(value)

    def test_audit_cannot_authorize_production_edit(self):
        value = copy.deepcopy(self.audit)
        value["verdict"]["production_edit_authorized_by_this_item"] = True
        with self.assertRaisesRegex(design.DesignError, "audit verdict"):
            design.validate_audit_value(value)

    def test_result_cannot_overclaim_or_record_actions(self):
        value = copy.deepcopy(self.result)
        value["claim_limits"] = ["Universal requirement for all importers."]
        with self.assertRaisesRegex(design.DesignError, "claim limits omit"):
            design.validate_result_value(value)
        value = copy.deepcopy(self.result)
        value["observations"]["checker_attempts"] = 1
        with self.assertRaisesRegex(design.DesignError, "observations differ"):
            design.validate_result_value(value)


if __name__ == "__main__":
    unittest.main()
