import copy
import json
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
from lib import exploration as e


class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'explorations').mkdir()
        (self.root / e.LEDGER).write_bytes(b'')
        (self.root / 'input.txt').write_text('synthetic fixture\n')
        (self.root / 'raw.txt').write_text('synthetic stdout / exit 0 / cleanup complete\n')
        (self.root / 'plan.md').write_text('# Test campaign\n\nEvidence class: E0\n')
        (self.root / 'config').mkdir()
        (self.root / 'config/research-queue.json').write_text('{"items": []}')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'baseline')
        self.start = dict(schema_version=1, evidence_class='E0', event='start',
                         id='EXPLORE-TEST-1', data=dict(
                             campaign='TEST-CAMPAIGN', question='Does this synthetic pair differ?',
                             sources=[dict(name='synthetic', revision='a' * 40)],
                             versions='test tool 1; model none', commands='test fixture, no process',
                             inputs=['input.txt'], sample='one predetermined pair', planned_runs=1,
                             controls='synthetic fixture only; no process launches'))
        self.finish = dict(schema_version=1, evidence_class='E0', event='finish',
                          id=self.start['id'], data=dict(
                              outcome='NO_SIGNAL', completed_runs=1, signal_count=0,
                              measurement_complete=True, engineering_failures_unresolved=False,
                              observations='one pair matched', limitations='synthetic, not scientific',
                              decision='do not promote', raw_output=['raw.txt'], cost='model none; time unknown'))
        self.promote = dict(schema_version=1, evidence_class='E0', event='promote',
                           id=self.start['id'], data=dict(confirmation_id='CONFIRM-TEST-1',
                           hypothesis='This relation merits controlled confirmation',
                           reason='Useful negative boundary; no confirmed result claimed'))
        self.queue = dict(selected_item='TEST-CAMPAIGN', items=[dict(
            id='TEST-CAMPAIGN', status='ACTIVE', evidence_refs=['plan.md'])])

    def git(self, *args):
        # The synthetic repository is deleted as soon as each test finishes.
        # Detached auto-maintenance can otherwise outlive the foreground Git
        # command and race TemporaryDirectory cleanup on Linux CI.
        return subprocess.check_output(
            ['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *args],
            cwd=self.root,
            stderr=subprocess.PIPE,
        )

    def append(self, row):
        with patch('lib.research_queue_v4.load_queue', return_value=self.queue):
            return e.append(self.root, row)

    def states(self):
        return e.validate(self.root, (self.root / e.LEDGER).read_bytes())

    def test_negative_path_only_writes_two_events(self):
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts}
        self.append(self.start)
        self.append(self.finish)
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts}
        self.assertEqual([p for p in after if before.get(p) != after[p]], [e.LEDGER])
        self.assertEqual(e.summary(self.states())['NO_SIGNAL'], 1)
        self.assertEqual(len(after[e.LEDGER].splitlines()), 2)

    def test_start_requires_selected_active_e0_campaign(self):
        for status, selected, text in [('READY', 'TEST-CAMPAIGN', 'Evidence class: E0'),
                                      ('ACTIVE', 'OTHER', 'Evidence class: E0'),
                                      ('ACTIVE', 'TEST-CAMPAIGN', 'Evidence class: E1')]:
            self.queue['items'][0]['status'] = status
            self.queue['selected_item'] = selected
            (self.root / 'plan.md').write_text('\n' + text + '\n')
            with self.subTest(status=status, selected=selected, text=text), self.assertRaises(ValueError):
                self.append(self.start)
        self.assertEqual((self.root / e.LEDGER).read_bytes(), b'')

    def test_missing_measurements_and_failures_are_not_negative_results(self):
        self.append(self.start)
        for key, value in [('measurement_complete', False), ('completed_runs', 0),
                           ('completed_runs', 2), ('engineering_failures_unresolved', True),
                           ('signal_count', 1)]:
            row = copy.deepcopy(self.finish)
            row['data'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.append(row)
        self.assertEqual(e.summary(self.states())['OPEN'], 1)

    def test_open_inconclusive_and_signal_denominators(self):
        for i, outcome in enumerate(['OPEN', 'INCONCLUSIVE', 'SIGNAL']):
            start = copy.deepcopy(self.start)
            start['id'] = f'EXPLORE-TEST-{i}'
            self.append(start)
            if outcome != 'OPEN':
                end = copy.deepcopy(self.finish)
                end['id'] = start['id']
                end['data'].update(outcome=outcome, completed_runs=0, measurement_complete=False,
                                   signal_count=int(outcome == 'SIGNAL'))
                self.append(end)
        summary = e.summary(self.states())
        self.assertEqual(summary['started'], 3)
        self.assertEqual([summary[k] for k in ['OPEN', 'INCONCLUSIVE', 'SIGNAL']], [1, 1, 1])

    def test_signal_requires_candidate_observation(self):
        self.append(self.start)
        self.finish['data']['outcome'] = 'SIGNAL'
        with self.assertRaises(ValueError):
            self.append(self.finish)

    def test_missing_raw_or_input_is_rejected(self):
        self.start['data']['inputs'] = ['absent.txt']
        with self.assertRaises(ValueError):
            self.append(self.start)
        self.start['data']['inputs'] = ['input.txt']
        self.append(self.start)
        self.finish['data']['raw_output'] = ['absent.txt']
        with self.assertRaises(ValueError):
            self.append(self.finish)

    def test_unsafe_paths_and_symlinks_rejected(self):
        (self.root / 'link').symlink_to(self.root / 'input.txt')
        for value in ['../input.txt', str(self.root / 'input.txt'), 'link']:
            self.start['data']['inputs'] = [value]
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.append(self.start)

    def test_out_of_order_duplicate_or_reclassified_events_rejected(self):
        with self.assertRaises(ValueError):
            self.append(self.finish)
        self.append(self.start)
        with self.assertRaises(ValueError):
            self.append(self.start)
        row = copy.deepcopy(self.finish)
        row['evidence_class'] = 'E1'
        with self.assertRaises(ValidationError):
            self.append(row)
        self.append(self.finish)
        with self.assertRaises(ValueError):
            self.append(self.finish)

    def test_committed_prefix_and_explicit_review_base(self):
        self.append(self.start)
        self.git('add', e.LEDGER)
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'start')
        baseline = self.git('rev-parse', 'HEAD').decode().strip()
        raw = (self.root / e.LEDGER).read_bytes()
        e.committed_prefix(self.root, raw, baseline)
        (self.root / e.LEDGER).write_bytes(raw.replace(b'synthetic', b'changed'))
        with self.assertRaises(ValueError):
            self.append(self.finish)
        with self.assertRaises(ValueError):
            e.committed_prefix(self.root, b'', baseline)

    def test_promotion_is_separate_planned_identity_with_no_execution_authority(self):
        self.append(self.start)
        with self.assertRaises(ValueError):
            self.append(self.promote)
        self.append(self.finish)
        frozen = (self.root / e.LEDGER).read_bytes()
        self.append(self.promote)
        self.assertTrue((self.root / e.LEDGER).read_bytes().startswith(frozen))
        result = e.proposal(self.states(), 'CONFIRM-TEST-1')
        self.assertEqual(result['derived_from'], 'EXPLORE-TEST-1')
        self.assertEqual(result['status'], 'PLANNED')
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(e.summary(self.states())['NO_SIGNAL'], 1)
        with self.assertRaises(ValueError):
            self.append(self.promote)

    def test_confirmation_identity_cannot_be_reused(self):
        self.append(self.start)
        self.append(self.finish)
        (self.root / 'config/research-queue.json').write_text('{"items": [{"id": "CONFIRM-TEST-1"}]}')
        with self.assertRaises(ValueError):
            self.append(self.promote)
        (self.root / 'config/research-queue.json').write_text('{"items": []}')
        self.append(self.promote)
        for row in [self.start, self.finish, self.promote]:
            row = dict(row, id='EXPLORE-SECOND-1')
            if row['event'] == 'promote':
                with self.assertRaises(ValueError):
                    self.append(row)
            else:
                self.append(row)

    def test_duplicate_json_and_partial_append_rejected(self):
        with self.assertRaises(ValueError):
            e.read_json('{"evidence_class":"E0","evidence_class":"E1"}')
        self.append(self.start)
        raw = (self.root / e.LEDGER).read_bytes()
        with self.assertRaises(ValueError):
            e.committed_prefix(self.root, raw[:-1])

    def test_old_raw_evidence_cannot_be_rewritten(self):
        self.append(self.start)
        self.append(self.finish)
        self.git('add', e.LEDGER)
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'closed')
        (self.root / 'raw.txt').write_text('different outcome')
        with self.assertRaises(ValueError):
            self.append(self.promote)

    def test_only_exploration_changes_use_light_ci(self):
        baseline = self.git('rev-parse', 'HEAD').decode().strip()
        self.append(self.start)
        self.append(self.finish)
        self.git('add', e.LEDGER)
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'exploration')
        self.assertEqual(e.validation_lane(self.root, baseline), 'exploration')
        (self.root / 'shared.py').write_text('shared tooling change')
        self.git('add', 'shared.py')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'shared')
        self.assertEqual(e.validation_lane(self.root, baseline), 'full')

    def test_live_ledger_is_valid_without_assurance_generation(self):
        raw = (e.ROOT / e.LEDGER).read_bytes()
        e.committed_prefix(e.ROOT, raw)
        self.assertEqual(e.summary(e.validate(e.ROOT, raw))['evidence_class'], 'E0')

    def test_closed_identity_survives_fresh_clone_without_ignored_input(self):
        (self.root / '.gitignore').write_text('local-input.txt\n')
        (self.root / 'local-input.txt').write_text('ephemeral build data')
        self.start['data']['inputs'] = ['local-input.txt']
        event = self.append(self.start)
        self.assertEqual(len(event['data']['input_sha256']['local-input.txt']), 64)
        self.append(self.finish)
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'closed screen')
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / 'clone'
            self.git('clone', '-q', '--no-hardlinks', str(self.root), str(clone))
            self.assertFalse((clone / 'local-input.txt').exists())
            raw = (clone / e.LEDGER).read_bytes()
            e.committed_prefix(clone, raw)
            self.assertEqual(e.summary(e.validate(clone, raw))['NO_SIGNAL'], 1)
            self.assertEqual(e.summary(e.validate(clone, raw))['unavailable_input_payloads'],
                             ['local-input.txt'])
            (clone / 'raw.txt').unlink()
            with self.assertRaises(ValueError):
                e.validate(clone, raw)

    def test_open_input_missing_or_closed_input_changed_is_rejected(self):
        self.append(self.start)
        p = self.root / 'input.txt'
        original = p.read_bytes()
        p.unlink()
        with self.assertRaises(ValueError):
            self.states()
        p.write_bytes(original)
        self.append(self.finish)
        p.write_text('different input')
        with self.assertRaisesRegex(ValueError, 'recorded input bytes changed'):
            self.states()

    def test_closed_unbound_missing_input_is_not_silently_accepted(self):
        self.append(self.start)
        self.append(self.finish)
        rows = [json.loads(line) for line in (self.root / e.LEDGER).read_text().splitlines()]
        del rows[0]['data']['input_sha256']
        (self.root / 'input.txt').unlink()
        with self.assertRaises(ValueError):
            e.validate(self.root, '\n'.join(json.dumps(row) for row in rows).encode())

    def test_live_historical_ledger_without_untracked_payloads(self):
        raw = (e.ROOT / e.LEDGER).read_bytes()
        tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=e.ROOT).decode().splitlines())
        paths = {e.LEGACY_IDENTITIES}
        for line in raw.splitlines():
            data = json.loads(line)['data']
            paths.update(data.get('inputs', []) + data.get('raw_output', []))
        for path in paths:
            if path in tracked or path == e.LEGACY_IDENTITIES:
                destination = self.root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(e.ROOT / path, destination)
        self.assertFalse((self.root / 'results/baseline/outcomes/nanoda-full.jsonl').exists())
        self.assertEqual(e.summary(e.validate(self.root, raw))['started'],
                         sum(json.loads(line)['event'] == 'start' for line in raw.splitlines()))
        binding = next(iter(json.loads((self.root / e.LEGACY_IDENTITIES).read_text()).values()))
        (self.root / binding['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'historical input identity file changed'):
            e.validate(self.root, raw)
