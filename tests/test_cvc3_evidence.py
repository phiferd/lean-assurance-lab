"""Pure CVC-3 closure-evidence tests; they never invoke the compiler."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc3_evidence as evidence
from lib import cvc_runner2 as runner
from lib.cvc_runner_audit import COMPARATORS
from lib.cvc_process import atomic


def stamp(seconds):
    return {'at': (datetime(2026, 9, 7, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
            'monotonic': 1000. + seconds}


def receipt(root, path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(root)), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def proof():
    return 'import Contract\n\n' + '\n\n'.join(
        f'theorem {name} : {typ} := by\n  exact placeholder' for name, typ in runner.TARGETS) + '\n'


def output():
    names = [name for name, _ in runner.TARGETS] + COMPARATORS
    return '\n'.join(f"'{name}' does not depend on any axioms" for name in names) + '\n'


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.out = self.root / runner.OUT
        self.out.mkdir(parents=True)
        (self.root / runner.MANIFEST).parent.mkdir(parents=True, exist_ok=True)
        (self.root / runner.MANIFEST).write_text('{}')
        assumptions = self.root / runner.ASSUMPTIONS
        assumptions.parent.mkdir(parents=True, exist_ok=True)
        assumptions.write_text(json.dumps({'conditional_axiom_policy': {
            'standard_allowed': [], 'source_helpers_allowed': []}}))
        self.manifest = {'compiler': 'fixture-compiler', 'environment': {'LANG': 'C', 'LEAN_PATH': '/fixture'},
                         'commands': [['fixture-compiler', '-o', '/fixture/Contract.olean', 'Contract.lean'],
                                      ['fixture-compiler', '-o', '/fixture/CVC2Proof.olean', 'CVC2Proof.lean']]}
        identity = {'run_id': runner.RUN, 'manifest_sha256': runner.sha(self.root / runner.MANIFEST),
                    'checkpoint': 'a' * 40, 'time': stamp(0)}
        atomic(self.out / 'start.json', identity)
        self.ledger = runner.Ledger(self.out / 'execution')
        self.ledger.initialize(identity)
        self.ledger.add({'kind': 'SESSION_START', 'number': 1, 'time': stamp(1)})
        self._add_attempt(1, 'Contract.lean', 'signature', None)
        self._add_attempt(2, 'CVC2Proof.lean', 'proof', 'SUCCESS')
        self.ledger.add({'kind': 'SESSION_END', 'number': 1, 'time': stamp(10), 'charged_seconds': 9.})

    def _add_attempt(self, number, name, phase, result):
        directory = self.out / 'attempts' / f'{number:02d}'
        directory.mkdir(parents=True)
        source = b'import Contract\n' if number == 1 else proof().encode()
        payload = source if number == 1 else runner.generate(source.decode())
        (directory / 'implementation.lean').write_bytes(source)
        (directory / name).write_bytes(payload)
        (directory / 'stdout').write_text('' if number == 1 else output())
        (directory / 'stderr').write_text('')
        reserved = {'kind': 'RESERVED', 'number': number, 'phase': phase, 'mode': 'proof', 'session': 1,
                    'time': stamp(number + 1), 'reserved_seconds': 300.,
                    'argv': self.manifest['commands'][number - 1],
                    'cwd': self.manifest['environment']['LEAN_PATH'].split(':')[0], 'env': self.manifest['environment'],
                    'manifest_sha256': runner.sha(self.root / runner.MANIFEST),
                    'source_sha256': hashlib.sha256(source).hexdigest(),
                    'input_sha256': hashlib.sha256(payload).hexdigest()}
        self.ledger.add(reserved)
        request = {'argv': reserved['argv'], 'cwd': reserved['cwd'], 'env': reserved['env'],
                   'seconds': 300., 'monotonic_started': stamp(number + 1)['monotonic'],
                   'started_at': stamp(number + 1)['at'], 'deadline_monotonic': stamp(number + 1)['monotonic'] + 300.}
        request['request_sha256'] = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        atomic(directory / 'request.json', request)
        supervisor = {'status': 'COMPLETE', 'returncode': 0, 'charged_seconds': 1., 'cleanup_completed': True,
                      'deadline_exceeded': False, 'request_sha256': request['request_sha256'],
                      'stdout_sha256': runner.sha(directory / 'stdout'), 'stderr_sha256': runner.sha(directory / 'stderr')}
        atomic(directory / 'supervisor.json', supervisor)
        raw = [receipt(self.root, directory / value) for value in
               ('implementation.lean', name, 'stdout', 'stderr', 'request.json', 'supervisor.json')]
        terminal = {'kind': 'TERMINAL', 'number': number, 'status': 'COMPLETE', 'returncode': 0,
                    'charged_seconds': 1., 'cleanup_completed': True, 'deadline_exceeded': False,
                    'time': stamp(number + 2), 'outputs': [{'path': 'absent.olean'}], 'raw_files': raw,
                    'supervisor_receipt': receipt(self.root, directory / 'supervisor.json')}
        if result:
            terminal.update(result=result, axiom_audit=runner.audit(output(), '',
                            {'conditional_axiom_policy': {'standard_allowed': [], 'source_helpers_allowed': []}}))
        self.ledger.add(terminal)

    def validate(self, payloads=False):
        with patch.object(evidence, '_recorded_manifest', return_value=self.manifest):
            return evidence.validate_run(self.root, require_payloads=payloads)

    def write_closure(self):
        summary = self.validate()
        base = self.root / 'results/research/conditional-validation-contracts/cvc-3'
        stdout = self.out / 'attempts/02/stdout'
        reports = evidence.reported_axioms(stdout.read_text())
        result = {'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.RUN, 'outcome': summary['outcome'],
                  'sessions': summary['sessions'], 'active_seconds': summary['active_seconds'], 'attempts': summary['attempts'],
                  'compilation_seconds': summary['process_seconds'], 'manifest': {'sha256': summary['manifest_sha256']},
                  'signature_elaborations': 1, 'proof_builds': 1, 'successful_proof_builds': 1,
                  'remaining_attempts_unspent': 10, 'unlisted_axioms': []}
        prior_path = self.root / 'results/research/conditional-validation-contracts/cvc-runner-2/result.json'
        prior_path.parent.mkdir(parents=True, exist_ok=True)
        atomic(prior_path, {'aggregate_preparation_and_runner_active_seconds': 5.,
                            'prior_costs_unchanged': {'preparation_compilation_seconds': 3.}})
        result['prior_costs'] = {'result': receipt(self.root, prior_path),
                                 'preparation_and_runner_active_seconds': 5., 'preparation_compilation_seconds': 3.}
        result['aggregate_active_seconds'] = 5. + summary['active_seconds']
        result['aggregate_compilation_seconds'] = 3. + summary['process_seconds']
        work = {'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.RUN, 'outcome': summary['outcome'],
                'status': 'COMPLETE', 'sessions': self.ledger.read()[1]['sessions'], 'active_seconds': summary['active_seconds'],
                'attempts_consumed': summary['attempts'], 'remaining_attempts_unspent': 10,
                'compilation_seconds': summary['process_seconds']}
        diagnostic = {'schema_version': 1, 'item_id': runner.ITEM, 'outcome': summary['outcome'],
                      'stdout': receipt(self.root, stdout),
                      'mandatory_comparator_reports': {name: reports[name] for name in COMPARATORS},
                      'unlisted_axioms': []}
        source = self.root / 'source.lean'; source.write_text('source')
        diagnostic['source_binding'] = receipt(self.root, source)
        closure = self.root / runner.CLOSURE
        closure.parent.mkdir(parents=True, exist_ok=True)
        atomic(closure, {'closure': {'modules': [{'module': 'Lean4Lean.Verify.Axioms',
                                                  'source': {'sha256': diagnostic['source_binding']['sha256'],
                                                             'bytes': diagnostic['source_binding']['bytes']}}]}})
        for name, value in [('result.json', result), ('work-record.json', work), ('stop-diagnostic.json', diagnostic)]:
            atomic(base / name, value)
        files = [receipt(self.root, base / name) for name in ('result.json', 'work-record.json', 'stop-diagnostic.json')]
        files += [receipt(self.root, self.out / name) for name in ('start.json', 'execution/events.jsonl', 'execution/state.json')]
        for row in self.ledger.read()[1]['attempts']:
            files += row['terminal']['raw_files']
        atomic(base / 'evidence-manifest.json', {'schema_version': 1, 'item_id': runner.ITEM, 'files': files})

    def closure(self):
        with patch.object(evidence, '_recorded_manifest', return_value=self.manifest):
            return evidence.validate_closure(self.root)

    def test_summary_uses_closed_ledger_and_audited_final_proof(self):
        summary = self.validate()
        self.assertEqual(summary['outcome'], 'SUCCESS')
        self.assertEqual(summary['attempts'], 2)
        self.assertEqual(len(summary['final_declarations']), 4)
        self.assertEqual(len(summary['final_axioms']), 6)
        self.assertFalse(summary['payloads_verified'])

    def test_tampered_raw_source_and_snapshot_are_rejected(self):
        path = self.out / 'attempts/02/CVC2Proof.lean'
        original = path.read_bytes()
        path.write_text('changed')
        with self.assertRaises(ValueError): self.validate()
        path.write_bytes(original)
        state = self.out / 'execution/state.json'
        value = json.loads(state.read_text()); value['count'] = 1; state.write_text(json.dumps(value))
        with self.assertRaises(ValueError): self.validate()

    def test_full_payload_mode_requires_compiler_output_receipt(self):
        self.validate()
        with self.assertRaises(ValueError): self.validate(payloads=True)

    def test_individual_session_cap_is_not_hidden_by_total_budget(self):
        events = runner.read_events(self.ledger.path)
        events[-1].update(time=stamp(5402), charged_seconds=5401.)
        from lib.cvc_prep import append
        self.ledger.path.unlink()
        for event in events:
            append(self.ledger.path, {k: v for k, v in event.items()
                                     if k not in {'event_sha256', 'previous_sha256'}})
        events = runner.read_events(self.ledger.path)
        self.ledger._snapshot(events)
        with self.assertRaisesRegex(ValueError, 'individual session cap'):
            self.validate()

    def test_failed_comparator_reports_preserve_exact_unlisted_axioms(self):
        stdout = "\n".join(
            f"'{name}' depends on axioms: [propext, Lean.Level.instLawfulBEqLevel, Lean.Level.isExplicitSubsumedAux_eq]"
            for name in COMPARATORS) + "\n"
        assumptions = {'conditional_axiom_policy': {'standard_allowed': ['propext'], 'source_helpers_allowed': []}}
        self.assertEqual(evidence.unlisted_comparator_axioms(stdout, assumptions), {
            "Lean.Level.isEquiv'_wf": ['Lean.Level.instLawfulBEqLevel', 'Lean.Level.isExplicitSubsumedAux_eq'],
            "Lean.Level.isEquiv'_complete": ['Lean.Level.instLawfulBEqLevel', 'Lean.Level.isExplicitSubsumedAux_eq'],
        })

    def test_closure_rejects_result_accounting_and_axiom_tampering(self):
        self.write_closure()
        self.assertGreater(self.closure()['evidence_files'], 3)
        result_path = self.root / 'results/research/conditional-validation-contracts/cvc-3/result.json'
        result = json.loads(result_path.read_text()); result['attempts'] = 3; atomic(result_path, result)
        with self.assertRaises(ValueError): self.closure()
        self.write_closure()
        result = json.loads(result_path.read_text()); result['unlisted_axioms'] = ['invented']; atomic(result_path, result)
        with self.assertRaises(ValueError): self.closure()


if __name__ == '__main__':
    unittest.main()
