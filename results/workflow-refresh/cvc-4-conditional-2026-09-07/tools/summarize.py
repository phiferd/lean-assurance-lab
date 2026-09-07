"""Generate the CVC-4 closure receipt after all required checks, once."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'results/research/conditional-validation-contracts/cvc-4-conditional'


def load(path):
    return json.loads(path.read_text())


def receipt(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


labels = ['01-source-mapping', '02-parameter-boundary', '03-close-item', '04-evidence',
          '05-queue', '06-queue-tests', '07-historical-publication', '08-publication-snapshot',
          '09-contribution', '10-declaration-catalog', '11-handoff-accounting', '12-full-suite',
          '13-current-state', '14-project-review', '15-artifact-status', '16-diff-check']
checks = []
for label in labels:
    path = BASE / (label + '.json')
    row = load(path)
    assert row['status'] == 'PASS' and row['returncode'] == 0 and row['tested_inputs_unchanged']
    assert receipt(ROOT / row['log']['path']) == row['log']
    assert receipt(ROOT / row['source_manifest']['path']) == row['source_manifest']
    checks.append({'label': label, 'receipt': receipt(path), 'command': row['command'],
                   'elapsed_seconds': row['elapsed_seconds']})
for row in load(BASE / 'closure-code-bindings.json'):
    assert receipt(ROOT / row['path']) == row
full = load(BASE / '12-full-suite.json')
assert full['fixtures_reconciled'] and full['reserved_launches'] == 23
assert full['known_instrumented_charge_seconds'] <= 115
counts = [int(x) for x in re.findall(r'^Ran (\d+) tests? in ', (BASE / '12-full-suite.log').read_text(), re.M)]
assert len(counts) == 2 and all(x > 0 for x in counts)
queue = load(ROOT / 'config/research-queue.json')
by_id = {r['id']: r for r in queue['items']}
assert by_id['CVC-4-CONDITIONAL']['status'] == 'COMPLETE'
assert by_id['CVC-4-CONDITIONAL']['closure']['outcome'] == 'BOUNDED_UNRESOLVED'
assert queue['selected_item'] == 'CVC-4-ADAPTER-REVIEW'
assert by_id[queue['selected_item']]['status'] == 'READY'
assert by_id[queue['selected_item']]['closure'] is None
assert not any(r['status'] == 'ACTIVE' for r in queue['items'])
assert by_id['CVC-4']['status'] == by_id['CVC-5']['status'] == 'PLANNED'
work = load(EVIDENCE / 'work-record.json')
assert work['status'] == 'CLOSED' and work['research_operations']['validator_launches'] == 12
result = load(EVIDENCE / 'result.json')
review = load(ROOT / 'results/research/queue-reviews/2026-09-07-cvc-4-conditional.json')
assert review['after']['ordering'] == [r['id'] for r in queue['items']]
assert review['after']['selected_item'] == queue['selected_item']
assert not (BASE / 'validation.json').exists()
record = {'schema_version': 1, 'item_id': 'CVC-4-CONDITIONAL', 'status': 'PASS',
          'outcome': 'BOUNDED_UNRESOLVED', 'completed_at': datetime.now(timezone.utc).isoformat(),
          'checks': checks, 'source_manifest': receipt(BASE / 'closure-code-bindings.json'),
          'workflow_tools': [receipt(p) for p in sorted((BASE / 'tools').glob('*.py'))],
          'tests': {'current': counts[0], 'historical': counts[1], 'total': sum(counts),
                    'historical_transition_tests_unchanged': True},
          'research_accounting': result['summary'],
          'administrative_fixtures': {'allocation_launches': 46, 'allocation_seconds': 230,
              'reserved_launches': 23, 'reserved_seconds': 115,
              'known_instrumented_charge_seconds': full['known_instrumented_charge_seconds'],
              'unused_allocation_launches': 23, 'unused_allocation_seconds': 115,
              'reconciled': True, 'separate_from_research_launches': True},
          'state_bindings': [receipt(ROOT / p) for p in ('config/research-queue.json',
              'docs/RESEARCH_STATUS.md', 'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md',
              'docs/PROJECT_REVIEW.md', 'docs/PUBLIC_STATUS.md', 'results/artifacts/graph.json',
              'results/assurance/current.json', 'results/assurance/milestone-9.json',
              'results/research/project-review.json', 'results/research/queue-reviews/2026-09-07-cvc-4-conditional.json')],
          'evidence_bindings': [receipt(p) for p in sorted(EVIDENCE.rglob('*'))
              if p.is_file() and '__pycache__' not in p.parts and p.name != 'controller.lock'],
          'completed_items': ['CVC-4-CONDITIONAL'], 'next_selected_item': queue['selected_item'],
          'next_item_started': False,
          'remaining_assurance_gaps': 'Broader assurance failures remain visible; neither finite observations nor this closure promotes semantic authority or discharges A7.',
          'external_research_action': 'NONE', 'delivery': 'Commit on main and push using scripts/push-main; Git records delivery separately.'}
(BASE / 'validation.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': record['status'], 'outcome': record['outcome'], 'tests': record['tests'],
                  'next_selected_item': record['next_selected_item'], 'next_item_started': False}))
