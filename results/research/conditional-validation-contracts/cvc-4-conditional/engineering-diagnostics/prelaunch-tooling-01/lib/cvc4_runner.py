"""Exact finite CVC-4 observer execution; observations are not semantic authority.

The unchanged supervisor owns process-group cleanup. This module supplies a
single-owner write-ahead ledger, frozen matrix and cumulative engineering time.
Filesystem, OS and committed Python/tooling identities remain trusted.
"""
from datetime import datetime
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time

from lib.cvc_prep import require, safe, bind, committed, lock, read_events, append
from lib.cvc_process import atomic, now, run_process, sha
from lib.cvc_signal_retry import signal_retry

ITEM, RUN = 'CVC-4-CONDITIONAL', 'CVC4-U1-A7-0001'
MANIFEST = 'config/cvc4-u1-a7-0001.json'
OUT = 'results/research/conditional-validation-contracts/cvc-4-conditional/run-0001'
WORK = 'results/research/conditional-validation-contracts/cvc-4-conditional/work-record.json'
LIMITS = {'active_seconds': 16200, 'interval_seconds': 5400,
          'validator_launches': 16, 'launch_seconds': 30,
          'candidate_control_pairs': 4, 'implementation_lineages': 2,
          'setup_builds': 0, 'research_network_requests': 0}
CODE = sorted(['lib/cvc4_runner.py', 'tests/test_cvc4_runner.py',
               'scripts/run-cvc4-observers', 'lib/cvc_prep.py',
               'lib/cvc_process.py', 'lib/cvc_signal_retry.py'])


def load(path):
    return json.loads(Path(path).read_text())


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def stamp():
    return {'at': now(), 'monotonic': time.monotonic()}


def elapsed(start, end):
    require(finite(start.get('monotonic')) and finite(end.get('monotonic')), 'invalid monotonic clock')
    a, b = datetime.fromisoformat(start['at']), datetime.fromisoformat(end['at'])
    require(a.tzinfo is not None and b.tzinfo is not None, 'naive accounting clock')
    wall, mono = (b - a).total_seconds(), end['monotonic'] - start['monotonic']
    require(finite(wall) and finite(mono), 'clock rollback/reboot or invalid work charge')
    return max(wall, mono)


def work_total(work, current, enforce=False):
    intervals = work['intervals']
    require(isinstance(intervals, list) and intervals, 'missing engineering intervals')
    total = 0.
    for number, row in enumerate(intervals, 1):
        require(row['number'] == number, 'work interval number reset')
        if number > 1:
            previous = intervals[number - 2]
            require(previous.get('end') is not None, 'overlapping work intervals')
            elapsed(previous['end'], row['start'])
        closed = row.get('end') is not None
        require(closed or number == len(intervals), 'nonfinal open work interval')
        charge = elapsed(row['start'], row['end'] if closed else current)
        if closed:
            require(finite(row.get('charged_seconds')) and row['charged_seconds'] == charge,
                    'closed work charge changed')
        if enforce:
            require(charge <= LIMITS['interval_seconds'], 'work interval cap exceeded')
        total += charge
    if enforce:
        require(total <= LIMITS['active_seconds'], 'cumulative engineering cap exceeded')
    return total


def work_snapshot(root, current, require_open=True):
    work = load(safe(root, WORK))
    require(work['item_id'] == ITEM and work['limits'] == LIMITS, 'work identity or limits changed')
    require(not require_open or (work['status'] == 'ACTIVE' and work['intervals'][-1].get('end') is None),
            'launch requires an active work interval')
    snapshot = {'intervals': work['intervals']}
    work_total(snapshot, current, enforce=require_open)
    closed = sum(r['charged_seconds'] for r in snapshot['intervals'] if r.get('end') is not None)
    require(work['active_seconds_closed'] == closed, 'closed cumulative work differs')
    return snapshot


def work_continuation(previous, current, previous_time, current_time):
    old, new = previous['intervals'], current['intervals']
    require(len(new) >= len(old), 'engineering intervals truncated')
    elapsed(previous_time, current_time)
    for index, row in enumerate(old):
        require(row['number'] == new[index]['number'] and row['start'] == new[index]['start'],
                'engineering start changed')
        if row.get('end') is not None:
            require(row == new[index], 'closed engineering interval changed')
        elif new[index].get('end') is not None:
            elapsed(previous_time, new[index]['end'])
    require(work_total(current, current_time) >= work_total(previous, previous_time),
            'previously observed engineering work erased')


