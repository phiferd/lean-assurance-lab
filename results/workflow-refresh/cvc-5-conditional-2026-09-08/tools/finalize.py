"""Finalize exact closure checks and all active work without a hash/time cycle."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
ITEM = ROOT / 'results/research/conditional-validation-contracts/cvc-5-conditional'
sys.path.insert(0, str(ROOT))
from lib.cvc5_package import binding, validate
from lib.research_queue_v2 import load_queue


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def bound(path):
    return binding(ROOT, path.relative_to(ROOT))


def checks(last):
    rows = []
    for number in range(1, last + 1):
        candidates = [p for p in BASE.glob(f'{number:02d}-*.json')
                      if not p.stem.endswith('-start') and 'fixture-reservation' not in p.name]
        assert len(candidates) == 1, (number, candidates)
        path = candidates[0]; row = json.loads(path.read_text())
        assert row['status'] == 'PASS' and row['returncode'] == 0 and row['tested_inputs_unchanged'], path
        assert bound(ROOT / row['log']['path']) == row['log'], 'changed raw log'
        assert row.get('fixtures_reconciled', True), 'unreconciled fixtures'
        rows.append({'label': path.stem, 'receipt': bound(path), 'command': row['command'],
                     'elapsed_seconds': row['elapsed_seconds']})
    for name in ('closure-code-bindings.json', 'closure-decision-bindings.json'):
        for row in json.loads((BASE / name).read_text()):
            assert bound(ROOT / row['path']) == row, 'bound input changed: ' + row['path']
    return rows


if sys.argv[1] == 'close-work':
    checks(15)
    work = json.loads((ITEM / 'work-record.json').read_text())
    assert work['status'] == 'ACTIVE'
    now, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    interval = work['intervals'][-1]
    interval.update(end_utc=now, end_monotonic=tick, active_seconds=tick-interval['start_monotonic'])
    work.update(status='COMPLETE', active_seconds=sum(r['active_seconds'] for r in work['intervals']),
                administrative_tail=str((BASE / 'administrative-tail.json').relative_to(ROOT)),
                accounting_note='Primary interval includes all research support, engineering, diagnosis and full closure tests. Final generation/verification uses the paired administrative tail, added by validation.json and enforced against the same 3600-second cap. Concurrent delegated time is included in elapsed parent work. Repository commit/push is delivery after technical closure.')
    assert work['active_seconds'] < 3600
    dump(ITEM / 'work-record.json', work)
    dump(BASE / 'administrative-tail.json', {'item_id': 'CVC-5-CONDITIONAL', 'status': 'ACTIVE',
         'start_utc': now, 'start_monotonic': tick, 'end_utc': None, 'end_monotonic': None,
         'active_seconds': None, 'maximum_combined_active_seconds': 3600,
         'reason': 'Final canonical generation and verification after closing the project-review-bound primary record; charged to the same item.'})
    print('Primary work closed; final administration remains on the same cumulative clock.')
elif sys.argv[1] == 'finish':
    rows = checks(20)
    assert not (BASE / 'validation.json').exists(), 'closure cannot be overwritten'
    package = validate(ROOT)
    queue = load_queue(ROOT)
    assert queue['selected_item'] == 'CVC-NEXT-AUTHORIZATION' and queue['handoff']['status'] == 'PAUSED'
    assert not any(i['status'] in ('READY', 'ACTIVE') for i in queue['items'])
    next_item = next(i for i in queue['items'] if i['id'] == queue['selected_item'])
    assert next_item['status'] == 'WAITING' and next_item['closure'] is None
    review = json.loads((ROOT / 'results/research/queue-reviews/2026-09-08-cvc-5-conditional.json').read_text())
    assert review['after']['ordering'] == [i['id'] for i in queue['items']]
    assert review['completed_items'] == ['CVC-5-CONDITIONAL'] and review['next_item_started'] is False
    for ident, dependency in [('CVC-4', 'CVC-3'), ('CVC-5', 'CVC-4')]:
        old = next(i for i in queue['items'] if i['id'] == ident)
        assert old['status'] == 'PLANNED' and old['depends_on'] == [dependency]
    log = (BASE / '07-full-suite.log').read_text()
    test_counts = [int(n) for n in re.findall(r'^Ran (\d+) tests? in ', log, re.M)]
    assert len(test_counts) == 2 and all(n > 0 for n in test_counts), test_counts
    assert len(re.findall(r'^OK$', log, re.M)) == 2 and not re.search(r'^FAILED|\bskipped=', log, re.M)
    assert 'test_m8_current_catalog_transition_leaves_historical_attestations_unchanged' in log
    assert 'test_m10_to_successor_transition_preserves_protocol_history' in log
    fixtures = json.loads((BASE / '07-full-suite.json').read_text())
    assert fixtures['fixtures_reconciled'] and fixtures['reserved_launches'] == 23
    assert fixtures['known_instrumented_charge_seconds'] <= 115
    refresh = json.loads((BASE / 'current-state/result.json').read_text())
    assert refresh['status'] == 'COMPLETE' and all(r['returncode'] == 0 for r in refresh['completed_commands'])
    for rel in ('lib/research_queue.py', 'tests/test_research_queue.py'):
        original = subprocess.check_output(['git', 'show', f"{json.loads((ITEM/'work-record.json').read_text())['base_commit']}:{rel}"], cwd=ROOT)
        assert (ROOT / rel).read_bytes() == original, 'v1 historical binding changed'
    # Resolve every actual package document link after the pending validation file is created.
    for target in re.findall(r'\]\(([^)]+)\)', (ITEM / 'README.md').read_text()):
        if target.endswith('/validation.json'):
            continue
        assert (ITEM / target).resolve().is_file(), target
    tail = json.loads((BASE / 'administrative-tail.json').read_text())
    assert tail['status'] == 'ACTIVE'
    now, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tail.update(status='COMPLETE', end_utc=now, end_monotonic=tick, active_seconds=tick-tail['start_monotonic'])
    assert abs((datetime.fromisoformat(now)-datetime.fromisoformat(tail['start_utc'])).total_seconds()-tail['active_seconds']) < 2
    total = package['active_seconds'] + tail['active_seconds']
    assert 0 <= total <= 3600, 'item cumulative active cap exceeded'
    dump(BASE / 'administrative-tail.json', tail)
    state_paths = ['config/research-queue.json', 'docs/RESEARCH_STATUS.md', 'docs/RESEARCH_WORKFLOW.md',
        'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md', 'docs/PROJECT_REVIEW.md',
        'docs/PUBLIC_STATUS.md', 'results/research/project-review.json', 'results/artifacts/graph.json',
        'results/assurance/current.json', 'results/assurance/milestone-9.json']
    record = {'schema_version': 1, 'item_id': 'CVC-5-CONDITIONAL', 'outcome': 'SUCCESS', 'status': 'PASS',
        'completed_at': now, 'checks': rows, 'package': package,
        'test_counts': {'current': test_counts[0], 'unchanged_historical': test_counts[1], 'total': sum(test_counts), 'skipped': 0},
        'fixture_accounting': {'reserved_launches': 23, 'reserved_seconds': 115,
            'instrumented_charge_seconds': fixtures['known_instrumented_charge_seconds'],
            'reconciled': True, 'allocation': bound(BASE / 'administrative-fixture-allocation.json'),
            'historical_unknown_costs': 'Unchanged; no unknown historical duration is treated as zero.'},
        'active_accounting': {'primary_seconds': package['active_seconds'], 'administrative_tail_seconds': tail['active_seconds'],
            'combined_seconds': total, 'limit_seconds': 3600, 'work_record': bound(ITEM / 'work-record.json'),
            'administrative_tail': bound(BASE / 'administrative-tail.json')},
        'state_bindings': [binding(ROOT, p) for p in state_paths],
        'package_bindings': [bound(p) for p in sorted(ITEM.iterdir()) if p.is_file()],
        'finalizer': bound(Path(__file__).resolve()),
        'completed_items': ['CVC-5-CONDITIONAL'], 'next_selected_item': 'CVC-NEXT-AUTHORIZATION',
        'next_item_status': 'WAITING', 'next_item_started': False, 'queue_execution': 'PAUSED',
        'readiness_gate': 'Expected refusal confirmed by 15-pause-gate; integrity passing does not authorize execution.',
        'external_research_action': 'NONE', 'delivery': 'main commit and scripts/push-main verify delivery separately.',
        'declaration_test_context': 'Complete current tests and unchanged historical modules ran through the required attested suite; no historical test was reinterpreted against current planning bytes.'}
    dump(BASE / 'validation.json', record)
    print(json.dumps({'status': 'PASS', 'tests': sum(test_counts), 'active_seconds': total, 'next': 'CVC-NEXT-AUTHORIZATION (WAITING; PAUSED)'}))
else:
    raise SystemExit('use close-work or finish')
