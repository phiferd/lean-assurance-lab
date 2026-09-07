"""Exact CVC3-U1-PROOF-0001 runner; inert-tested CVC-RUNNER-2 successor.

One filesystem lock, an append-only event log and an atomic derived snapshot
govern each run. No CLI command, runtime, path, budget or fixture override exists.
The fixed Lean runtime, Python/OS and reviewed proof source remain trusted.
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

from lib.cvc_prep import require, safe, sha, bind, committed, lock, read_events, append
from lib.cvc_process import atomic, now, run_process, sync_dir
from lib.cvc_runner_audit import generate, audit, TARGETS, NEGATIVE

RUN = 'CVC3-U1-PROOF-0001'
ITEM = 'CVC-3'
MANIFEST = 'config/cvc-u1-proof-0001.json'
BASE = 'external/cvc3-u1-proof-0001'
OUT = 'results/research/conditional-validation-contracts/cvc-3/run-0001'
PROTOCOL = 'results/research/conditional-validation-contracts/cvc-2/execution-protocol.json'
ASSUMPTIONS = 'results/research/conditional-validation-contracts/cvc-2/assumptions.json'
SIGNATURE = 'research/conditional-validation-contracts/cvc2/Contract.lean'
PREPARATION = 'results/research/conditional-validation-contracts/cvc-prep-2/result.json'
PREP_MANIFEST = 'config/cvc-u1-dependencies-0002.json'
RUNTIME = 'results/research/conditional-validation-contracts/cvc-prep-1/runtime-manifest.json'
CLOSURE = 'results/research/conditional-validation-contracts/alt-payloads/source-closure.json'
ENTRY_REVIEW = 'results/research/conditional-validation-contracts/cvc-runner-2/entry-review.json'
LIMITS = {'sessions': 4, 'session_seconds': 5400, 'active_seconds': 21600,
          'attempts': 12, 'attempt_seconds': 300, 'checker_launches': 0,
          'network_requests': 0, 'dependency_compilations': 0}
FIXED = {
    PROTOCOL: '5410789482c8474a367064b1d8ef047c76f2e9a74e3b3bce84d124a3dce5d6f0',
    ASSUMPTIONS: 'faaa491087375e7bb2fb55060a74d14efecdd4edf80edb9591351fed3a28133f',
    SIGNATURE: '20f3c65a3bfcd3a491f58a9562d203eeb91084f88c728206a725e252e533e5d3',
    PREPARATION: '75cb5a26ce3748104d88f65263d583bdf42af5604df45ae5e2361d52f2f297f4',
    PREP_MANIFEST: '3767971c7de7aff15bb47951d84638be1eb5908c5fa8280ccab862c63c6cb8c2',
    RUNTIME: 'efba5b65f8390cac96c683ff4b813c9eb905cafafd21e0b2a078c8bc2efadb42',
    CLOSURE: '2b5a2989059e0735922dc60fdcd3b3af3e7b44c2ab646af9f810fb28f1de4875',
    'results/research/conditional-validation-contracts/cvc-2/examples.json':
        '1e3cd9a7b295e587b1f3146859799d820b3d8ea4e2907580a647696835a32a22',
    'results/research/conditional-validation-contracts/cvc-2/contract.json':
        'edc98f1ce33867a4c9debba61dc686dd5f7ade981fe9cf0fac0bf4d4cbaab2f0',
}
CODE = ['lib/cvc_runner2.py', 'lib/cvc_process.py', 'lib/cvc_runner_audit.py',
        'lib/cvc_prep.py', 'lib/cvc_prep2.py', 'lib/cvc_prep_binding.py', 'lib/research_queue.py',
        'scripts/run-cvc-u1-proof-successor', 'scripts/bind-cvc-u1-proof',
        'tests/test_cvc_runner2.py', 'tests/test_cvc_process.py', 'tests/cvc_runner2_fixture.py',
        'lib/cvc_fixture_budget.py', 'lib/cvc_runner2_evidence.py',
        'scripts/validate-cvc-runner2', 'tests/test_cvc_runner2_evidence.py']


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


def commands(root, compiler, number):
    target = Path(root) / BASE / 'Contract.olean' if number == 1 else Path(root) / OUT / 'attempts' / f'{number:02d}' / 'CVC2Proof.olean'
    return [compiler, '-o', str(target), 'Contract.lean' if number == 1 else 'CVC2Proof.lean']


def build_manifest(root):
    """Read-only construction; callers refuse rebinding once a run has begun."""
    root = Path(root).resolve()
    prep, runtime = load(root / PREPARATION), load(root / RUNTIME)
    python = Path(os.path.realpath(os.sys.executable))
    return {'schema_version': 1, 'run_id': RUN, 'item_id': ITEM, 'implementation_item': 'CVC-RUNNER-2',
            'workspace': BASE, 'run_directory': OUT, 'limits': LIMITS,
            'fixed_inputs': [{'path': p, 'sha256': digest} for p, digest in sorted(FIXED.items())],
            'controller_inputs': [binding(root, p) for p in CODE],
            'preparation_costs': prep['costs'],
            'compiler': load(root / PREP_MANIFEST)['compiler']['path'],
            'environment': environment(root, runtime['runtime_root']),
            'commands': [commands(root, runtime['runtime_root'] + '/bin/lean', n) for n in range(1, 13)],
            'python': {'path': str(python), 'sha256': sha(python)},
            'result_modes': {'proof': [{'name': n, 'type': t} for n, t in TARGETS],
                             'counterexample': [{'name': n, 'type': t} for n, t in NEGATIVE]}}


def validate_manifest(root, require_commit=False):
    root = Path(root).resolve()
    m = load(safe(root, MANIFEST))
    require(m == build_manifest(root), 'manifest differs from exact fixed inputs, commands, limits or runtime')
    for row in m['fixed_inputs'] + m['controller_inputs']:
        bind(root, row)
        if require_commit:
            committed(root, row['path'])
    if require_commit:
        committed(root, MANIFEST)
    require(load(root / PREPARATION)['outcome'] == 'SUCCESS', 'complete preparation required')
    return m


def verify_payloads(root, m):
    from lib.cvc_prep_binding import verify_runtime
    from lib import cvc_prep2 as prep
    verify_runtime(root, load(root / RUNTIME))
    pm = load(root / PREP_MANIFEST)
    modules = {r['module']: r for r in load(root / CLOSURE)['closure']['modules'] if r['kind'] != 'core_runtime'}
    prep.check_sources(root, pm, modules)
    prep.verify_output_set(root, root / pm['materialization']['build_root'], load(root / PREPARATION)['outputs'])
    require(m['compiler'] == load(root / PREP_MANIFEST)['compiler']['path'], 'compiler path changed')


def gate(root):
    from lib.research_queue import load_queue
    q = load_queue(root)
    rows = {row['id']: row for row in q['items']}
    require(q['frontier_id'] == 'F-CONDITIONAL-VALIDATION-CONTRACTS' and q['selected_item'] == ITEM
            and rows[ITEM]['status'] in {'READY', 'ACTIVE'}, 'CVC-3 not selected and separately promoted')
    for key in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2'):
        require(rows[key]['status'] == 'COMPLETE' and rows[key]['closure']['outcome'] == 'SUCCESS',
                'unmet successful prerequisite: ' + key)
    for path in ('config/research-queue.json', 'docs/RESEARCH_STATUS.md'):
        committed(root, path)
    review = load(root / ENTRY_REVIEW)
    require(review['item_id'] == ITEM and review['decision'] == 'PROMOTE'
            and review['run_id'] == RUN and review['manifest'] == binding(root, MANIFEST),
            'separate entry review does not bind this run')
    committed(root, ENTRY_REVIEW)
    checkpoint = review['implementation_checkpoint']
    require(isinstance(checkpoint, str) and len(checkpoint) == 40
            and all(c in '0123456789abcdef' for c in checkpoint), 'invalid implementation checkpoint')
    for path in [MANIFEST, *CODE, *FIXED]:
        historical = subprocess.check_output(['git', 'show', checkpoint + ':' + path], cwd=root)
        require(historical == (root / path).read_bytes(), 'entry checkpoint differs: ' + path)


def stamp():
    return {'at': now(), 'monotonic': time.monotonic()}


def elapsed(start, end):
    a, b = datetime.fromisoformat(start['at']), datetime.fromisoformat(end['at'])
    require(a.tzinfo and b.tzinfo, 'naive accounting time')
    wall, mono = (b-a).total_seconds(), end['monotonic'] - start['monotonic']
    require(all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in (wall, mono)),
            'clock rollback, reboot or invalid elapsed evidence')
    return max(wall, mono)


def derive(events):
    state = {'sessions': [], 'attempts': [], 'outcome': None, 'control_stop': None}
    require(events and events[0]['kind'] == 'START' and events[0]['run_id'] == RUN, 'missing fixed run start')
    for event in events[1:]:
        kind = event['kind']
        if kind == 'SESSION_START':
            require(state['outcome'] is None and state['control_stop'] is None, 'session after stop')
            require(len(state['sessions']) < 4 and (not state['sessions'] or 'end' in state['sessions'][-1]),
                    'session cap or overlapping session')
            if state['sessions']:
                elapsed(state['sessions'][-1]['end'], event['time'])
            require(event['number'] == len(state['sessions'])+1, 'session number reset')
            state['sessions'].append({'number': event['number'], 'start': event['time']})
        elif kind == 'SESSION_END':
            require(state['sessions'] and 'end' not in state['sessions'][-1], 'no open session')
            session = state['sessions'][-1]
            require(event['number'] == session['number'], 'wrong session end')
            used = elapsed(session['start'], event['time'])
            require(used == event['charged_seconds'], 'session charge changed')
            session.update(end=event['time'], charged_seconds=used)
        elif kind == 'RESERVED':
            require(state['outcome'] is None and state['control_stop'] is None, 'attempt after stop')
            n = len(state['attempts']) + 1
            require(type(event['number']) is int and event['number'] == n <= 12, 'attempt cap or number reset')
            require(not state['attempts'] or 'terminal' in state['attempts'][-1], 'orphan before new attempt')
            require(state['sessions'] and 'end' not in state['sessions'][-1], 'attempt outside open session')
            require(event['session'] == len(state['sessions']), 'wrong attempt session')
            require(event['phase'] == ('signature' if n == 1 else 'proof'), 'signature must be attempt 1')
            require(event['mode'] in ('proof', 'counterexample'), 'result mode')
            permitted = budget(state, event['time'])
            require(0 < event['reserved_seconds'] <= permitted, 'reservation exceeds finite budget')
            state['attempts'].append({'reservation': event})
        elif kind == 'TERMINAL':
            require(state['attempts'] and event['number'] == len(state['attempts'])
                    and 'terminal' not in state['attempts'][-1], 'duplicate or unordered terminal')
            require(event['status'] in ('COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED'), 'unknown terminal status')
            cost = event['charged_seconds']
            require(type(cost) in (int, float) and math.isfinite(cost) and cost >= 0, 'nonfinite terminal charge')
            row = state['attempts'][-1]
            if event.get('orphan'):
                require(event['status'] == 'INTERRUPTED' and cost >= row['reservation']['reserved_seconds'],
                        'orphan cannot get a free retry')
            if event['status'] == 'COMPLETE':
                require(event.get('outputs') and event.get('returncode') == 0, 'successful attempt lacks outputs')
            row['terminal'] = event
            if event['number'] == 1 and event['status'] != 'COMPLETE':
                state['outcome'] = 'BOUNDED_UNRESOLVED'
            if event.get('result'):
                require(event['number'] > 1 and event['status'] == 'COMPLETE'
                        and event['result'] == ('SUCCESS' if row['reservation']['mode'] == 'proof' else 'NEGATIVE')
                        and event.get('axiom_audit'), 'invalid proof outcome')
                state['outcome'] = event['result']
            if cost > row['reservation']['reserved_seconds'] or event.get('cleanup_unverified') or event.get('deadline_exceeded'):
                state['control_stop'] = 'process duration or cleanup could not satisfy reservation'
            used = elapsed(state['sessions'][-1]['start'], event['time'])
            total = active_seconds(state, event['time'])
            orphans = [attempt['reservation'] for attempt in state['attempts']
                       if attempt.get('terminal', {}).get('orphan')]
            used += sum(attempt['reserved_seconds'] for attempt in orphans
                        if attempt['session'] == len(state['sessions']))
            total += sum(attempt['reserved_seconds'] for attempt in orphans)
            if used > 5400 or total > 21600:
                state['control_stop'] = 'terminal audit and verification exceeded active design budget'
            if state['control_stop']:
                state['outcome'] = 'BOUNDED_UNRESOLVED'
        elif kind == 'CONTROL_STOP':
            require(isinstance(event.get('reason'), str) and event['reason'], 'missing stop reason')
            state['control_stop'] = event['reason']
            state['outcome'] = 'BOUNDED_UNRESOLVED'
        else:
            raise ValueError('unknown accounting event: ' + str(kind))
    return state


def active_seconds(state, current):
    return sum(session['charged_seconds'] if 'charged_seconds' in session else elapsed(session['start'], current)
               for session in state['sessions'])


def budget(state, current):
    require(state['outcome'] is None and state['control_stop'] is None, 'run already stopped')
    require(state['sessions'] and 'end' not in state['sessions'][-1], 'no active design session')
    require(len(state['sessions']) <= 4 and len(state['attempts']) < 12, 'session or attempt cap exhausted')
    used = elapsed(state['sessions'][-1]['start'], current)
    total = active_seconds(state, current)
    orphan_charge = sum(row['reservation']['reserved_seconds'] for row in state['attempts']
                        if row.get('terminal', {}).get('orphan'))
    session_orphan_charge = sum(row['reservation']['reserved_seconds'] for row in state['attempts']
                               if row.get('terminal', {}).get('orphan')
                               and row['reservation']['session'] == len(state['sessions']))
    # Conservatively add orphan timeout reservations to wall/monotonic design
    # time. Double charging is explicit; a crash cannot recover used budget.
    left = min(300., 5400. - used - session_orphan_charge, 21600. - total - orphan_charge)
    require(left > 0, 'session or cumulative active time exhausted')
    return left


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


def open_run(root, m, create=False):
    directory, workspace = safe(root, OUT, False), safe(root, BASE, False)
    marker = directory / 'start.json'
    ledger = Ledger(directory / 'execution')
    exists = marker.exists() or ledger.path.exists() or ledger.snapshot.exists() or workspace.exists()
    if not exists:
        require(create, 'begin a design session before work or attempts')
        require(not directory.exists() or {p.name for p in directory.iterdir()} <= {'controller.lock'},
                'unrecognized partial run directory')
        identity = {'run_id': RUN, 'manifest_sha256': sha(root / MANIFEST),
                    'checkpoint': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                    'time': stamp()}
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
    require(all(events[0][key] == val for key, val in identity.items()), 'initial ledger identity changed')
    return ledger, state


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
        output_base = root / BASE if row['number'] == 1 else directory
        stem = 'Contract' if row['number'] == 1 else 'CVC2Proof'
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


def verify_attempts(root, state):
    signature_outputs = []
    for row in state['attempts']:
        reserved, term = row['reservation'], row.get('terminal')
        require(reserved['argv'] == commands(root, load(root / MANIFEST)['compiler'], reserved['number']),
                'prior attempt argv changed')
        require(reserved['env'] == load(root / MANIFEST)['environment'], 'prior environment changed')
        for file in reserved.get('evidence', []):
            verify_receipt(root, file)
        if term:
            for file in term.get('raw_files', []) + term.get('outputs', []):
                verify_receipt(root, file)
            if term.get('supervisor_receipt'):
                verify_receipt(root, term['supervisor_receipt'])
            directory = root / OUT / 'attempts' / f"{reserved['number']:02d}"
            implementation = directory / 'implementation.lean'
            compiled_input = directory / ('Contract.lean' if reserved['number'] == 1 else 'CVC2Proof.lean')
            if implementation.exists():
                require(sha(implementation) == reserved['source_sha256'], 'reserved implementation changed')
            if compiled_input.exists():
                require(sha(compiled_input) == reserved['input_sha256'], 'reserved compiler input changed')
            if term.get('result'):
                require(generate(implementation.read_text(), reserved['mode']) == compiled_input.read_bytes(),
                        'generated proof audit changed')
                require(term['axiom_audit'] == audit((directory / 'stdout').read_text(), (directory / 'stderr').read_text(),
                                                    load(root / ASSUMPTIONS), reserved['mode']), 'prior axiom audit changed')
        if reserved['number'] == 1 and term and term['status'] == 'COMPLETE':
            signature_outputs = term['outputs']
    if len(state['attempts']) >= 1 and state['attempts'][0].get('terminal', {}).get('status') == 'COMPLETE':
        require(any(row['path'] == BASE + '/Contract.olean' for row in signature_outputs), 'signature olean binding missing')
        expected = {row['path'] for row in signature_outputs}
        actual = {str(path.relative_to(root)) for path in (root / BASE).glob('Contract.*') if path.name != 'Contract.lean'}
        require(actual == expected, 'signature output set changed')
        require(sha(root / BASE / 'Contract.lean') == FIXED[SIGNATURE], 'materialized signature changed')


def workspace_check(root, state):
    workspace = root / BASE
    outputs = [file['path'].split('/')[-1] for row in state['attempts'][:1]
               for file in row.get('terminal', {}).get('outputs', [])]
    allowed = {'.run.json', 'tmp', 'Contract.lean', 'proof-input.lean', 'CVC2Proof.lean', *outputs}
    require(all(not p.is_symlink() and p.name in allowed for p in workspace.iterdir()), 'unknown workspace input')
    expected_dirs = {f"{row['reservation']['number']:02d}" for row in state['attempts']}
    attempts = root / OUT / 'attempts'
    require(not attempts.exists() or {p.name for p in attempts.iterdir()} == expected_dirs,
            'unrecorded or missing attempt directory')


def session(root, end=False):
    root = Path(root).resolve()
    gate(root); validate_manifest(root, True)
    owner = lock(safe(root, OUT + '/controller.lock', False))
    try:
        gate(root); m = validate_manifest(root, True)
        ledger, state = open_run(root, m, create=not end)
        state = recover(root, ledger, state)
        current = stamp()
        if end:
            require(state['sessions'] and 'end' not in state['sessions'][-1], 'no open session')
            used = elapsed(state['sessions'][-1]['start'], current)
            ledger.add({'kind': 'SESSION_END', 'number': len(state['sessions']), 'time': current, 'charged_seconds': used})
            if used > 5400 or active_seconds(ledger.read()[1], current) > 21600:
                ledger.add({'kind': 'CONTROL_STOP', 'reason': 'active design budget exceeded'})
        else:
            ledger.add({'kind': 'SESSION_START', 'number': len(state['sessions'])+1, 'time': current})
        return ledger.read()[1]
    finally:
        owner.close()


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
        if state['outcome'] is not None or state['control_stop'] is not None:
            return state
        require(resume == bool(state['attempts']), 'use --resume only for an existing attempt ledger')
        budget(state, stamp())
        if preflight:
            return state
        n = len(state['attempts']) + 1
        source = root / SIGNATURE if n == 1 else safe(root, BASE + '/proof-input.lean')
        original = source.read_bytes()
        payload = original if n == 1 else generate(original.decode(), mode)
        name = 'Contract.lean' if n == 1 else 'CVC2Proof.lean'
        directory = root / OUT / 'attempts' / f'{n:02d}'
        require(not directory.exists(), 'cannot overwrite an attempt')
        current = stamp(); seconds = budget(state, current)
        reserved = {'kind': 'RESERVED', 'number': n, 'phase': 'signature' if n == 1 else 'proof', 'mode': mode,
                    'session': len(state['sessions']), 'time': current, 'reserved_seconds': seconds,
                    'argv': commands(root, m['compiler'], n), 'cwd': str(root / BASE), 'env': m['environment'],
                    'source_sha256': hashlib.sha256(original).hexdigest(),
                    'input_sha256': hashlib.sha256(payload).hexdigest(),
                    'manifest_sha256': sha(root / MANIFEST),
                    'remaining_attempts_after_reservation': 12 - n,
                    'active_seconds_before': active_seconds(state, current)}
        ledger.add(reserved)  # Durable before even creating the supervisor.
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
            term['raw_files'] = [receipt(root, directory / x) for x in
                                 ('stdout', 'stderr', 'implementation.lean', name, 'request.json', 'supervisor.json')
                                 if (directory / x).is_file()]
            if (directory / 'process.json').is_file():
                term['raw_files'].append(receipt(root, directory / 'process.json'))
            stage = 'integrity'
            require(hashlib.sha256((directory / name).read_bytes()).hexdigest() == reserved['input_sha256']
                    and (root / BASE / name).read_bytes() == payload and source.read_bytes() == original,
                    'source or generated input changed during attempt')
            output_base = root / BASE if n == 1 else directory
            stem = 'Contract' if n == 1 else 'CVC2Proof'
            outputs = [p for p in output_base.glob(stem + '.*') if p.suffix != '.lean']
            require(not any(p.is_symlink() or not p.is_file() for p in outputs), 'invalid compiler output')
            term['outputs'] = [receipt(root, p) for p in sorted(outputs)]
            stage = 'audit'
            if term['status'] == 'COMPLETE':
                require(any(p.name == stem + '.olean' for p in outputs), 'required compiled output missing')
                if n > 1:
                    term['axiom_audit'] = audit((directory / 'stdout').read_text(), (directory / 'stderr').read_text(),
                                               load(root / ASSUMPTIONS), mode)
                    term['result'] = 'SUCCESS' if mode == 'proof' else 'NEGATIVE'
                else:
                    require('sorry' not in ((directory / 'stdout').read_text() + (directory / 'stderr').read_text()).lower(),
                            'signature sorry diagnostic')
            stage = 'integrity'
            validate_manifest(root, True); verify_payloads(root, m)
            verify_attempts(root, state)
        except (OSError, ValueError, UnicodeError) as error:
            term.pop('result', None)
            term.update(status='FAILED', error=str(error))
            if stage == 'integrity' or ((directory / 'request.json').exists() and not (directory / 'supervisor.json').exists()):
                term['cleanup_unverified'] = True
            if directory.exists():
                term['raw_files'] = [receipt(root, path) for path in sorted(directory.iterdir())
                                     if path.is_file() and not path.is_symlink()]
        term['time'] = stamp()
        term['remaining_attempts'] = 12 - n
        term['remaining_active_seconds'] = max(0, 21600 - active_seconds(state, term['time']))
        ledger.add(term)
        return ledger.read()[1]
    finally:
        owner.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify-inputs', 'begin-session', 'end-session', 'preflight', 'attempt'))
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--mode', choices=('proof', 'counterexample'), default='proof')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.action == 'verify-inputs':
        m = validate_manifest(root); verify_payloads(root, m)
        print('PASS: fixed inputs/runtime/dependencies; zero Lean or proof launches')
        return 0
    if args.action in ('begin-session', 'end-session'):
        result = session(root, end=args.action == 'end-session')
    else:
        result = execute(root, args.resume, args.mode, preflight=args.action == 'preflight')
    print(json.dumps(result, indent=2))
    if result['control_stop'] or result['outcome'] == 'BOUNDED_UNRESOLVED':
        return 1
    if result['attempts'] and result['attempts'][-1].get('terminal', {}).get('status') != 'COMPLETE':
        return 1
    return 0
