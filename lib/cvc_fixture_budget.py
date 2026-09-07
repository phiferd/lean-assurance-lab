"""One launch owner and durable, source-bound inert fixture reservations."""
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import tempfile
import time

from lib.cvc_prep import lock, append, read_events, require
from lib.cvc_process import sha, now, atomic

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['lib/cvc_process.py', 'lib/cvc_runner2.py', 'lib/cvc_runner_audit.py',
           'lib/cvc_fixture_budget.py', 'tests/test_cvc_process.py',
           'tests/test_cvc_runner2.py', 'tests/cvc_runner2_fixture.py']
PLAN = {'test_success_retains_raw_logs_and_guard_receipt': 2,
        'test_failed_start_is_receipted': 2,
        'test_cancellation_reaps_child_without_killing_test_controller': 2,
        'test_timeout_terminates_descendant_group': 3,
        'test_leaf_deadline_is_independent_of_supervisor_timeout': 2,
        'test_controller_sigkill_leaves_supervisor_cleanup_receipt': 4}


def checkpoint(path, events):
    atomic(path.with_suffix('.state.json'), {'count': len(events),
           'tail': events[-1]['event_sha256'] if events else None})


def read_accounting(path):
    marker, snapshot = path.with_suffix('.identity.json'), path.with_suffix('.state.json')
    identity = {'item_id': 'CVC-RUNNER-2', 'process_cap': 80, 'process_seconds_cap': 400,
                'seconds_per_process': 5, 'process_counts': PLAN, 'source_paths': SOURCES}
    if not marker.exists():
        require(not path.exists() and not snapshot.exists() and not (path.parent / 'fixtures').exists(),
                'existing fixture evidence needs explicit conservative binding; cannot reset')
        path.touch(); atomic(marker, identity); checkpoint(path, [])
    require(json.loads(marker.read_text()) == identity and path.is_file() and snapshot.is_file(),
            'missing or changed fixture accounting identity')
    events, saved = read_events(path), json.loads(snapshot.read_text())
    n = saved.get('count')
    require(type(n) is int and 0 <= n <= len(events)
            and saved['tail'] == (events[n-1]['event_sha256'] if n else None), 'fixture ledger truncated or reset')
    totals(events)
    checkpoint(path, events)
    return events


def totals(events):
    pending, count, charged = None, 0, 0.
    for row in events:
        if row['kind'] == 'RESERVED':
            require(pending is None and type(row['processes']) is int and 0 < row['processes'] <= 80,
                    'invalid or orphan fixture reservation')
            require(row['seconds_per_process'] == 5, 'fixture deadline changed')
            require(PLAN.get(row['test'].split('.')[-1]) == row['processes'], 'unbound fixture process count')
            pending = row; count += row['processes']
        elif row['kind'] == 'TERMINAL':
            require(pending is not None and row['number'] == pending['number'], 'unpaired fixture terminal')
            require(row['source_bindings_unchanged'] is True, 'prior fixture source binding violation')
            require(type(row['charged_seconds']) in (int, float) and math.isfinite(row['charged_seconds'])
                    and 0 <= row['charged_seconds'] <= 5 * pending['processes'], 'fixture charge exceeded bound')
            charged += row['charged_seconds']; pending = None
        else:
            raise ValueError('unknown fixture event')
    require(pending is None, 'unreconciled fixture consumes full reservation; investigate before retry')
    return count, charged


@contextmanager
def fixture(test, processes):
    target = os.environ.get('CVC_RUNNER2_FIXTURE_LEDGER')
    temp = tempfile.TemporaryDirectory() if target is None else None
    path = Path(target) if target else Path(temp.name) / 'fixture-ledger.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    owner = lock(path.with_suffix('.lock'))
    try:
        require(PLAN.get(test.split('.')[-1]) == processes, 'fixture must use its fixed maximum process topology')
        events = read_accounting(path)
        count, charged = totals(events)
        extra_path = os.environ.get('CVC_PREP_FIXTURE_LEDGER')
        extra = [] if not extra_path or not Path(extra_path).exists() else [json.loads(x) for x in Path(extra_path).read_text().splitlines()]
        count += sum(r.get('reserved_launches', 0) for r in extra)
        charged += sum(r.get('charged_seconds', 0) for r in extra)
        require(count + processes <= 80 and charged + 5 * processes <= 400, 'fixture cap exhausted')
        identities = [{'path': rel, 'sha256': sha(ROOT / rel)} for rel in SOURCES]
        number = len([row for row in events if row['kind'] == 'RESERVED']) + 1
        directory = path.parent / 'fixtures' / f'{number:02d}'
        require(not directory.exists(), 'fixture directory cannot be replayed')
        append(path, {'kind': 'RESERVED', 'number': number, 'test': test, 'processes': processes,
                      'reserved_process_seconds': 5 * processes,
                      'seconds_per_process': 5, 'at': now(), 'monotonic': time.monotonic(),
                      'bindings': identities})
        checkpoint(path, read_events(path))
        directory.mkdir(parents=True)
        begin, result = time.monotonic(), {'status': 'INTERRUPTED'}
        try:
            yield directory, result
        finally:
            elapsed = time.monotonic() - begin
            unchanged = all(sha(ROOT / row['path']) == row['sha256'] for row in identities)
            files = [{'path': str(p.relative_to(path.parent)), 'sha256': sha(p)} for p in directory.rglob('*') if p.is_file()]
            append(path, {'kind': 'TERMINAL', 'number': number, 'at': now(),
                          'charged_seconds': elapsed * processes, 'wall_seconds': elapsed,
                          'status': result['status'], 'source_bindings_unchanged': unchanged, 'files': files})
            checkpoint(path, read_events(path))
            require(unchanged, 'tested files changed during fixture execution')
            require(elapsed < 5, 'fixture wall bound exceeded')
    finally:
        owner.close()
        if temp:
            temp.cleanup()