def file_receipt(root, path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'missing or symlink receipt')
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def verify_receipt(root, row):
    require(set(row) == {'path', 'bytes', 'sha256'} and type(row['bytes']) is int, 'invalid receipt')
    require(file_receipt(root, safe(root, row['path'])) == row, 'retained receipt changed: ' + row['path'])


def payload_path(root, name):
    path = Path(name)
    if not path.is_absolute():
        return safe(root, name)
    require(path.resolve() == path and path.is_file(), 'payload must have a canonical regular path')
    return path


def validate_manifest(root, require_commit=False, require_payloads=True):
    root = Path(root).resolve()
    m = load(safe(root, MANIFEST))
    fields = {'schema_version', 'item_id', 'run_id', 'run_directory', 'work_record', 'limits',
              'fixed_inputs', 'payloads', 'tooling_inputs', 'validation_record', 'work_baseline', 'cells'}
    require(set(m) == fields and m['schema_version'] == 1 and m['item_id'] == ITEM
            and m['run_id'] == RUN and m['run_directory'] == OUT and m['work_record'] == WORK,
            'wrong fixed observer manifest')
    require(m['limits'] == LIMITS, 'fixed observer ceilings changed')
    require([r['path'] for r in m['tooling_inputs']] == CODE, 'exact tooling inventory required')
    tracked = m['fixed_inputs'] + m['tooling_inputs'] + [m['validation_record'], m['work_baseline']]
    require(m['fixed_inputs'] and len({r['path'] for r in tracked}) == len(tracked), 'missing/duplicate binding')
    for row in tracked:
        bind(root, row)
        if require_commit:
            committed(root, row['path'])
    require(m['work_baseline']['path'] != WORK, 'work baseline must be a separate immutable snapshot')
    payloads = m['payloads']
    require(payloads and len({r['path'] for r in payloads}) == len(payloads), 'missing/duplicate runtime payload')
    for row in payloads:
        require(set(row) == {'path', 'sha256'} and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'invalid payload binding')
        if require_payloads:
            require(sha(payload_path(root, row['path'])) == row['sha256'], 'runtime payload changed: ' + row['path'])
    executables = {str(Path(r['path']) if Path(r['path']).is_absolute() else root / r['path']) for r in payloads}
    bound_files = executables | {str(root / r['path']) for r in tracked}
    cells = m['cells']
    require(isinstance(cells, list) and 1 <= len(cells) <= LIMITS['validator_launches'], 'finite launch cap')
    require(len({r['id'] for r in cells}) == len(cells), 'duplicate matrix cell')
    require(len({r['pair_id'] for r in cells}) <= LIMITS['candidate_control_pairs']
            and len({r['implementation'] for r in cells}) <= LIMITS['implementation_lineages'], 'pair/lineage cap')
    combinations = set()
    for cell in cells:
        require(set(cell) == {'id', 'pair_id', 'role', 'implementation', 'argv', 'cwd', 'env', 'expected'},
                'unexpected cell fields')
        require(all(isinstance(cell[k], str) and re.fullmatch(r'[A-Za-z0-9_.-]+', cell[k])
                    for k in ('id', 'pair_id', 'implementation')), 'invalid cell identity')
        require(cell['role'] in ('candidate', 'control'), 'unknown pair role')
        combination = (cell['pair_id'], cell['role'], cell['implementation'])
        require(combination not in combinations, 'duplicate scientific matrix cell')
        combinations.add(combination)
        require(isinstance(cell['argv'], list) and cell['argv'] and
                all(isinstance(s, str) and s and '\0' not in s for s in cell['argv'])
                and cell['argv'][0] in executables, 'exact bound executable and argv required')
        argument_bindings = bound_files if require_payloads else bound_files | {
            str(Path(cell['cwd']) / r['path']) for r in tracked}
        for argument in cell['argv'][1:]:
            require(not Path(argument).is_absolute() or argument in argument_bindings,
                    'absolute argv file is not an exact bound input')
        cwd = Path(cell['cwd'])
        require(cwd.is_absolute() and (not require_payloads or (cwd.resolve() == cwd and cwd.is_dir())),
                'exact canonical cwd required')
        require(isinstance(cell['env'], dict) and all(isinstance(k, str) and isinstance(v, str)
                and k and '=' not in k and '\0' not in k + v for k, v in cell['env'].items()), 'invalid exact environment')
        expected = cell['expected']
        require(set(expected) == {'returncode', 'stdout_pattern', 'stderr_pattern'}
                and type(expected['returncode']) is int and 0 <= expected['returncode'] <= 255,
                'fixed normal-exit hypothesis required')
        require(cell['role'] != 'control' or expected['returncode'] == 0, 'acceptance control must expect zero exit')
        for stream in ('stdout', 'stderr'):
            require(isinstance(expected[stream + '_pattern'], str), 'expected output pattern required')
            re.compile(expected[stream + '_pattern'])
    # A pair cannot silently omit its acceptance control for one implementation.
    for pair, _, implementation in combinations:
        require({(pair, 'candidate', implementation), (pair, 'control', implementation)} <= combinations,
                'candidate/control matrix incomplete')
    seen_controls = set()
    for cell in cells:
        key = (cell['pair_id'], cell['implementation'])
        require(cell['role'] == 'control' or key in seen_controls, 'control must precede its candidate')
        if cell['role'] == 'control':
            seen_controls.add(key)
    checked = load(bind(root, m['validation_record']))
    require(checked['status'] == 'PASS' and checked['returncode'] == 0
            and checked['source_bindings'] == m['tooling_inputs'], 'tooling lacks exact passing tests')
    verify_receipt(root, checked['log'])
    if require_commit:
        committed(root, checked['log']['path'])
        committed(root, MANIFEST)
    return m


