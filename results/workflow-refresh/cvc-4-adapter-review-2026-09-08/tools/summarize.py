"""Freeze final closure accounting and check exact required validation receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import sys
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.cvc4_adapter_review import BASE as EVIDENCE, validate

def load(p): return json.loads(p.read_text())
def receipt(p):
    raw = p.read_bytes()
    return {'path': str(p.relative_to(ROOT)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
def dump(p, v): p.write_text(json.dumps(v, indent=2) + '\n')

labels = ['01-queue', '02-review-tests', '03-review-evidence', '04-prior-evidence',
          '05-queue-tests', '06-historical', '07-snapshot', '08-full-suite',
          '09-contribution', '10-catalog', '11-current-state', '12-project-review',
          '13-artifact-status', '14-diff-check']
checks = []
for label in labels:
    path = BASE / (label + '.json')
    row = load(path)
    assert row['status'] == 'PASS' and row['returncode'] == 0 and row['tested_inputs_unchanged']
    assert receipt(ROOT / row['log']['path']) == row['log']
    assert receipt(ROOT / row['source_manifest']['path']) == row['source_manifest']
    checks.append({'label': label, 'receipt': receipt(path), 'command': row['command'], 'elapsed_seconds': row['elapsed_seconds']})
for name in ('closure-code-bindings.json', 'closure-decision-bindings.json'):
    assert all(receipt(ROOT / row['path']) == row for row in load(BASE / name))
full = load(BASE / '08-full-suite.json')
assert full['fixtures_reconciled'] and full['reserved_launches'] == 23
log = (BASE / '08-full-suite.log').read_text()
counts = [int(n) for n in re.findall(r'^Ran (\d+) tests? in ', log, re.M)]
assert len(counts) == 2 and all(counts) and 'skipped=' not in log
queue = load(ROOT / 'config/research-queue.json')
by_id = {r['id']: r for r in queue['items']}
assert by_id['CVC-4-ADAPTER-REVIEW']['closure']['outcome'] == 'SUCCESS'
assert queue['selected_item'] == 'CVC-4-OWNERSHIP-1'
assert by_id[queue['selected_item']]['status'] == 'READY' and by_id[queue['selected_item']]['closure'] is None
assert not any(r['status'] == 'ACTIVE' for r in queue['items'])
assert by_id['CVC-4']['status'] == by_id['CVC-5']['status'] == 'PLANNED'
assert not (ROOT / 'results/research/conditional-validation-contracts/cvc-4-ownership-1').exists()
work = load(ROOT / EVIDENCE / 'work-record.json')
assert work['status'] == 'ACTIVE' and not (BASE / 'validation.json').exists()
interval = work['intervals'][-1]
assert interval['end_utc'] is None
interval['end_utc'] = datetime.now(timezone.utc).isoformat()
interval['end_monotonic'] = time.monotonic()
interval['active_seconds'] = interval['end_monotonic'] - interval['start_monotonic']
work['active_seconds'] = sum(r['active_seconds'] for r in work['intervals'])
work['status'] = 'COMPLETE'
work['administrative_fixtures'] = {'allocation': 'results/workflow-refresh/cvc-4-adapter-review-2026-09-08/administrative-fixture-allocation.json', 'reserved_launches': 23, 'reserved_seconds': 115, 'known_instrumented_charge_seconds': full['known_instrumented_charge_seconds'], 'reconciled': True}
work['delegation'] = {'independent_scientific_review': 'GPT-6 Astra Ultra; read-only, no launches', 'closure_audit': 'Luna medium; read-only, no launches', 'accounting': 'Parallel advisory work occurred inside the root active interval; root owned all state and fixture launches.'}
dump(ROOT / EVIDENCE / 'work-record.json', work)
result = validate(ROOT)
record = {'schema_version': 1, 'item_id': 'CVC-4-ADAPTER-REVIEW', 'status': 'PASS', 'outcome': 'SUCCESS', 'decision': 'SUCCESSOR', 'completed_at': interval['end_utc'], 'checks': checks, 'source_manifest': receipt(BASE / 'closure-code-bindings.json'), 'decision_manifest': receipt(BASE / 'closure-decision-bindings.json'), 'tests': {'current': counts[0], 'historical': counts[1], 'total': sum(counts), 'skips': 0, 'historical_transition_tests_unchanged': True}, 'research_accounting': result, 'administrative_fixtures': work['administrative_fixtures'], 'evidence_bindings': [receipt(p) for p in sorted((ROOT / EVIDENCE).glob('*')) if p.is_file()], 'state_bindings': [receipt(ROOT / p) for p in ('config/research-queue.json', 'docs/RESEARCH_STATUS.md', 'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md', 'docs/PROJECT_REVIEW.md', 'docs/PUBLIC_STATUS.md', 'results/artifacts/graph.json', 'results/assurance/current.json', 'results/assurance/milestone-9.json', 'results/research/project-review.json')], 'completed_items': ['CVC-4-ADAPTER-REVIEW'], 'next_selected_item': queue['selected_item'], 'next_item_started': False, 'external_research_action': 'NONE', 'delivery': 'Git main commit and scripts/push-main record delivery separately.'}
dump(BASE / 'validation.json', record)
print(json.dumps({'status': 'PASS', 'tests': record['tests'], 'active_seconds': work['active_seconds'], 'next_item': queue['selected_item'], 'next_item_started': False}))
