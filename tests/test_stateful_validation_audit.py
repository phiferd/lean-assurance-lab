"""Synthetic positive and adversarial receipts for the independent stateful audit."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from lib import stateful_validation_audit as audit


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "results/research/stateful-validation-pilot-1/scientific-contract.json").read_text())


def encode(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"


def synthetic(comparison_id, side):
    """Make in-memory protocol data without calling the auditor's model."""
    comparison = next(row for row in CONTRACT["comparisons"] if row["id"] == comparison_id)
    requests = []
    for declaration_id in comparison[side]:
        declaration = CONTRACT["declarations"][declaration_id]
        requests.append({"id": declaration_id, "name": declaration["name"],
                         "type": declaration["type"], "value": declaration["value"]})
    fixture = {"comparison": comparison_id, "side": side, "requests": requests}
    records = [{"kind": "begin", "comparison": comparison_id, "side": side,
                "api": "Lean.Kernel.Environment.addDecl", "skipKernelTC": False,
                "trustLevel": 0, "environment": []}]
    environment = {}
    for index, (request, outcome) in enumerate(zip(requests, comparison[f"{side}_outcomes"])):
        if outcome == "ACCEPT":
            environment[request["name"]] = {
                "name": request["name"], "type": request["type"], "value": request["value"],
                "safety": "safe", "levelParams": [],
            }
        records.append({"kind": "step", "comparison": comparison_id, "side": side,
                        "index": index, "request": request, "outcome": outcome,
                        "environment": [copy.deepcopy(environment[name]) for name in sorted(environment)]})
    records.append({"kind": "end", "comparison": comparison_id, "side": side,
                    "steps": len(requests)})
    output = b"".join(encode(record) for record in records)
    return fixture, records, output


class StatefulAuditTests(unittest.TestCase):
    def refuse(self, action, code):
        with self.assertRaises(audit.AuditError) as raised:
            action()
        self.assertEqual(raised.exception.code, code)

    def test_contract_and_all_twelve_synthetic_histories(self):
        result = audit.audit_contract(CONTRACT)
        self.assertEqual((result["comparisons"], result["histories"], result["steps"]), (6, 12, 25))
        for comparison in CONTRACT["comparisons"]:
            for side in ("fresh", "prefixed"):
                with self.subTest(comparison=comparison["id"], side=side):
                    fixture, _, output = synthetic(comparison["id"], side)
                    parsed = audit.audit_fixture(encode(fixture), CONTRACT, comparison["id"], side)
                    receipt = audit.audit_output(output, b"", parsed, CONTRACT)
                    self.assertEqual(receipt["status"], "PASS")
                    self.assertEqual(receipt["target_outcome"], "ACCEPT")

    def test_contract_source_option_and_expected_result_changes_are_rejected(self):
        for mutate in (
            lambda d: d.update(source_commit="0" * 40),
            lambda d: d["options"].update({"debug.skipKernelTC": True}),
            lambda d: d["comparisons"][2]["prefixed_outcomes"].__setitem__(0, "ACCEPT"),
            lambda d: d["declarations"]["ordered"].__setitem__("value", ["sort", 0]),
        ):
            changed = copy.deepcopy(CONTRACT)
            mutate(changed)
            self.refuse(lambda: audit.audit_contract(changed), "E_CONTRACT")

    def test_bad_fixture_request_and_duplicate_json_key_are_rejected(self):
        fixture, _, _ = synthetic("accepted-independent", "prefixed")
        changed = copy.deepcopy(fixture)
        changed["requests"][0]["name"] = "LALState.Wrong"
        self.refuse(lambda: audit.audit_fixture(encode(changed), CONTRACT,
                                                "accepted-independent", "prefixed"), "E_FIXTURE")
        changed = copy.deepcopy(fixture)
        changed["requests"][0]["extra"] = 1
        self.refuse(lambda: audit.audit_fixture(encode(changed), CONTRACT,
                                                "accepted-independent", "prefixed"), "E_SCHEMA")
        raw = encode(fixture).replace(b'"side":"prefixed"', b'"side":"prefixed","side":"fresh"', 1)
        self.refuse(lambda: audit.audit_fixture(raw, CONTRACT,
                                                "accepted-independent", "prefixed"), "E_JSON")

    def test_rejected_step_cannot_add_a_fallback_axiom_or_reserve_name(self):
        fixture, records, _ = synthetic("rejected-name-reuse", "prefixed")
        changed = copy.deepcopy(records)
        changed[1]["environment"] = [{"name": "LALState.Reuse", "type": ["sort", 0],
                                      "value": ["sort", 0], "safety": "safe", "levelParams": []}]
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_ENVIRONMENT")
        changed = copy.deepcopy(records)
        changed[2]["outcome"] = "alreadyDeclared"
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_OUTCOME")

    def test_duplicate_rejection_preserves_exact_prior_body(self):
        fixture, records, _ = synthetic("rejected-duplicate", "prefixed")
        changed = copy.deepcopy(records)
        changed[2]["environment"][0]["value"] = ["sort", 1]
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_ENVIRONMENT")

    def test_order_extra_missing_and_malformed_records_are_rejected(self):
        fixture, records, output = synthetic("accepted-reduction", "prefixed")
        changed = copy.deepcopy(records)
        changed[2]["index"] = 0
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_STEP")
        self.refuse(lambda: audit.audit_output(output + encode(records[-1]), b"", fixture,
                                               CONTRACT), "E_OUTPUT")
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, records[:-2] + records[-1:])),
                                               b"", fixture, CONTRACT), "E_OUTPUT")
        changed = copy.deepcopy(records)
        changed[1]["request"]["extra"] = "x"
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_SCHEMA")
        self.refuse(lambda: audit.audit_output(output, b"warning", fixture, CONTRACT), "E_STDERR")
        changed = copy.deepcopy(records)
        changed[0]["trustLevel"] = False  # Python equality alone conflates this with zero.
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_BEGIN")
        changed = copy.deepcopy(records)
        changed[-1]["steps"] = True
        self.refuse(lambda: audit.audit_output(b"".join(map(encode, changed)), b"", fixture,
                                               CONTRACT), "E_END")

    def test_pi_lambda_application_and_delta_are_independent_semantic_checks(self):
        env = {"LALState.Alias": (("sort", 2), ("sort", 1))}
        identity = ("lam", ("const", "LALState.Alias"), ("var", 0))
        applied = ("app", identity, ("sort", 0))
        # Alias reduces to Sort 1, whose inhabitants include Sort 0.
        self.assertEqual(audit._nf(applied, env), ("sort", 0))
        self.assertEqual(audit._nf(audit._infer(applied, env), env), ("sort", 1))
        bad_argument = ("app", identity, ("sort", 1))
        self.refuse(lambda: audit._infer(bad_argument, env), "E_TYPE")
        self.refuse(lambda: audit._infer(("const", "LALState.Unknown"), env), "E_DEPENDENCY")


if __name__ == "__main__":
    unittest.main()