def gate(root):
    queue = load(safe(root, 'config/research-queue.json'))
    rows = {r['id']: r for r in queue['items']}
    require(queue['frontier_id'] == 'F-CONDITIONAL-VALIDATION-CONTRACTS'
            and queue['selected_item'] == ITEM and rows[ITEM]['status'] == 'ACTIVE', 'observer item not selected ACTIVE')
    require(rows['CVC-A7-REPAIR-1']['status'] == 'COMPLETE'
            and rows['CVC-A7-REPAIR-1']['closure']['outcome'] == 'SUCCESS', 'checked A7 prerequisite required')
    for path in ('config/research-queue.json', 'docs/RESEARCH_STATUS.md'):
        committed(root, path)


def budget(state, current):
    require(not state['control_stop'] and not state['hypothesis_mismatch'], 'run paused or hypothesis mismatch')
    require(not state['attempts'] or 'terminal' in state['attempts'][-1], 'pending reservation needs reconciliation')
    require(len(state['attempts']) < LIMITS['validator_launches'], 'validator launch cap exhausted')
    require(state['work']['intervals'][-1].get('end') is None, 'no active work interval')
    used = work_total(state['work'], current, enforce=True)
    remaining = min(LIMITS['active_seconds'] - used,
                    LIMITS['interval_seconds'] - elapsed(state['work']['intervals'][-1]['start'], current))
    require(remaining >= LIMITS['launch_seconds'], 'insufficient active budget for fixed 30-second reservation')
    return LIMITS['launch_seconds']


