from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from lib import valid_dependent_term_audit as audit


ROOT = Path(__file__).resolve().parents[1]
DESIGN = json.loads((ROOT / "results/research/valid-dependent-term-pilot-1/design.json").read_text())
S0 = {"tag": "sort", "level": 0}
B0 = {"tag": "bvar", "index": 0}


def pi_term():
    return {"tag": "pi", "domain": copy.deepcopy(S0), "body": copy.deepcopy(B0)}


def lam_term():
    return {"tag": "lam", "domain": copy.deepcopy(S0), "body": copy.deepcopy(B0)}


def app_term():
    return {"tag": "app", "function": lam_term(), "argument": pi_term()}


def let_term():
    return {"tag": "let", "type": copy.deepcopy(S0), "value": pi_term(),
            "body": copy.deepcopy(B0)}


def mixed_term():
    nested_pi = {"tag": "pi", "domain": copy.deepcopy(S0),
                 "body": {"tag": "pi", "domain": copy.deepcopy(B0),
                          "body": {"tag": "bvar", "index": 1}}}
    return {"tag": "let", "type": copy.deepcopy(S0),
            "value": {"tag": "app", "function": lam_term(), "argument": nested_pi},
            "body": copy.deepcopy(B0)}


def reducible_sort_zero():
    return {"tag": "app",
            "function": {"tag": "lam", "domain": {"tag": "sort", "level": 1},
                         "body": copy.deepcopy(B0)},
            "argument": copy.deepcopy(S0)}


def app_with_raw_result_type():
    domain = reducible_sort_zero()
    return {"tag": "app",
            "function": {"tag": "lam", "domain": domain, "body": copy.deepcopy(B0)},
            "argument": pi_term()}


def let_with_raw_result_type():
    domain = {"tag": "let", "type": {"tag": "sort", "level": 1},
              "value": copy.deepcopy(S0), "body": copy.deepcopy(B0)}
    return {"tag": "let", "type": domain, "value": pi_term(), "body": copy.deepcopy(B0)}


TERMS = {"pi": pi_term, "lambda": lam_term, "application": app_term,
         "let": let_term, "mixed": mixed_term}


def dev_design(count=10):
    design = copy.deepcopy(DESIGN)
    design["case_contract"]["count_per_category"] = count
    design["case_contract"]["total"] = count * len(design["case_contract"]["order"])
    design["case_contract"]["distinct_term_hashes"] = design["case_contract"]["total"]
    return design


def case_for(category, index=1, term=None, design=None):
    design = design or dev_design()
    term = copy.deepcopy(term if term is not None else TERMS[category]())
    expected = audit._nf(audit._infer(term))
    return {
        "schema_version": 1,
        "case_id": f"vdtp1-{category}-{index:02d}",
        "case_seed_sha256": audit._case_seed(design, category, index - 1),
        "category": category,
        "category_index": index,
        "selection_attempt": 0,
        "term": term,
        "expected_type_nf": expected,
        "derivation": audit._derive(term),
        "metrics": audit._metrics(term, expected),
    }


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode() + b"\n"


