from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from lib import binder_model_audit as audit


def check(**overrides):
    record = {
        "operation": "LIFT", "context": ["x", "y"],
        "named_source": ["v", "y"], "source": ["b", 1],
        "named_arguments": [], "arguments": [], "parameters": {"s": 1, "d": 1},
        "contexts_after": [["x", "fresh", "y"]],
        "named_expected": [["v", "y"]], "expected": [["b", 2]],
    }
    record.update(overrides)
    audit.audit_operation(**record)


class HandWrittenSmokeTests(unittest.TestCase):
    """Synthetic operation examples; none consumes a scientific ordinal."""

    def test_single_lift_at_interior_cutoff(self):
        check()

    def test_single_substitution_lowers_later_context_index(self):
        check(operation="SUBST", context=["c0", "c1", "c2"],
              named_source=["a", ["v", "c0"], ["v", "c2"]],
              source=["a", ["b", 0], ["b", 2]],
              named_arguments=[["v", "c1"]], arguments=[["b", 0]], parameters={},
              contexts_after=[["c1", "c2"]],
              named_expected=[["a", ["v", "c1"], ["v", "c2"]]],
              expected=[["a", ["b", 0], ["b", 1]]])

    def test_lift_composition_checks_intermediate_and_final_results(self):
        check(operation="LIFT_COMPOSE", context=["c0", "c1"],
              named_source=["v", "c1"], source=["b", 1],
              parameters={"s1": 0, "d1": 1, "s2": 2, "d2": 1},
              contexts_after=[["j0", "c0", "c1"], ["j0", "c0", "j1", "c1"]],
              named_expected=[["v", "c1"], ["v", "c1"]],
              expected=[["b", 2], ["b", 3]])

    def test_substitution_composition_checks_intermediate_and_final_results(self):
        check(operation="SUBST_COMPOSE", context=["c0", "c1", "c2"],
              named_source=["a", ["v", "c0"], ["v", "c2"]],
              source=["a", ["b", 0], ["b", 2]],
              named_arguments=[["v", "c1"], ["v", "c2"]],
              arguments=[["b", 0], ["b", 0]], parameters={},
              contexts_after=[["c1", "c2"], ["c2"]],
              named_expected=[["a", ["v", "c1"], ["v", "c2"]],
                              ["a", ["v", "c2"], ["v", "c2"]]],
              expected=[["a", ["b", 0], ["b", 1]], ["a", ["b", 0], ["b", 0]]])

    def test_capture_avoiding_substitution_matches_alpha_renamed_output(self):
        check(operation="SUBST", context=["c0", "c1"],
              named_source=["l", "c1", ["s"], ["v", "c0"]],
              source=["l", ["s"], ["b", 1]],
              named_arguments=[["v", "c1"]], arguments=[["b", 0]], parameters={},
              contexts_after=[["c1"]],
              named_expected=[["l", "freshBinder", ["s"], ["v", "c1"]]],
              expected=[["l", ["s"], ["b", 1]]])


class NegativeAndPrimitiveTests(unittest.TestCase):
    def test_consistently_wrong_named_and_index_expectation_reaches_semantic_gate(self):
        with self.assertRaisesRegex(audit.AuditError, "E_EXPECTATION"):
            check(named_expected=[["v", "y"]], expected=[["b", 2]],
                  contexts_after=[["x", "fresh", "y"]],
                  named_source=["v", "x"], source=["b", 0])

    def test_capture_result_with_consistent_translation_is_still_rejected(self):
        with self.assertRaisesRegex(audit.AuditError, "E_EXPECTATION"):
            check(operation="SUBST", context=["c0", "c1"],
                  named_source=["l", "c1", ["s"], ["v", "c0"]],
                  source=["l", ["s"], ["b", 1]],
                  named_arguments=[["v", "c1"]], arguments=[["b", 0]], parameters={},
                  contexts_after=[["c1"]],
                  named_expected=[["l", "c1", ["s"], ["v", "c1"]]],
                  expected=[["l", ["s"], ["b", 0]]])

    def test_lambda_and_let_nonbody_fields_use_outer_depth(self):
        lam = ["l", ["b", 0], ["a", ["b", 0], ["b", 1]]]
        self.assertEqual(audit._shift(lam, 1),
                         ["l", ["b", 1], ["a", ["b", 0], ["b", 2]]])
        let = ["t", ["b", 0], ["b", 0], ["a", ["b", 0], ["b", 1]]]
        self.assertEqual(audit._shift(let, 1),
                         ["t", ["b", 1], ["b", 1], ["a", ["b", 0], ["b", 2]]])

    def test_nested_shadowing_and_argument_lifting(self):
        term = ["l", "x", ["s"], ["l", "x", ["s"], ["v", "x"]]]
        self.assertEqual(audit._translate(term, ["x"]),
                         ["l", ["s"], ["l", ["s"], ["b", 0]]])
        under_binder = ["l", ["b", 0], ["a", ["b", 0], ["b", 2]]]
        self.assertEqual(audit._instantiate1(under_binder, ["b", 0]),
                         ["l", ["b", 0], ["a", ["b", 0], ["b", 1]]])

    def test_integer_types_and_db_scope_fail_closed(self):
        with self.assertRaisesRegex(audit.AuditError, "E_NATURAL"):
            audit._validate_db(["b", True])
        with self.assertRaisesRegex(audit.AuditError, "E_NATURAL"):
            audit._validate_db(["b", -1])
        with self.assertRaisesRegex(audit.AuditError, "E_DB_SCOPE"):
            audit._scoped(["b", 2], 2)

    def test_missing_duplicate_extra_and_reordered_ordinals_fail(self):
        with self.assertRaisesRegex(audit.AuditError, "E_COHORT"):
            audit._check_ordinals([])
        with self.assertRaisesRegex(audit.AuditError, "E_DUPLICATE_ORDINAL"):
            audit._check_ordinals([0, 0])
        with self.assertRaisesRegex(audit.AuditError, "E_ORDINAL"):
            audit._check_ordinals([10_000])
        with self.assertRaisesRegex(audit.AuditError, "E_ORDER"):
            audit._check_ordinals([1, 0])

    def test_row_schema_and_strict_ndjson_fail_closed(self):
        with self.assertRaisesRegex(audit.AuditError, "E_FIELDS"):
            audit.audit_vector({"id": "non-scientific-invalid-fixture"})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "vectors.ndjson"
            path.write_text('{"id":"a","id":"b"}\n')
            with self.assertRaisesRegex(audit.AuditError, "E_JSON_DUPLICATE_KEY"):
                audit.audit_corpus(path)
            path.write_text('{ "id": "a" }\n')
            with self.assertRaisesRegex(audit.AuditError, "E_NDJSON_CANONICAL"):
                audit.audit_corpus(path)


if __name__ == "__main__":
    unittest.main()