def derive(events):
    require(events and events[0]['kind'] == 'START' and events[0]['run_id'] == RUN, 'missing fixed run start')
    start = events[0]
    state = {'attempts': [], 'control_stop': None, 'hypothesis_mismatch': False,
             'work': start['work'], 'accounted_at': start['time'], 'reconciliations': []}
    work_total(state['work'], state['accounted_at'])
    for event in events[1:]:
        if 'work' in event:
            work_continuation(state['work'], event['work'], state['accounted_at'], event['time'])
            state.update(work=event['work'], accounted_at=event['time'])
        kind, n = event['kind'], event.get('number')
        if kind == 'RESERVED':
            require(type(n) is int and n == len(state['attempts']) + 1, 'reservation count reset')
            require(event['cell']['id'] not in {r['reservation']['cell']['id'] for r in state['attempts']}, 'cell already reserved')
            require(event['reserved_seconds'] == budget(state, event['time']), 'reservation differs from fixed timeout')
            require(event['manifest_sha256'] == start['manifest_sha256'] and event['checkpoint'] == start['checkpoint'],
                    'reservation tooling/manifest changed')
            if event['cell']['role'] == 'candidate':
                cell = event['cell']
                require(any(r['reservation']['cell']['role'] == 'control'
                            and r['reservation']['cell']['pair_id'] == cell['pair_id']
                            and r['reservation']['cell']['implementation'] == cell['implementation']
                            and r['reservation']['cell']['expected']['returncode'] == 0
                            and r.get('terminal', {}).get('hypothesis_matched') is True for r in state['attempts']),
                        'candidate requires its exact successfully accepted control')
            state['attempts'].append({'reservation': event})
        elif kind == 'TERMINAL':
            require(state['attempts'] and n == len(state['attempts']) and 'terminal' not in state['attempts'][-1],
                    'duplicate or unreserved terminal')
            require(event['hypothesis_matched'] is None or type(event['hypothesis_matched']) is bool,
                    'invalid hypothesis comparison')
            require(finite(event.get('charged_seconds')) or
                    (event.get('charged_seconds') is None and event.get('control_error')), 'unknown cost cannot be success')
            require(not event.get('control_error') or event['hypothesis_matched'] is None, 'control error cannot be scientific result')
            state['attempts'][-1]['terminal'] = event
            state['control_stop'] = event.get('control_error')
            state['hypothesis_mismatch'] = event['hypothesis_matched'] is False
        elif kind == 'CONTROL_RECONCILED':
            require(state['control_stop'] and n == len(state['attempts']), 'no control pause to reconcile')
            require(finite(event['known_actual_seconds']) and event['cleanup_completed'] is True,
                    'reconciliation needs known actual cost and cleanup')
            state['reconciliations'].append(event)
            state['control_stop'] = None
        else:
            raise ValueError('unknown ledger event')
    return state


class Ledger:
    """A durable snapshot detects truncation; an appended WAL suffix is recoverable."""
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path, self.snapshot = self.directory / 'events.jsonl', self.directory / 'state.json'

    def _snapshot(self, events):
        atomic(self.snapshot, {'count': len(events), 'tail': events[-1]['event_sha256'], 'state': derive(events)})

    def initialize(self, identity):
        require(not self.path.exists() and not self.snapshot.exists(), 'ledger already initialized')
        append(self.path, {'kind': 'START', **identity})
        self._snapshot(read_events(self.path))

    def read(self):
        require(self.path.is_file() and self.snapshot.is_file(), 'missing accounting cannot reset run')
        events, saved = read_events(self.path), load(self.snapshot)
        n = saved['count']
        require(type(n) is int and 1 <= n <= len(events), 'ledger truncated behind snapshot')
        require(saved['tail'] == events[n - 1]['event_sha256'] and saved['state'] == derive(events[:n]),
                'snapshot or ledger prefix changed')
        state = derive(events)
        if n < len(events):
            self._snapshot(events)
        return events, state

    def add(self, event):
        events, _ = self.read()
        derive(events + [event])
        append(self.path, event)
        self._snapshot(read_events(self.path))


def open_run(root, manifest, create=False):
    directory = safe(root, OUT, False)
    marker = directory / 'start.json'
    ledger = Ledger(directory)
    if not marker.exists() and not ledger.path.exists() and not ledger.snapshot.exists():
        require(create, 'begin-run required; missing accounting cannot restart')
        require({p.name for p in directory.iterdir()} <= {'controller.lock'}, 'unrecognized partial run directory')
        current, baseline = stamp(), load(bind(root, manifest['work_baseline']))
        work = work_snapshot(root, current)
        require(baseline['item_id'] == ITEM and baseline['limits'] == LIMITS, 'wrong baseline work')
        previous_time = baseline['intervals'][-1].get('end') or baseline['intervals'][-1]['start']
        work_continuation({'intervals': baseline['intervals']}, work, previous_time, current)
        identity = {'run_id': RUN, 'manifest_sha256': sha(root / MANIFEST), 'manifest': manifest,
                    'checkpoint': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                    'time': current, 'work': work}
        atomic(marker, identity)
        ledger.initialize(identity)
    else:
        require(not create, 'begin-run cannot reset existing run')
    require(marker.is_file(), 'missing immutable run marker')
    identity = load(marker)
    require(identity['run_id'] == RUN and identity['manifest'] == manifest
            and identity['manifest_sha256'] == sha(root / MANIFEST), 'frozen manifest changed')
    events, state = ledger.read()
    require(all(events[0][k] == v for k, v in identity.items()), 'run marker and ledger differ')
    return ledger, state, identity


