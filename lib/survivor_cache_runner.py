"""One fixed source-mutant comparison with durable, finite launch accounting.

Trusted local source/filesystem and the OS are assumptions, not a sandbox.
Historical attempts retain their committed manifest and tooling identities.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from lib.cvc_prep import require, safe, bind, committed, lock, append, read_events
from lib.cvc_process import atomic, now, run_process, sha
from lib.cvc_signal_retry import signal_retry

ITEM = 'SURVIVOR-CACHE-1'
RUN = 'survivor-cache-0001'
BASE = 'results/research/survivor-cache-1'
OUT = BASE + '/run-0001'
WORK = BASE + '/work-record.json'
MANIFEST = 'config/survivor-cache-0001.json'
REVISION = '6ae1f0cd962f081f6c423454c5da729d841236a7'
MUTANT = 'nanoda-gen-3365809b3c41'
PROFILES = ('baseline', 'mutant')
SOURCE_ROOTS = {p: 'external/survivor-cache-0001-' + p for p in PROFILES}
TARGET_ROOTS = {p: SOURCE_ROOTS[p] + '-target' for p in PROFILES}
LIMITS = {'active_seconds': 5400, 'offline_build_reservations': 2,
          'per_build_seconds': 120, 'checker_reservations': 8,
          'per_checker_seconds': 30, 'fixed_pairs': 2,
          'research_network_requests': 0, 'proof_launches': 0,
          'external_research_actions': 0}
CODE = ['lib/survivor_cache_runner.py', 'scripts/execute-survivor-cache',
        'tests/test_survivor_cache_runner.py', 'lib/cvc_process.py',
        'lib/cvc_signal_retry.py', 'lib/cvc_prep.py',
        'lib/survivor_let_payload.py', 'lib/research_queue.py',
        'lib/research_queue_v2.py', 'lib/research_queue_v3.py']
SCIENCE_KEYS = ['work_record', 'entry_decision', 'source_materialization',
                'runtime_manifest', 'mutation_spec', 'source_lock', 'harness',
                'tests', 'observer_environment']
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'RUST_BACKTRACE': 'full'}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def strict_json(data):
    def invalid_constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=strict_object, parse_constant=invalid_constant)


def load(p):
    return strict_json(Path(p).read_text())


def binding(root, p):
    p = Path(p)
    return {'path': str(p.relative_to(root)), 'sha256': sha(p)}


def finite(x):
    return type(x) in (int, float) and math.isfinite(x) and x >= 0


def package_has_payload(package):
    absent = package['source'] is None and package['archive'] is None
    require(absent or (package['source'] is not None and package['archive'] is not None),
            'offline package binding is half-present')
    return not absent


def active_seconds(work, monotonic=None, utc=None):
    mono = time.monotonic() if monotonic is None else monotonic
    utc = datetime.now(timezone.utc) if utc is None else utc
    intervals = work['intervals']
    require(intervals and len([i for i in intervals if 'ended_monotonic' not in i]) == 1
            and 'ended_monotonic' not in intervals[-1], 'work needs one final active interval')
    charged = work['entry_overhead_conservative_seconds']
    require(finite(charged) and charged >= 120, 'invalid conservative overhead')
    previous_end = None
    for interval in intervals:
        start = datetime.fromisoformat(interval['started_at'])
        end = datetime.fromisoformat(interval['ended_at']) if 'ended_at' in interval else utc
        end_mono = interval.get('ended_monotonic', mono)
        require(start.tzinfo is not None and end.tzinfo is not None
                and finite(interval['started_monotonic']) and finite(end_mono), 'invalid work clock')
        md, ud = end_mono - interval['started_monotonic'], (end - start).total_seconds()
        require(md >= 0 and ud >= 0 and abs(md - ud) <= 5, 'work clocks disagree or rebooted')
        require(previous_end is None or interval['started_monotonic'] >= previous_end, 'work intervals overlap')
        previous_end = end_mono
        charged += max(md, ud)
    return charged


def gate(root, seconds=0):
    from lib.research_queue_v3 import load_queue
    q = load_queue(root, require_ready=True)
    row = next(r for r in q['items'] if r['id'] == ITEM)
    require(q['selected_item'] == ITEM and row['status'] == 'ACTIVE', 'G1: item not selected ACTIVE')
    w = load(root / WORK)
    require(w['item_id'] == ITEM and w['status'] == 'ACTIVE'
            and w['owner'] == 'root' and w['authorization']
            and w['budget'] == {'active_seconds': 5400, 'mutant_id': MUTANT,
                'build_launches': 2, 'checker_launches': 8, 'scientific_pairs': 2,
                'external_writes': 0}, 'G1: no exact bounded execution authority')
    used = active_seconds(w)
    require(used + seconds <= 5400, 'active-time cap cannot cover reservation')
    require(not (root / BASE / 'work-closure.json').exists(), 'item work already closed')
    return 5400 - used


def manifest_path(root, name):
    require(re.fullmatch(r'config/survivor-cache-0001(?:-r[2-9][0-9]*)?\.json', name),
            'wrong manifest path')
    return safe(root, name)


def validate_manifest(root, name=MANIFEST, launch=False, payload=True):
    root = Path(root).resolve()
    m = load(manifest_path(root, name))
    expected = {'schema_version', 'item_id', 'run_id', 'limits', 'tooling_inputs',
                'focused_test_receipt', *SCIENCE_KEYS}
    require(set(m) == expected and m['schema_version'] == 1 and m['item_id'] == ITEM
            and m['run_id'] == RUN and m['limits'] == LIMITS, 'wrong manifest or limits')
    required = {'work_record': WORK, 'entry_decision': BASE + '/entry-decision.json',
                'source_materialization': BASE + '/source-materialization.json',
                'runtime_manifest': BASE + '/runtime-manifest.json',
                'mutation_spec': 'mutations/' + MUTANT + '.json',
                'source_lock': BASE + '/source-lock.json',
                'harness': BASE + '/cache-contract-tests.rs'}
    for key, path in required.items():
        require(m[key]['path'] == path, 'wrong fixed binding: ' + key)
        bind(root, m[key])
    decision = load(root / m['entry_decision']['path'])
    require(decision['execution_authorized'] is True and decision['item_id'] == ITEM,
            'execution decision does not authorize item')
    require(m['observer_environment'] == ENV, 'observer environment differs')
    require(set(m['tests']) == {'control', 'candidate'}, 'wrong fixed test inventory')
    for role in ('control', 'candidate'):
        test = m['tests'][role]
        require(test['name'] == 'tc::cache_contract_tests::' + role, 'wrong exact test name')
        require(set(test) == ({'name'} if role == 'control' else
                {'name', 'failure_message', 'failure_location'}), 'wrong test contract')
    candidate = m['tests']['candidate']
    require(type(candidate['failure_message']) is str and candidate['failure_message']
            and candidate['failure_message'].isascii()
            and re.fullmatch(r'src/tc\.rs:[0-9]+:[0-9]+', candidate['failure_location']),
            'missing source-specific regression assertion')
    require([r['path'] for r in m['tooling_inputs']] == CODE, 'incomplete tooling binding')
    all_rows = m['tooling_inputs'] + [m[k] for k in required] + [m['focused_test_receipt']]
    for row in all_rows:
        bind(root, row)
        if launch:
            committed(root, row['path'])
    test = load(bind(root, m['focused_test_receipt']))
    require(test['status'] == 'PASS' and test['tooling_inputs'] == m['tooling_inputs']
            and type(test['test_count']) is int and test['test_count'] >= 15
            and test['real_process_launches'] == 0 and type(test['logs']) is list and test['logs'],
            'focused tests do not bind current tooling')
    for row in test['logs']:
        bind(root, row)
        if launch:
            committed(root, row['path'])
    if name != MANIFEST:
        first = load(manifest_path(root, MANIFEST))
        require(all(m[k] == first[k] for k in SCIENCE_KEYS) and m['limits'] == first['limits'],
                'repair revision changes science, authority or budget')
    if payload:
        verify_payload(root, m)
    if launch:
        gate(root)
        for p in (name, 'config/research-queue.json', 'docs/RESEARCH_STATUS.md',
                  'docs/research/SURVIVOR_CACHE_PLAN.md'):
            committed(root, p)
    return m


def verify_payload(root, m):
    """Read-only exact two-source/two-runtime verification; never compiles."""
    from lib.survivor_let_payload import tree_binding, lock_packages, bind as rich_binding
    source = load(bind(root, m['source_materialization']))
    runtime = load(bind(root, m['runtime_manifest']))
    source_lock = load(bind(root, m['source_lock']))
    spec = load(bind(root, m['mutation_spec']))
    harness = bind(root, m['harness']).read_bytes()
    require(spec['id'] == MUTANT and spec['source_file'] == 'src/tc.rs'
            and spec['source_span'] == '483' and spec['replace_occurrence'] == 0
            and spec['original'] == 'flag == InferFlag::InferOnly'
            and spec['mutated'] == '(flag != InferFlag::InferOnly)', 'wrong canonical mutation')
    require(source['revision'] == source_lock['revision'] == REVISION
            and source['source_roots'] == SOURCE_ROOTS and source['harness'] == m['harness']
            and source['patch'] == {'path': 'src/tc.rs', 'line': 483, 'occurrence': 0,
                'original': spec['original'], 'mutated': spec['mutated']}, 'source selection drift')
    require(runtime['source'] == source and set(runtime['environments']) == set(PROFILES),
            'runtime/source mismatch')
    require(set(source['files_after_patch']) == set(PROFILES), 'source profile inventory drift')
    for profile in PROFILES:
        source_root = safe(root, SOURCE_ROOTS[profile])
        expected_paths = {row['source_path'] for row in source_lock['files']}
        require(len(expected_paths) == len(source_lock['files']) and expected_paths ==
                {p.relative_to(source_root).as_posix() for p in source_root.rglob('*') if p.is_file()},
                'source inventory drift')
        require(len(source['files_after_patch'][profile]) == len(source_lock['files']), 'source binding inventory drift')
        after = {row['path']: row for row in source['files_after_patch'][profile]}
        require(len(after) == len(source['files_after_patch'][profile]), 'duplicate source binding')
        for row in source_lock['files']:
            original = safe(root, row['binding']['path'])
            require(rich_binding(root, original) == row['binding'], 'canonical donor drift')
            target = safe(root, SOURCE_ROOTS[profile] + '/' + row['source_path'])
            require(rich_binding(root, target) == after[str(target.relative_to(root))], 'materialized hash drift')
            expected = original.read_bytes()
            if row['source_path'] == 'src/tc.rs':
                lines = expected.splitlines(keepends=True)
                require(lines[482].count(spec['original'].encode()) == 1, 'canonical mutation site differs')
                if profile == 'mutant':
                    lines[482] = lines[482].replace(spec['original'].encode(), spec['mutated'].encode(), 1)
                expected = b''.join(lines) + harness
            require(target.read_bytes() == expected, 'source differs beyond fixed harness and single mutation')
    tools = runtime['tools']
    require(set(tools) == {'cargo', 'rustc', 'cc', 'rustlib'}, 'runtime tool inventory differs')
    cargo = Path(tools['cargo']['path'])
    require(cargo.is_absolute() and cargo.name == 'cargo', 'wrong cargo path')
    builds = {}
    for profile in PROFILES:
        env = runtime['environments'][profile]
        require(env == {'HOME': str(Path.home()), 'CARGO_HOME': env.get('CARGO_HOME'),
                'CARGO_TARGET_DIR': str(root / TARGET_ROOTS[profile]), 'RUSTC': str(cargo.parent / 'rustc'),
                'CARGO_NET_OFFLINE': 'true', 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin:' + str(cargo.parent),
                'RUST_BACKTRACE': 'full'}, 'build environment drift')
        cargo_home = Path(env['CARGO_HOME'])
        require(cargo_home.is_absolute() and cargo_home.is_dir()
                and cargo_home.resolve().is_relative_to(root / 'external'), 'unisolated Cargo home')
        source_root = root / SOURCE_ROOTS[profile]
        for ancestor in [source_root, *source_root.parents, cargo_home]:
            for name in ('config', 'config.toml'):
                location = ancestor / (name if ancestor == cargo_home else '.cargo/' + name)
                require(not location.exists(), 'unexpected Cargo configuration: ' + str(location))
        builds[profile] = {'argv': [str(cargo), 'test', '--release', '--locked', '--offline',
                            '--lib', '--no-run', '--message-format=json'],
                          'cwd': str(source_root), 'env': env}
    require(tree_binding(root, root / runtime['registry_index']['path']) == runtime['registry_index'], 'registry index drift')
    locked = lock_packages(root / SOURCE_ROOTS['baseline'] / 'Cargo.lock')
    require({(p['name'], p['version']): p['lock_checksum'] for p in runtime['locked_packages']} == locked,
            'runtime package identities changed')
    reuse = runtime['reuse']
    require(set(reuse) == {'path', 'sha256', 'decision'}, 'runtime reuse binding malformed')
    predecessor = load(bind(root, {key: reuse[key] for key in ('path', 'sha256')}))
    require(runtime['locked_packages'] == predecessor['locked_packages']
            and runtime['registry_index'] == predecessor['registry_index']
            and runtime['tools'] == predecessor['tools'], 'inherited offline runtime differs')
    for package in runtime['locked_packages']:
        if not package_has_payload(package):
            continue
        require(package['archive']['sha256'] == package['lock_checksum'], 'archive lock mismatch')
        for kind in ('source', 'archive'):
            row = package[kind]
            actual = tree_binding(root, root / row['path']) if kind == 'source' else rich_binding(root, root / row['path'])
            require(actual == row, 'offline package drift')
    for name, row in tools.items():
        actual = tree_binding(root, Path(row['path'])) if name == 'rustlib' else rich_binding(root, Path(row['path']))
        require(actual == row, 'tool/runtime identity drift')
    require(tools['rustc']['path'] == str(cargo.parent / 'rustc') and tools['cc']['path'] == '/usr/bin/cc',
            'runtime tool command drift')
    return builds


def derive(events):
    require(events and events[0]['kind'] == 'START' and events[0]['run_id'] == RUN,
            'missing start')
    attempts, repairs = [], []
    for event in events[1:]:
        kind = event['kind']
        if kind == 'RESERVED':
            require(not attempts or 'terminal' in attempts[-1], 'unreconciled reservation')
            require(type(event['number']) is int and event['number'] == len(attempts) + 1
                    and type(event.get('cell')) is int, 'nonconsecutive reservation or invalid cell')
            phase = event['phase']
            require(phase in {'build', 'checker'}, 'unknown process phase')
            limit, seconds = (2, 120) if phase == 'build' else (8, 30)
            require(sum(a['reservation']['phase'] == phase for a in attempts) < limit
                    and event['reserved_seconds'] == seconds, 'reservation cap')
            action = next_action(attempts, repairs)
            require(action == (phase, event.get('cell')), 'launch violates build/control/repair order')
            require(finite(event['active_seconds']) and event['active_seconds'] + seconds <= 5400,
                    'invalid active budget reservation')
            attempts.append({'reservation': event})
        elif kind == 'TERMINAL':
            require(attempts and 'terminal' not in attempts[-1]
                    and event['number'] == len(attempts), 'terminal without latest reservation')
            require(event['status'] in {'COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED'}
                    and finite(event['charged_seconds']), 'invalid terminal cost/status')
            require(type(event.get('cleanup_completed')) is bool and type(event.get('engineering_pause')) is bool,
                    'missing cleanup/audit state')
            if attempts[-1]['reservation']['phase'] == 'checker':
                require(event.get('classification') in {'TEST_PASS', 'REGRESSION_FAILURE', 'TIMEOUT', 'INDETERMINATE'},
                        'unknown test classification')
                require(event.get('classification') not in {'TIMEOUT', 'INDETERMINATE'} or event['engineering_pause'],
                        'unrecognized output must pause')
            require(event['cleanup_completed'] or event['engineering_pause'], 'cleanup failure must pause')
            attempts[-1]['terminal'] = event
        elif kind == 'REPAIR':
            require(attempts and 'terminal' in attempts[-1]
                    and event['after_number'] == len(attempts)
                    and (not repairs or repairs[-1]['after_number'] != len(attempts)), 'invalid repair')
            require(next_action(attempts, repairs) == ('PAUSED', None), 'repair without engineering pause')
            require(event['phase'] == attempts[-1]['reservation']['phase']
                    and event.get('cell') == attempts[-1]['reservation'].get('cell'), 'repair changes cell')
            repairs.append(event)
        else:
            raise ValueError('unknown ledger event')
    return {'attempts': attempts, 'repairs': repairs,
            'next_action': next_action(attempts, repairs),
            'charged_seconds': sum(a.get('terminal', {}).get('charged_seconds',
                                   a['reservation']['reserved_seconds']) for a in attempts)}


def next_action(attempts, repairs):
    if not attempts:
        return ('build', 0)
    last = attempts[-1]
    if 'terminal' not in last:
        return ('PAUSED', None)
    if repairs and repairs[-1]['after_number'] == len(attempts):
        return (repairs[-1]['phase'], repairs[-1].get('cell'))
    r, t = last['reservation'], last['terminal']
    if t.get('engineering_pause') or not t.get('cleanup_completed'):
        return ('PAUSED', None)
    if r['phase'] == 'build':
        return (('build', 1) if r['cell'] == 0 else ('checker', 0)) if t['status'] == 'COMPLETE' and t.get('binary') else ('PAUSED', None)
    c = r['cell']
    if c < 3 and t['classification'] != 'TEST_PASS':
        return ('STOP', None)
    return ('DONE', None) if c == 3 else ('checker', c + 1)


class Ledger:
    def __init__(self, root):
        self.root = Path(root)
        self.directory = self.root / OUT / 'execution'
        self.path = self.directory / 'events.jsonl'
        self.snapshot = self.directory / 'state.json'

    def initialize(self):
        require(not self.directory.exists(), 'refuse reset of run directory')
        self.directory.mkdir(parents=True)
        append(self.path, {'kind': 'START', 'run_id': RUN, 'at': now(), 'monotonic': time.monotonic()})
        self.save()

    def save(self):
        events = read_events(self.path)
        atomic(self.snapshot, {'count': len(events), 'tail': events[-1]['event_sha256']})

    def read(self):
        events = read_events(self.path)
        s = load(self.snapshot)
        require(type(s['count']) is int and 1 <= s['count'] <= len(events)
                and events[s['count'] - 1]['event_sha256'] == s['tail'], 'ledger truncation/reset')
        return events, derive(events)

    def add(self, event):
        events, _ = self.read()
        derive(events + [event])
        append(self.path, event)
        self.save()


def matrix(m):
    return [{'id': role + '-' + observer, 'input': role, 'observer': observer}
            for role, observer in [('control', 'baseline'), ('control', 'mutant'),
                                   ('candidate', 'baseline'), ('candidate', 'mutant')]]


def classify(cell, tests, rec, stdout, stderr):
    if rec['status'] == 'TIMED_OUT':
        return 'TIMEOUT'
    if not rec.get('cleanup_completed') or rec.get('deadline_exceeded') or rec.get('error'):
        return 'INDETERMINATE'
    test = tests[cell['input']]
    name = re.escape(test['name'].encode())
    seconds = rb'[0-9]+(?:\.[0-9]+)?'
    passed = (rb'\nrunning 1 test\ntest ' + name + rb' \.\.\. ok\n\n'
              rb'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; '
              rb'[0-9]+ filtered out; finished in ' + seconds + rb's\n\n')
    if (rec['status'] == 'COMPLETE' and rec['returncode'] == 0 and stderr == b''
            and re.fullmatch(passed, stdout)):
        return 'TEST_PASS'
    if cell['input'] == 'candidate' and rec['status'] == 'FAILED' and rec['returncode'] == 101 and stderr == b'':
        # Full libtest envelope plus source-bound explicit assertion. The stack
        # body can contain runtime address/frame variation, but never another
        # panic/test or altered failure assertion.
        prefix = b'\nrunning 1 test\ntest ' + test['name'].encode() + b' ... FAILED\n\nfailures:\n\n---- ' + test['name'].encode() + b' stdout ----\n'
        suffix = (rb'\n\nfailures:\n    ' + name + rb'\n\ntest result: FAILED\. '
                  rb'0 passed; 1 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in '
                  + seconds + rb's\n\n')
        body = stdout[len(prefix):] if stdout.startswith(prefix) else b''
        ending = re.search(suffix, body)
        if ending:
            body = body[:ending.start()]
            panic = (rb"\nthread '" + name + rb"' \([0-9]+\) panicked at "
                     + re.escape(test['failure_location'].encode()) + rb':\n'
                     + re.escape(test['failure_message'].encode()) + rb'\n')
            if re.match(panic, body) and body.count(b'panicked at ') == 1:
                trace = body[re.match(panic, body).end():]
                if trace.startswith(b'stack backtrace:\n') and b'::check_declar' not in trace:
                    return 'REGRESSION_FAILURE'
    return 'INDETERMINATE'


def build_artifact(root, reservation, stdout):
    profile = PROFILES[reservation['cell']]
    artifacts = []
    finished = []
    for line in stdout.splitlines():
        row = strict_json(line)
        require(type(row) is dict and row.get('reason') in
                {'compiler-artifact', 'compiler-message', 'build-script-executed', 'build-finished'},
                'malformed Cargo message stream')
        if row['reason'] == 'build-finished':
            finished.append(row)
        if row['reason'] == 'compiler-artifact' and row.get('executable'):
            require(row['profile']['test'] is True and 'lib' in row['target']['kind']
                    and row['target']['src_path'] == str(root / SOURCE_ROOTS[profile] / 'src/lib.rs'),
                    'unexpected executable Cargo artifact')
            artifacts.append(row)
    require(len(artifacts) == 1 and len(finished) == 1 and finished[0].get('success') is True,
            'missing/extra executable library-test artifact')
    path = Path(artifacts[0]['executable'])
    require(path.is_absolute() and path.is_relative_to(root / TARGET_ROOTS[profile] / 'release/deps')
            and path.is_file() and not path.is_symlink(), 'test artifact outside fixed target')
    return path


def process_absent(directory):
    marker = directory / 'process.json'
    require(marker.is_file(), 'unknown child identity; reconciliation required')
    p = load(marker)
    for pid, group in ((p['pid'], True), (p['supervisor_pid'], False)):
        try:
            (os.killpg if group else os.kill)(pid, 0)
        except ProcessLookupError:
            continue
        except PermissionError as exc:
            raise ValueError('cannot establish process absence') from exc
        raise ValueError('process or group still present')


def finish_attempt(root, reservation):
    d = root / reservation['directory']
    rec = load(d / 'supervisor.json')
    request = load(d / 'request.json')
    require(rec['request_sha256'] == request['request_sha256'], 'wrong supervisor request')
    require(request['argv'] == reservation['argv'] and request['cwd'] == reservation['cwd']
            and request['env'] == reservation['env'] and request['seconds'] == reservation['reserved_seconds'],
            'supervisor request differs from reservation')
    require(rec['stdout_sha256'] == sha(d / 'stdout') and rec['stderr_sha256'] == sha(d / 'stderr'), 'raw log drift')
    require(finite(rec['charged_seconds']) and rec['monotonic_ended'] >= rec['monotonic_started']
            and abs(rec['charged_seconds'] - (rec['monotonic_ended'] - rec['monotonic_started'])) < .1,
            'invalid process accounting')
    phase = reservation['phase']
    t = {'kind': 'TERMINAL', 'number': reservation['number'], 'status': rec['status'],
         'returncode': rec['returncode'], 'charged_seconds': rec['charged_seconds'],
         'cleanup_completed': rec['cleanup_completed'], 'at': now(),
         'engineering_pause': bool(rec.get('error') or not rec['cleanup_completed'] or rec['deadline_exceeded']),
         'receipts': [binding(root, d / n) for n in ('request.json', 'supervisor.json', 'stdout', 'stderr')]}
    if phase == 'build':
        t['engineering_pause'] |= rec['status'] != 'COMPLETE'
        if rec['status'] == 'COMPLETE' and not t['engineering_pause']:
            try:
                path = build_artifact(root, reservation, (d / 'stdout').read_bytes())
            except (ValueError, KeyError, TypeError) as error:
                t['engineering_pause'] = True
                t['artifact_audit_error'] = type(error).__name__ + ': ' + str(error)
                return t
            require(path.is_file() and not path.is_symlink(), 'missing selected build output')
            product = root / ('external/survivor-cache-0001-products/build-' + str(reservation['number'])) / 'test-binary'
            require(not product.exists(), 'immutable build product already exists')
            product.parent.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(path, product)
            product.chmod(0o555)
            require(sha(product) == sha(path), 'build product changed during copy')
            t['binary'] = binding(root, product)
            t['build_output_sha256'] = sha(path)
    else:
        m = load(root / reservation['manifest']['path'])
        cell = matrix(m)[reservation['cell']]
        t['classification'] = classify(cell, m['tests'], rec, (d / 'stdout').read_bytes(), (d / 'stderr').read_bytes())
        # Unknown output needs an audit repair, not a scientific negative.
        t['engineering_pause'] |= t['classification'] in {'INDETERMINATE', 'TIMEOUT'}
    return t


def verify_attempts(root, events, live=False):
    state = derive(events)
    for attempt in state['attempts']:
        r = attempt['reservation']
        bind(root, r['manifest'])
        require(r['directory'] == OUT + '/attempts/' + f"{r['number']:02d}", 'wrong attempt directory')
        # Reproduce original source/tooling bindings from this attempt's Git tree.
        m = load(root / r['manifest']['path'])
        for row in m['tooling_inputs'] + [m['focused_test_receipt']]:
            data = subprocess.check_output(['git', 'show', r['commit'] + ':' + row['path']], cwd=root)
            import hashlib
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'historical tooling mismatch')
        if 'terminal' not in attempt:
            continue
        t = attempt['terminal']
        for row in t['receipts']:
            bind(root, row)
        raw = load(root / r['directory'] / 'supervisor.json')
        require(t['status'] == raw['status'] and t['charged_seconds'] == raw['charged_seconds']
                and t['returncode'] == raw['returncode']
                and t['cleanup_completed'] == raw['cleanup_completed'], 'terminal differs from raw receipt')
        request = load(root / r['directory'] / 'request.json')
        require(request['argv'] == r['argv'] and request['cwd'] == r['cwd']
                and request['env'] == r['env'] and request['seconds'] == r['reserved_seconds']
                and request['request_sha256'] == raw['request_sha256'], 'request/reservation mismatch')
        import hashlib
        checksum = request['request_sha256']
        canonical_request = {k: v for k, v in request.items() if k != 'request_sha256'}
        require(hashlib.sha256(json.dumps(canonical_request, sort_keys=True).encode()).hexdigest() == checksum,
                'request checksum mismatch')
        d = root / r['directory']
        require(sha(d / 'stdout') == raw['stdout_sha256'] and sha(d / 'stderr') == raw['stderr_sha256'],
                'raw outcome checksum mismatch')
        if r['phase'] == 'checker':
            require(len(t['receipts']) == 4 and {v['path'] for v in t['receipts']} ==
                    {str((d / n).relative_to(root)) for n in ('request.json', 'supervisor.json', 'stdout', 'stderr')},
                    'missing raw outcome bindings')
            cell = matrix(m)[r['cell']]
            tests = m['tests']
            require(r['argv'][1:] == ['--exact', tests[cell['input']]['name'], '--test-threads=1']
                    and r['cwd'] == str(root) and r['env'] == m['observer_environment'], 'cell command drift')
            expected_binary = next(a['terminal']['binary'] for a in state['attempts'][:r['number'] - 1]
                    if a['reservation']['phase'] == 'build' and PROFILES[a['reservation']['cell']] == cell['observer']
                    and a.get('terminal', {}).get('binary'))
            require(r['argv'][0] == str(root / expected_binary['path']), 'wrong cell binary')
            # If tooling later changes, replay the original committed normalizer
            # in its own historical validation context; never reinterpret here.
            current_normalizer = next(x for x in m['tooling_inputs'] if x['path'] == 'lib/survivor_cache_runner.py')
            if sha(root / current_normalizer['path']) == current_normalizer['sha256']:
                require(t['classification'] == classify(cell, tests, raw, (d / 'stdout').read_bytes(),
                                                        (d / 'stderr').read_bytes()), 'normalized outcome drift')
            else:
                data = subprocess.check_output(['git', 'show', r['commit'] + ':lib/survivor_cache_runner.py'], cwd=root)
                namespace = {'__name__': 'historical_survivor_normalizer'}
                exec(compile(data, '<bound historical normalizer>', 'exec'), namespace)
                require(t['classification'] == namespace['classify'](cell, tests, raw, (d / 'stdout').read_bytes(),
                                                                    (d / 'stderr').read_bytes()), 'historical normalized drift')
        if t.get('binary') and live:
            bind(root, t['binary'])
    return state


def execute(root, name=MANIFEST, repair_record=None, reconcile=False):
    root = Path(root).resolve()
    m = validate_manifest(root, name, launch=True)
    out = root / OUT
    with lock(out / 'controller.lock'):
        ledger = Ledger(root)
        if not ledger.directory.exists():
            ledger.initialize()
        events, state = ledger.read()
        verify_attempts(root, events, live=True)
        if reconcile:
            require(state['attempts'] and 'terminal' not in state['attempts'][-1], 'no orphan to reconcile')
            r = state['attempts'][-1]['reservation']
            process_absent(root / r['directory'])
            ledger.add(finish_attempt(root, r))
            return ledger.read()[1]
        if repair_record:
            p = safe(root, repair_record)
            require(p.parent == out / 'repairs', 'repair record outside fixed run')
            committed(root, repair_record)
            rr = load(p)
            require(rr['item_id'] == ITEM and rr['ledger_tail'] == events[-1]['event_sha256']
                    and rr['reason'] and rr['manifest'] == binding(root, root / name), 'unbound repair')
            require(name != MANIFEST, 'repair requires new exact tooling manifest revision')
            require(state['attempts'] and 'terminal' in state['attempts'][-1], 'orphan needs receipt reconciliation first')
            last = state['attempts'][-1]['reservation']
            previous = load(bind(root, last['manifest']))
            require(m['tooling_inputs'] != previous['tooling_inputs']
                    and m['focused_test_receipt'] != previous['focused_test_receipt'],
                    'repair must bind changed tested tooling')
            require(type(rr.get('regression_evidence')) is list and rr['regression_evidence'],
                    'repair needs regression evidence')
            for row in rr['regression_evidence']:
                bind(root, row)
                committed(root, row['path'])
            process_absent(root / last['directory'])
            ledger.add({'kind': 'REPAIR', 'after_number': last['number'], 'phase': last['phase'],
                        'cell': last.get('cell'), 'record': binding(root, p), 'at': now()})
            events, state = ledger.read()
        action, cell_index = state['next_action']
        require(action not in {'PAUSED', 'STOP'}, 'launch paused; inspect retained evidence and repair if eligible')
        if action == 'DONE':
            return state
        seconds = 120 if action == 'build' else 30
        remaining = gate(root, seconds)
        payload = verify_payload(root, m)
        if action == 'build':
            b = payload[PROFILES[cell_index]]
            argv, cwd, env = b['argv'], b['cwd'], b['env']
        else:
            cell = matrix(m)[cell_index]
            successful = [a for a in state['attempts'] if a['reservation']['phase'] == 'build'
                          and PROFILES[a['reservation']['cell']] == cell['observer']
                          and a.get('terminal', {}).get('binary')]
            require(len(successful) == 1, 'G5: no unique attributable successful build')
            selected = successful[0]['terminal']['binary']
            bind(root, selected)
            argv = [str(root / selected['path']), '--exact', m['tests'][cell['input']]['name'], '--test-threads=1']
            cwd, env = str(root), m['observer_environment']
        remaining = gate(root, seconds)  # Recheck after potentially expensive identity verification.
        n = len(state['attempts']) + 1
        directory = out / 'attempts' / f'{n:02d}'
        directory.mkdir(parents=True, exist_ok=False)
        r = {'kind': 'RESERVED', 'number': n, 'phase': action, 'cell': cell_index,
             'reserved_seconds': seconds, 'active_seconds': 5400 - remaining,
             'at': now(), 'monotonic': time.monotonic(), 'argv': argv, 'cwd': cwd, 'env': env,
             'directory': str(directory.relative_to(root)), 'manifest': binding(root, root / name),
             'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()}
        ledger.add(r)
        with signal_retry():
            run_process(argv, cwd, env, directory, seconds,
                        deadline_monotonic=min(r['monotonic'] + seconds, time.monotonic() + remaining))
        # Persist failure/cleanup receipts too; no auto-reset or fabricated terminal.
        ledger.add(finish_attempt(root, r))
        return ledger.read()[1]


def evidence(root):
    root = Path(root).resolve()
    events, state = Ledger(root).read()
    verify_attempts(root, events)
    return state


def main(validate=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', default=MANIFEST)
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--evidence', action='store_true')
    parser.add_argument('--repair-record')
    parser.add_argument('--reconcile', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = evidence(root) if args.evidence else (validate_manifest(root, args.manifest)
             if validate or args.validate else execute(root, args.manifest, args.repair_record, args.reconcile))
    print(json.dumps(result, indent=2))
    return 0
