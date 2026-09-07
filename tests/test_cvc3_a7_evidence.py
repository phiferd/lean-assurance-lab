"""Pure regressions for the actual terminal A7 transcript; no process fixtures."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc3_a7_evidence as evidence
from lib import cvc_a7_runner as runner
from lib.cvc_prep import append, read_events
from lib.cvc_process import atomic


class A7ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = evidence.load(ROOT / runner.MANIFEST)
        self.out = self.root / runner.OUT
        self.out.parent.mkdir(parents=True)
        shutil.copytree(ROOT / runner.OUT, self.out)
        for path in (runner.MANIFEST, runner.SIGNATURE, runner.BASELINE, runner.ENTRY_REVIEW):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        self.events = read_events(self.out / 'execution/events.jsonl')

    def validate(self, full=False, closure=False):
        with patch.object(evidence, '_recorded_manifest', return_value=self.manifest), \
                patch.object(evidence, '_activation'), \
                patch.object(evidence, '_preserved_preparation'), \
                patch.object(evidence, '_git', side_effect=lambda root, checkpoint, path: (ROOT / path).read_bytes()):
            return (evidence.validate_closure if closure else evidence.validate_run)(self.root, full)

    def rewrite(self, events):
        path = self.out / 'execution/events.jsonl'
        path.unlink()
        for event in events:
            append(path, {key: value for key, value in event.items()
                          if key not in {'event_sha256', 'previous_sha256'}})
        values = read_events(path)
        atomic(self.out / 'execution/state.json', {
            'count': len(values), 'tail': values[-1]['event_sha256'], 'state': runner.derive(values)})

    def rebind(self, events, path):
        receipt = runner.receipt(self.root, path)
        for event in events:
            if event['kind'] == 'TERMINAL':
                event['raw_files'] = [receipt if row['path'] == receipt['path'] else row
                                      for row in event['raw_files']]
                if event.get('supervisor_receipt', {}).get('path') == receipt['path']:
                    event['supervisor_receipt'] = receipt

    def closure_files(self):
        summary = self.validate()
        state = runner.derive(self.events)
        base = self.root / evidence.BASE
        result = {key: summary[key] for key in (
            'item_id', 'run_id', 'outcome', 'sessions', 'active_seconds', 'attempts',
            'signature_elaborations', 'baseline_builds', 'successful_baselines',
            'proof_builds', 'successful_proof_builds', 'compilation_seconds',
            'remaining_attempts_unspent', 'scientific_status')}
        result.update(schema_version=1, manifest=runner.receipt(self.root, self.root / runner.MANIFEST),
                      checker_launches=0, dependency_compilations=0, research_network_requests=0,
                      recommendation={'action': 'Prepare a bounded parser successor',
                                      'target': 'Fixed A7 baseline transcript', 'priority': 1,
                                      'next_item': 'CVC-A7-REPAIR-1', 'prerequisites': ['Retain terminal run'],
                                      'evidence_refs': [runner.OUT + '/attempts/02/stdout']})
        original = 'results/research/conditional-validation-contracts/cvc-3/result.json'
        prepared = 'results/research/conditional-validation-contracts/cvc-conditional-1/result.json'
        for relative in (original, prepared):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        old, prep = evidence.load(self.root / original), evidence.load(self.root / prepared)
        result.update(input_checkpoint=evidence.load(self.root / runner.ENTRY_REVIEW)['implementation_checkpoint'],
                      activation_checkpoint=evidence.load(self.out / 'start.json')['checkpoint'],
                      prior_costs={
                          'original_proof_result': runner.receipt(self.root, self.root / original),
                          'conditional_preparation_result': runner.receipt(self.root, self.root / prepared),
                          'preparation_runner_proof_active_seconds': prep['combined_preparation_runner_proof_active_seconds'],
                          'compilation_seconds': old['aggregate_compilation_seconds'],
                          'prior_failed_fixture_actual_duration': None,
                          'prior_failed_fixture_cap_compliance': 'NOT_ESTABLISHED'},
                      aggregate_active_seconds=prep['combined_preparation_runner_proof_active_seconds'] + summary['active_seconds'],
                      aggregate_compilation_seconds=old['aggregate_compilation_seconds'] + summary['compilation_seconds'])
        atomic(base / 'result.json', result)
        review = self.root / evidence.REVIEW
        review.parent.mkdir(parents=True, exist_ok=True)
        atomic(review, {'schema_version': 1, 'stopped_item': runner.ITEM, 'outcome': evidence.OUTCOME,
                        'recommendation': result['recommendation'], 'after': {'selected_item': 'CVC-A7-REPAIR-1'},
                        'budget_carry_forward': {
                            'terminal_a7_attempts': 2, 'proposed_successor_attempts_max': 4,
                            'combined_a7_attempts_max': 6, 'original_cvc3_attempts': old['attempts'],
                            'all_proof_phase_builds_max': old['attempts'] + 6,
                            'a7_active_seconds_consumed': summary['active_seconds'],
                            'successor_active_seconds_max': 3600, 'counters_reused': False,
                            'a7_sessions_consumed': 1, 'successor_sessions_max': 1,
                            'combined_a7_sessions_max': 2,
                            'combined_a7_active_seconds_max': summary['active_seconds'] + 3600}})
        identity = {'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.RUN, 'outcome': evidence.OUTCOME}
        atomic(base / 'work-record.json', {**identity, 'status': 'COMPLETE', 'sessions': state['sessions'],
               'active_seconds': summary['active_seconds'], 'attempts_consumed': summary['attempts'],
               'compilation_seconds': summary['compilation_seconds'],
               'remaining_attempts_unspent': summary['remaining_attempts_unspent']})
        atomic(base / 'stop-diagnostic.json', {**identity, 'failed_attempt': 2,
               'baseline_audit_error': summary['baseline_audit_error'], 'control_stop': summary['control_stop'],
               'process_outcome': {'status': 'COMPLETE', 'returncode': 0,
                                   'cleanup_completed': True, 'deadline_exceeded': False},
               'runner_terminal_status': 'FAILED',
               **{stream: runner.receipt(self.root, self.out / 'attempts/02' / stream)
                  for stream in ('stdout', 'stderr')}})
        (base / 'report.md').write_text('Bounded baseline audit failure; no checked Lab result.\n')
        self.bind_closure()

    def bind_closure(self):
        base = self.root / evidence.BASE
        paths = {base / name for name in ('result.json', 'work-record.json', 'stop-diagnostic.json', 'report.md')}
        paths |= {self.out / name for name in ('start.json', 'execution/events.jsonl', 'execution/state.json')}
        paths.add(self.root / evidence.REVIEW)
        paths |= {self.root / row['path'] for event in self.events if event['kind'] == 'TERMINAL'
                  for row in event['raw_files']}
        atomic(base / 'evidence-manifest.json', {'schema_version': 1, 'item_id': runner.ITEM,
               'files': [runner.receipt(self.root, path) for path in sorted(paths)]})

    def test_actual_transcript_replays_failure_without_promoting_baseline(self):
        summary = self.validate()
        self.assertEqual(summary['outcome'], 'BOUNDED_UNRESOLVED')
        self.assertEqual(summary['baseline_audit_error'], 'malformed full axiom list')
        self.assertEqual((summary['attempts'], summary['successful_baselines'], summary['proof_builds']), (2, 0, 0))
        self.assertEqual(summary['compilation_seconds'], 2.71219816734083)
        self.assertFalse(summary['payloads_verified'])

    def test_raw_transcript_and_compiled_raw_receipts_are_required(self):
        for name in ('stdout', 'Baseline.olean'):
            path = self.out / 'attempts/02' / name
            original = path.read_bytes()
            path.write_bytes(original + b'changed')
            with self.assertRaises(ValueError):
                self.validate()
            path.write_bytes(original)
        self.validate()

    def test_snapshot_and_fixed_source_tampering_are_rejected(self):
        path = self.out / 'execution/state.json'
        original = path.read_bytes()
        value = json.loads(original)
        value['count'] -= 1
        atomic(path, value)
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            self.validate()
        path.write_bytes(original)
        (self.out / 'attempts/01/Contract.lean').write_text('changed')
        with self.assertRaises(ValueError):
            self.validate()

    def test_rehashed_ledger_cannot_forge_an_audit_downgrade(self):
        events = copy.deepcopy(self.events)
        events[-2]['error'] = 'invented mismatch'
        self.rewrite(events)
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            self.validate()

    def test_rehashed_receipts_cannot_change_process_success_to_failure(self):
        events = copy.deepcopy(self.events)
        path = self.out / 'attempts/02/supervisor.json'
        supervisor = evidence.load(path)
        supervisor['status'] = 'FAILED'
        atomic(path, supervisor)
        self.rebind(events, path)
        self.rewrite(events)
        with self.assertRaisesRegex(ValueError, 'compiler process'):
            self.validate()

    def test_rehashed_request_receipt_still_requires_internal_request_hash(self):
        events = copy.deepcopy(self.events)
        path = self.out / 'attempts/02/request.json'
        request = evidence.load(path)
        request['seconds'] = 301
        atomic(path, request)
        self.rebind(events, path)
        self.rewrite(events)
        with self.assertRaisesRegex(ValueError, 'request hash'):
            self.validate()

    def test_portable_mode_works_without_ignored_signature_payload(self):
        self.validate()
        with self.assertRaises(ValueError):
            self.validate(full=True)

    def test_closure_binds_accounting_and_diagnostic_independently_of_manifest(self):
        self.closure_files()
        self.assertGreater(self.validate(closure=True)['evidence_files'], 15)
        path = self.root / evidence.BASE / 'result.json'
        result = evidence.load(path)
        result['compilation_seconds'] = 0
        atomic(path, result)
        self.bind_closure()
        with self.assertRaisesRegex(ValueError, 'result differs'):
            self.validate(closure=True)
        self.closure_files()
        path = self.root / evidence.BASE / 'stop-diagnostic.json'
        diagnostic = evidence.load(path)
        diagnostic['baseline_audit_error'] = 'invented'
        atomic(path, diagnostic)
        self.bind_closure()
        with self.assertRaisesRegex(ValueError, 'stop diagnostic'):
            self.validate(closure=True)

    def test_closure_rejects_aggregate_cost_and_successor_budget_resets(self):
        self.closure_files()
        path = self.root / evidence.BASE / 'result.json'
        result = evidence.load(path)
        result['aggregate_active_seconds'] = result['active_seconds']
        atomic(path, result)
        self.bind_closure()
        with self.assertRaisesRegex(ValueError, 'aggregate costs'):
            self.validate(closure=True)
        self.closure_files()
        path = self.root / evidence.REVIEW
        review = evidence.load(path)
        review['budget_carry_forward']['proposed_successor_attempts_max'] = 6
        atomic(path, review)
        self.bind_closure()
        with self.assertRaisesRegex(ValueError, 'carry-forward'):
            self.validate(closure=True)

    def test_predecessor_bound_bytes_are_preserved_without_unstarted_gate(self):
        artifact = self.root / 'prior-evidence.json'
        artifact.write_text('preserved')
        manifest = self.root / evidence.PREP_EVIDENCE
        manifest.parent.mkdir(parents=True, exist_ok=True)
        atomic(manifest, {'schema_version': 1, 'item_id': 'CVC-CONDITIONAL-1', 'outcome': 'SUCCESS',
                          'files': [runner.receipt(self.root, artifact)]})
        bound_manifest = manifest.read_bytes()
        with patch.object(evidence, '_git', return_value=bound_manifest):
            evidence._preserved_preparation(self.root, {'checkpoint': 'a' * 40})
            artifact.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'binding changed'):
                evidence._preserved_preparation(self.root, {'checkpoint': 'a' * 40})


if __name__ == '__main__':
    unittest.main()
