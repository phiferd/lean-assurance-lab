"""Pure same-item successor regressions, including unchanged original controls."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_cvc4_runner as original_tests
from lib import cvc4_runner2 as runner


class ObserverSuccessorTests(original_tests.ObserverRunnerTests):
    def setUp(self):
        # Reuse the exact frozen control tests against the new module without
        # modifying their source or the original production runner's globals.
        adaptation = patch.object(original_tests, 'runner', runner)
        adaptation.start()
        self.addCleanup(adaptation.stop)
        super().setUp()
        self.real_predecessor = runner.validate_predecessor
        self.old = {'launch_count': runner.INHERITED_LAUNCHES,
                    'known_process_seconds': runner.INHERITED_PROCESS_SECONDS,
                    'work': {'intervals': deepcopy(self.work['intervals'])},
                    'accounted_at': original_tests.clock(0)}
        self.prior = self.context.enter_context(patch.object(runner, 'validate_predecessor', return_value=self.old))
        self.write_json('predecessor.json', {'pure_test_placeholder': True})
        self.manifest['predecessor'] = self.binding('predecessor.json')
        self.save_manifest()

    def test_sixteen_launch_ceiling_is_enforced(self):
        self.manifest['cells'] = [self.cell(role, 'pair' + str(pair), implementation)
                                  for pair in range(4) for implementation in ('one', 'two')
                                  for role in ('control', 'candidate')][:-2]
        self.save_manifest()
        self.begin()
        state = runner.execute(self.root, 'run')
        self.assertEqual(len(state['attempts']), 14)
        with self.assertRaisesRegex(ValueError, 'combined validator launch cap exhausted'):
            runner.budget(state, original_tests.clock(self.tick))
        self.assertEqual(self.process.call_count, 14)
        result = runner.validate_run(self.root)
        self.assertEqual(result['inherited_launch_count'], 2)
        self.assertEqual(result['combined_launch_count'], 16)
        self.assertEqual(result['combined_process_seconds'], 7. + runner.INHERITED_PROCESS_SECONDS)

    def test_new_matrix_cannot_claim_sixteen_additional_launches(self):
        self.manifest['cells'] = [self.cell(role, 'pair' + str(pair), implementation)
                                  for pair in range(4) for implementation in ('one', 'two')
                                  for role in ('control', 'candidate')]
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'includes predecessor'):
            runner.validate_manifest(self.root)
        self.process.assert_not_called()

    def test_inherited_cost_is_written_into_start_and_cannot_reset(self):
        self.begin()
        events, state = self.ledger().read()
        self.assertEqual(events[0]['predecessor']['launches'], 2)
        self.assertEqual(events[0]['predecessor']['known_process_seconds'], runner.INHERITED_PROCESS_SECONDS)
        altered = deepcopy(events)
        altered[0]['predecessor']['launches'] = 0
        with self.assertRaisesRegex(ValueError, 'inherited predecessor cost changed'):
            runner.derive(altered)
        altered = deepcopy(events)
        altered[0]['predecessor']['known_process_seconds'] = 0
        with self.assertRaisesRegex(ValueError, 'inherited predecessor cost changed'):
            runner.derive(altered)

    def test_prior_observed_engineering_work_cannot_be_erased_by_new_baseline(self):
        self.old['accounted_at'] = original_tests.clock(8)
        self.work['intervals'] = [{'number': 1, 'start': original_tests.clock(0),
                                   'end': original_tests.clock(5), 'charged_seconds': 5.},
                                  {'number': 2, 'start': original_tests.clock(6), 'end': None}]
        self.work['active_seconds_closed'] = 5.
        self.write_json(runner.WORK, self.work)
        self.write_json('work-baseline.json', self.work)
        self.manifest['work_baseline'] = self.binding('work-baseline.json')
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'rollback|erased'):
            self.begin()
        self.process.assert_not_called()

    def predecessor_fixture(self):
        old_cells, new_cells, fixed = [], [], [self.binding('input.txt')]
        for pair in ('right-succ', 'zero', 'unowned'):
            for role in ('control', 'candidate'):
                name = 'E-CONTROL' if pair == 'right-succ' and role == 'control' else pair + '-' + role
                old_config, new_config = 'old-configs/' + name + '.json', 'new-configs/' + name + '.json'
                config = {'export_file_path': str(self.root / 'input.txt'), 'semantic_flag': True}
                self.write_json(old_config, config)
                self.write_json(new_config, {**config, 'print_axioms': False})
                fixed.extend([self.binding(old_config), self.binding(new_config)])
                for implementation in ('official', 'nanoda'):
                    old = self.cell(role, pair, implementation)
                    old['id'] = name + '-' + implementation
                    if implementation == 'nanoda':
                        old['argv'][1] = str(self.root / old_config)
                    revised = deepcopy(old)
                    if implementation == 'nanoda':
                        revised['argv'][1] = str(self.root / new_config)
                    old_cells.append(old)
                    new_cells.append(revised)
        old_manifest = {'cells': old_cells, 'payloads': deepcopy(self.manifest['payloads']),
                        'fixed_inputs': [r for r in fixed if not r['path'].startswith('new-configs/')]}
        self.write_json(runner.predecessor.MANIFEST, old_manifest)
        record = {'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.predecessor.RUN,
                  'checkpoint': runner.PREDECESSOR_CHECKPOINT, 'manifest': self.binding(runner.predecessor.MANIFEST),
                  'launches': 2, 'known_process_seconds': runner.INHERITED_PROCESS_SECONDS}
        for key, filename in (('start', 'start.json'), ('events', 'events.jsonl'), ('snapshot', 'state.json')):
            path = self.write(runner.predecessor.OUT + '/' + filename, key + '\n')
            record[key] = runner.file_receipt(self.root, path)
        self.write(runner.predecessor.OUT + '/attempts/02/stdout', runner.PREDECESSOR_STDOUT.decode())
        self.write(runner.predecessor.OUT + '/attempts/02/stderr', '')
        self.write_json('predecessor.json', record)
        self.manifest.update(predecessor=self.binding('predecessor.json'), cells=new_cells, fixed_inputs=fixed)
        self.save_manifest()
        summary = {**deepcopy(self.old), 'checkpoint': runner.PREDECESSOR_CHECKPOINT,
                   'pending': False, 'control_stop': None, 'hypothesis_mismatch': True,
                   'reconciliations': [], 'manifest': old_manifest,
                   'attempts': [{'reservation': {'cell': deepcopy(cell)},
                                 'terminal': {'hypothesis_matched': matched, 'returncode': 0,
                                              'process_status': 'COMPLETE'}}
                                for cell, matched in zip(old_cells[:2], (True, False))]}
        prior_validation = self.context.enter_context(patch.object(runner.predecessor, 'validate_run', return_value=summary))
        supervised = self.context.enter_context(patch.object(runner.predecessor, 'supervisor', return_value=(
            {'cleanup_completed': True, 'deadline_exceeded': False, 'status': 'COMPLETE', 'returncode': 0}, [])))
        return summary, prior_validation, supervised

    def test_exact_prior_reporting_mismatch_is_replayed_without_relabeling(self):
        summary, prior_validation, supervised = self.predecessor_fixture()
        result = self.real_predecessor(self.root, self.manifest, require_payloads=False)
        self.assertIs(result, summary)
        self.assertIs(result['attempts'][1]['terminal']['hypothesis_matched'], False)
        prior_validation.assert_called_once_with(self.root, require_payloads=False)
        self.assertEqual(supervised.call_count, 2)
        self.process.assert_not_called()

    def test_predecessor_wrong_cost_count_or_observation_is_refused(self):
        summary, _, _ = self.predecessor_fixture()
        mutations = [lambda s: s.update(launch_count=1), lambda s: s.update(launch_count=3),
                     lambda s: s.update(known_process_seconds=None), lambda s: s.update(control_stop='unknown cleanup'),
                     lambda s: s.update(pending=True),
                     lambda s: s['attempts'][1]['terminal'].update(hypothesis_matched=True),
                     lambda s: s['attempts'][1]['terminal'].update(returncode=101)]
        original = deepcopy(summary)
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                summary.clear()
                summary.update(deepcopy(original))
                mutation(summary)
                with self.assertRaises(ValueError):
                    self.real_predecessor(self.root, self.manifest)

    def test_predecessor_exact_raw_diagnostic_is_required(self):
        self.predecessor_fixture()
        path = self.root / runner.predecessor.OUT / 'attempts/02/stdout'
        path.write_bytes(b'Checked 1 declarations with no errors\n')
        with self.assertRaisesRegex(ValueError, 'exact pretty-printer diagnostic'):
            self.real_predecessor(self.root, self.manifest)

    def test_successor_may_change_only_print_axioms(self):
        self.predecessor_fixture()
        candidate = self.manifest['cells'][1]
        path = Path(candidate['argv'][1])
        config = json.loads(path.read_text())
        config['semantic_flag'] = False
        path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'beyond disabling axiom printing'):
            self.real_predecessor(self.root, self.manifest)

    def test_reporting_switch_requires_json_boolean_false(self):
        self.predecessor_fixture()
        path = Path(self.manifest['cells'][1]['argv'][1])
        config = json.loads(path.read_text())
        config['print_axioms'] = 0
        path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'beyond disabling axiom printing'):
            self.real_predecessor(self.root, self.manifest)

    def test_scientific_expectations_payloads_and_old_binding_inventory_cannot_change(self):
        self.predecessor_fixture()
        original = deepcopy(self.manifest)
        mutations = [lambda m: m['cells'][1]['expected'].update(stdout_pattern='any'),
                     lambda m: m['payloads'][0].update(sha256='0' * 64),
                     lambda m: m['fixed_inputs'].pop(0),
                     lambda m: m['cells'].pop()]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = deepcopy(original)
                mutation(changed)
                with self.assertRaises(ValueError):
                    self.real_predecessor(self.root, changed)


if __name__ == '__main__':
    unittest.main()
