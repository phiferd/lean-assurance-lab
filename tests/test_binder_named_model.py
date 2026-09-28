"""Hand-written development fixtures; these are not scientific vectors."""
import unittest

from lib.binder_named_model import ModelError, alpha_equal, free_names, substitute, to_indices


class NamedModelTests(unittest.TestCase):
    def test_capture_avoided_under_lambda(self):
        source = ["l", "c1", ["s"], ["a", ["v", "c0"], ["v", "c1"]]]
        actual = substitute(source, "c0", ["v", "c1"])
        self.assertEqual(free_names(actual), {"c1"})
        self.assertNotEqual(actual[1], "c1")
        self.assertEqual(to_indices(actual, ["c1"]),
                         ["l", ["s"], ["a", ["b", 1], ["b", 0]]])

    def test_nested_shadow_and_outer_name_in_inner_domain(self):
        source = ["l", "x", ["s"],
                  ["l", "x", ["v", "x"], ["a", ["v", "x"], ["v", "c0"]]]]
        actual = substitute(source, "c0", ["v", "x"])
        self.assertEqual(free_names(actual), {"x"})
        self.assertEqual(to_indices(actual, ["x"]),
                         ["l", ["s"], ["l", ["b", 0], ["a", ["b", 0], ["b", 2]]]])

    def test_let_type_and_value_outside_binder(self):
        source = ["t", "x", ["v", "x"], ["v", "c0"], ["a", ["v", "x"], ["v", "c0"]]]
        actual = substitute(source, "c0", ["v", "x"])
        self.assertEqual(to_indices(actual, ["x"]),
                         ["t", ["b", 0], ["b", 0], ["a", ["b", 0], ["b", 1]]])

    def test_alpha_equivalence_checks_free_names(self):
        self.assertTrue(alpha_equal(["l", "x", ["s"], ["v", "x"]],
                                    ["l", "y", ["s"], ["v", "y"]]))
        self.assertFalse(alpha_equal(["l", "x", ["s"], ["v", "x"]],
                                     ["l", "y", ["s"], ["v", "x"]]))

    def test_invalid_scope_fails(self):
        with self.assertRaises(ModelError):
            to_indices(["v", "missing"], ["c0"])


if __name__ == "__main__":
    unittest.main()