def supervisor(root, reservation):
    directory = safe(root, OUT + '/attempts/' + f"{reservation['number']:02d}")
    request, result = load(directory / 'request.json'), load(directory / 'supervisor.json')
    claimed = request.pop('request_sha256')
    cell = reservation['cell']
    require(digest(request) == claimed and result['request_sha256'] == claimed
            and request['argv'] == cell['argv'] and request['cwd'] == cell['cwd'] and request['env'] == cell['env']
            and request['seconds'] == reservation['reserved_seconds']
            and finite(request['deadline_monotonic'])
            and request['monotonic_started'] >= reservation['time']['monotonic']
            and request['deadline_monotonic'] <= reservation['time']['monotonic'] + reservation['reserved_seconds'],
            'supervisor/request identity differs from reservation')
    require(result['status'] in ('COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED')
            and finite(result['charged_seconds']), 'unknown supervisor cost/status')
    require(finite(result['monotonic_started']) and finite(result['monotonic_ended'])
            and result['monotonic_started'] == request['monotonic_started']
            and result['monotonic_ended'] >= result['monotonic_started'] + result['charged_seconds'],
            'supervisor timing differs')
    receipts = []
    for stream in ('stdout', 'stderr'):
        path = directory / stream
        require(path.is_file() and sha(path) == result[stream + '_sha256'], 'raw output missing/changed')
        receipts.append(file_receipt(root, path))
    receipts.extend(file_receipt(root, directory / name) for name in ('request.json', 'supervisor.json'))
    return result, receipts


def verify_attempts(root, state, identity):
    for row in state['attempts']:
        reservation = row['reservation']
        require(reservation['cell'] in identity['manifest']['cells'], 'prior matrix invocation changed')
        require(reservation['checkpoint'] == identity['checkpoint'], 'prior tooling checkpoint changed')
        terminal = row.get('terminal')
        if terminal:
            for receipt in terminal['receipts']:
                verify_receipt(root, receipt)
            if terminal['hypothesis_matched'] is not None:
                result, receipts = supervisor(root, reservation)
                require(receipts == terminal['receipts'] and result['charged_seconds'] == terminal['charged_seconds'],
                        'terminal receipt differs from exact supervisor evidence')
                require(compare(root, reservation, result) == terminal['hypothesis_matched'], 'retained comparison changed')
    for event in state['reconciliations']:
        for receipt in event['receipts']:
            verify_receipt(root, receipt)
    attempts = root / OUT / 'attempts'
    expected = {f"{r['reservation']['number']:02d}" for r in state['attempts']}
    if attempts.exists():
        require({p.name for p in attempts.iterdir()} <= expected, 'unrecorded attempt directory')


def compare(root, reservation, result):
    require(result.get('cleanup_completed') is True and result.get('deadline_exceeded') is False
            and result['status'] in ('COMPLETE', 'FAILED') and not result.get('error')
            and type(result.get('returncode')) is int and result['returncode'] >= 0
            and result['charged_seconds'] <= reservation['reserved_seconds'], 'process/control failure pauses launches')
    directory = root / OUT / 'attempts' / f"{reservation['number']:02d}"
    expected = reservation['cell']['expected']
    return result['returncode'] == expected['returncode'] and all(
        re.fullmatch(expected[stream + '_pattern'], (directory / stream).read_text()) is not None
        for stream in ('stdout', 'stderr'))


