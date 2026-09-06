import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from cvc2_artifact import decode_sort_definition


class CVC2ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / "corpus/generated/universe-imax-right-succ.ndjson").read_bytes()
        self.records = [json.loads(line) for line in self.raw.splitlines()]

    def decode(self, records):
        return decode_sort_definition(
            ("\n".join(json.dumps(record) for record in records) + "\n").encode()
        )

    def reject(self, records):
        with self.assertRaises(ValueError):
            self.decode(records)

    def change(self, index, key, value):
        records = copy.deepcopy(self.records)
        records[index][key] = value
        return records

    def test_exact_existing_candidate_shape(self):
        self.assertEqual(decode_sort_definition(self.raw), {
            "name": "universeIMaxRightSucc", "params": ["u", "v"],
            "value_level": ["imax", ["param", "u"], ["succ", ["param", "v"]]],
            "type_level": ["succ", ["max", ["param", "u"],
                                    ["succ", ["param", "v"]]]],
        })

    def test_exact_existing_control_shape(self):
        raw = (ROOT / "corpus/generated/universe-imax-right-succ-control.ndjson").read_bytes()
        self.assertEqual(decode_sort_definition(raw), {
            "name": "universeIMaxRightSuccControl", "params": ["u", "v"],
            "value_level": ["max", ["param", "u"], ["succ", ["param", "v"]]],
            "type_level": ["succ", ["max", ["param", "u"],
                                    ["succ", ["param", "v"]]]],
        })

    def test_duplicate_json_keys_at_every_depth_are_rejected(self):
        replacements = [
            (b'"il":1', b'"il":1,"il":1'),
            (b'"pre":0', b'"pre":0,"pre":0'),
            (b'"exporter":{', b'"exporter":{},"exporter":{'),
            (b'"safety":"safe"', b'"safety":"safe","safety":"safe"'),
        ]
        for old, new in replacements:
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                decode_sort_definition(self.raw.replace(old, new, 1))

    def test_duplicate_namespace_ids_and_implicit_ids_are_rejected(self):
        for index in [1, 4, 10]:
            records = copy.deepcopy(self.records)
            records.insert(index + 1, copy.deepcopy(records[index]))
            with self.subTest(index=index):
                self.reject(records)
        for index, namespace in [(1, "in"), (4, "il")]:
            with self.subTest(implicit=namespace):
                self.reject(self.change(index, namespace, 0))

    def test_forward_and_unresolved_references_are_rejected(self):
        # Each namespace has its own already-defined reference boundary.
        for index, key, values in [
            (4, "param", [0, 99]), (6, "succ", [4, 99]),
            (7, "max", [[1, 5], [1, 99]]),
            (8, "imax", [[1, 6], [1, 99]]), (10, "sort", [99]),
        ]:
            for value in values:
                with self.subTest(index=index, value=value):
                    self.reject(self.change(index, key, value))
        records = copy.deepcopy(self.records)
        records[3], records[5] = records[5], records[3]
        self.reject(records)  # param references name 3 before its declaration
        for key in ["name", "type", "value"]:
            records = copy.deepcopy(self.records)
            records[-1]["def"][key] = 99
            with self.subTest(definition=key):
                self.reject(records)

    def test_boolean_noninteger_and_negative_ids_are_rejected(self):
        for value in [True, False, 1.0, "1", None, -1]:
            for index, key in [(1, "in"), (4, "il"), (10, "ie"),
                               (4, "param"), (6, "succ"), (10, "sort")]:
                with self.subTest(value=value, index=index, key=key):
                    self.reject(self.change(index, key, value))
            for key in ["name", "type", "value", "all", "levelParams"]:
                records = copy.deepcopy(self.records)
                records[-1]["def"][key] = [value] if key in {"all", "levelParams"} else value
                with self.subTest(value=value, definition=key):
                    self.reject(records)
            records = copy.deepcopy(self.records)
            records[1]["str"]["pre"] = value
            self.reject(records)
            self.reject(self.change(7, "max", [1, value]))
            self.reject(self.change(8, "imax", [1, value]))

    def test_extra_fields_are_rejected(self):
        paths = [(0,), (0, "meta"), (0, "meta", "exporter"),
                 (0, "meta", "format"), (0, "meta", "lean"),
                 (1,), (1, "str"), (4,), (10,), (-1,), (-1, "def")]
        for path in paths:
            records = copy.deepcopy(self.records)
            target = records
            for part in path:
                target = target[part]
            target["extra"] = 0
            with self.subTest(path=path):
                self.reject(records)

    def test_missing_fields_are_rejected(self):
        for index, field in [(0, "meta"), (1, "str"), (4, "param"),
                             (10, "sort"), (-1, "def")]:
            records = copy.deepcopy(self.records)
            del records[index][field]
            with self.subTest(index=index, field=field):
                self.reject(records)
        for field in self.records[-1]["def"]:
            records = copy.deepcopy(self.records)
            del records[-1]["def"][field]
            with self.subTest(definition=field):
                self.reject(records)

    def test_header_versions_are_fixed_and_lean_strings_are_provenance_only(self):
        for section, key, bad in [("exporter", "name", "other"),
                                  ("exporter", "version", "3.0.0"),
                                  ("format", "version", "3.0.0"),
                                  ("lean", "githash", 123),
                                  ("lean", "version", "")]:
            records = copy.deepcopy(self.records)
            records[0]["meta"][section][key] = bad
            with self.subTest(section=section, key=key):
                self.reject(records)
        records = copy.deepcopy(self.records)
        records[0]["meta"]["lean"] = {"githash": "different provenance", "version": "other"}
        self.assertEqual(self.decode(records), decode_sort_definition(self.raw))

    def test_parameter_ownership_includes_unused_level_records(self):
        records = copy.deepcopy(self.records)
        records.insert(-1, {"in": 4, "str": {"pre": 0, "str": "unowned"}})
        records.insert(-1, {"il": 7, "param": 4})
        self.reject(records)
        records = copy.deepcopy(self.records)
        records[-1]["def"]["levelParams"] = [2]
        self.reject(records)
        for params in [[2, 2], [2, 3, 0], [2, 3, 99], None]:
            records = copy.deepcopy(self.records)
            records[-1]["def"]["levelParams"] = params
            self.reject(records)
        records = copy.deepcopy(self.records)
        records[3]["str"]["str"] = "u"
        self.reject(records)  # distinct IDs cannot disguise duplicate names

    def test_only_final_single_safe_opaque_definition_is_supported(self):
        for key, value in [("safety", "unsafe"), ("safety", True),
                           ("hints", "regular"), ("all", []), ("all", [2]),
                           ("all", [1, 1]), ("name", 0)]:
            records = copy.deepcopy(self.records)
            records[-1]["def"][key] = value
            with self.subTest(key=key, value=value):
                self.reject(records)
        self.reject(self.records[:-1])
        self.reject(self.records + [self.records[-1]])
        self.reject(self.records + [{"ie": 2, "sort": 0}])
        records = copy.deepcopy(self.records)
        records[-1] = {"thm": records[-1]["def"]}
        self.reject(records)

    def test_other_names_levels_and_expression_forms_are_rejected(self):
        for index, replacement in [
            (1, {"in": 1, "num": {"pre": 0, "num": 1}}),
            (4, {"il": 1, "mvar": 2}), (4, {"il": 1, "zero": True}),
            (10, {"ie": 0, "bvar": 0}), (10, {"ie": 0, "mvar": 1}),
            (10, {"ie": 0, "const": {"name": 1, "levels": []}}),
        ]:
            records = copy.deepcopy(self.records)
            records[index] = replacement
            with self.subTest(replacement=replacement):
                self.reject(records)
        for value in ["", 1, None]:
            records = copy.deepcopy(self.records)
            records[1]["str"]["str"] = value
            self.reject(records)
        records = copy.deepcopy(self.records)
        records[2]["str"]["pre"] = 1
        self.reject(records)
        for value in [1, [1], [1, 2, 3], {"left": 1, "right": 2}]:
            self.reject(self.change(7, "max", value))

    def test_valid_changed_references_remain_changed_in_extracted_body(self):
        original = decode_sort_definition(self.raw)
        replaced = self.decode(self.change(11, "sort", 4))
        self.assertEqual(replaced["value_level"][0], "max")
        self.assertNotEqual(replaced["value_level"], original["value_level"])
        records = copy.deepcopy(self.records)
        records[-1]["def"]["value"] = 0
        self.assertEqual(self.decode(records)["value_level"], original["type_level"])
        zero_body = self.decode(self.change(11, "sort", 0))
        self.assertEqual(zero_body["value_level"], ["zero"])
        changed_child = self.decode(self.change(8, "imax", [1, 0]))
        self.assertEqual(changed_child["value_level"], ["imax", ["param", "u"], ["zero"]])
        self.assertEqual(changed_child["type_level"], original["type_level"])

    def test_extracted_trees_do_not_share_mutable_nodes(self):
        decoded = self.decode(self.change(11, "sort", 4))
        expected_type = copy.deepcopy(decoded["type_level"])
        decoded["value_level"][1][1] = "changed"
        self.assertEqual(decoded["type_level"], expected_type)

    def test_invalid_json_encoding_and_nonobject_records_are_rejected(self):
        for raw in [b"", b"\xff", self.raw + b"\n", self.raw + b"null\n",
                    b"null\n", self.raw.replace(b'"il":1', b'"il":NaN', 1),
                    self.raw.replace(b'"il":1', b'"il":Infinity', 1),
                    self.raw.decode()]:
            with self.subTest(raw=repr(raw)[:60]), self.assertRaises(ValueError):
                decode_sort_definition(raw)


if __name__ == "__main__":
    unittest.main()
