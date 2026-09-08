"""Close one planning item, preserving exact validation and paired-clock costs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
ITEM = ROOT / 'results/research/alt-survivors-2026-09-08'
sys.path.insert(0, str(ROOT))
from lib.research_queue_v2 import load_queue


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def binding(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def checks(last):
    rows = []
    for number in range(1, last + 1):
        candidates = [p for p in BASE.glob(f'{number:02d}-*.json')
                      if not p.stem.endswith('-start') and 'fixture-reservation' not in p.name]
        assert len(candidates) == 1, (number, candidates)
        p = candidates[0]; r = read(p)
        assert r['status'] == 'PASS' and r['returncode'] == 0 and r['tested_inputs_unchanged'], p
        assert r.get('fixtures_reconciled', True), p
        assert binding(ROOT / r['log']['path']) == r['log'], 'raw log drift'
        rows.append({'label': p.stem, 'receipt': binding(p), 'command': r['command'],
                     'elapsed_seconds': r['elapsed_seconds']})
    for name in ('closure-code-bindings.json', 'closure-decision-bindings.json'):
        for r in read(BASE / name):
            assert binding(ROOT / r['path']) == r, 'changed closure input: ' + r['path']
    return rows


def stamp():
    return datetime.now(timezone.utc).isoformat(), time.monotonic()


def close_work():
    checks(9)
    work = read(ITEM / 'work-record.json')
    assert work['status'] == 'ACTIVE'
    utc, mono = stamp()
    interval = work['intervals'][-1]
    wall = (datetime.fromisoformat(utc) - datetime.fromisoformat(interval['start_utc'])).total_seconds()
    elapsed = mono - interval['start_monotonic']
    assert wall >= 0 and elapsed >= 0 and abs(wall - elapsed) < 2
    interval.update(end_utc=utc, end_monotonic=mono, active_seconds=max(wall, elapsed))
    work.update(status='COMPLETE', active_seconds=sum(r['active_seconds'] for r in work['intervals']),
                research_counts=read(ITEM / 'result.json')['research_counts'],
                administrative_tail=str((BASE / 'administrative-tail.json').relative_to(ROOT)),
                accounting_note='Paired primary interval includes candidate analysis, delegated support, engineering and required closure tests. Final state generation and verification are charged to the same cap through the administrative tail. Parallel support is contained in the primary interval. Git delivery follows technical closure.')
    assert work['active_seconds'] <= 5400
    dump(ITEM / 'work-record.json', work)
    dump(BASE / 'administrative-tail.json', {'item_id': 'ALT-SURVIVORS', 'status': 'ACTIVE',
         'start_utc': utc, 'start_monotonic': mono, 'end_utc': None, 'end_monotonic': None,
         'active_seconds': None, 'combined_limit_seconds': 5400})
    print('Primary work closed; final administrative interval remains charged to the same item.')


def finish():
    rows = checks(15)
    assert not (BASE / 'validation.json').exists(), 'never overwrite closure'
    queue = load_queue(ROOT)
    assert queue['selected_item'] == 'SURVIVOR-LET-REUSE-1' and queue['handoff']['status'] == 'PAUSED'
    selected = next(i for i in queue['items'] if i['id'] == queue['selected_item'])
    assert selected['status'] == 'WAITING' and selected['closure'] is None
    item = next(i for i in queue['items'] if i['id'] == 'ALT-SURVIVORS')
    assert item['status'] == 'COMPLETE' and item['closure']['outcome'] == 'SUCCESS'
    review = read(ROOT / 'results/research/queue-reviews/2026-09-08-alt-survivors.json')
    assert review['after']['ordering'] == [i['id'] for i in queue['items']]
    assert review['completed_items'] == ['ALT-SURVIVORS'] and review['next_item_started'] is False
    old = read(ITEM / 'entry-snapshot/config/research-queue.json')
    for original in old['items']:
        if original['id'] in ('ALT-SURVIVORS', 'CVC-NEXT-AUTHORIZATION'):
            continue
        current = next(i for i in queue['items'] if i['id'] == original['id'])
        assert {k: v for k, v in original.items() if k != 'priority'} == {
            k: v for k, v in current.items() if k != 'priority'}, original['id']
    log = (BASE / '06-full-suite.log').read_text()
    counts = [int(n) for n in re.findall(r'^Ran (\d+) tests? in ', log, re.M)]
    assert len(counts) == 2 and len(re.findall(r'^OK$', log, re.M)) == 2
    assert not re.search(r'^FAILED|\bskipped=', log, re.M)
    assert 'test_m8_current_catalog_transition_leaves_historical_attestations_unchanged' in log
    assert 'test_m10_to_successor_transition_preserves_protocol_history' in log
    fixtures = read(BASE / '06-full-suite.json')
    assert fixtures['fixtures_reconciled'] and fixtures['reserved_launches'] == 23
    assert read(BASE / 'current-state/result.json')['status'] == 'COMPLETE'
    work, tail = read(ITEM / 'work-record.json'), read(BASE / 'administrative-tail.json')
    assert work['status'] == 'COMPLETE' and tail['status'] == 'ACTIVE'
    utc, mono = stamp()
    wall = (datetime.fromisoformat(utc) - datetime.fromisoformat(tail['start_utc'])).total_seconds()
    elapsed = mono - tail['start_monotonic']
    assert min(wall, elapsed) >= 0 and abs(wall - elapsed) < 2
    tail.update(status='COMPLETE', end_utc=utc, end_monotonic=mono, active_seconds=max(wall, elapsed))
    total = work['active_seconds'] + tail['active_seconds']
    assert total <= 5400
    dump(BASE / 'administrative-tail.json', tail)
    state_paths = ['config/research-queue.json', 'docs/RESEARCH_STATUS.md',
                   'docs/research/SURVIVOR_TRIAGE_PROPOSAL_PLAN.md', 'docs/PROJECT_REVIEW.md',
                   'results/research/project-review.json', 'results/artifacts/graph.json',
                   'results/assurance/current.json', 'docs/PUBLIC_STATUS.md']
    result = {'schema_version': 1, 'item_id': 'ALT-SURVIVORS', 'outcome': 'SUCCESS', 'status': 'PASS',
        'completed_at': utc, 'checks': rows,
        'test_counts': {'current': counts[0], 'unchanged_historical': counts[1], 'total': sum(counts), 'skipped': 0},
        'fixture_accounting': {'reserved_launches': 23, 'reserved_seconds': 115,
            'known_instrumented_charge_seconds': fixtures['known_instrumented_charge_seconds'],
            'reconciled': True, 'allocation': binding(BASE / 'administrative-fixture-allocation.json'),
            'historical_unknown_costs': 'Unchanged; never reinterpreted as zero.'},
        'active_accounting': {'primary_seconds': work['active_seconds'],
            'administrative_tail_seconds': tail['active_seconds'], 'combined_seconds': total,
            'limit_seconds': 5400, 'work_record': binding(ITEM / 'work-record.json'),
            'administrative_tail': binding(BASE / 'administrative-tail.json')},
        'state_bindings': [binding(ROOT / p) for p in state_paths],
        'proposal_bindings': [binding(p) for p in sorted(ITEM.iterdir()) if p.is_file()],
        'completed_items': ['ALT-SURVIVORS'], 'next_item': 'SURVIVOR-LET-REUSE-1',
        'next_item_status': 'WAITING', 'next_item_started': False, 'queue_execution': 'PAUSED',
        'research_counts': read(ITEM / 'result.json')['research_counts'],
        'delivery': 'Main-only commit and scripts/push-main verify delivery separately.'}
    dump(BASE / 'validation.json', result)
    print(json.dumps({'status': 'PASS', 'tests': sum(counts), 'active_seconds': total,
                      'next_item': 'SURVIVOR-LET-REUSE-1 (WAITING; PAUSED)'}))


if __name__ == '__main__':
    if sys.argv[1:] == ['close-work']:
        close_work()
    elif sys.argv[1:] == ['finish']:
        finish()
    else:
        raise SystemExit('use close-work or finish')