def execute(root, action='attempt', cell_id=None):
    root = Path(root).resolve()
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        gate(root)
        manifest = validate_manifest(root, True)
        ledger, state, identity = open_run(root, manifest, create=action == 'begin-run')
        verify_attempts(root, state, identity)
        if action == 'begin-run':
            return state
        require(not state['attempts'] or 'terminal' in state['attempts'][-1], 'pending reservation requires explicit reconciliation')
        remaining = [c for c in manifest['cells'] if c['id'] not in {r['reservation']['cell']['id'] for r in state['attempts']}]
        require(cell_id is None or (remaining and cell_id == remaining[0]['id']), 'cell already used or out of fixed order')
        require(remaining, 'fixed comparison finished; terminal replay refused')
        for cell in remaining:
            gate(root)
            require(validate_manifest(root, True) == manifest, 'manifest changed before launch')
            verify_attempts(root, state, identity)
            current, work = stamp(), None
            work = work_snapshot(root, current)
            work_continuation(state['work'], work, state['accounted_at'], current)
            state.update(work=work, accounted_at=current)
            seconds = budget(state, current)
            if action == 'preflight':
                return state
            n = len(state['attempts']) + 1
            reserved = {'kind': 'RESERVED', 'number': n, 'cell': cell, 'time': current, 'work': work,
                        'reserved_seconds': seconds, 'manifest_sha256': identity['manifest_sha256'],
                        'checkpoint': identity['checkpoint'], 'active_seconds_before': work_total(work, current)}
            ledger.add(reserved)
            state = ledger.read()[1]
            directory = safe(root, OUT + '/attempts/' + f'{n:02d}', False)
            terminal = {'kind': 'TERMINAL', 'number': n, 'hypothesis_matched': None,
                        'charged_seconds': None, 'receipts': []}
            try:
                directory.mkdir(parents=True)
                with signal_retry():
                    result = run_process(cell['argv'], cell['cwd'], cell['env'], directory, seconds,
                                         deadline_monotonic=current['monotonic'] + seconds)
                recorded, terminal['receipts'] = supervisor(root, reserved)
                require(recorded == result, 'returned and durable supervisor receipts differ')
                terminal['charged_seconds'] = result['charged_seconds']
                terminal['process_status'] = result['status']
                terminal['returncode'] = result['returncode']
                terminal['hypothesis_matched'] = compare(root, reserved, result)
                require(validate_manifest(root, True) == manifest, 'bound input changed during launch')
                verify_attempts(root, state, identity)
            except (OSError, ValueError, UnicodeError, KeyError, TypeError) as error:
                terminal.update(control_error=str(error), hypothesis_matched=None)
                if directory.exists():
                    terminal['receipts'] = [file_receipt(root, p) for p in sorted(directory.iterdir())
                                            if p.is_file() and not p.is_symlink()]
            terminal['time'] = stamp()
            # Keep the last valid snapshot if live accounting was damaged; the
            # failure itself must still acquire a durable terminal receipt.
            try:
                terminal['work'] = work_snapshot(root, terminal['time'], require_open=False)
                work_continuation(work, terminal['work'], current, terminal['time'])
                work_total(terminal['work'], terminal['time'], enforce=True)
            except (OSError, ValueError, KeyError, TypeError) as error:
                terminal['work'] = work
                terminal.update(control_error='work accounting failure: ' + str(error), hypothesis_matched=None)
            ledger.add(terminal)
            state = ledger.read()[1]
            if action != 'run' or state['control_stop'] or state['hypothesis_mismatch']:
                return state
        return state
    finally:
        owner.close()


def reconcile_control(root):
    """Retain a failed cell and clear its pause only with exact known cleanup/cost."""
    root = Path(root).resolve()
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        gate(root)
        manifest = validate_manifest(root, True)
        ledger, state, identity = open_run(root, manifest)
        verify_attempts(root, state, identity)
        require(state['attempts'], 'no reservation to reconcile')
        row = state['attempts'][-1]
        require(state['control_stop'] or 'terminal' not in row, 'no control pause or pending reservation')
        result, receipts = supervisor(root, row['reservation'])
        require(result['cleanup_completed'] is True, 'cleanup remains unverified')
        current, work = stamp(), None
        work = work_snapshot(root, current)
        work_continuation(state['work'], work, state['accounted_at'], current)
        if 'terminal' not in row:
            ledger.add({'kind': 'TERMINAL', 'number': row['reservation']['number'], 'time': current, 'work': work,
                        'hypothesis_matched': None, 'charged_seconds': result['charged_seconds'], 'receipts': receipts,
                        'control_error': 'controller lost before terminal; failed cell retained, never replayed'})
        ledger.add({'kind': 'CONTROL_RECONCILED', 'number': row['reservation']['number'], 'time': current, 'work': work,
                    'known_actual_seconds': result['charged_seconds'], 'cleanup_completed': True, 'receipts': receipts})
        return ledger.read()[1]
    finally:
        owner.close()


