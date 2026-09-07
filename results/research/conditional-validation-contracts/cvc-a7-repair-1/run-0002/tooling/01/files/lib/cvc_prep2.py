"""CVC-PREP-2 explicit successor: reuse 27 modules and prepare the remaining 10.

Derived from frozen lib/cvc_prep.py; predecessor bytes and run IDs are unchanged.

Reviewed local code and a trusted filesystem are assumed; this is not a sandbox
for arbitrary Lean source. The CLI has no general command or fixture override.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

ITEM, RUN, COUNT = 'CVC-PREP-2', 'CVC-U1-DEPS-0002', 10
BASE = 'external/cvc-u1-dependencies-0002'
OUT = 'results/research/conditional-validation-contracts/cvc-prep-2'
CLOSURE = 'results/research/conditional-validation-contracts/alt-payloads/source-closure.json'
PRIOR = 'results/research/conditional-validation-contracts/cvc-prep-1'
PRIOR_BASE = 'external/cvc-u1-dependencies-0001/build/lib/lean'
SUCCESSOR = PRIOR + '/successor-proposal.json'
PROPOSAL = 'results/research/conditional-validation-contracts/alt-payloads/proposal.json'
MANIFEST = 'config/cvc-u1-dependencies-0002.json'
LIMITS = {'max_sessions': 2, 'session_seconds': 5400, 'max_active_seconds': 10800,
          'max_compilation_attempts': 10, 'attempt_timeout_seconds': 300,
          'max_compilation_seconds': 3000}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def js(path):
    return json.loads(Path(path).read_text())


def safe(root, name, exists=True):
    require(isinstance(name, str) and name and not Path(name).is_absolute()
            and '..' not in Path(name).parts, 'unsafe repository path')
    p = Path(root)
    for part in Path(name).parts:
        p = p / part
        require(not p.is_symlink(), 'symlink path refused: ' + name)
    require(not exists or p.exists(), 'missing path: ' + name)
    return p


def bind(root, row):
    require(set(row) == {'path', 'sha256'} and isinstance(row['sha256'], str)
            and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'invalid binding')
    p = safe(root, row['path'])
    require(p.is_file() and sha(p) == row['sha256'], 'binding changed: ' + row['path'])
    return p


def committed(root, rel):
    p = safe(root, rel)
    try:
        blob = subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=root,
                                       stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError('uncommitted required file: ' + rel) from error
    require(blob == p.read_bytes(), 'required file differs from HEAD: ' + rel)


def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), 'symlink lock')
    stream = path.open('a+')
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        stream.close()
        raise ValueError('concurrent controller refused')
    return stream


def gate(root):
    from lib.research_queue import load_queue
    queue = load_queue(root)
    require(queue['frontier_id'] == 'F-CONDITIONAL-VALIDATION-CONTRACTS'
            and queue['selected_item'] == ITEM, 'item not selected')
    row = next(r for r in queue['items'] if r['id'] == ITEM)
    require(row['status'] in {'ACTIVE', 'READY'}, 'item not selected ACTIVE/READY')


def validate_manifest(root, path, require_commit=False):
    root, path = Path(root).resolve(), Path(path).resolve()
    require(path == root / MANIFEST, 'wrong manifest path')
    m = js(path)
    fields = {'schema_version', 'item_id', 'run_id', 'source_closure', 'runtime_manifest',
              'work_record', 'materialization', 'limits', 'compiler', 'controller',
              'tests', 'immutable_bindings', 'ledger_root', 'predecessor', 'seed_outputs', 'commands'}
    require(set(m) == fields and m['schema_version'] == 1 and m['item_id'] == ITEM
            and m['run_id'] == RUN, 'wrong manifest')
    expected_paths = {'source_closure': CLOSURE, 'runtime_manifest': PRIOR + '/runtime-manifest.json',
                      'work_record': OUT + '/initial-work-record.json', 'controller': 'lib/cvc_prep2.py',
                      'tests': 'tests/test_cvc_prep2.py', 'predecessor': PRIOR + '/result.json',
                      'commands': OUT + '/command-manifest.json'}
    for key, expected in expected_paths.items():
        require(m[key]['path'] == expected, 'wrong bound input: ' + key)
        bind(root, m[key])
    require(isinstance(m['immutable_bindings'], list), 'immutable bindings required')
    immutable = {row['path'] for row in m['immutable_bindings']}
    require(len(immutable) == len(m['immutable_bindings']) and
            {'lib/cvc_prep_binding.py', 'lib/research_queue.py', 'scripts/prepare-cvc-u1-successor',
             'scripts/bind-cvc-u1-successor', PROPOSAL, SUCCESSOR, OUT + '/inert-test-receipt.json'} <= immutable,
            'missing or duplicate controller input binding')
    for row in m['immutable_bindings']:
        bind(root, row)
    require(m['limits'] == LIMITS, 'fixed limits differ')
    require(m['ledger_root'] == OUT + '/execution', 'wrong ledger root')
    mat = m['materialization']
    expected_mat = {'root': BASE, 'source_root': BASE + '/src',
                    'build_root': BASE + '/build/lib/lean', 'tmp_root': BASE + '/tmp'}
    require(set(mat) == {*expected_mat, 'donors'} and all(mat[k] == v for k, v in expected_mat.items()),
            'materialization outside fixed workspace')
    for value in expected_mat.values():
        safe(root, value, False)
    require(isinstance(mat['donors'], list) and len(mat['donors']) == 2, 'donors missing')
    proposal, runtime_manifest = js(root / PROPOSAL), js(bind(root, m['runtime_manifest']))
    runtime_root = runtime_manifest['runtime_root']
    require(runtime_root == proposal['runtime']['path'], 'runtime path differs from proposal')
    expected_env = {'LEAN_SYSROOT': runtime_root,
                    'LEAN_PATH': str(root / mat['build_root']) + ':' + runtime_root + '/lib/lean',
                    'PATH': runtime_root + '/bin:/usr/bin:/bin',
                    'TMPDIR': str(root / mat['tmp_root']), 'LANG': 'C.UTF-8'}
    c = m['compiler']
    require(c == {'path': runtime_root + '/bin/lean',
                  'sha256': proposal['runtime']['lean_binary']['sha256'],
                  'argv_prefix': ['-o'], 'env': expected_env}, 'compiler declaration differs')
    cp = Path(c['path'])
    require(cp.is_file() and not cp.is_symlink() and sha(cp) == c['sha256'], 'compiler differs')
    closure = js(bind(root, m['source_closure']))['closure']
    rows = [r for r in closure['modules'] if r['kind'] != 'core_runtime']
    modules, order = {r['module']: r for r in rows}, closure['topological_noncore_order']
    require(len(rows) == len(modules) == len(order) == len(set(order)) == 37
            and set(order) == set(modules), 'exact 37-module topology required')
    seen = set()
    for module in order:
        require(re.fullmatch(r'(Lean4Lean|Batteries)(\.[A-Za-z_][A-Za-z_0-9]*)+', module),
                'Lab or unknown module')
        require(all(i['module'] in seen for i in modules[module]['imports']
                    if i['module'] in modules), 'dependency order differs')
        seen.add(module)
    successor = js(safe(root, SUCCESSOR))
    prior = js(bind(root, m['predecessor']))
    require(prior['item_id'] == 'CVC-PREP-1' and prior['outcome'] == 'BOUNDED_UNRESOLVED'
            and prior['completed_modules'] == prior['compilation_attempts'] == 27,
            'wrong predecessor closure')
    require([r['module'] for r in prior['attempts']] == order[:27]
            and all(r['status'] == 'COMPLETE' for r in prior['attempts']), 'prior successes differ')
    require(order[27:] == successor['remaining_order'] and len(order[27:]) == COUNT,
            'remaining order differs')
    seed = relocated_outputs(prior['outputs'])
    require(len(seed) == 119 and m['seed_outputs'] == seed, 'seed output binding differs')
    command_manifest = js(bind(root, m['commands']))
    require(command_manifest == commands(root, m, order[27:]), 'exact command manifest differs')
    order = order[27:]
    if require_commit:
        gate(root)
        for row in [m[k] for k in expected_paths] + m['immutable_bindings']:
            committed(root, row['path'])
        committed(root, MANIFEST)
    return m, order, modules


def donors(m, modules):
    found = {}
    for donor in m['materialization']['donors']:
        require(set(donor) == {'root', 'files'}, 'bad donor')
        base = Path(donor['root'])
        require(base.is_absolute() and base.is_dir() and base.resolve() == base, 'donor unavailable')
        for row in donor['files']:
            require(set(row) == {'module', 'path', 'sha256', 'bytes'}
                    and row['module'] not in found, 'bad donor row')
            p = safe(base, row['path'])
            expected = modules.get(row['module'], {}).get('source', {})
            require(p.is_file() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
                    and expected.get('sha256') == row['sha256'] and expected.get('bytes') == row['bytes'],
                    'donor mismatch: ' + row['module'])
            found[row['module']] = (p, row)
    require(set(found) == set(modules), 'donors must exactly cover closure')
    return found


def output_map(rows):
    """Identity comparison is independent of filesystem traversal ordering."""
    require(isinstance(rows, list), 'output list required')
    result = {}
    for row in rows:
        require(set(row) == {'path', 'bytes', 'sha256'} and isinstance(row['path'], str)
                and type(row['bytes']) is int and row['bytes'] >= 0
                and isinstance(row['sha256'], str) and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                'invalid output receipt')
        require(row['path'] not in result, 'duplicate output binding')
        result[row['path']] = row
    return result


def relocated_outputs(rows):
    output_map(rows)
    result = []
    for row in rows:
        path = Path(row['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'unsafe predecessor output')
        require(path.is_relative_to(PRIOR_BASE), 'output outside predecessor build')
        dest = str(Path(BASE + '/build/lib/lean') / path.relative_to(PRIOR_BASE))
        result.append({**row, 'path': dest})
    return result


def verify_output_set(root, build, expected):
    # Compare exact path/size/hash maps, while rejecting duplicates and symlinks.
    require(output_map(inventory(root, build)) == output_map(expected),
            'changed, missing or unrecorded dependency output')
    allowed_dirs = {str(parent) for row in expected
                    for parent in Path(row['path']).relative_to(build.relative_to(root)).parents}
    require({str(p.relative_to(build)) for p in build.rglob('*') if p.is_dir()} <= allowed_dirs,
            'unrecorded output directory')
    return expected


def seed_inputs(root, m):
    prior = js(bind(root, m['predecessor']))
    expected = prior['outputs']
    require(m['seed_outputs'] == relocated_outputs(expected), 'seed identities changed')
    verify_output_set(root, safe(root, PRIOR_BASE), expected)
    return expected


def commands(root, m, order):
    return {'schema_version': 1, 'run_id': RUN, 'environment': m['compiler']['env'],
            'commands': [{'number': n, 'module': module,
                          'argv': [m['compiler']['path'], '-o',
                                   str(root / m['materialization']['build_root'] /
                                       (module.replace('.', '/') + '.olean')),
                                   module.replace('.', '/') + '.lean'],
                          'cwd': str(root / m['materialization']['source_root'])}
                         for n, module in enumerate(order, 1)]}


def materialize(root, m, modules):
    # Revalidate ALL inputs before the first copy, even if called independently.
    runtime(root, m)
    rows = donors(m, modules)
    prior_outputs = seed_inputs(root, m)
    src = safe(root, m['materialization']['source_root'], False)
    build = safe(root, m['materialization']['build_root'], False)
    require(not src.exists() and not build.exists(), 'materialization must be fresh')
    for module, (source, row) in rows.items():
        dest = src / (module.replace('.', '/') + '.lean')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as reader, dest.open('xb') as writer:
            shutil.copyfileobj(reader, writer)
        require(dest.stat().st_size == row['bytes'] and sha(dest) == row['sha256'], 'donor changed during copy')
    for source_row, dest_row in zip(prior_outputs, m['seed_outputs']):
        source, dest = safe(root, source_row['path']), safe(root, dest_row['path'], False)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as reader, dest.open('xb') as writer:
            shutil.copyfileobj(reader, writer)
        require(dest.stat().st_size == dest_row['bytes'] and sha(dest) == dest_row['sha256'],
                'seed output changed during copy')
    safe(root, m['materialization']['tmp_root'], False).mkdir(parents=True)
    verify_output_set(root, build, m['seed_outputs'])
    return rows


def check_sources(root, m, modules):
    src = safe(root, m['materialization']['source_root'])
    expected = {mod.replace('.', '/') + '.lean': row['source'] for mod, row in modules.items()}
    paths = list(src.rglob('*'))
    require(not any(p.is_symlink() for p in paths), 'source symlink')
    require({str(p.relative_to(src)) for p in paths if p.is_file()} == set(expected), 'unknown or missing source')
    allowed_dirs = {str(parent) for rel in expected for parent in Path(rel).parents if str(parent) != '.'}
    require({str(p.relative_to(src)) for p in paths if p.is_dir()} <= allowed_dirs, 'unknown source directory')
    for rel, row in expected.items():
        p = src / rel
        require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'source changed')
    workspace = safe(root, m['materialization']['root'])
    require({p.name for p in workspace.iterdir()} == {'src', 'build', 'tmp', '.preparation.json'},
            'unknown workspace entry')


def runtime(root, m):
    return importlib.import_module('lib.cvc_prep_binding').verify_runtime(root, js(bind(root, m['runtime_manifest'])))


def ldir(root, m):
    return safe(root, m['ledger_root'], False)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read_events(path):
    if not path.exists():
        return []
    require(not path.is_symlink(), 'symlink ledger')
    data = path.read_bytes()
    require(not data or data.endswith(b'\n'), 'truncated ledger')
    previous, rows = '0' * 64, []
    for line in data.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError('malformed ledger') from error
        checksum = row.pop('event_sha256', None)
        require(row.get('previous_sha256') == previous and checksum == hashlib.sha256(canonical(row)).hexdigest(),
                'ledger chain invalid')
        row['event_sha256'] = checksum
        rows.append(row)
        previous = checksum
    return rows


def append(path, event):
    rows = read_events(path)
    row = {**event, 'previous_sha256': rows[-1]['event_sha256'] if rows else '0' * 64}
    row['event_sha256'] = hashlib.sha256(canonical(row)).hexdigest()
    with path.open('ab') as stream:
        stream.write(canonical(row) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def derive(events):
    state = {}
    for row in events:
        n = row.get('number')
        require(type(n) is int and 0 <= n <= COUNT, 'invalid attempt number')
        if row.get('kind') == 'RESERVED':
            require(n == len(state) and n not in state, 'duplicate or nonconsecutive reservation')
            require(not state or state[n - 1].get('terminal', {}).get('status') == 'COMPLETE',
                    'reservation after failure or orphan')
            require(finite(row.get('reserved_seconds')) and row['reserved_seconds'] <= 300,
                    'invalid reservation duration')
            require(n != 0 or row.get('module') == 'START', 'missing start reservation')
            state[n] = dict(row)
        elif row.get('kind') == 'TERMINAL':
            require(n in state and n == max(state) and 'terminal' not in state[n], 'invalid terminal')
            require(row.get('status') in {'COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED'}
                    and finite(row.get('charged_seconds')), 'invalid terminal charge/status')
            state[n]['terminal'] = row
        else:
            raise ValueError('unknown event')
    return state


def attempt_budget(work, state, current):
    sessions = work.get('sessions')
    require(isinstance(sessions, list) and 1 <= len(sessions) <= 2, 'session count')
    total, live_left, previous_end = 0., None, None
    for i, session in enumerate(sessions):
        start = datetime.fromisoformat(session['started_at'])
        end = datetime.fromisoformat(session['ended_at']) if session.get('ended_at') else current
        require(start.tzinfo is not None and end.tzinfo is not None, 'naive session time')
        require(previous_end is None or start >= previous_end, 'overlapping sessions')
        used = (end - start).total_seconds()
        require(0 <= used <= 5400, 'session exhausted or reversed')
        total += used
        if session.get('ended_at') is None:
            require(i == len(sessions) - 1, 'non-final open session')
            live_left = 5400 - used
        previous_end = end
    require(live_left is not None and total <= 10800, 'active time exhausted or no open session')
    attempts = [r for n, r in state.items() if n != 0]
    require(len(attempts) < COUNT, 'attempt cap exhausted')
    charges = [r.get('terminal', {}).get('charged_seconds', r['reserved_seconds']) for r in attempts]
    require(all(finite(c) for c in charges), 'invalid compilation charge')
    remaining = min(300., 3000. - sum(charges), live_left, 10800. - total)
    require(remaining > 0, 'compilation/session budget exhausted')
    return remaining


def kill(proc):
    # Kill the group even when its leader exited; descendants must not escape.
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=0.1)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired as error:
        raise ValueError('process group could not be reaped within cleanup bound') from error


def log_receipt(stdout, stderr):
    return {name + '_sha256': sha(path) if path.is_file() else None
            for name, path in [('stdout', stdout), ('stderr', stderr)]}


def run_process(argv, cwd, env, stdout, stderr, deadline):
    """The production runner has no fixture switch. Tests call this with inert argv."""
    begin, started, proc = time.monotonic(), now(), None
    status, error, rc = 'FAILED', None, None
    def interrupt(_signum, _frame):
        raise KeyboardInterrupt
    previous_handler = signal.signal(signal.SIGTERM, interrupt)
    try:
        with stdout.open('xb') as so, stderr.open('xb') as se:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=so, stderr=se, start_new_session=True)
            rc = proc.wait(timeout=max(0.001, deadline - 0.2))
            status = 'COMPLETE' if rc == 0 else 'FAILED'
    except subprocess.TimeoutExpired:
        status, error = 'TIMED_OUT', 'process deadline reached'
    except KeyboardInterrupt:
        status, error = 'INTERRUPTED', 'controller interrupted'
    except OSError as exc:
        status, error = 'FAILED', 'failed start or IO: ' + str(exc)
    finally:
        try:
            if proc is not None:
                kill(proc)
                rc = proc.returncode
        finally:
            signal.signal(signal.SIGTERM, previous_handler)
    elapsed = time.monotonic() - begin
    # Never conceal cleanup/OS scheduling cost by clipping elapsed time.
    if elapsed > deadline:
        status, error = 'TIMED_OUT', 'elapsed including cleanup exceeded reservation'
    result = {'status': status, 'returncode': rc, 'charged_seconds': elapsed,
              'started_at': started, 'ended_at': now(), **log_receipt(stdout, stderr)}
    if error:
        result['error'] = error
    return result


def inventory(root, build):
    rows = []
    if not build.exists():
        return rows
    for p in sorted(build.rglob('*')):
        require(not p.is_symlink(), 'output symlink')
        if p.is_file():
            rows.append({'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha(p)})
        else:
            require(p.is_dir(), 'nonregular output')
    return rows


def verify_prior_outputs(root, state, build=None, seed=None):
    expected = list(seed or [])
    for n, row in state.items():
        if n and row.get('terminal', {}).get('status') == 'COMPLETE':
            outputs = row['terminal'].get('outputs')
            require(isinstance(outputs, list) and outputs, 'completed dependency lacks output receipt')
            expected.extend(outputs)
    require(len({r['path'] for r in expected}) == len(expected), 'duplicate output binding')
    for row in expected:
        require(set(row) == {'path', 'bytes', 'sha256'}, 'invalid output receipt')
        p = safe(root, row['path'])
        require(p.is_file() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'],
                'completed output changed')
    if build is not None:
        verify_output_set(root, build, expected)
    return expected


def preflight(root, path):
    root = Path(root).resolve()
    owner = lock(safe(root, OUT + '/execution/controller.lock', False))
    try:
        require(not safe(root, OUT + '/execution/stop.json', False).exists(),
                'recorded first control stop; not ready')
        m, order, modules = validate_manifest(root, path, False)
        gate(root)
        runtime(root, m)
        donors(m, modules)
        seed_inputs(root, m)
        attempt_budget(js(bind(root, m['work_record'])), {}, datetime.now(timezone.utc))
        return {'item_id': ITEM, 'run_id': RUN, 'module_count': len(order), 'compiler_launches': 0}
    finally:
        owner.close()


def durable_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def execute(root, path, resume=False):
    root, path = Path(root).resolve(), Path(path).resolve()
    owner = lock(safe(root, OUT + '/execution/controller.lock', False))
    stop_path = safe(root, OUT + '/execution/stop.json', False)
    try:
        require(not stop_path.exists(), 'recorded first control stop; no retry')
        m, order, modules = validate_manifest(root, path, True)
        ld, workspace = ldir(root, m), safe(root, BASE, False)
        ep, marker = ld / 'events.jsonl', ld / 'start.json'
        exists = marker.exists() or ep.exists() or workspace.exists()
        require(resume == exists, 'resume mismatch or preexisting workspace')
        if exists:
            require(marker.is_file() and ep.is_file() and workspace.is_dir(), 'missing durable start/ledger/workspace')
            identity = js(marker)
            require(identity['manifest_sha256'] == sha(path) and identity['run_id'] == RUN,
                    'start identity changed')
            require(js(workspace / '.preparation.json') == identity, 'workspace identity changed')
            events = read_events(ep)
            require(events, 'missing or empty ledger cannot reset')
            state = derive(events)
            for n, row in state.items():
                require(n == 0 or row['module'] == order[n - 1], 'ledger module differs')
            # Reconcile an orphan before inspecting mutable payloads. It is a
            # charged terminal failure, never permission to launch again.
            orphans = [r for r in state.values() if 'terminal' not in r]
            if orphans:
                for row in orphans:
                    append(ep, {'kind': 'TERMINAL', 'number': row['number'], 'status': 'INTERRUPTED',
                                'charged_seconds': row['reserved_seconds'], 'at': now(),
                                'reason': 'orphan reservation conservatively charged'})
                return 1
            if any(n and r['terminal']['status'] != 'COMPLETE' for n, r in state.items()):
                return 1
        else:
            # All donors and runtime must pass before any materialization.
            runtime(root, m)
            donors(m, modules)
            seed_inputs(root, m)
            attempt_budget(js(bind(root, m['work_record'])), {}, datetime.now(timezone.utc))
            identity = {'run_id': RUN, 'manifest_sha256': sha(path), 'started_at': now(),
                        'checkpoint_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()}
            durable_json(marker, identity)
            workspace.mkdir(parents=True)
            durable_json(workspace / '.preparation.json', identity)
            append(ep, {'kind': 'RESERVED', 'number': 0, 'module': 'START', 'reserved_seconds': 0, 'at': now()})
            append(ep, {'kind': 'TERMINAL', 'number': 0, 'status': 'COMPLETE', 'charged_seconds': 0, 'at': now()})
            materialize(root, m, modules)
            state = derive(read_events(ep))
        build = safe(root, m['materialization']['build_root'])
        runtime(root, m)
        check_sources(root, m, modules)
        verify_prior_outputs(root, state, build, m['seed_outputs'])
        for n, module in enumerate(order, 1):
            if n in state:
                continue
            # Every immutable/controller/source/runtime/output input is checked
            # under one lock immediately before reservation and spawn.
            validate_manifest(root, path, True)
            runtime(root, m)
            donors(m, modules)
            seed_inputs(root, m)
            check_sources(root, m, modules)
            previous_outputs = verify_prior_outputs(root, state, build, m['seed_outputs'])
            deadline = attempt_budget(js(bind(root, m['work_record'])), state, datetime.now(timezone.utc))
            src = safe(root, m['materialization']['source_root'])
            out = build / (module.replace('.', '/') + '.olean')
            out.parent.mkdir(parents=True, exist_ok=True)
            logs = ld / 'logs'
            logs.mkdir(exist_ok=True)
            stdout, stderr = logs / f'{n:02d}.stdout', logs / f'{n:02d}.stderr'
            argv = [m['compiler']['path'], '-o', str(out), module.replace('.', '/') + '.lean']
            reserved = {'kind': 'RESERVED', 'number': n, 'module': module, 'reserved_seconds': deadline,
                        'argv': argv, 'cwd': str(src), 'env': m['compiler']['env'],
                        'stdout': str(stdout.relative_to(root)), 'stderr': str(stderr.relative_to(root)),
                        'source_sha256': modules[module]['source']['sha256'],
                        'runtime_manifest_sha256': m['runtime_manifest']['sha256'],
                        'prior_outputs': previous_outputs, 'at': now(),
                        'deadline_at': (datetime.now(timezone.utc) + timedelta(seconds=deadline)).isoformat()}
            append(ep, reserved)
            term = run_process(argv, src, m['compiler']['env'], stdout, stderr, deadline)
            term.update(kind='TERMINAL', number=n)
            try:
                actual = inventory(root, build)
                known = {r['path']: r for r in previous_outputs}
                require(all(r in actual for r in previous_outputs), 'prior output changed during compile')
                new = [r for r in actual if r['path'] not in known]
                stem = str((build / module.replace('.', '/')).relative_to(root))
                require(all(r['path'].startswith(stem + '.') for r in new), 'output outside reserved module')
                term['outputs'] = new
                require(term['status'] != 'COMPLETE' or str(out.relative_to(root)) in {r['path'] for r in new},
                        'required olean missing')
            except (OSError, ValueError) as error:
                term['status'], term['output_binding_error'] = 'FAILED', str(error)
                # Retain a forensic listing without treating partial products as
                # successful dependency inputs.
                term['partial_paths'] = [str(p.relative_to(root)) for p in sorted(build.rglob('*'))]
                try:
                    term['partial_outputs'] = inventory(root, build)
                except (OSError, ValueError) as binding_error:
                    term['partial_inventory_error'] = str(binding_error)
            append(ep, term)
            print(json.dumps({'attempt': n, 'module': module, 'status': term['status'],
                              'seconds': term['charged_seconds']}), flush=True)
            if term['status'] != 'COMPLETE':
                return 1
            state = derive(read_events(ep))
        runtime(root, m)
        check_sources(root, m, modules)
        verify_prior_outputs(root, state, build, m['seed_outputs'])
        return 0
    except (ValueError, OSError, KeyError, KeyboardInterrupt) as error:
        # A pre-reservation identity/control failure is still terminal. Restoring
        # the input later must not turn this stopped run into permission to retry.
        if not stop_path.exists():
            durable_json(stop_path, {'run_id': RUN, 'status': 'CONTROL_STOP', 'at': now(),
                                     'error_type': type(error).__name__, 'reason': str(error)})
        raise
    finally:
        owner.close()
