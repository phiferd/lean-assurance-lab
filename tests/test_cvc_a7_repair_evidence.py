"""Pure tamper regressions for repair evidence; no compiler/process launches."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lib import cvc_a7_repair_audit as audit
from lib import cvc_a7_repair_evidence as evidence
from lib import cvc_a7_repair_runner as runner

ROOT = Path(__file__).resolve().parents[1]
OLD_ATTEMPT = ROOT / 'results/research/conditional-validation-contracts/cvc-3-conditional/run-0001/attempts/02'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class ProcessEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'attempt'
        self.directory.mkdir()
        for name in ('request.json', 'supervisor.json', 'process.json', 'stdout', 'stderr'):
            shutil.copyfile(OLD_ATTEMPT / name, self.directory / name)
        request = evidence.load(self.directory / 'request.json')
        self.supervisor = evidence.load(self.directory / 'supervisor.json')
        self.reserved = {key: request[key] for key in ('argv', 'cwd', 'env')}
        self.reserved.update(reserved_seconds=request['seconds'], time={'monotonic': request['deadline_monotonic'] - request['seconds']})
        self.terminal = {**self.supervisor, 'time': {'monotonic': self.supervisor['monotonic_ended'] + 1}}
        self.rebind()

    def rebind(self):
        self.receipts = {str(path.relative_to(self.root)): runner.receipt(self.root, path)
                         for path in self.directory.iterdir()}
        self.terminal['supervisor_receipt'] = self.receipts['attempt/supervisor.json']

    def validate(self):
        return evidence._process(self.root, self.directory, self.reserved, self.terminal, self.receipts)

    def test_retained_successful_supervisor_receipt_validates(self):
        self.assertEqual(self.validate()['status'], 'COMPLETE')

    def test_rehashed_receipt_does_not_replace_internal_request_hash(self):
        request = evidence.load(self.directory / 'request.json')
        request['seconds'] = 301
        write(self.directory / 'request.json', request)
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'request hash'):
            self.validate()

    def test_request_cannot_change_invocation_even_after_rehashing(self):
        request = evidence.load(self.directory / 'request.json')
        request.pop('request_sha256')
        request['argv'] = ['other-compiler']
        request['request_sha256'] = evidence._digest(json.dumps(request, sort_keys=True).encode())
        write(self.directory / 'request.json', request)
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'request differs'):
            self.validate()

    def test_cleanup_and_deadline_tampering_fail_after_rebinding(self):
        original = copy.deepcopy(self.supervisor)
        for field, value in (('cleanup_completed', False), ('deadline_exceeded', True)):
            mutated = {**original, field: value}
            write(self.directory / 'supervisor.json', mutated)
            self.terminal.update(mutated)
            self.rebind()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate()

    def test_terminal_cost_and_raw_stream_cannot_be_rewritten(self):
        self.terminal['charged_seconds'] = 0
        with self.assertRaisesRegex(ValueError, 'terminal differs'):
            self.validate()
        self.terminal['charged_seconds'] = self.supervisor['charged_seconds']
        (self.directory / 'stdout').write_text('altered')
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'stream digest'):
            self.validate()

    def test_forged_process_identity_is_rejected(self):
        process = evidence.load(self.directory / 'process.json')
        process['request_sha256'] = 'a' * 64
        write(self.directory / 'process.json', process)
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'process identity'):
            self.validate()


class AuditReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'attempt'
        self.directory.mkdir()
        for relative in (runner.SIGNATURE, runner.EXPECTATIONS, runner.ASSUMPTIONS):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def baseline(self):
        source = audit.baseline_source(evidence.load(self.root / runner.EXPECTATIONS))
        for name in ('implementation.lean', 'Baseline.lean'):
            (self.directory / name).write_bytes(source)
        raw = (OLD_ATTEMPT / 'stdout').read_bytes()
        self.assertEqual(evidence._digest(raw[:1862]), 'f5da4d60a8f5fab22d9efa101e41ee4669c629a8a66846caf690aed6b5b034fc')
        stdout = raw[1862:].decode()  # Fixture only; production never cleans evidence.
        (self.directory / 'stdout').write_text(stdout)
        (self.directory / 'stderr').write_text('')
        self.reservation = {'phase': 'baseline', 'mode': 'proof', 'source_sha256': evidence._digest(source),
                            'input_sha256': evidence._digest(source)}
        self.terminal = {'status': 'COMPLETE', 'baseline_audit': audit.audit_baseline(stdout, '')}

    def replay(self, module=audit, supervisor='COMPLETE'):
        evidence._replay(self.root, module, self.reservation, self.terminal, {'status': supervisor}, self.directory)

    def test_baseline_replays_against_exact_original_audit_module(self):
        self.baseline()
        self.replay()
        self.terminal['baseline_audit']['assumptions'] = []
        with self.assertRaisesRegex(ValueError, 'bound replay'):
            self.replay()

    def test_bound_generator_and_immutable_expectations_are_required(self):
        self.baseline()
        changed = (self.directory / 'Baseline.lean').read_bytes() + b'-- changed\n'
        for name in ('implementation.lean', 'Baseline.lean'):
            (self.directory / name).write_bytes(changed)
        self.reservation.update(source_sha256=evidence._digest(changed), input_sha256=evidence._digest(changed))
        with self.assertRaisesRegex(ValueError, 'bound generator'):
            self.replay()

    def test_format_failure_is_a_repair_pause_not_scientific_mismatch(self):
        self.baseline()
        (self.directory / 'stdout').write_text((OLD_ATTEMPT / 'stdout').read_text())
        self.terminal = {'status': 'FAILED', 'error': 'source-positioned compiler diagnostic',
                         'repair_pause': 'source-positioned compiler diagnostic'}
        self.replay()
        self.terminal['scientific_mismatch'] = True
        with self.assertRaisesRegex(ValueError, 'classification'):
            self.replay()

    def test_failed_compilation_cannot_supply_successful_audit(self):
        self.baseline()
        with self.assertRaisesRegex(ValueError, 'failed compiler promoted'):
            self.replay(supervisor='FAILED')


class BindingAndClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'evidence.json'
        self.path.write_text('retained stop evidence')
        self.receipt = runner.receipt(self.root, self.path)

    def test_portability_only_omits_absent_ignored_compiler_products(self):
        product = {'path': 'external/Contract.olean', 'bytes': 2, 'sha256': 'a' * 64}
        with patch.object(evidence, '_ignored', return_value=True):
            evidence._receipt(self.root, product, full=False)
            for path in ('external/stdout', 'external/Contract.lean', 'external/request.json'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    evidence._receipt(self.root, {**product, 'path': path}, full=False)
        with patch.object(evidence, '_ignored', return_value=False), self.assertRaises(ValueError):
            evidence._receipt(self.root, product, full=False)

    def test_present_ignored_product_must_still_match_receipt(self):
        path = self.root / 'external/Contract.olean'
        path.parent.mkdir()
        path.write_bytes(b'original')
        receipt = runner.receipt(self.root, path)
        path.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            evidence._receipt(self.root, receipt, full=False)

    def stop(self, kind, outcome='BOUNDED_UNRESOLVED'):
        return {'outcome': outcome, 'stop': {'kind': kind, 'reason': 'specific retained boundary',
                'evidence': [self.receipt], 'attempted_repairs': [], 'remaining_options_blocked': []}}

    def test_engineering_pause_cannot_claim_unspent_build_or_time_cap(self):
        summary = {'run_outcome': None, 'attempts': 2, 'active_seconds': 50}
        for kind in ('build_cap', 'active_time_cap', 'scientific_mismatch', 'unrepairable_gap'):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                evidence._closure_stop(self.root, self.stop(kind), summary, {'attempts': []})

    def test_true_cap_and_documented_unrepairable_boundary_are_distinct(self):
        summary = {'run_outcome': None, 'attempts': 4, 'active_seconds': 50}
        evidence._closure_stop(self.root, self.stop('build_cap'), summary, {'attempts': []})
        result = self.stop('unrepairable_gap')
        result['stop'].update(attempted_repairs=['Named local parser repair attempted'],
                              remaining_options_blocked=['Necessary immutable input lacks required theorem'],
                              no_feasible_authorized_repair=True)
        evidence._closure_stop(self.root, result, summary, {'attempts': []})

    def test_success_requires_checked_run_and_no_unreconciled_process_stop(self):
        summary = {'run_outcome': 'SUCCESS', 'control_stop': None}
        result = self.stop('completed_proof', 'SUCCESS')
        evidence._closure_stop(self.root, result, summary, {'attempts': []})
        for changed in ({**summary, 'run_outcome': None}, {**summary, 'control_stop': 'cleanup unknown'}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                evidence._closure_stop(self.root, result, changed, {'attempts': []})

    def test_rehashed_tooling_archive_cannot_replace_git_checkpoint(self):
        relative = 'lib/cvc_a7_repair_audit.py'
        directory = runner.OUT + '/tooling/01'
        path = self.root / directory / 'files' / relative
        path.parent.mkdir(parents=True)
        path.write_bytes(b'changed tooling')
        row = {'path': relative, 'sha256': evidence._digest(path.read_bytes()), 'archive': runner.receipt(self.root, path)}
        revision = {'number': 1, 'inputs': [row], 'checkpoint': 'a' * 40}
        manifest = {'controller_inputs': [{'path': relative, 'sha256': row['sha256']}]}
        with patch.object(runner, 'verify_revision'), patch.object(evidence, '_git', return_value=b'original tooling'):
            with self.assertRaisesRegex(ValueError, 'Git checkpoint'):
                evidence._revision(self.root, manifest, revision)

    def test_scientific_success_requires_all_four_per_result_reports(self):
        result = {'model_id': 'CVC-U1-A7', 'assumptions': list(audit.A7), 'conditional': True,
                  'transitive_axioms': {n: [] for n, _ in runner.TARGETS}}
        result['transitive_axioms'].update({n: list(audit.A7) for n in audit.COMPARATORS})
        evidence._result_envelope(result, runner.TARGETS)
        del result['transitive_axioms']['Lab.CVC2.required_acceptance']
        with self.assertRaisesRegex(ValueError, 'inventory'):
            evidence._result_envelope(result, runner.TARGETS)

    def test_tooling_revision_cannot_broaden_fixed_a7_envelope(self):
        result = {'model_id': 'CVC-U1-A7', 'assumptions': list(audit.A7), 'conditional': True,
                  'transitive_axioms': {n: [] for n, _ in runner.TARGETS}}
        result['transitive_axioms'].update({n: list(audit.A7) for n in audit.COMPARATORS})
        result['transitive_axioms']['Lab.CVC2.preservation'] = ['Other.assumption']
        with self.assertRaisesRegex(ValueError, 'envelope'):
            evidence._result_envelope(result, runner.TARGETS)

    def test_initial_accounting_must_match_committed_activation_work(self):
        rows = [{'id': item, 'status': 'COMPLETE', 'closure': {'outcome': 'SUCCESS'}}
                for item in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2', 'CVC-AXIOMS-1', 'CVC-CONDITIONAL-1')]
        rows += [{'id': runner.ITEM, 'status': 'ACTIVE'}, {'id': 'CVC-3-CONDITIONAL', 'status': 'COMPLETE',
                                                          'closure': {'outcome': 'BOUNDED_UNRESOLVED'}}]
        queue = {'frontier_id': 'F-CONDITIONAL-VALIDATION-CONTRACTS', 'selected_item': runner.ITEM, 'items': rows}
        work = {'item_id': runner.ITEM, 'run_id': runner.RUN, 'policy': runner.POLICY, 'status': 'ACTIVE',
                'intervals': [{'number': 1, 'start': {'at': '2026-09-07T12:00:00+00:00', 'monotonic': 100}}]}
        start = {'checkpoint': 'a' * 40, 'work': {'intervals': copy.deepcopy(work['intervals'])}}
        def git(root, checkpoint, path):
            return json.dumps(work if path == runner.WORK else queue).encode()
        with patch.object(evidence, '_git', side_effect=git):
            evidence._activation(self.root, start)
            start['work']['intervals'][0]['start']['monotonic'] = 101
            with self.assertRaisesRegex(ValueError, 'committed activation accounting'):
                evidence._activation(self.root, start)

    def test_success_cannot_hide_an_exceeded_interval_or_cumulative_cap(self):
        work = {'intervals': [{'number': 1, 'start': {'at': '2026-09-07T12:00:00+00:00', 'monotonic': 100},
                              'end': {'at': '2026-09-07T12:00:10+00:00', 'monotonic': 110}, 'charged_seconds': 10}]}
        summary = {'attempts': 3, 'combined_a7_attempts': 5, 'combined_a7_active_seconds': 65.59774324996397}
        evidence._success_limits(work, summary)
        with self.assertRaisesRegex(ValueError, 'cumulative A7'):
            evidence._success_limits(work, {**summary, 'combined_a7_attempts': 7})
        over = copy.deepcopy(work)
        over['intervals'][0].update(end={'at': '2026-09-07T13:00:01+00:00', 'monotonic': 3701}, charged_seconds=3601)
        with self.assertRaisesRegex(ValueError, 'interval cap'):
            evidence._success_limits(over, summary)


class ActualClosureMetadataTests(unittest.TestCase):
    """Mutate real closure metadata; run evidence is separately replayed above."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.result_path = self.root / evidence.BASE / 'result.json'
        self.result = evidence.load(ROOT / evidence.BASE / 'result.json')
        self.summary = {**self.result['summary'], 'payloads_verified': False}
        paths = {evidence.BASE + '/result.json', runner.WORK, runner.MANIFEST, evidence.PREDECESSOR,
                 evidence.BASE + '/execution-protocol.json', runner.OUT + '/execution/events.jsonl'}
        paths.update(receipt['path'] for receipt in self.result['stop']['evidence'])
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def validate(self):
        with patch.object(evidence, 'validate_run', return_value=self.summary):
            return evidence.validate_closure(self.root)

    def test_actual_closure_metadata_matches_audited_run(self):
        self.assertTrue(self.validate()['closure_verified'])
        self.assertEqual(self.validate()['outcome'], 'SUCCESS')

    def test_result_cannot_reset_actual_work_or_omit_checked_declarations(self):
        for field, value in (('summary', {**self.result['summary'], 'active_seconds': 0}),
                             ('result_declarations', self.result['result_declarations'][:-1]),
                             ('transitive_axioms', {})):
            write(self.result_path, {**self.result, field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate()

    def test_rebinding_work_receipt_does_not_authorize_a_build_count_reset(self):
        path = self.root / runner.WORK
        work = evidence.load(path)
        work['research_operations']['proof_builds'] = 0
        write(path, work)
        write(self.result_path, {**self.result, 'work_record': runner.receipt(self.root, path)})
        with self.assertRaisesRegex(ValueError, 'operation counts'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