def validate_run(root, require_payloads=True):
    """Read-only closure replay; no active frontier or latest-HEAD requirement.

The committed checkpoint binds the manifest, tooling and passing test bytes.
Missing ignored runtimes may be explicitly excluded from clone-safe replay;
this exclusion permits evidence inspection, never another observer launch.
"""
    root = Path(root).resolve()
    manifest = validate_manifest(root, require_payloads=require_payloads)
    marker = load(safe(root, OUT + '/start.json'))
    require(marker['manifest'] == manifest and marker['manifest_sha256'] == sha(root / MANIFEST)
            and marker['run_id'] == RUN and re.fullmatch('[0-9a-f]{40}', marker['checkpoint']), 'run identity changed')
    checked = load(bind(root, manifest['validation_record']))
    paths = [MANIFEST, checked['log']['path']] + [r['path'] for r in
            manifest['fixed_inputs'] + manifest['tooling_inputs'] + [manifest['validation_record'], manifest['work_baseline']]]
    for path in paths:
        original = subprocess.check_output(['git', 'show', marker['checkpoint'] + ':' + path],
                                           cwd=root, stderr=subprocess.DEVNULL)
        require(original == safe(root, path).read_bytes(), 'bound checkpoint file differs: ' + path)
    ledger = Ledger(safe(root, OUT))
    # Closure never repairs a stale snapshot. The owner must first reconcile
    # an interrupted write using the operational entry point under its lock.
    events, snapshot = read_events(ledger.path), load(ledger.snapshot)
    require(events and snapshot['count'] == len(events) and snapshot['tail'] == events[-1]['event_sha256']
            and snapshot['state'] == derive(events), 'unreconciled or changed ledger snapshot')
    require(all(events[0][k] == v for k, v in marker.items()), 'initial run identity differs')
    state = derive(events)
    verify_attempts(root, state, marker)
    current = stamp()
    work = work_snapshot(root, current, require_open=False)
    work_continuation(state['work'], work, state['accounted_at'], current)
    attempts = state['attempts']
    reconciled = {r['number']: r['known_actual_seconds'] for r in state['reconciliations']}
    costs = [r.get('terminal', {}).get('charged_seconds', reconciled.get(r['reservation']['number'])) for r in attempts]
    costs = [c if c is not None else reconciled.get(r['reservation']['number']) for c, r in zip(costs, attempts)]
    return {**state, 'manifest': manifest, 'checkpoint': marker['checkpoint'], 'launch_count': len(attempts),
            'known_process_seconds': sum(costs) if all(finite(c) for c in costs) else None,
            'active_seconds': work_total(work, current), 'pending': bool(attempts and 'terminal' not in attempts[-1]),
            'matrix_complete': len(attempts) == len(manifest['cells']) and all('terminal' in r for r in attempts),
            'hypotheses_all_matched': len(attempts) == len(manifest['cells']) and
                all(r.get('terminal', {}).get('hypothesis_matched') is True for r in attempts)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify-inputs', 'begin-run', 'preflight', 'attempt', 'run', 'reconcile-control'))
    parser.add_argument('--cell', help='must identify the next unused fixed matrix cell')
    args = parser.parse_args(argv)
    require(args.cell is None or args.action == 'attempt', '--cell is only valid for one attempt')
    root = Path(__file__).resolve().parents[1]
    if args.action == 'verify-inputs':
        validate_manifest(root)
        print('PASS: exact finite observer inputs and tested tooling; zero launches')
        return 0
    state = reconcile_control(root) if args.action == 'reconcile-control' else execute(root, args.action, args.cell)
    print(json.dumps(state, indent=2))
    return int(bool(state['control_stop'] or state['hypothesis_mismatch']))
