from copy import deepcopy
import json
from pathlib import Path
import unittest

from lib.cvc4_evidence import BASE, check_mapping, nanoda_missing_parameter_records, validate

ROOT = Path(__file__).resolve().parents[1]


class SourceMappingTests(unittest.TestCase):
    def setUp(self):
        self.mapping = json.loads((ROOT / BASE / 'mapping/mapping.json').read_text())

    def test_exact_source_locks_and_proof_assumptions(self):
        self.assertEqual(check_mapping(ROOT, self.mapping), 12)

    def test_source_range_cannot_extend_past_actual_file(self):
        row = next(r for r in self.mapping['sources'] if r['id'] == 'OFFICIAL.INSTALLED.REPLAY')
        row['line_ranges'][-1]['end_line'] = 195
        with self.assertRaisesRegex(ValueError, 'source locator outside'):
            check_mapping(ROOT, self.mapping)

    def test_assumptions_cannot_be_silently_removed(self):
        self.mapping['checked_model']['transitive_axioms']['Lab.CVC2.preservation'].pop()
        with self.assertRaisesRegex(ValueError, 'assumption envelope changed'):
            check_mapping(ROOT, self.mapping)


class ClosureEvidenceTests(unittest.TestCase):
    def test_completed_result_replays_with_original_tooling(self):
        self.assertEqual(validate(ROOT)['outcome'], 'BOUNDED_UNRESOLVED')


class ParameterRecordBoundaryTests(unittest.TestCase):
    def test_frozen_ownership_streams_lack_the_declared_v_parameter_record(self):
        for filename, missing_name_id in (('e-owned-control.ndjson', 3), ('e-unowned.ndjson', 2)):
            with self.subTest(filename=filename):
                raw = (ROOT / BASE / 'inputs' / filename).read_bytes()
                self.assertEqual(nanoda_missing_parameter_records(raw), [missing_name_id])

    def test_explicit_declared_parameter_record_has_no_gap(self):
        raw = (b'{"in":1,"str":{"pre":0,"str":"decl"}}\n'
               b'{"in":2,"str":{"pre":0,"str":"u"}}\n'
               b'{"il":1,"param":2}\n'
               b'{"il":2,"succ":1}\n'
               b'{"ie":0,"sort":2}\n'
               b'{"ie":1,"sort":1}\n'
               b'{"def":{"all":[1],"hints":"opaque","levelParams":[2],'
               b'"name":1,"safety":"safe","type":0,"value":1}}\n')
        self.assertEqual(nanoda_missing_parameter_records(raw), [])


if __name__ == '__main__':
    unittest.main()
