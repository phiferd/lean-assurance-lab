import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
from lib import exploration as e
from lib import exploration_bookkeeping as b


class BookkeepingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'explorations').mkdir()
        (self.root / e.LEDGER).write_text('')
        (self.root / 'plan.md').write_text('\nEvidence class: E0\n')
        self.row = dict(argv=['checker', 'input'], exit_code=0, timed_out=False,
                        cleanup_complete=True)
        for stream in ('stdout', 'stderr'):
            (self.root / stream).write_text(stream)
            self.row['raw_' + stream + '_path'] = stream
            self.row[stream + '_sha256'] = hashlib.sha256(stream.encode()).hexdigest()
        (self.root / 'final.json').write_text(json.dumps({'cells': [{'receipt': self.row}]}))

    def test_duplicate_exports_count_once_and_verify_streams(self):
        (self.root / 'copy.json').write_text(json.dumps(self.row))
        launches, _ = b.inventory(self.root, ['final.json', 'copy.json', 'final.json'])
        self.assertEqual(len(launches), 1)
        (self.root / 'stdout').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'raw stream differs'):
            b.inventory(self.root, ['final.json'])

    def test_conflicting_copy_and_overlap_fail_closed(self):
        rows = {}
        b.merge(rows, [self.row])
        wrong = dict(self.row, exit_code=1)
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            b.merge(rows, [wrong])
        wrong = dict(self.row, raw_stderr_path='different')
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            b.merge(rows, [wrong])

    def test_prelaunch_exports_deduplicate_and_unknown_errors_refuse(self):
        value = dict(error='memory monitor backend unavailable before launch', cells=[])
        for name in ('error.json', 'result.json'):
            (self.root / name).write_text(json.dumps(value))
        launches, prelaunch = b.inventory(self.root, ['error.json', 'result.json'])
        self.assertEqual((len(launches), len(prelaunch)), (0, 1))
        (self.root / 'error.json').write_text('{"error":"unknown failure"}')
        with self.assertRaisesRegex(ValueError, 'unclassified'):
            b.inventory(self.root, ['error.json'])

    def test_receipt_paths_cannot_escape(self):
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            b.receipts(self.root, {'receipt': '../outside.json'})

    def test_start_draft_leaves_science_and_ledger_untouched(self):
        queue = dict(selected_item='CAMPAIGN', items=[dict(id='CAMPAIGN',
                     status='READY', evidence_refs=['plan.md'])])
        with patch('lib.research_queue_v4.load_queue', return_value=queue), \
             patch('subprocess.check_output', return_value=b'a' * 40):
            result = b.draft(self.root, 'start', 'EXPLORE-DRAFT-1')
        self.assertIsNone(result['event']['data']['question'])
        self.assertIsNone(result['event']['data']['planned_runs'])
        self.assertEqual(result['event']['data']['campaign'], 'CAMPAIGN')
        self.assertEqual((self.root / e.LEDGER).read_bytes(), b'')
        with self.assertRaises(ValidationError):
            e.validate(self.root, (json.dumps(dict(result['event'], at='2026-09-30T00:00:00Z')) + '\n').encode())

    def test_finish_draft_populates_only_supported_mechanics(self):
        states = {'EXPLORE-DRAFT-1': {'start': {'data': {'planned_runs': 1}}}}
        with patch('lib.exploration.validate', return_value=states):
            result = b.draft(self.root, 'finish', 'EXPLORE-DRAFT-1', ['final.json'], 'final.json')
            with self.assertRaisesRegex(ValueError, 'included'):
                b.draft(self.root, 'finish', 'EXPLORE-DRAFT-1', [], 'final.json')
        data = result['event']['data']
        self.assertEqual(data['completed_runs'], 1)
        for key in ('outcome', 'signal_count', 'measurement_complete',
                    'engineering_failures_unresolved', 'observations', 'decision'):
            self.assertIsNone(data[key])

    def test_campaign_counts_require_explicit_final_and_consistency(self):
        states = {'EXPLORE-DRAFT-1': {'start': {'data': {'campaign': 'CAMPAIGN'}},
                   'finish': {'data': {'raw_output': ['final.json'], 'completed_runs': 1}}}}
        with patch('lib.exploration.validate', return_value=states):
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                b.counts(self.root, 'CAMPAIGN', [])
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                b.counts(self.root, 'CAMPAIGN', ['missing.json'])
            result = b.counts(self.root, 'CAMPAIGN', ['final.json'])
            self.assertEqual(result['actual_launches'], 1)
            states['EXPLORE-DRAFT-1']['finish']['data']['completed_runs'] = 2
            with self.assertRaisesRegex(ValueError, 'disagrees'):
                b.counts(self.root, 'CAMPAIGN', ['final.json'])

    def test_existing_campaign_acceptance_preserves_evidence(self):
        root = e.ROOT
        campaign = 'E0-SEMANTIC-ASSURANCE-SCREENING-1'
        names = [('DATA-RECURSION', 'revision-2/attempt-0003'),
                 ('EXPRESSION-SHARING', 'attempt-0001'),
                 ('PROOF-TRANSFER-A', 'attempt-0002'),
                 ('PROOF-TRANSFER-B', 'attempt-0001'),
                 ('SUBSTITUTED-TARGET', 'attempt-0001'),
                 ('INVALID-TARGET', 'attempt-0001')]
        finals = [f'explorations/runs/EXPLORE-SEMANTIC-{name}-1/{attempt}/result.json'
                  for name, attempt in names]
        before = (root / e.LEDGER).read_bytes()
        result = b.counts(root, campaign, finals)
        self.assertEqual([result[k] for k in ('final_cells', 'actual_launches',
                         'prelaunch_failures', 'retained_nonfinal_cells')], [40, 48, 3, 8])
        self.assertEqual((root / e.LEDGER).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
