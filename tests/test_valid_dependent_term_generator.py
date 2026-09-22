from __future__ import annotations

import hashlib
import hmac
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import valid_dependent_term_generator as generator  # noqa: E402


SCRIPT = ROOT / "scripts" / "generate-valid-dependent-term-pilot-1"


class ValidDependentTermGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.design = generator.load_design(ROOT)
        cls.cases = generator.generate_all(cls.design)

    def test_canonical_bytes_and_case_seed_follow_frozen_encoding(self):
        value = {"z": "λ", "a": [1, True]}
        self.assertEqual(generator.canonical_bytes(value), b'{"a":[1,true],"z":"\xce\xbb"}')
        self.assertEqual(generator.canonical_bytes(value, newline=True)[-1:], b"\n")

        preimage = self.design["deterministic_selection"]["master_seed_preimage_ascii_no_newline"]
        master = hashlib.sha256(preimage.encode("ascii")).digest()
        expected = hmac.new(master, b"pi\x00\x00\x00", hashlib.sha256).hexdigest()
        self.assertEqual(generator.generate_case(self.design, "pi", 0)["case_seed_sha256"], expected)

    def test_exact_count_order_attempts_uniqueness_and_bands(self):
        self.assertEqual(len(self.cases), 50)
        expected_order = [
            (category, index)
            for category in self.design["case_contract"]["order"]
            for index in range(1, 11)
        ]
        self.assertEqual(
            [(case["category"], case["category_index"]) for case in self.cases],
            expected_order,
        )
        self.assertEqual(Counter(case["category"] for case in self.cases), Counter({
            "pi": 10,
            "lambda": 10,
            "application": 10,
            "let": 10,
            "mixed": 10,
        }))
        self.assertEqual({case["selection_attempt"] for case in self.cases}, {0})
        hashes = [generator.expr_hash(case["term"]) for case in self.cases]
        self.assertEqual(len(set(hashes)), 50)

        policy = self.design["size_policy"]
        for case in self.cases:
            slot = case["category_index"] - 1
            bands = [band for band in policy["bands"] if slot in band["slots_zero_based"]]
            self.assertEqual(len(bands), 1)
            metrics = case["metrics"]
            self.assertGreaterEqual(metrics["node_count"], bands[0]["minimum_nodes"])
            self.assertLessEqual(metrics["node_count"], bands[0]["maximum_nodes"])
            self.assertGreaterEqual(
                metrics["node_count"], policy["category_minimum_nodes"][case["category"]]
            )
            self.assertLessEqual(metrics["ast_depth"], policy["maximum_ast_depth"])
            self.assertLessEqual(metrics["binder_depth"], policy["maximum_binder_depth"])
            self.assertLessEqual(
                metrics["maximum_input_sort_level"], policy["input_sort_levels"]["maximum"]
            )
            self.assertLessEqual(
                metrics["maximum_derived_sort_level"], policy["maximum_derived_sort_level"]
            )
            self.assertLessEqual(
                metrics["normalized_type_nodes"], policy["maximum_normalized_type_nodes"]
            )
            self.assertEqual(metrics["node_count"], sum(metrics["constructor_counts"].values()))

    def test_root_categories_and_frozen_predicates(self):
        roots = {
            "pi": "pi",
            "lambda": "lam",
            "application": "app",
            "let": "let",
            "mixed": "let",
        }
        for case in self.cases:
            term = case["term"]
            counts = case["metrics"]["constructor_counts"]
            self.assertEqual(term["tag"], roots[case["category"]])
            self.assertTrue(generator._matches_category(term, case["category"]))
            if case["category"] == "pi":
                self.assertEqual((counts["lam"], counts["app"], counts["let"]), (0, 0, 0))
            elif case["category"] == "lambda":
                self.assertEqual((counts["app"], counts["let"]), (0, 0))
            elif case["category"] == "application":
                self.assertEqual(counts["let"], 0)
                self.assertTrue(generator._has_beta_redex(term))
            elif case["category"] == "let":
                self.assertEqual(counts["app"], 0)
                self.assertTrue(generator._has_using_binder(term, "let"))
            else:
                self.assertTrue(generator._has_beta_redex(term))
                self.assertTrue(generator._has_active_zeta(term))

    def test_full_derivations_cover_every_rule_with_exact_shapes(self):
        rules: set[str] = set()
        premise_counts = {"sort": 0, "bvar": 0, "pi": 2, "lam": 2, "app": 2, "let": 3}
        node_keys = set(self.design["derivation_contract"]["node_exact_keys"])
        witness_shapes = self.design["derivation_contract"]["witness_shapes"]

        def visit(node):
            self.assertEqual(set(node), node_keys)
            self.assertIsInstance(node["context"], list)
            self.assertEqual(node["rule"], node["term"]["tag"])
            self.assertEqual(len(node["premises"]), premise_counts[node["rule"]])
            self.assertEqual(set(node["witness"]), set(witness_shapes[node["rule"]]))
            rules.add(node["rule"])
            for premise in node["premises"]:
                visit(premise)

        for category in self.design["case_contract"]["order"]:
            case = next(case for case in self.cases if case["category"] == category)
            self.assertEqual(case["derivation"]["context"], [])
            visit(case["derivation"])
        self.assertEqual(rules, {"sort", "bvar", "pi", "lam", "app", "let"})

    def test_numeric_imax_beta_and_zeta_positive_witnesses(self):
        dependent_pi = generator._pi(generator._sort(0), generator._bvar(0))
        dependent = generator._infer(dependent_pi)
        self.assertEqual(dependent["witness"], {
            "domain_level": 1,
            "body_level": 0,
            "result_level": 0,
        })

        nondependent_pi = generator._pi(generator._sort(0), generator._sort(0))
        nondependent = generator._infer(nondependent_pi)
        self.assertEqual(nondependent["witness"]["result_level"], 1)

        application = generator._app(
            generator._lam(generator._sort(0), generator._bvar(0)), dependent_pi
        )
        app_derivation = generator._infer(application)
        self.assertEqual(app_derivation["witness"]["domain_nf"], generator._sort(0))
        self.assertEqual(
            app_derivation["witness"]["argument_type_nf"], generator._sort(0)
        )
        self.assertEqual(generator._normalize(application), dependent_pi)

        let_term = generator._let(generator._sort(0), dependent_pi, generator._bvar(0))
        let_derivation = generator._infer(let_term)
        self.assertEqual(let_derivation["witness"]["annotation_nf"], generator._sort(0))
        self.assertEqual(generator._normalize(let_term), dependent_pi)

    def test_nested_shift_and_capture_avoiding_substitution(self):
        expr = generator._let(
            generator._bvar(0),
            generator._bvar(1),
            generator._pi(
                generator._bvar(1),
                generator._app(generator._bvar(2), generator._bvar(0)),
            ),
        )
        shifted = generator._shift(expr, 2, 0)
        expected_shift = generator._let(
            generator._bvar(2),
            generator._bvar(3),
            generator._pi(
                generator._bvar(3),
                generator._app(generator._bvar(4), generator._bvar(0)),
            ),
        )
        self.assertEqual(shifted, expected_shift)

        source = generator._lam(
            generator._sort(0),
            generator._app(generator._bvar(1), generator._bvar(0)),
        )
        replacement = generator._pi(generator._bvar(0), generator._bvar(1))
        substituted = generator._subst(source, replacement, 0)
        expected_substitution = generator._lam(
            generator._sort(0),
            generator._app(
                generator._pi(generator._bvar(1), generator._bvar(2)),
                generator._bvar(0),
            ),
        )
        self.assertEqual(substituted, expected_substitution)
        self.assertEqual(generator._subst(generator._bvar(2), replacement, 0), generator._bvar(1))

    def test_repeat_generation_is_byte_deterministic(self):
        repeated = generator.generate_all(self.design)
        self.assertEqual(generator.canonical_bytes(repeated), generator.canonical_bytes(self.cases))
        for category_offset, category in enumerate(self.design["case_contract"]["order"]):
            for slot in (0, 4, 9):
                expected = self.cases[category_offset * 10 + slot]
                self.assertEqual(
                    generator.canonical_bytes(generator.generate_case(self.design, category, slot)),
                    generator.canonical_bytes(expected),
                )

    def test_rendered_module_has_exact_declarations_and_no_bypass(self):
        source = generator.render_module(self.cases)
        self.assertTrue(source.endswith("\n"))
        self.assertEqual(source.count("\ndef "), 50)
        self.assertIn("namespace ValidDependentTermPilot1", source)
        self.assertIn("def pi01", source)
        self.assertIn("def mixed10", source)
        for forbidden in ("skipKernelTC", "unsafe", "axiom", "theorem"):
            self.assertNotIn(forbidden, source)

    def test_cli_validate_only_is_nonwriting_and_normal_output_is_fresh(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            validate_target = base / "validate-only-must-not-exist"
            validate = subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", str(validate_target), "--validate-only"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            manifest = json.loads(validate.stdout)
            self.assertFalse(validate_target.exists())
            self.assertEqual(manifest["case_count"], 50)
            self.assertEqual(len(manifest["cases"]), 50)

            output = base / "development-output"
            written = subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            written_manifest = json.loads(written.stdout)
            self.assertEqual(written_manifest, manifest)
            self.assertEqual(json.loads((output / "manifest.json").read_text()), manifest)
            self.assertEqual(len(list((output / "cases").glob("*.json"))), 50)
            module_path = output / manifest["module"]["path"]
            self.assertEqual(
                hashlib.sha256(module_path.read_bytes()).hexdigest(), manifest["module"]["sha256"]
            )

            refused = subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", str(output)],
                cwd=ROOT,
                capture_output=True,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn(b"FAIL:", refused.stderr)


if __name__ == "__main__":
    unittest.main()
