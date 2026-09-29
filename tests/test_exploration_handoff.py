"""E0 handoffs stay small; shared and assurance changes keep full validation."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib import exploration as e
from lib import exploration_handoff as h


class ExplorationHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = {'selected_item': 'E0-TEST', 'items': [
            {'id': 'E0-TEST', 'status': 'READY', 'evidence_refs': ['docs/research/E0.md']},
            {'id': 'NEXT', 'status': 'PLANNED', 'evidence_refs': []}],
            'strategic_review': {'path': 'results/research/queue-reviews/new.json'}}
        self.write(e.LEDGER, '')
        self.write('config/research-queue.json', json.dumps(self.queue))
        self.write('docs/research/E0.md', '# Pilot\n\nEvidence class: E0\n')
        self.write('results/assurance/current.json', '{"retained": true}\n')
        self.write('results/artifacts/graph.json', '{"retained": true}\n')
        self.git('init', '-q')
        self.commit('base')
        self.base = self.git('rev-parse', 'HEAD').decode().strip()
        self.write('explorations/runs/EXPLORE-TEST-1/input', 'input')
        self.write('explorations/runs/EXPLORE-TEST-1/raw', 'raw')
        common = dict(schema_version=1, evidence_class='E0', id='EXPLORE-TEST-1',
                      at='2026-09-29T12:00:00Z')
        self.start = dict(common, event='start', data=dict(
            campaign='E0-TEST', question='Does this sample differ?',
            sources=[dict(name='test', revision='a'*40)], versions='test',
            commands='test', inputs=['explorations/runs/EXPLORE-TEST-1/input'],
            sample='one', planned_runs=1, controls='test'))
        self.finish = dict(common, event='finish', data=dict(
            outcome='NO_SIGNAL', completed_runs=1, signal_count=0,
            measurement_complete=True, engineering_failures_unresolved=False,
            observations='matched', limitations='synthetic', decision='stop',
            raw_output=['explorations/runs/EXPLORE-TEST-1/raw'], cost='unknown'))
        self.write(e.LEDGER, '\n'.join(json.dumps(r) for r in [self.start, self.finish])+'\n')
        self.queue['items'][0]['status'] = 'COMPLETE'
        self.queue['items'][1]['status'] = 'READY'
        self.queue['selected_item'] = 'NEXT'
        self.write('config/research-queue.json', json.dumps(self.queue))
        self.write(self.queue['strategic_review']['path'], json.dumps(
            dict(phase='CLOSURE', stopped_item='E0-TEST')))

    def write(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value)

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                                        *args], cwd=self.root, stderr=subprocess.PIPE)

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', message)

    def test_handoff_gets_light_lane_with_planning_updates(self):
        self.write('docs/research/NEXT.md', '# New plan\n')
        self.commit('handoff')
        self.assertEqual(e.validation_lane(self.root, self.base), 'exploration-handoff')

    def test_shared_assurance_historical_and_unknown_changes_keep_full_lane(self):
        paths = h.changed_paths(self.root, self.base, worktree=True)
        for path in ['lib/runner.py', 'tests/test_runner.py', '.github/workflows/unit-tests.yml',
                     'schemas/exploration-event.schema.json', 'AGENTS.md',
                     'results/assurance/current.json', 'results/artifacts/graph.json',
                     'results/workflow-refresh/new/result.json', 'docs/research/E0.md',
                     'misc.txt']:
            with self.subTest(path=path):
                self.assertFalse(h.qualifies(self.root, self.base, paths | {path}))

    def test_no_completed_e0_cannot_use_handoff(self):
        self.write(e.LEDGER, json.dumps(self.start)+'\n')
        self.assertFalse(h.qualifies(self.root, self.base,
                                    h.changed_paths(self.root, self.base, worktree=True)))

    def test_write_only_updates_two_planning_views_and_check_is_read_only(self):
        fake = dict(OUTPUT='results/research/project-review.json', REPORT='docs/PROJECT_REVIEW.md',
                    build=lambda: {'planning': 'only'}, render=lambda r: 'planning only\n')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*')
                  if p.is_file() and '.git' not in p.parts}
        with patch('lib.research_queue_v4.load_queue', return_value=self.queue), \
             patch.object(h.runpy, 'run_path', return_value=fake) as builder:
            result = h.handoff(self.root, self.base, write=True)
            self.assertEqual(builder.call_count, 1)
            self.assertFalse(result['assurance_refreshed'])
            self.assertEqual(result['selected_item'], 'NEXT')
            after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*')
                     if p.is_file() and '.git' not in p.parts}
            self.assertEqual(set(after)-set(before), {fake['OUTPUT'], fake['REPORT']})
            self.assertTrue(all(after[p] == b for p, b in before.items()))
            h.handoff(self.root, self.base)
            self.assertEqual(after, {str(p.relative_to(self.root)): p.read_bytes()
                                    for p in self.root.rglob('*')
                                    if p.is_file() and '.git' not in p.parts})
            self.write(fake['REPORT'], 'stale')
            with self.assertRaisesRegex(ValueError, 'planning view is stale'):
                h.handoff(self.root, self.base)

    def test_invalid_queue_or_started_successor_stops_before_generation(self):
        with patch('lib.research_queue_v4.load_queue', side_effect=ValueError('bad queue')), \
             patch.object(h, 'planning_view') as view:
            with self.assertRaisesRegex(ValueError, 'bad queue'):
                h.handoff(self.root, self.base, write=True)
            view.assert_not_called()
        queue = copy.deepcopy(self.queue)
        queue['items'][1]['status'] = 'ACTIVE'
        with patch('lib.research_queue_v4.load_queue', return_value=queue), \
             patch.object(h, 'planning_view') as view:
            with self.assertRaisesRegex(ValueError, 'unstarted'):
                h.handoff(self.root, self.base, write=True)
            view.assert_not_called()

    def test_last_real_campaign_without_assurance_cascade_qualifies(self):
        # The retained commit demonstrates the exact old lane mismatch. Reading
        # it does not rewrite its evidence or reclassify its original validation.
        base = '6bf5d4f8ef73d4d8364e824b0a50543d7af0e493'
        commit = '462a8e026dd3d0a67efc66652b528af2c3791da3'
        paths = set(h.git(e.ROOT, 'diff', '--name-only', base, commit).decode().splitlines())
        self.assertFalse(h.qualifies(e.ROOT, base, paths))
        stripped = {p for p in paths if not p.startswith((
            'results/assurance/', 'results/artifacts/', 'results/workflow-refresh/'))
                    and p != 'docs/PUBLIC_STATUS.md'}
        self.assertTrue(h.qualifies(e.ROOT, base, stripped))
