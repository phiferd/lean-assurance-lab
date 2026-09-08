"""Freeze closure accounting after the complete exact-input validation batch."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc4_ownership_runner as runner
from lib.cvc4_ownership_evidence import validate


def load(p): return json.loads(p.read_text())
def dump(p, v): p.write_text(json.dumps(v, indent=2) + '\n')
def receipt(p):
    raw = p.read_bytes()
    return {'path': str(p.relative_to(ROOT)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


labels = ['01-queue', '02-queue-tests', '03-ownership-evidence', '04-predecessor-review',
          '05-historical', '06-snapshot', '07-full-suite', '08-contribution', '09-catalog',
          '11-current-state', '12-project-review', '13-artifact-status',
          '14-diff-check', '15-portable-evidence']
checks = []
for label in labels:
    path = BASE / (label + '.json')
    row = load(path)
    assert row['status'] == 'PASS' and row['returncode'] == 0 and row['tested_inputs_unchanged']
    assert receipt(ROOT / row['log']['path']) == row['log']
    assert receipt(ROOT / row['source_manifest']['path']) == row['source_manifest']
    checks.append({'label': label, 'receipt': receipt(path), 'command': row['command'], 'elapsed_seconds': row['elapsed_seconds']})
for name in ('closure-code-bindings.json', 'closure-decision-bindings.json'):
    assert all(receipt(ROOT / r['path']) == r for r in load(BASE / name))
full = load(BASE / '07-full-suite.json')
assert full['fixtures_reconciled'] and full['reserved_launches'] == 23
log = (BASE / '07-full-suite.log').read_text()
counts = [int(n) for n in re.findall(r'^Ran (\d+) tests? in ', log, re.M)]
assert len(counts) == 2 and all(counts) and 'skipped=' not in log
diagnostic = load(BASE / 'administrative-context-repair.json')
failure = load(BASE / '10-declaration-tests.json')
assert failure['status'] == 'FAIL' and failure['returncode'] == 1 and failure['tested_inputs_unchanged']
assert receipt(ROOT / diagnostic['failure']['path']) == diagnostic['failure']
assert receipt(ROOT / diagnostic['failure_log']['path']) == diagnostic['failure_log']
for test in diagnostic['failed_tests']:
    assert re.search(r'^' + re.escape(test) + r' \([^\n]+\) \.\.\. ok$', log, re.M), test
assert all(receipt(ROOT / row['path']) == row for row in load(BASE / 'closure-finalizer-bindings.json'))

queue = load(ROOT / 'config/research-queue.json'); by_id = {r['id']: r for r in queue['items']}
assert by_id[runner.ITEM]['closure']['outcome'] == 'SUCCESS'
assert queue['selected_item'] == 'CVC-5-CONDITIONAL'
assert by_id[queue['selected_item']]['status'] == 'READY' and by_id[queue['selected_item']]['closure'] is None
assert not any(r['status'] == 'ACTIVE' for r in queue['items'])
assert by_id['CVC-4']['status'] == by_id['CVC-5']['status'] == 'PLANNED'
assert not (ROOT / 'results/research/conditional-validation-contracts/cvc-5-conditional').exists()
evidence = validate(ROOT)
assert evidence['outcome'] == 'SUCCESS' and evidence['research_counts']['combined_observer_launches'] == 16
workpath = ROOT / runner.WORK; work = load(workpath)
assert work['status'] == 'ACTIVE' and work['intervals'][-1]['end'] is None
assert not (BASE / 'validation.json').exists()
work['administrative_fixtures'] = {'allocation': str((BASE / 'administrative-fixture-allocation.json').relative_to(ROOT)),
        'reserved_launches': 23, 'reserved_seconds': 115,
        'known_instrumented_charge_seconds': full['known_instrumented_charge_seconds'], 'reconciled': True}
work['research_counts'] = evidence['research_counts']
work['intervals'][-1]['end'] = runner.stamp()
work['intervals'][-1]['charged_seconds'] = runner.elapsed(work['intervals'][-1]['start'], work['intervals'][-1]['end'])
work['active_seconds_closed'] = runner.work_total(work, work['intervals'][-1]['end'], enforce=True)
work['status'] = 'COMPLETE'
dump(workpath, work)
record = {'schema_version': 1, 'item_id': runner.ITEM, 'status': 'PASS', 'outcome': evidence['outcome'],
          'completed_at': work['intervals'][-1]['end']['at'], 'checks': checks,
          'source_manifest': receipt(BASE / 'closure-code-bindings.json'),
          'decision_manifest': receipt(BASE / 'closure-decision-bindings.json'),
          'tests': {'current': counts[0], 'historical': counts[1], 'total': sum(counts), 'skips': 0,
                    'historical_transition_tests_unchanged': True},
          'research_accounting': evidence, 'final_active_seconds': work['active_seconds_closed'],
          'work_record': receipt(workpath), 'administrative_fixtures': work['administrative_fixtures'],
          'evidence_bindings': [receipt(p) for p in sorted(workpath.parent.rglob('*')) if p.is_file() and not p.name.endswith('.lock')],
          'state_bindings': [receipt(ROOT / p) for p in ('config/research-queue.json', 'docs/RESEARCH_STATUS.md',
                    'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md', 'docs/PROJECT_REVIEW.md', 'docs/PUBLIC_STATUS.md',
                    'results/artifacts/graph.json', 'results/assurance/current.json', 'results/assurance/milestone-9.json', 'results/research/project-review.json')],
          'supplemental_validation_failure': {'receipt': receipt(BASE / '10-declaration-tests.json'), 'diagnosis': receipt(BASE / 'administrative-context-repair.json'), 'resolution': 'All three historical tests passed unchanged in the required attested full suite; no tests or gates weakened.'}, 'finalizer_bindings': receipt(BASE / 'closure-finalizer-bindings.json'), 'completed_items': [runner.ITEM], 'next_selected_item': queue['selected_item'], 'next_item_started': False,
          'external_research_action': 'NONE', 'delivery': 'Final main commit and scripts/push-main verify delivery separately.'}
dump(BASE / 'validation.json', record)
print(json.dumps({'status': 'PASS', 'tests': record['tests'], 'active_seconds': work['active_seconds_closed'],
                  'next_item': queue['selected_item'], 'next_item_started': False}))