class SemanticPrimitiveTests(unittest.TestCase):
    def test_shift_and_capture_avoiding_substitution(self):
        term = {"tag": "lam", "domain": copy.deepcopy(S0),
                "body": {"tag": "app", "function": {"tag": "bvar", "index": 0},
                         "argument": {"tag": "bvar", "index": 1}}}
        self.assertEqual(audit._shift(term, 2)["body"]["argument"]["index"], 3)
        body = {"tag": "lam", "domain": copy.deepcopy(S0),
                "body": {"tag": "bvar", "index": 1}}
        self.assertEqual(audit._subst(body, pi_term())["body"], pi_term())

    def test_beta_and_zeta_normalization(self):
        self.assertEqual(audit._nf(app_term()), pi_term())
        self.assertEqual(audit._nf(let_term()), pi_term())

    def test_pi_universe_witness_v_zero_and_nonzero(self):
        prop_pi = audit._derive(pi_term())
        self.assertEqual(prop_pi["witness"],
                         {"domain_level": 1, "body_level": 0, "result_level": 0})
        type_pi = audit._derive({"tag": "pi", "domain": copy.deepcopy(S0),
                                 "body": copy.deepcopy(S0)})
        self.assertEqual(type_pi["witness"],
                         {"domain_level": 1, "body_level": 1, "result_level": 1})

    def test_derivation_preserves_raw_app_and_let_substitution_results(self):
        application = audit._derive(app_with_raw_result_type())
        self.assertEqual(application["type"], reducible_sort_zero())
        self.assertEqual(application["witness"]["result_type"], reducible_sort_zero())
        self.assertEqual(audit._nf(application["type"]), S0)
        let = audit._derive(let_with_raw_result_type())
        self.assertEqual(let["type"], let_with_raw_result_type()["type"])
        self.assertEqual(let["witness"]["result_type"], let_with_raw_result_type()["type"])
        self.assertEqual(audit._nf(let["type"]), S0)

    def test_loose_bvar_and_app_let_conversion_fail_closed(self):
        with self.assertRaisesRegex(audit.AuditError, "E_LOOSE_BVAR"):
            audit._infer(copy.deepcopy(B0))
        bad_app = app_term()
        bad_app["argument"] = copy.deepcopy(S0)
        with self.assertRaisesRegex(audit.AuditError, "E_APP_CONVERSION"):
            audit._infer(bad_app)
        bad_let = let_term()
        bad_let["value"] = copy.deepcopy(S0)
        with self.assertRaisesRegex(audit.AuditError, "E_LET_CONVERSION"):
            audit._infer(bad_let)


