"""Adversarial offline closure replay; no scientific process is invoked."""
from contextlib import ExitStack
import copy
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = SourceFileLoader('string_reconstruction_closure', str(ROOT / 'scripts/validate-nanoda-string-reconstruction-closure'))
spec = importlib.util.spec_from_loader(loader.name, loader)
v = importlib.util.module_from_spec(spec)
loader.exec_module(v)


class ClosureReplay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = self.root / v.REL
        self.base.mkdir(parents=True)
        self.freeze = 'a' * 40
        self.entry = v.ENTRY
        self.frozen = {}
        self.start = datetime(2026, 9, 13, tzinfo=timezone.utc).timestamp()
        self.work = {'item_id': v.ITEM, 'status': 'ACTIVE', 'started_at': self.stamp(0),
                     'start_monotonic': 1000., 'budget': {'active_seconds': 5400}, 'base_commit': 'b' * 40}
        self.write('work-record.json', self.work, self.entry)
        self.write('entry-lock.json', {'base_commit': self.work['base_commit'],
            'bindings': [{'path': 'CONSTITUTION.md', 'sha256': v.sha(b'constitution')}]}, self.entry)
        self.frozen[(self.work['base_commit'], 'CONSTITUTION.md')] = b'constitution'
        self.closure = {'item_id': v.ITEM, 'outcome': 'SUCCESS', 'status': 'COMPLETE', 'started_at': self.stamp(0),
                        'start_monotonic': 1000., 'completed_at': self.stamp(100),
                        'end_monotonic': 1100., 'active_seconds': 100.}
        self.write('work-closure.json', self.closure)
        self.science = copy.deepcopy(v.SCIENTIFIC)
        self.write('scientific-inputs.json', self.science, self.freeze)
        design = v.SCIENTIFIC['design_binding']
        raw_design = (ROOT / design['path']).read_bytes()
        self.put(design['path'], raw_design)
        self.frozen[(self.freeze, design['path'])] = raw_design
        matrix = v.SCIENTIFIC['matrix_binding']
        raw_matrix = (ROOT / matrix['path']).read_bytes()
        self.put(matrix['path'], raw_matrix)
        self.frozen[(self.freeze, matrix['path'])] = raw_matrix
        bundle = 'results/research/hsbm-pilot-1/nanoda-history.bundle'
        self.put(bundle, b'retained source archive')
        self.frozen[(self.freeze, bundle)] = b'retained source archive'
        self.write('source-lock.json', {'tip': v.SOURCE, 'tree': 'e8816d9dc69c669d99181a8fece5aaeed9a6c13d',
                                      'history_bundle': bundle, 'history_bundle_sha256': v.sha(b'retained source archive')}, self.freeze)
        self.patch = b'diff --git a/src/tests.rs b/src/tests.rs\n@@ -1 +1 @@\n-mod old;\n+mod string_reconstruction;\ndiff --git a/src/tests/string_reconstruction.rs b/src/tests/string_reconstruction.rs\nnew file mode 100644\n'
        self.write_raw('patches/string-reconstruction.patch', self.patch, self.freeze)
        for name in ('run-cell.py', 'dependency-lock.json'):
            self.write(name, {}, self.freeze)
        self.put('lib/cvc_process.py', b'trusted frozen tooling')
        self.frozen[(self.freeze, 'lib/cvc_process.py')] = b'trusted frozen tooling'
        self.write('requests.json', {'item_id': v.ITEM, 'cap': 8, 'requests': [{'id': 1, 'charged_requests': 3}], 'charged_read_only_requests': 3})
        self.account = {'builds': 2, 'test_processes': 2, 'pending': None, 'reservations': []}
        for n, kind in enumerate(('focused', 'full'), 1):
            self.make_attempt(n, kind)
        self.write('execution/accounting.json', self.account)
        draft = 'results/action-recommendations/drafts/string-reconstruction-pr.md'
        self.put(draft, b'Unsubmitted preventive test draft.')
        self.put('results/research/external-contributions.json', json.dumps({'contributions': [{'submission_material': draft}]}).encode())
        self.result = {'item_id': v.ITEM, 'outcome': 'SUCCESS', 'entry_commit': self.entry, 'freeze_commit': self.freeze,
                       'execution_commits': {r['cell_id']: self.freeze for r in self.account['reservations']},
                       'research_counts': {'source_setup_requests': 3, 'builds': 2, 'test_processes': 2,
                                           'proofs': 0, 'mutants': 0, 'new_exports': 0, 'external_research_writes': 0},
                       'next_item': {'id': 'NEXT-ITEM', 'status': 'READY', 'started': False},
                       'recommendation': {'draft': draft}, 'output_bindings': []}
        self.closure.update(research_counts=self.result['research_counts'], next_item='NEXT-ITEM', next_item_started=False)
        self.write('work-closure.json', self.closure)
        self.write('closure-queue.json', {'selected_item': 'NEXT-ITEM', 'items': [
            {'id': v.ITEM, 'status': 'COMPLETE', 'closure': {'outcome': 'SUCCESS'}},
            {'id': 'NEXT-ITEM', 'status': 'READY'}]})
        self.write('closure-external-contributions.json', {'contributions': [{'submission_material': draft,
            'research_items': [v.ITEM], 'lifecycle': 'LOCAL_DRAFT', 'upstream': None}]})
        self.rebind_outputs()
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(v, 'ROOT', self.root))
        stack.enter_context(patch.object(v, 'git_bytes', side_effect=lambda c, p: self.frozen[(c, p)]))
        stack.enter_context(patch.object(v, 'commit_time', return_value=self.start))
        self.spawn = stack.enter_context(patch.object(v.subprocess, 'check_output', side_effect=AssertionError('unexpected subprocess')))

    def stamp(self, seconds):
        return datetime.fromtimestamp(self.start + seconds, timezone.utc).isoformat()

    def put(self, path, raw):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)

    def write_raw(self, name, raw, commit=None):
        path = v.REL + '/' + name
        self.put(path, raw)
        if commit:
            self.frozen[(commit, path)] = raw

    def write(self, name, obj, commit=None):
        self.write_raw(name, json.dumps(obj).encode(), commit)

    def load(self, name):
        return json.loads((self.base / name).read_bytes())

    def make_attempt(self, n, kind):
        cell = f'{n:03d}-{kind}'
        bindings = []
        for (commit, path), raw in list(self.frozen.items()):
            if commit == self.freeze and '/execution/' not in path:
                bindings.append({'path': path, 'sha256': v.sha(raw), 'bytes': len(raw)})
        # Historical runtime bytes need not be installed on this replay machine.
        bindings.append({'path': '/absent/historical/cargo', 'sha256': 'a' * 64, 'bytes': 20})
        bindings.extend(dict(value, path='/absent/source/' + name) for name, value in v.FIXTURES.items())
        manifest = {'item_id': v.ITEM, 'cell_id': cell, 'source_revision': v.SOURCE,
                    'patch_sha256': v.sha(self.patch), 'bindings': bindings, 'cwd': '/absent/source',
                    'argv': ['/absent/historical/cargo', 'test', '--offline', '--locked'] +
                            (['string_reconstruction'] if kind == 'focused' else []) + ['--', '--nocapture'],
                    'environment': {'CARGO_NET_OFFLINE': 'true'}, 'timeout_seconds': 120,
                    'expected': {'library_tests_passed': 2 if kind == 'focused' else 40,
                                 'library_tests_failed': 0, 'named_tests': v.NAMES}}
        self.write('execution/' + cell + '-manifest.json', manifest, self.freeze)
        begin = n * 20.
        request = {'argv': manifest['argv'], 'cwd': manifest['cwd'], 'env': manifest['environment'], 'seconds': 120,
                   'monotonic_started': 1000. + begin, 'started_at': self.stamp(begin), 'deadline_monotonic': 1120. + begin}
        request['request_sha256'] = v.sha(json.dumps(request, sort_keys=True).encode())
        stdout = ('\n'.join('test ' + name + ' ... ok' for name in v.NAMES) +
                  '\ntest result: ok. ' + str(manifest['expected']['library_tests_passed']) + ' passed; 0 failed; 0 ignored;\n').encode()
        if kind == 'full':
            stdout += b'test result: ok. 0 passed; 0 failed; 0 ignored;\ntest result: ok. 0 passed; 0 failed; 8 ignored;\n'
        receipt = {'status': 'COMPLETE', 'returncode': 0, 'charged_seconds': 1.,
                   'started_at': request['started_at'], 'ended_at': self.stamp(begin + 1),
                   'monotonic_started': 1000. + begin, 'monotonic_ended': 1001. + begin,
                   'request_sha256': request['request_sha256'], 'stdout_sha256': v.sha(stdout),
                   'stderr_sha256': v.sha(b''), 'cleanup_completed': True, 'deadline_exceeded': False}
        prefix = 'execution/' + cell + '/'
        self.write(prefix + 'request.json', request)
        self.write(prefix + 'supervisor.json', receipt)
        self.write_raw(prefix + 'stdout', stdout)
        self.write_raw(prefix + 'stderr', b'')
        self.account['reservations'].append({'cell_id': cell, 'build_number': n, 'test_number': n,
            'manifest_sha256': v.sha((self.base / ('execution/' + cell + '-manifest.json')).read_bytes()),
            'active_seconds_at_reservation': begin, 'remaining_active_seconds': 5400. - begin,
            'status': 'COMPLETE', 'receipt': v.REL + '/' + prefix + 'supervisor.json'})

    def rebind_outputs(self):
        self.result['output_bindings'] = []
        for p in sorted(self.root.rglob('*')):
            if p.is_file() and p.name != 'result.json':
                raw = p.read_bytes()
                self.result['output_bindings'].append({'path': str(p.relative_to(self.root)), 'sha256': v.sha(raw), 'bytes': len(raw)})
        self.write('result.json', self.result)

    def refuse(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            v.validate()
        self.spawn.assert_not_called()

    def test_portable_complete_replay_requires_no_runtime_installation(self):
        self.assertEqual(v.validate()['status'], 'PASS')
        self.spawn.assert_not_called()

    def test_entry_work_record_cannot_be_rewritten(self):
        self.work['start_monotonic'] = 1010.
        self.write('work-record.json', self.work)
        self.refuse('immutable entry')

    def test_inputs_cannot_change_after_freeze_even_with_updated_output_hash(self):
        self.science['cells'].pop()
        self.write('scientific-inputs.json', self.science)
        self.rebind_outputs()
        self.refuse('inputs changed')

    def test_wrong_scientific_matrix_cannot_be_legitimized_by_git_binding(self):
        self.science['cells'].pop()
        self.write('scientific-inputs.json', self.science, self.freeze)
        self.refuse('fixed string-reconstruction')

    def test_unicode_scalar_order_cannot_change(self):
        self.science['payloads'][1]['unicode_scalars'].reverse()
        self.write('scientific-inputs.json', self.science, self.freeze)
        self.refuse('fixed string-reconstruction')

    def test_qualified_exclusion_cannot_be_dropped(self):
        self.science['exclusions'].pop()
        self.write('scientific-inputs.json', self.science, self.freeze)
        self.refuse('fixed string-reconstruction')

    def test_predecessor_design_is_bound_without_semantic_promotion(self):
        self.frozen[(self.freeze, v.SCIENTIFIC['design_binding']['path'])] = b'changed design'
        self.refuse('predecessor design binding')

    def replace_manifest(self, change):
        name = 'execution/001-focused-manifest.json'
        manifest = self.load(name)
        change(manifest)
        self.write(name, manifest, self.freeze)
        self.account['reservations'][0]['manifest_sha256'] = v.sha((self.base / name).read_bytes())
        self.write('execution/accounting.json', self.account)
        self.rebind_outputs()

    def test_design_binding_cannot_be_omitted_from_launch_manifest(self):
        self.replace_manifest(lambda m: m.update(bindings=[row for row in m['bindings']
            if row['path'] != v.SCIENTIFIC['design_binding']['path']]))
        self.refuse('missing required tooling/scientific')

    def test_matrix_binding_cannot_be_omitted_from_launch_manifest(self):
        self.replace_manifest(lambda m: m.update(bindings=[row for row in m['bindings']
            if row['path'] != v.SCIENTIFIC['matrix_binding']['path']]))
        self.refuse('missing required tooling/scientific')

    def test_declaration_presence_cannot_be_promoted(self):
        self.science['fixture']['declarations_present'] = True
        self.write('scientific-inputs.json', self.science, self.freeze)
        self.refuse('fixed string-reconstruction')

    def test_unicode_scalars_cannot_be_replaced_with_utf8_bytes(self):
        self.science['payloads'][1]['unicode_scalars'] = list('Aé𝄞'.encode())
        self.write('scientific-inputs.json', self.science, self.freeze)
        self.refuse('fixed string-reconstruction')

    def test_fixture_binding_cannot_be_omitted_from_launch_manifest(self):
        self.replace_manifest(lambda m: m.update(bindings=[row for row in m['bindings']
            if not row['path'].endswith('Empty/export')]))
        self.refuse('missing required fixture')

    def test_changed_fixture_hash_cannot_be_legitimized_by_manifest(self):
        def change(m):
            next(row for row in m['bindings'] if row['path'].endswith('Empty/export'))['sha256'] = 'a' * 64
        self.replace_manifest(change)
        self.refuse('fixture bytes differ')

    def test_production_patch_refused_even_if_committed(self):
        raw = self.patch.replace(b'src/tests.rs', b'src/tc.rs')
        self.write_raw('patches/string-reconstruction.patch', raw, self.freeze)
        self.refuse('test-only patch')

    def test_deducted_work_time_refused(self):
        self.closure['active_seconds'] = 90.
        self.write('work-closure.json', self.closure)
        self.refuse('deducted time')

    def test_nan_clock_does_not_evade_budget(self):
        self.closure['end_monotonic'] = float('nan')
        self.write('work-closure.json', self.closure)
        self.refuse('finite')

    def test_deleted_attempt_cannot_reduce_counts(self):
        self.account['reservations'].pop()
        self.account['builds'] = self.account['test_processes'] = 1
        self.write('execution/accounting.json', self.account)
        self.rebind_outputs()
        self.refuse('reservation count')

    def test_orphan_raw_attempt_refused(self):
        (self.base / 'execution/003-full').mkdir()
        self.refuse('orphan')

    def test_pending_cleanup_refused(self):
        self.account['pending'] = '002-full'
        self.write('execution/accounting.json', self.account)
        self.rebind_outputs()
        self.refuse('pending reservation')

    def test_reservation_numbers_cannot_reset(self):
        self.account['reservations'][1]['build_number'] = 1
        self.write('execution/accounting.json', self.account)
        self.rebind_outputs()
        self.refuse('counters reset')

    def test_post_launch_commit_refused(self):
        with patch.object(v, 'commit_time', return_value=self.start + 30):
            self.refuse('committed after launch')

    def test_raw_request_hash_is_recomputed(self):
        name = 'execution/001-focused/request.json'
        request = self.load(name)
        request['argv'] = ['arbitrary-program']
        self.write(name, request)
        self.rebind_outputs()
        self.refuse('raw request digest')

    def test_valid_request_hash_does_not_authorize_different_invocation(self):
        name = 'execution/001-focused/request.json'
        request = self.load(name)
        request['argv'] = ['arbitrary-program']
        request.pop('request_sha256')
        request['request_sha256'] = v.sha(json.dumps(request, sort_keys=True).encode())
        self.write(name, request)
        receipt_name = 'execution/001-focused/supervisor.json'
        receipt = self.load(receipt_name)
        receipt['request_sha256'] = request['request_sha256']
        self.write(receipt_name, receipt)
        self.rebind_outputs()
        self.refuse('invocation differs')

    def test_forged_pass_count_without_named_tests_refused(self):
        stdout = b'test result: ok. 2 passed; 0 failed; 0 ignored;\n'
        self.write_raw('execution/001-focused/stdout', stdout)
        name = 'execution/001-focused/supervisor.json'
        receipt = self.load(name)
        receipt['stdout_sha256'] = v.sha(stdout)
        self.write(name, receipt)
        self.rebind_outputs()
        self.refuse('missing named')

    def test_inflated_pass_summary_refused(self):
        path = self.base / 'execution/001-focused/stdout'
        stdout = path.read_bytes().replace(b'2 passed;', b'40 passed;')
        path.write_bytes(stdout)
        name = 'execution/001-focused/supervisor.json'
        receipt = self.load(name)
        receipt['stdout_sha256'] = v.sha(stdout)
        self.write(name, receipt)
        self.rebind_outputs()
        self.refuse('library test summary')

    def test_output_binding_cannot_be_omitted(self):
        self.result['output_bindings'] = [r for r in self.result['output_bindings'] if not r['path'].endswith('/stderr')]
        self.write('result.json', self.result)
        self.refuse('incomplete closure')

    def test_external_draft_requires_ledger_index(self):
        self.write('closure-external-contributions.json', {'contributions': []})
        self.rebind_outputs()
        self.refuse('draft absent')

    def test_draft_path_in_unrelated_ledger_text_is_not_attribution(self):
        self.write('closure-external-contributions.json', {'contributions': [], 'notes': self.result['recommendation']['draft']})
        self.rebind_outputs()
        self.refuse('draft absent')

    def test_same_draft_for_different_item_refused(self):
        ledger = self.load('closure-external-contributions.json')
        ledger['contributions'][0]['research_items'] = ['ANOTHER-ITEM']
        self.write('closure-external-contributions.json', ledger)
        self.rebind_outputs()
        self.refuse('incorrectly attributed')

    def test_closure_snapshot_survives_later_live_frontier_and_submission(self):
        self.put('config/research-queue.json', b'{"selected_item":"LATER"}')
        self.put('results/research/external-contributions.json', b'{"contributions":[]}')
        # The live ledger was included in this synthetic output inventory; remove
        # its incidental binding, just as production binds the explicit snapshot.
        self.result['output_bindings'] = [r for r in self.result['output_bindings']
            if r['path'] != 'results/research/external-contributions.json']
        self.write('result.json', self.result)
        self.assertEqual(v.validate()['status'], 'PASS')

    def test_snapshot_cannot_claim_started_successor(self):
        queue = self.load('closure-queue.json')
        queue['items'][1]['status'] = 'ACTIVE'
        self.write('closure-queue.json', queue)
        self.rebind_outputs()
        self.refuse('closure queue state')

    def test_counts_cannot_disagree_between_closure_and_result(self):
        self.closure['research_counts'] = dict(self.result['research_counts'], builds=1)
        self.write('work-closure.json', self.closure)
        self.rebind_outputs()
        self.refuse('closure/result counts')

    def test_successor_must_remain_unstarted(self):
        self.result['next_item']['started'] = True
        self.write('result.json', self.result)
        self.refuse('unstarted successor')

    def test_old_historical_binding_is_checked_at_its_base_commit(self):
        self.frozen[(self.work['base_commit'], 'CONSTITUTION.md')] = b'changed history'
        self.refuse('historical entry binding')

    def test_failed_attempt_is_retained_and_charged_before_successful_retry(self):
        failed = self.load('execution/002-full/supervisor.json')
        failed.update(status='FAILED', returncode=101)
        self.write('execution/002-full/supervisor.json', failed)
        self.account['reservations'][1]['status'] = 'FAILED'
        self.make_attempt(3, 'full')
        self.account['builds'] = self.account['test_processes'] = 3
        self.write('execution/accounting.json', self.account)
        self.result['execution_commits']['003-full'] = self.freeze
        self.result['research_counts'].update(builds=3, test_processes=3)
        self.closure['research_counts'] = self.result['research_counts']
        self.write('work-closure.json', self.closure)
        self.rebind_outputs()
        self.assertEqual(v.validate()['reservations'], 3)

    def test_full_suite_cannot_hide_missing_documentation_phase(self):
        name = 'execution/002-full/stdout'
        stdout = (self.base / name).read_bytes().split(b'test result: ok. 0 passed;')[0]
        self.write_raw(name, stdout)
        receipt = self.load('execution/002-full/supervisor.json')
        receipt['stdout_sha256'] = v.sha(stdout)
        self.write('execution/002-full/supervisor.json', receipt)
        self.rebind_outputs()
        self.refuse('documentation suite summaries')


if __name__ == '__main__':
    unittest.main()
