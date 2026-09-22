"""Adversarial tests for the recursor-type trust-boundary package."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from lib import recursor_type_trust_boundary as boundary


class RecursorTypeTrustBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = boundary.load_json(boundary.ROOT / boundary.POLICY)
        cls.contract = boundary.load_json(boundary.ROOT / boundary.CONTRACT)

    def test_exact_package_passes(self):
        result = boundary.validate(boundary.ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["new_checker_attempts"], 0)

    def test_source_hash_and_locator_tampering_fail(self):
        policy = copy.deepcopy(self.policy)
        policy["source_bindings"]["kiota_parser"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(boundary.BoundaryError, "binding differs"):
            boundary.validate_policy_value(policy)
        policy = copy.deepcopy(self.policy)
        policy["source_findings"][0]["line_ranges"] = [[1, 2]]
        with self.assertRaisesRegex(boundary.BoundaryError, "source finding differs"):
            boundary.validate_policy_value(policy)

    def test_policy_overclaim_and_catalog_promotion_fail(self):
        policy = copy.deepcopy(self.policy)
        policy["policy"] = "All checker implementations universally require record equality."
        policy["catalog_action"]["action"] = "PROMOTE"
        with self.assertRaisesRegex(boundary.BoundaryError, "scoped policy differs"):
            boundary.validate_policy_value(policy)

    def test_missing_unblock_condition_fails(self):
        policy = copy.deepcopy(self.policy)
        policy["implementation_boundary"]["exact_unblocking_condition"] = "Do the repair."
        with self.assertRaisesRegex(boundary.BoundaryError, "unblock condition"):
            boundary.validate_policy_value(policy)

    def test_raw_diagnostic_hash_tampering_fails(self):
        policy = copy.deepcopy(self.policy)
        policy["observed_ordering"]["bare_candidate"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(boundary.BoundaryError, "ordering evidence differs"):
            boundary.validate_policy_value(policy)

    def test_swapped_or_weakened_regression_outcomes_fail(self):
        contract = copy.deepcopy(self.contract)
        contract["required_regression"]["candidate_expected"] = "ACCEPT"
        contract["required_regression"]["control_expected"] = "OPTIONAL"
        with self.assertRaisesRegex(boundary.BoundaryError, "required regression"):
            boundary.validate_contract_value(contract)

    def test_pair_delta_tampering_fails(self):
        contract = copy.deepcopy(self.contract)
        contract["preserved_pair"]["only_scalar_difference"]["pointer"] = "/other"
        with self.assertRaisesRegex(boundary.BoundaryError, "pair delta"):
            boundary.validate_contract_value(contract)

    def test_launch_edit_and_external_action_fail(self):
        for field in ("new_checker_attempts", "production_checker_edits", "external_actions"):
            contract = copy.deepcopy(self.contract)
            contract[field] = 1
            with self.assertRaisesRegex(boundary.BoundaryError, "unauthorized launch or edit"):
                boundary.validate_contract_value(contract)

    def test_production_ready_without_design_fails(self):
        contract = copy.deepcopy(self.contract)
        contract["repair_readiness"]["production_edit_ready"] = True
        with self.assertRaisesRegex(boundary.BoundaryError, "readiness boundary"):
            boundary.validate_contract_value(contract)


if __name__ == "__main__":
    unittest.main()