class CaseAuditTests(unittest.TestCase):
    def setUp(self):
        self.design = dev_design()
        self.case = case_for("pi", design=self.design)

    def refuse(self, changed, code):
        with self.assertRaises(audit.AuditError) as raised:
            audit.audit_case(changed, self.design)
        self.assertEqual(raised.exception.code, code)

    def test_all_five_static_dev_categories_pass(self):
        for category in self.design["case_contract"]["order"]:
            result = audit.audit_case(case_for(category, design=self.design), self.design)
            self.assertEqual(set(result), {"case_id", "status", "term_sha256",
                                           "expected_type_sha256", "derivation_sha256",
                                           "metrics_sha256"})
            self.assertEqual(result["status"], "PASS")

    def test_unknown_missing_ast_and_case_keys_rejected(self):
        changed = copy.deepcopy(self.case); changed["unknown"] = 1
        self.refuse(changed, "E_CASE_KEYS")
        changed = copy.deepcopy(self.case); changed.pop("metrics")
        self.refuse(changed, "E_CASE_KEYS")
        changed = copy.deepcopy(self.case); changed["term"]["unknown"] = 1
        self.refuse(changed, "E_AST_KEYS")
        changed = copy.deepcopy(self.case); changed["term"]["tag"] = "const"
        self.refuse(changed, "E_AST_TAG")

    def test_wrong_derivation_rule_premises_context_term_type_and_witness(self):
        mutations = [
            (lambda d: d.update(rule="lam"), "E_DERIVATION_RULE"),
            (lambda d: d["premises"].pop(), "E_DERIVATION_PREMISES"),
            (lambda d: d.update(context=[copy.deepcopy(S0)]), "E_DERIVATION_CONTEXT"),
            (lambda d: d.update(term=copy.deepcopy(S0)), "E_DERIVATION_TERM"),
            (lambda d: d.update(type={"tag": "sort", "level": 1}), "E_DERIVATION_TYPE"),
            (lambda d: d["witness"].update(result_level=2), "E_DERIVATION_WITNESS"),
        ]
        for mutate, code in mutations:
            changed = copy.deepcopy(self.case)
            mutate(changed["derivation"])
            self.refuse(changed, code)
        changed = copy.deepcopy(self.case); changed["derivation"].pop("context")
        self.refuse(changed, "E_DERIVATION_KEYS")

    def test_app_and_let_conversion_and_substitution_witnesses_are_replayed(self):
        for category in ("application", "let"):
            changed = case_for(category, design=self.design)
            changed["derivation"]["witness"]["result_type"] = {"tag": "sort", "level": 1}
            self.refuse(changed, "E_DERIVATION_WITNESS")

    def test_category_metrics_seed_expected_type_and_size_tamper(self):
        changed = copy.deepcopy(self.case); changed["category"] = "lambda"
        changed["case_id"] = "vdtp1-lambda-01"
        changed["case_seed_sha256"] = audit._case_seed(self.design, "lambda", 0)
        self.refuse(changed, "E_CATEGORY")
        changed = copy.deepcopy(self.case); changed["metrics"]["node_count"] += 1
        self.refuse(changed, "E_METRICS")
        changed = copy.deepcopy(self.case); changed["metrics"]["node_count"] = True
        self.refuse(changed, "E_NATURAL")
        changed = copy.deepcopy(self.case); changed["case_seed_sha256"] = "0" * 64
        self.refuse(changed, "E_SEED")
        changed = copy.deepcopy(self.case); changed["selection_attempt"] = 1
        self.refuse(changed, "E_SELECTION_ATTEMPT")
        changed = copy.deepcopy(self.case); changed["expected_type_nf"] = {"tag": "sort", "level": 1}
        self.refuse(changed, "E_EXPECTED_TYPE")
        large_slot = case_for("pi", index=8, design=self.design)
        self.refuse(large_slot, "E_SIZE")

    def test_file_loader_rejects_duplicate_and_missing_keys_and_binds_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            path.write_bytes(canonical(self.case))
            result = audit.audit_case_file(path, self.design)
            self.assertEqual(set(result), {"case_id", "status", "term_sha256",
                                           "expected_type_sha256", "derivation_sha256",
                                           "metrics_sha256", "path", "sha256", "bytes"})
            self.assertEqual(result["bytes"], len(path.read_bytes()))
            self.assertEqual(result["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            raw = canonical(self.case).decode().rstrip("\n")
            path.write_text(raw[:-1] + ',"case_id":"duplicate"}\n')
            with self.assertRaisesRegex(audit.AuditError, "E_DUPLICATE_KEY"):
                audit.audit_case_file(path, self.design)
            missing = copy.deepcopy(self.case); missing.pop("term")
            path.write_bytes(canonical(missing))
            with self.assertRaisesRegex(audit.AuditError, "E_CASE_KEYS"):
                audit.audit_case_file(path, self.design)
            unknown = copy.deepcopy(self.case); unknown["unknown"] = None
            path.write_bytes(canonical(unknown))
            with self.assertRaisesRegex(audit.AuditError, "E_CASE_KEYS"):
                audit.audit_case_file(path, self.design)


class CorpusAuditTests(unittest.TestCase):
    def write_cases(self, directory, cases):
        paths = []
        for position, case in enumerate(cases):
            path = Path(directory) / f"{position:02d}.json"
            path.write_bytes(canonical(case))
            paths.append(path)
        return paths

    def test_exact_dev_corpus_order_passes_and_reordering_fails(self):
        design = dev_design(count=1)
        cases = [case_for(category, design=design) for category in design["case_contract"]["order"]]
        with tempfile.TemporaryDirectory() as directory:
            paths = self.write_cases(directory, cases)
            result = audit.audit_corpus(paths, design)
            self.assertEqual(set(result), {"status", "case_count", "category_counts",
                                           "cases", "aggregate_sha256"})
            self.assertEqual(result["case_count"], 5)
            with self.assertRaisesRegex(audit.AuditError, "E_CORPUS_ORDER"):
                audit.audit_corpus(list(reversed(paths)), design)

    def test_duplicate_terms_are_rejected_after_valid_order(self):
        design = dev_design(count=2)
        design["case_contract"]["order"] = ["pi"]
        design["case_contract"]["total"] = 2
        design["case_contract"]["distinct_term_hashes"] = 2
        cases = [case_for("pi", index=index, term=pi_term(), design=design) for index in (1, 2)]
        with tempfile.TemporaryDirectory() as directory:
            paths = self.write_cases(directory, cases)
            with self.assertRaisesRegex(audit.AuditError, "E_CORPUS_DUPLICATE"):
                audit.audit_corpus(paths, design)

    def test_count_is_rejected_before_reading_cases(self):
        design = dev_design(count=1)
        with self.assertRaisesRegex(audit.AuditError, "E_CORPUS_COUNT"):
            audit.audit_corpus([], design)


if __name__ == "__main__":
    unittest.main()
