"""Bounded same-item CVC-A7 repair continuation; no configurable launch surface.

Frozen semantics and append-only reservations survive tooling revisions. The
owner's cumulative work intervals include engineering before runner activation.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time
import types

from lib.cvc_prep import require, safe, sha, bind, committed, lock, read_events, append
from lib.cvc_process import atomic, now, run_process, sync_dir
from lib.cvc_runner_audit import generate, TARGETS, NEGATIVE
from lib.cvc_a7_repair_audit import audit, audit_baseline, baseline_source, ScientificMismatch
from lib import cvc_a7_runner as predecessor

RUN = 'CVC3-U1-A7-PROOF-0002'
ITEM = 'CVC-A7-REPAIR-1'
MANIFEST = 'config/cvc-u1-a7-proof-0002.json'
BASE = 'external/cvc3-u1-a7-proof-0002'
OUT = 'results/research/conditional-validation-contracts/cvc-a7-repair-1/run-0002'
WORK = 'results/research/conditional-validation-contracts/cvc-a7-repair-1/work-record.json'
VALIDATION = 'results/research/conditional-validation-contracts/cvc-a7-repair-1/tooling-validation.json'
POLICY = 'config/cvc-a7-repair-policy.json'
PROTOCOL = 'results/research/conditional-validation-contracts/cvc-a7-repair-1/execution-protocol.json'
BASELINE = 'research/conditional-validation-contracts/cvc-a7-repair/Baseline.lean'
AUDIT = 'lib/cvc_a7_repair_audit.py'
SIGNATURE, PREPARATION, PREP_MANIFEST = predecessor.SIGNATURE, predecessor.PREPARATION, predecessor.PREP_MANIFEST
RUNTIME, CLOSURE = predecessor.RUNTIME, predecessor.CLOSURE
ASSUMPTIONS, EXPECTATIONS = predecessor.ASSUMPTIONS, predecessor.EXPECTATIONS
LIMITS = {'active_seconds': 7144.402256750036, 'interval_seconds': 3600,
          'attempts': 4, 'attempt_seconds': 300, 'checker_launches': 0,
          'network_requests': 0, 'dependency_compilations': 0}
FIXED = {**predecessor.FIXED,
         PROTOCOL: '7e1b62d347ee5c3f6a19d6a619f6a87cb908d8525fad9636c3e9af36477b8bb2',
         POLICY: '514fcf97ac4634ec4b303ab51578830ce2f5f302fdb978c03bb4c7d5f5779c28',
         'results/research/conditional-validation-contracts/cvc-3-conditional/result.json':
         'be2321767214d22ceee34e15a15d52f6164cd51f4954c4eda21e09da7309fa33'}
REPAIRABLE = ['lib/cvc_a7_repair_runner.py', AUDIT, BASELINE,
              'tests/test_cvc_a7_repair_runner.py', 'tests/test_cvc_a7_repair_audit.py',
              'scripts/run-cvc-u1-a7-repair', 'scripts/bind-cvc-u1-a7-repair',
              'scripts/render-cvc-a7-repair-baseline']
CODE = sorted(set(predecessor.CODE + REPAIRABLE))


def load(path):
    return json.loads(Path(path).read_text())

def binding(root, relative):
    path = safe(root, relative)
    return {'path': relative, 'sha256': sha(path)}

def receipt(root, path):
    path = Path(path)
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': sha(path)}

def verify_receipt(root, row):
    require(set(row) == {'path', 'bytes', 'sha256'} and type(row['bytes']) is int, 'invalid file receipt')
    p = safe(root, row['path'])
    require(p.is_file() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'],
            'prior receipt changed: ' + row['path'])

def environment(root, runtime):
    return {'LEAN_SYSROOT': runtime,
            'LEAN_PATH': ':'.join([str(Path(root) / BASE),
                                  str(Path(root) / 'external/cvc-u1-dependencies-0002/build/lib/lean'),
                                  runtime + '/lib/lean']),
            'PATH': runtime + '/bin:/usr/bin:/bin', 'LANG': 'C.UTF-8',
            'TMPDIR': str(Path(root) / BASE / 'tmp')}

def stem_for(stage):
    require(stage in ('signature', 'baseline', 'proof'), 'unknown stage')
    return {'signature': 'Contract', 'baseline': 'Baseline', 'proof': 'CVC2Proof'}[stage]

def verify_payloads(root, m):
    from lib.cvc_prep_binding import verify_runtime
    from lib import cvc_prep2 as prep
    verify_runtime(root, load(root / RUNTIME))
    pm = load(root / PREP_MANIFEST)
    modules = {r['module']: r for r in load(root / CLOSURE)['closure']['modules'] if r['kind'] != 'core_runtime'}
    prep.check_sources(root, pm, modules)
    prep.verify_output_set(root, root / pm['materialization']['build_root'], load(root / PREPARATION)['outputs'])
    require(m['compiler'] == load(root / PREP_MANIFEST)['compiler']['path'], 'compiler path changed')

def stamp():
    return {'at': now(), 'monotonic': time.monotonic()}

def elapsed(start, end):
    a, b = datetime.fromisoformat(start['at']), datetime.fromisoformat(end['at'])
    require(a.tzinfo and b.tzinfo, 'naive accounting time')
    wall, mono = (b-a).total_seconds(), end['monotonic'] - start['monotonic']
    require(all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in (wall, mono)),
            'clock rollback, reboot or invalid elapsed evidence')
    return max(wall, mono)

class Ledger:
    """WAL precedes snapshot. A valid suffix recovers a interrupted snapshot.

    Missing snapshot or shortened/replaced prefix fails closed. The workspace
    marker prevents deleting just the accounting directory to reset a run.
    Deliberately replacing all evidence is outside the trusted-filesystem model.
    """
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / 'events.jsonl'
        self.snapshot = self.directory / 'state.json'

    def initialize(self, identity):
        require(not self.path.exists() and not self.snapshot.exists(), 'already initialized')
        self.directory.mkdir(parents=True, exist_ok=True)
        append(self.path, {'kind': 'START', **identity})
        self._snapshot(read_events(self.path))

    def _snapshot(self, events):
        atomic(self.snapshot, {'count': len(events), 'tail': events[-1]['event_sha256'], 'state': derive(events)})

    def read(self):
        require(self.path.is_file() and self.snapshot.is_file(), 'missing accounting cannot reset run')
        events, saved = read_events(self.path), load(self.snapshot)
        n = saved.get('count')
        require(type(n) is int and 1 <= n <= len(events), 'ledger truncated behind snapshot')
        require(saved.get('tail') == events[n-1]['event_sha256']
                and saved.get('state') == derive(events[:n]), 'snapshot or ledger prefix changed')
        state = derive(events)
        if n != len(events):
            self._snapshot(events)
        return events, state

    def add(self, event):
        events, _ = self.read()
        derive(events + [event])
        append(self.path, event)
        self._snapshot(read_events(self.path))

def recover(root, ledger, state):
    if not state['attempts'] or 'terminal' in state['attempts'][-1]:
        return state
    row = state['attempts'][-1]['reservation']
    directory = root / OUT / 'attempts' / f"{row['number']:02d}"
    supervisor = directory / 'supervisor.json'
    term = {'kind': 'TERMINAL', 'number': row['number'], 'status': 'INTERRUPTED',
            'charged_seconds': row['reserved_seconds'], 'orphan': True,
            'reason': 'unreconciled reservation consumes full timeout; never replay',
            'time': stamp(), 'outputs': [], 'raw_files': []}
    if supervisor.exists():
        recovered = load(supervisor)
        request = load(directory / 'request.json')
        request_hash = request.pop('request_sha256')
        require(hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() == request_hash
                and recovered['request_sha256'] == request_hash
                and request['argv'] == row['argv'] and request['cwd'] == row['cwd'] and request['env'] == row['env']
                and request['seconds'] == row['reserved_seconds']
                and request['deadline_monotonic'] <= row['time']['monotonic'] + row['reserved_seconds'],
                'orphan supervisor identity changed')
        require(recovered['charged_seconds'] >= 0 and math.isfinite(recovered['charged_seconds']), 'invalid orphan receipt')
        term['charged_seconds'] = max(term['charged_seconds'], recovered['charged_seconds'])
        term['supervisor_receipt'] = receipt(root, supervisor)
        term['cleanup_unverified'] = not recovered['cleanup_completed']
        term['deadline_exceeded'] = recovered.get('deadline_exceeded', False)
        term['raw_files'] = [receipt(root, directory / stream) for stream in ('stdout', 'stderr') if (directory / stream).is_file()]
        for stream in ('stdout', 'stderr'):
            if (directory / stream).exists():
                require(sha(directory / stream) == recovered[stream + '_sha256'], 'orphan raw output changed')
        output_base = directory
        stem = stem_for(row['phase'])
        term['outputs'] = [receipt(root, path) for path in output_base.glob(stem + '.*') if path.suffix != '.lean']
    elif (directory / 'request.json').exists():
        # A supervisor may still be finishing cleanup. Never overlap a new
        # compiler with an unverified process; a later read can reconcile safely.
        require(time.monotonic() > row['time']['monotonic'] + row['reserved_seconds'] + 1,
                'orphan supervisor still inside cleanup bound; do not overlap')
        term['cleanup_unverified'] = True
        term['reason'] = 'supervisor receipt missing after cleanup bound; full charge and persistent launch stop'
        term['raw_files'] = [receipt(root, path) for path in sorted(directory.iterdir()) if path.is_file()]
    ledger.add(term)
    return ledger.read()[1]

def workspace_check(root, state):
    workspace = root / BASE
    outputs = [file['path'].split('/')[-1] for row in state['attempts'] if row['reservation']['phase'] == 'signature'
               for file in row.get('terminal', {}).get('outputs', [])]
    allowed = {'.run.json', 'tmp', 'Contract.lean', 'proof-input.lean', 'CVC2Proof.lean', 'Baseline.lean', *outputs}
    require(all(not p.is_symlink() and p.name in allowed for p in workspace.iterdir()), 'unknown workspace input')
    expected_dirs = {f"{row['reservation']['number']:02d}" for row in state['attempts']}
    attempts = root / OUT / 'attempts'
    require(not attempts.exists() or {p.name for p in attempts.iterdir()} == expected_dirs,
            'unrecorded or missing attempt directory')


def phase(state):
    successful = [row['reservation']['phase'] for row in state['attempts']
                  if row.get('terminal', {}).get('status') == 'COMPLETE']
    return 'signature' if 'signature' not in successful else 'baseline' if 'baseline' not in successful else 'proof'


def build_manifest(root):
    root = Path(root).resolve()
    runtime = load(root / RUNTIME)
    python = Path(os.path.realpath(os.sys.executable))
    compiler = load(root / PREP_MANIFEST)['compiler']['path']
    return {'schema_version': 1, 'run_id': RUN, 'item_id': ITEM,
            'workspace': BASE, 'run_directory': OUT, 'limits': LIMITS,
            'fixed_inputs': [{'path': p, 'sha256': h} for p, h in sorted(FIXED.items())],
            'controller_inputs': [binding(root, p) for p in CODE],
            'compiler': compiler, 'environment': environment(root, runtime['runtime_root']),
            'commands': [{'number': n, 'stages': {stage: commands(root, compiler, n, stage)
                         for stage in ('signature', 'baseline', 'proof')}} for n in range(1, 5)],
            'python': {'path': str(python), 'sha256': sha(python)},
            'work_record': WORK, 'validation_record': VALIDATION,
            'result_modes': {'proof': [{'name': n, 'type': t} for n, t in TARGETS],
                             'counterexample': [{'name': n, 'type': t} for n, t in NEGATIVE]}}


def validate_manifest(root, require_commit=False):
    root = Path(root).resolve()
    m = load(safe(root, MANIFEST))
    expected = build_manifest(root)
    require({k: v for k, v in m.items() if k != 'controller_inputs'} ==
            {k: v for k, v in expected.items() if k != 'controller_inputs'},
            'manifest differs from fixed scientific inputs, commands, limits or runtime')
    require([r['path'] for r in m['controller_inputs']] == CODE, 'initial controller inventory changed')
    for row in m['fixed_inputs'] + [r for r in m['controller_inputs'] if r['path'] not in REPAIRABLE]:
        bind(root, row)
        if require_commit:
            committed(root, row['path'])
    require((root / BASELINE).read_bytes() == baseline_source(load(root / EXPECTATIONS)),
            'baseline must be generated from unchanged reviewed declarations')
    require(load(root / PREPARATION)['outcome'] == 'SUCCESS', 'complete preparation required')
    if require_commit:
        committed(root, MANIFEST)
    return m


def gate(root):
    from lib.research_queue import load_queue
    q = load_queue(root)
    rows = {row['id']: row for row in q['items']}
    require(q['frontier_id'] == 'F-CONDITIONAL-VALIDATION-CONTRACTS'
            and q['selected_item'] == ITEM and rows[ITEM]['status'] == 'ACTIVE',
            'repair item is not selected ACTIVE')
    require(rows['CVC-3-CONDITIONAL']['status'] == 'COMPLETE'
            and rows['CVC-3-CONDITIONAL']['closure']['outcome'] == 'BOUNDED_UNRESOLVED',
            'historical A7 predecessor must remain terminal')
    for key in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2', 'CVC-AXIOMS-1', 'CVC-CONDITIONAL-1'):
        require(rows[key]['status'] == 'COMPLETE' and rows[key]['closure']['outcome'] == 'SUCCESS',
                'unmet successful prerequisite: ' + key)
    for path in ('config/research-queue.json', 'docs/RESEARCH_STATUS.md', POLICY):
        committed(root, path)


def work_total(work, current, enforce_limits=False):
    intervals = work['intervals']
    require(intervals, 'missing engineering accounting interval')
    total = 0.
    for number, interval in enumerate(intervals, 1):
        require(interval['number'] == number, 'work interval number reset')
        if number > 1:
            previous = intervals[number-2]
            require('end' in previous, 'overlapping work intervals')
            elapsed(previous['end'], interval['start'])
        end = interval.get('end', current)
        charge = elapsed(interval['start'], end)
        if enforce_limits:
            require(charge <= LIMITS['interval_seconds'], 'work interval cap exceeded')
        if 'end' in interval:
            require(interval.get('charged_seconds') == charge, 'closed interval charge changed')
        else:
            require(number == len(intervals), 'open nonfinal work interval')
        total += charge
    if enforce_limits:
        require(total <= LIMITS['active_seconds'], 'cumulative active budget exhausted')
    return total


def work_snapshot(root, current, require_open=True):
    record = load(safe(root, WORK))
    require(record['item_id'] == ITEM and record['run_id'] == RUN and record['policy'] == POLICY,
            'wrong work accounting identity')
    require(not require_open or (record['status'] == 'ACTIVE' and 'end' not in record['intervals'][-1]),
            'launch requires active work interval')
    result = {'intervals': record['intervals']}
    work_total(result, current, enforce_limits=require_open)
    require(record['active_seconds_closed'] == sum(i['charged_seconds'] for i in result['intervals'] if 'end' in i),
            'closed cumulative work total changed')
    return result


def work_continuation(previous, current, previous_time=None, current_time=None):
    old, new = previous['intervals'], current['intervals']
    require(len(new) >= len(old), 'work accounting truncated')
    for index, row in enumerate(old):
        require(new[index]['number'] == row['number'] and new[index]['start'] == row['start'],
                'engineering start or interval changed')
        if 'end' in row:
            require(new[index] == row, 'closed engineering interval changed')
        elif 'end' in new[index] and previous_time is not None:
            elapsed(previous_time, new[index]['end'])
    if previous_time is not None and current_time is not None:
        elapsed(previous_time, current_time)
        require(work_total(current, current_time) >= work_total(previous, previous_time),
                'previously observed active work erased')


def active_seconds(state, current):
    return work_total(state['work'], current)


def budget(state, current):
    require(state['outcome'] is None and not state['repair_pause'] and not state['control_stop'],
            'run stopped or awaiting repair/reconciliation')
    require(len(state['attempts']) < LIMITS['attempts'], 'four-build cumulative cap exhausted')
    require(state['revisions'], 'no exact tested tooling revision')
    work = state['work']
    work_total(work, current, enforce_limits=True)
    require('end' not in work['intervals'][-1], 'no active work interval')
    # Unknown orphan duration remains unknown; reserve its full timeout again
    # against remaining active budget rather than recovering a cheap retry.
    unknown = sum(r['reservation']['reserved_seconds'] for r in state['attempts']
                  if r.get('terminal', {}).get('orphan'))
    left = min(float(LIMITS['attempt_seconds']), LIMITS['active_seconds'] - work_total(work, current) - unknown,
               LIMITS['interval_seconds'] - elapsed(work['intervals'][-1]['start'], current))
    require(left > 0, 'active interval or cumulative time exhausted')
    return left


def derive(events):
    require(events and events[0]['kind'] == 'START' and events[0]['run_id'] == RUN,
            'missing fixed repair run start')
    state = {'attempts': [], 'revisions': [], 'outcome': None, 'repair_pause': None,
             'control_stop': None, 'reconciliations': [], 'work': events[0]['work'],
             'accounted_at': events[0]['time']}
    work_total(state['work'], events[0]['time'])
    for event in events[1:]:
        kind = event['kind']
        if 'work' in event:
            work_continuation(state['work'], event['work'], state['accounted_at'], event['time'])
            state['work'] = event['work']
            work_total(state['work'], event['time'])
        if kind == 'TOOLING_REVISION':
            require(state['outcome'] is None and not state['control_stop'], 'revision cannot clear scientific/control stop')
            require(not state['attempts'] or 'terminal' in state['attempts'][-1], 'revision with orphan')
            require(event['number'] == len(state['revisions']) + 1, 'tooling revision number reset')
            require([r['path'] for r in event['inputs']] == CODE, 'tooling inventory differs')
            if state['revisions']:
                require([(r['path'], r['sha256']) for r in event['inputs']] !=
                        [(r['path'], r['sha256']) for r in state['revisions'][-1]['inputs']],
                        'repair requires changed tested tooling bytes')
            state['revisions'].append(event)
            state['repair_pause'] = None
        elif kind == 'RESERVED':
            require(state['outcome'] is None and not state['repair_pause'] and not state['control_stop'],
                    'launch after stop or without repair revision')
            n = len(state['attempts']) + 1
            require(type(event['number']) is int and event['number'] == n <= LIMITS['attempts'],
                    'attempt count reset or four-build cap exceeded')
            require(not state['attempts'] or 'terminal' in state['attempts'][-1], 'orphan before next launch')
            require(event['phase'] == phase(state), 'signature then clean counted baseline required')
            require(event['mode'] in ('proof', 'counterexample'), 'unknown result mode')
            require(event['tooling_revision'] == len(state['revisions']), 'attempt uses unbound tooling revision')
            require(0 < event['reserved_seconds'] <= budget(state, event['time']), 'reservation exceeds budget')
            state['attempts'].append({'reservation': event})
        elif kind == 'TERMINAL':
            require(state['attempts'] and event['number'] == len(state['attempts'])
                    and 'terminal' not in state['attempts'][-1], 'duplicate or unordered terminal')
            row = state['attempts'][-1]
            require(event['status'] in ('COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED'), 'unknown terminal status')
            cost = event['charged_seconds']
            require(type(cost) in (int, float) and math.isfinite(cost) and cost >= 0, 'invalid process cost')
            if event.get('orphan'):
                require(event['status'] == 'INTERRUPTED' and cost >= row['reservation']['reserved_seconds'],
                        'orphan cannot receive a free retry')
            if event['status'] == 'COMPLETE':
                require(event.get('outputs') and event.get('returncode') == 0, 'success lacks compiled evidence')
            if event.get('baseline_audit'):
                require(row['reservation']['phase'] == 'baseline' and event['status'] == 'COMPLETE',
                        'audit outside successful baseline')
            if row['reservation']['phase'] == 'baseline' and event['status'] == 'COMPLETE':
                require(event.get('baseline_audit'), 'clean baseline audit required')
            row['terminal'] = event
            if event.get('result'):
                require(row['reservation']['phase'] == 'proof' and event['status'] == 'COMPLETE'
                        and event['result'] == ('SUCCESS' if row['reservation']['mode'] == 'proof' else 'NEGATIVE')
                        and event.get('axiom_audit'), 'invalid proof outcome')
                state['outcome'] = event['result']
            if event.get('scientific_mismatch'):
                state['outcome'] = 'BOUNDED_UNRESOLVED'
            if event.get('repair_pause'):
                require(event['status'] != 'COMPLETE', 'successful attempt cannot request repair')
                state['repair_pause'] = event['repair_pause']
            if (event.get('orphan') or event.get('cleanup_unverified') or event.get('deadline_exceeded')
                    or event['status'] in ('TIMED_OUT', 'INTERRUPTED') or cost > row['reservation']['reserved_seconds']):
                state['control_stop'] = 'process accounting, deadline or cleanup requires reconciliation'
            if 'work' in event:
                try:
                    work_total(state['work'], event['time'], enforce_limits=True)
                except ValueError:
                    state['control_stop'] = 'active accounting exceeded interval or cumulative bound'
        elif kind == 'CONTROL_RECONCILED':
            require(state['control_stop'] and state['outcome'] is None and state['attempts']
                    and 'terminal' in state['attempts'][-1], 'no reconcilable process pause')
            require(event['number'] == len(state['attempts']) and event['cleanup_completed'] is True
                    and type(event['known_actual_seconds']) in (int, float)
                    and math.isfinite(event['known_actual_seconds']) and event['known_actual_seconds'] >= 0
                    and event.get('supervisor_receipt') and event.get('raw_files')
                    and event.get('request_receipt'), 'incomplete reconciliation evidence')
            work_total(state['work'], event['time'], enforce_limits=True)
            state['reconciliations'].append(event)
            state['control_stop'] = None
        elif kind == 'CONTROL_STOP':
            require(isinstance(event.get('reason'), str) and event['reason'], 'missing control stop reason')
            state['control_stop'] = event['reason']
        else:
            raise ValueError('unknown repair accounting event: ' + str(kind))
        if 'time' in event:
            elapsed(state['accounted_at'], event['time'])
            state['accounted_at'] = event['time']
    return state


def commands(root, compiler, number, stage):
    stem = stem_for(stage)
    target = Path(root) / OUT / 'attempts' / f'{number:02d}' / (stem + '.olean')
    return [compiler, '-o', str(target), stem + '.lean']


def validation(root):
    checked = load(safe(root, VALIDATION))
    require(checked.get('schema_version') == 1 and checked.get('status') == 'PASS'
            and checked.get('returncode') == 0 and isinstance(checked.get('command'), list)
            and checked['command'] and all(isinstance(x, str) and x for x in checked['command']),
            'passing focused-check receipt required')
    require(checked.get('source_bindings') == [binding(root, p) for p in CODE],
            'focused checks do not bind exact tooling source inventory')
    verify_receipt(root, checked['log'])
    for path in CODE:
        committed(root, path)
    committed(root, VALIDATION)
    committed(root, checked['log']['path'])
    return checked


def archive_revision(root, number, current, work):
    checked = validation(root)
    directory = root / OUT / 'tooling' / f'{number:02d}'
    require(not directory.exists(), 'cannot overwrite tooling revision')
    directory.mkdir(parents=True)
    rows = []
    for relative in CODE:
        source = safe(root, relative)
        dest = directory / 'files' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
        rows.append({**binding(root, relative), 'archive': receipt(root, dest)})
    (directory / 'validation.json').write_bytes((root / VALIDATION).read_bytes())
    (directory / 'validation.log').write_bytes(safe(root, checked['log']['path']).read_bytes())
    revision = {'kind': 'TOOLING_REVISION', 'number': number, 'time': current, 'work': work,
                'checkpoint': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'inputs': rows, 'validation': receipt(root, directory / 'validation.json'),
                'log': receipt(root, directory / 'validation.log')}
    sync_dir(directory)
    return revision


def verify_revision(root, revision, live=False):
    require([r['path'] for r in revision['inputs']] == CODE, 'revision inventory changed')
    require(len(revision['checkpoint']) == 40 and all(x in '0123456789abcdef' for x in revision['checkpoint']),
            'invalid revision checkpoint')
    for row in revision['inputs']:
        verify_receipt(root, row['archive'])
        require(row['sha256'] == row['archive']['sha256'], 'archived tooling digest differs')
        original = subprocess.check_output(['git', 'show', revision['checkpoint'] + ':' + row['path']],
                                           cwd=root, stderr=subprocess.DEVNULL)
        require(original == safe(root, row['archive']['path']).read_bytes(),
                'tooling archive differs from its exact Git checkpoint: ' + row['path'])
        if live:
            bind(root, {'path': row['path'], 'sha256': row['sha256']})
            committed(root, row['path'])
    verify_receipt(root, revision['validation']); verify_receipt(root, revision['log'])
    checked = load(safe(root, revision['validation']['path']))
    require(checked['status'] == 'PASS' and checked['returncode'] == 0
            and checked['source_bindings'] == [{'path': r['path'], 'sha256': r['sha256']} for r in revision['inputs']]
            and checked['log']['sha256'] == revision['log']['sha256']
            and checked['log']['bytes'] == revision['log']['bytes'], 'archived test binding changed')


def bound_audit(root, revision):
    # Only new tooling paths can evolve. Imported predecessor dependencies stay
    # fixed by the immutable initial manifest, so original parser replay cannot
    # silently import successor helper semantics.
    verify_revision(root, revision)
    path = next(row['archive']['path'] for row in revision['inputs'] if row['path'] == AUDIT)
    module = types.ModuleType('cvc_bound_audit_' + str(revision['number']))
    exec(compile(safe(root, path).read_bytes(), path, 'exec'), module.__dict__)
    return module


def open_run(root, m, create=False):
    directory, workspace = safe(root, OUT, False), safe(root, BASE, False)
    marker = directory / 'start.json'
    ledger = Ledger(directory / 'execution')
    exists = marker.exists() or ledger.path.exists() or ledger.snapshot.exists() or workspace.exists()
    if not exists:
        require(create, 'begin-run before attempts')
        committed(root, WORK)
        require(not directory.exists() or {p.name for p in directory.iterdir()} <= {'controller.lock'},
                'unrecognized partial run directory')
        current = stamp()
        identity = {'run_id': RUN, 'manifest_sha256': sha(root / MANIFEST), 'time': current,
                    'work': work_snapshot(root, current),
                    'checkpoint': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()}
        directory.mkdir(parents=True, exist_ok=True)
        atomic(marker, identity)
        workspace.mkdir(parents=True)
        atomic(workspace / '.run.json', identity)
        (workspace / 'tmp').mkdir()
        ledger.initialize(identity)
    require(marker.is_file() and (workspace / '.run.json').is_file(), 'partial/missing run identity')
    identity = load(marker)
    require(identity['run_id'] == RUN and identity['manifest_sha256'] == sha(root / MANIFEST)
            and load(workspace / '.run.json') == identity, 'run identity changed')
    events, state = ledger.read()
    require(all(events[0][k] == value for k, value in identity.items()), 'initial ledger identity changed')
    return ledger, state


def adopt_revision(root, initial=False):
    root = Path(root).resolve()
    gate(root); m = validate_manifest(root, True)
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        gate(root); m = validate_manifest(root, True); validation(root)
        ledger, state = open_run(root, m, create=initial)
        state = recover(root, ledger, state)
        require(initial == (not state['revisions']), 'use begin-run only for first tooling binding')
        require(state['outcome'] is None and not state['control_stop'], 'cannot adopt after scientific/control stop')
        verify_attempts(root, state)
        current = stamp(); work = work_snapshot(root, current)
        work_continuation(state['work'], work, state['accounted_at'], current)
        next_inputs = [binding(root, p) for p in CODE]
        if state['revisions']:
            require(next_inputs != [{'path': r['path'], 'sha256': r['sha256']} for r in state['revisions'][-1]['inputs']],
                    'repair checkpoint must change tooling bytes')
        else:
            require(next_inputs == m['controller_inputs'], 'initial tooling differs from manifest')
        revision = archive_revision(root, len(state['revisions']) + 1, current, work)
        ledger.add(revision)
        return ledger.read()[1]
    finally:
        owner.close()


def verify_attempts(root, state):
    m = load(root / MANIFEST)
    for revision in state['revisions']:
        verify_revision(root, revision)
    for reconciliation in state['reconciliations']:
        verify_receipt(root, reconciliation['supervisor_receipt'])
        verify_receipt(root, reconciliation['request_receipt'])
        for file in reconciliation['raw_files']:
            verify_receipt(root, file)
    for row in state['attempts']:
        reserved, term = row['reservation'], row.get('terminal')
        require(reserved['argv'] == commands(root, m['compiler'], reserved['number'], reserved['phase'])
                and reserved['env'] == m['environment'] and reserved['cwd'] == str(root / BASE),
                'prior exact invocation changed')
        revision = state['revisions'][reserved['tooling_revision'] - 1]
        require(reserved['tooling_checkpoint'] == revision['checkpoint'], 'prior checkpoint changed')
        if not term:
            continue
        for file in term.get('raw_files', []) + term.get('outputs', []) + term.get('signature_materialization', []):
            verify_receipt(root, file)
        if term.get('supervisor_receipt'):
            verify_receipt(root, term['supervisor_receipt'])
        directory = root / OUT / 'attempts' / f"{reserved['number']:02d}"
        implementation = directory / 'implementation.lean'
        compiled = directory / (stem_for(reserved['phase']) + '.lean')
        require(term.get('orphan') or (implementation.is_file() and compiled.is_file()),
                'prior exact source or compiler input missing')
        if implementation.exists():
            require(sha(implementation) == reserved['source_sha256'], 'reserved source changed')
        if compiled.exists():
            require(sha(compiled) == reserved['input_sha256'], 'reserved compiler input changed')
        if term.get('baseline_audit'):
            original = bound_audit(root, revision)
            require(compiled.read_bytes() == original.baseline_source(load(root / EXPECTATIONS)),
                    'baseline differs from its original generator and fixed expectations')
            require(term['baseline_audit'] == original.audit_baseline((directory / 'stdout').read_text(),
                    (directory / 'stderr').read_text()), 'prior baseline audit differs under bound tooling')
        if term.get('result'):
            original = bound_audit(root, revision)
            require(generate(implementation.read_text(), reserved['mode']) == compiled.read_bytes(),
                    'generated proof input changed')
            require(term['axiom_audit'] == original.audit((directory / 'stdout').read_text(),
                    (directory / 'stderr').read_text(), load(root / ASSUMPTIONS), reserved['mode']),
                    'prior proof audit differs under bound tooling')
        if reserved['phase'] == 'signature' and term['status'] == 'COMPLETE':
            require(any(r['path'] == BASE + '/Contract.olean' for r in term.get('signature_materialization', [])),
                    'successful signature lacks importable bound output')
            require(sha(root / BASE / 'Contract.lean') == FIXED[SIGNATURE], 'materialized signature changed')


def execute(root, resume=False, mode='proof', preflight=False):
    root = Path(root).resolve()
    gate(root); validate_manifest(root, True)
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        gate(root); m = validate_manifest(root, True)
        ledger, state = open_run(root, m)
        state = recover(root, ledger, state)
        verify_payloads(root, m)
        verify_attempts(root, state); workspace_check(root, state)
        if state['outcome'] is not None or state['control_stop'] or state['repair_pause']:
            return state
        verify_revision(root, state['revisions'][-1], live=True)
        require(resume == bool(state['attempts']), 'use --resume only after a reserved attempt')
        current = stamp(); work = work_snapshot(root, current)
        work_continuation(state['work'], work, state['accounted_at'], current); state['work'] = work
        budget(state, current)
        if preflight:
            return state
        n, current_phase = len(state['attempts']) + 1, phase(state)
        source = root / SIGNATURE if current_phase == 'signature' else root / BASELINE if current_phase == 'baseline' else safe(root, BASE + '/proof-input.lean')
        original = source.read_bytes()
        payload = original if current_phase != 'proof' else generate(original.decode(), mode)
        name = stem_for(current_phase) + '.lean'
        directory = root / OUT / 'attempts' / f'{n:02d}'
        require(not directory.exists(), 'cannot overwrite an attempt')
        current = stamp(); seconds = budget(state, current)
        reserved = {'kind': 'RESERVED', 'number': n, 'phase': current_phase, 'mode': mode,
                    'time': current, 'work': work, 'reserved_seconds': seconds,
                    'argv': commands(root, m['compiler'], n, current_phase), 'cwd': str(root / BASE), 'env': m['environment'],
                    'source_sha256': hashlib.sha256(original).hexdigest(), 'input_sha256': hashlib.sha256(payload).hexdigest(),
                    'manifest_sha256': sha(root / MANIFEST), 'tooling_revision': len(state['revisions']),
                    'tooling_checkpoint': state['revisions'][-1]['checkpoint'],
                    'remaining_attempts_after_reservation': LIMITS['attempts'] - n,
                    'active_seconds_before': active_seconds(state, current)}
        ledger.add(reserved)
        term = {'kind': 'TERMINAL', 'number': n, 'status': 'FAILED', 'charged_seconds': seconds,
                'outputs': [], 'raw_files': []}
        stage = 'materialize'
        try:
            directory.mkdir(parents=True)
            (directory / 'implementation.lean').write_bytes(original)
            (directory / name).write_bytes(payload)
            (root / BASE / name).write_bytes(payload)
            require(source.read_bytes() == original, 'source changed before launch')
            sync_dir(directory)
            stage = 'process'
            proc = run_process(reserved['argv'], root / BASE, m['environment'], directory, seconds,
                               deadline_monotonic=current['monotonic'] + seconds)
            term.update(proc)
            term['supervisor_receipt'] = receipt(root, directory / 'supervisor.json')
            term['raw_files'] = [receipt(root, p) for p in sorted(directory.iterdir()) if p.is_file()]
            stage = 'integrity'
            require(sha(directory / name) == reserved['input_sha256'] and (root / BASE / name).read_bytes() == payload
                    and source.read_bytes() == original, 'source or compiler input changed during launch')
            stem = stem_for(current_phase)
            outputs = [p for p in directory.glob(stem + '.*') if p.suffix != '.lean']
            require(not any(p.is_symlink() or not p.is_file() for p in outputs), 'invalid compiler output')
            term['outputs'] = [receipt(root, p) for p in sorted(outputs)]
            stage = 'audit'
            if term['status'] == 'COMPLETE':
                require(any(p.name == stem + '.olean' for p in outputs), 'required compiled output missing')
                if current_phase == 'baseline':
                    term['baseline_audit'] = audit_baseline((directory / 'stdout').read_text(), (directory / 'stderr').read_text())
                elif current_phase == 'proof':
                    term['axiom_audit'] = audit((directory / 'stdout').read_text(), (directory / 'stderr').read_text(),
                                               load(root / ASSUMPTIONS), mode)
                    term['result'] = 'SUCCESS' if mode == 'proof' else 'NEGATIVE'
                else:
                    require('sorry' not in ((directory / 'stdout').read_text() + (directory / 'stderr').read_text()).lower(),
                            'signature sorry diagnostic')
                    for path in outputs:
                        (root / BASE / path.name).write_bytes(path.read_bytes())
                    term['signature_materialization'] = [receipt(root, root / BASE / p.name) for p in sorted(outputs)]
            elif current_phase != 'proof':
                term['repair_pause'] = 'fixed signature/baseline compilation requires tooling diagnosis'
            stage = 'integrity'
            validate_manifest(root, True); verify_payloads(root, m)
            verify_revision(root, state['revisions'][-1], live=True)
            verify_attempts(root, state)
        except (OSError, ValueError, UnicodeError) as error:
            term.pop('result', None); term.pop('baseline_audit', None); term.pop('axiom_audit', None)
            term.update(status='FAILED', error=str(error))
            if isinstance(error, ScientificMismatch):
                term['scientific_mismatch'] = True
            elif stage == 'audit' or stage == 'materialize':
                term['repair_pause'] = str(error)
            else:
                term['cleanup_unverified'] = True
            if directory.exists():
                term['raw_files'] = [receipt(root, p) for p in sorted(directory.iterdir()) if p.is_file() and not p.is_symlink()]
        term['time'] = stamp()
        term['work'] = work_snapshot(root, term['time'], require_open=False)
        term['remaining_attempts'] = LIMITS['attempts'] - n
        term['remaining_active_seconds'] = max(0, LIMITS['active_seconds'] - work_total(term['work'], term['time']))
        ledger.add(term)
        return ledger.read()[1]
    finally:
        owner.close()



def reconcile_control(root):
    """Clear a process pause only using its exact durable supervisor receipt.

    The failed reservation and terminal record remain untouched. Missing or
    unverified cleanup/actual-duration evidence cannot be reconciled here.
    """
    root = Path(root).resolve()
    gate(root); m = validate_manifest(root, True)
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        ledger, state = open_run(root, m)
        state = recover(root, ledger, state)
        require(state['outcome'] is None and state['control_stop'] and state['attempts'],
                'no process pause to reconcile')
        verify_payloads(root, m); verify_attempts(root, state)
        row = state['attempts'][-1]['reservation']
        directory = root / OUT / 'attempts' / f"{row['number']:02d}"
        request_path, supervisor = directory / 'request.json', directory / 'supervisor.json'
        require(request_path.is_file() and supervisor.is_file(), 'missing process receipt; costs/cleanup remain unknown')
        request, proc = load(request_path), load(supervisor)
        request_hash = request.pop('request_sha256')
        require(hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() == request_hash
                and proc['request_sha256'] == request_hash and request['argv'] == row['argv']
                and request['cwd'] == row['cwd'] and request['env'] == row['env']
                and request['seconds'] == row['reserved_seconds']
                and request['deadline_monotonic'] <= row['time']['monotonic'] + row['reserved_seconds'],
                'reconciliation supervisor/request identity mismatch')
        cost = proc['charged_seconds']
        require(proc.get('cleanup_completed') is True and type(cost) in (int, float)
                and math.isfinite(cost) and cost >= 0 and proc.get('status') in
                ('COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED'), 'unverified process cleanup or actual duration')
        raw = []
        for stream in ('stdout', 'stderr'):
            path = directory / stream
            require(path.is_file() and sha(path) == proc[stream + '_sha256'], 'reconciled raw output missing or changed')
            raw.append(receipt(root, path))
        current = stamp(); work = work_snapshot(root, current)
        work_continuation(state['work'], work, state['accounted_at'], current)
        ledger.add({'kind': 'CONTROL_RECONCILED', 'number': row['number'], 'time': current, 'work': work,
                    'cleanup_completed': True, 'known_actual_seconds': cost,
                    'supervisor_receipt': receipt(root, supervisor), 'request_receipt': receipt(root, request_path),
                    'raw_files': raw})
        return ledger.read()[1]
    finally:
        owner.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify-inputs', 'begin-run', 'adopt-revision', 'reconcile-control', 'preflight', 'attempt'))
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--mode', choices=('proof', 'counterexample'), default='proof')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.action == 'verify-inputs':
        m = validate_manifest(root); verify_payloads(root, m)
        print('PASS: exact scientific inputs, local runtime/dependencies and bounded manifest; zero launches')
        return 0
    if args.action == 'reconcile-control':
        result = reconcile_control(root)
    elif args.action in ('begin-run', 'adopt-revision'):
        result = adopt_revision(root, initial=args.action == 'begin-run')
    else:
        result = execute(root, args.resume, args.mode, preflight=args.action == 'preflight')
    print(json.dumps(result, indent=2))
    if result['control_stop'] or result['repair_pause'] or result['outcome'] == 'BOUNDED_UNRESOLVED':
        return 1
    if result['attempts'] and result['attempts'][-1].get('terminal', {}).get('status') != 'COMPLETE':
        return 1
    return 0
