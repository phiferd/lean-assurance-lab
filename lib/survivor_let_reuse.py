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

ITEM = 'SURVIVOR-LET-REUSE-1'
RUN = 'survivor-let-reuse-0001'
BASE = 'results/research/survivor-let-reuse-1'
OUT = BASE + '/run-0001'
WORK = BASE + '/work-record.json'
PROPOSAL = 'results/research/alt-survivors-2026-09-08/execution-proposal.json'
MANIFEST = 'config/survivor-let-reuse-0001.json'
PROPOSAL_SHA256 = '7f77289c8a70fdcf59fb6f77d9847c25cc8a61fa4b9a7061b9c49148a3af6d6d'
LIMITS = {'active_seconds': 5400, 'interval_seconds': 5400,
          'offline_build_reservations': 2, 'per_build_seconds': 120,
          'checker_reservations': 8, 'per_checker_seconds': 30, 'fixed_pairs': 1,
          'max_scientific_byte_variants': 0, 'research_network_requests': 0,
          'proof_launches': 0, 'external_research_actions': 0}
CODE = ['lib/survivor_let_reuse.py', 'lib/survivor_let_payload.py',
        'scripts/bind-survivor-let-payload', 'scripts/execute-survivor-let-reuse',
        'scripts/validate-survivor-let-reuse', 'tests/test_survivor_let_reuse.py',
        'lib/cvc_process.py', 'lib/cvc_signal_retry.py', 'lib/cvc_prep.py',
        'lib/research_queue.py', 'lib/research_queue_v2.py']
SCIENCE_KEYS = ['proposal', 'work_record', 'entry_decision', 'source_materialization',
                'runtime_manifest', 'fixed_inputs', 'configs', 'matrix', 'observer_environment']
SUCCESS = b'Checked 1 declarations with no errors\n'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'RUST_BACKTRACE': 'full'}


def load(p):
    return json.loads(Path(p).read_text())


def binding(root, p):
    p = Path(p)
    return {'path': str(p.relative_to(root)), 'sha256': sha(p)}


def finite(x):
    return type(x) in (int, float) and math.isfinite(x) and x >= 0


def active_seconds(work, monotonic=None, utc=None):
    mono = time.monotonic() if monotonic is None else monotonic
    utc = datetime.now(timezone.utc) if utc is None else utc
    started = datetime.fromisoformat(work['started_utc'])
    require(started.tzinfo is not None and finite(work['started_monotonic'])
            and finite(work['conservative_pre_record_seconds']), 'invalid work clock')
    md, ud = mono - work['started_monotonic'], (utc - started).total_seconds()
    require(md >= 0 and ud >= 0 and abs(md - ud) <= 5, 'work clocks disagree or rebooted')
    return max(md, ud) + work['conservative_pre_record_seconds']


def gate(root, seconds=0):
    from lib.research_queue_v2 import load_queue
    q = load_queue(root, require_ready=True)
    row = next(r for r in q['items'] if r['id'] == ITEM)
    require(q['frontier_id'] == 'F-SURVIVOR-LET-REUSE' and q['selected_item'] == ITEM
            and row['status'] == 'ACTIVE', 'G1: item not selected ACTIVE')
    w = load(root / WORK)
    require(w['item_id'] == ITEM and w['status'] == 'ACTIVE'
            and w['owner_authorization'] == 'Authorized. Please execute SURVIVOR-LET-REUSE-1'
            and w['active_seconds_limit'] == 5400, 'G1: no exact execution authority')
    used = active_seconds(w)
    require(used + seconds <= 5400, 'active-time cap cannot cover reservation')
    require(not (root / BASE / 'work-closure.json').exists(), 'item work already closed')
    return 5400 - used


def manifest_path(root, name):
    require(re.fullmatch(r'config/survivor-let-reuse-0001(?:-r[2-9][0-9]*)?\.json', name),
            'wrong manifest path')
    return safe(root, name)


def validate_manifest(root, name=MANIFEST, launch=False, payload=True):
    root = Path(root).resolve()
    m = load(manifest_path(root, name))
    expected = {'schema_version', 'item_id', 'run_id', 'limits', 'tooling_inputs',
                'focused_test_receipt', *SCIENCE_KEYS}
    require(set(m) == expected and m['schema_version'] == 1 and m['item_id'] == ITEM
            and m['run_id'] == RUN and m['limits'] == LIMITS, 'wrong manifest or limits')
    required = {'proposal': PROPOSAL, 'work_record': WORK,
                'entry_decision': BASE + '/entry-decision.json',
                'source_materialization': BASE + '/source-materialization.json',
                'runtime_manifest': BASE + '/runtime-manifest.json'}
    for key, path in required.items():
        require(m[key]['path'] == path, 'wrong fixed binding: ' + key)
        bind(root, m[key])
    require(m['proposal']['sha256'] == PROPOSAL_SHA256, 'different frozen execution proposal')
    proposal = load(root / PROPOSAL)
    require(proposal['limits'] == LIMITS and m['matrix'] == proposal['matrix'], 'science drift')
    decision = load(root / m['entry_decision']['path'])
    require(decision['execution_authorized'] is True and decision['item_id'] == ITEM
            and decision['proposal'] == m['proposal'], 'execution decision does not bind proposal')
    expected_fixed = [{'path': proposal[k]['path'], 'sha256': proposal[k]['sha256']}
                      for k in ('mutation_spec', 'source_lock', 'control', 'candidate', 'historical_official_result')]
    require(m['fixed_inputs'] == expected_fixed, 'fixed scientific identity differs')
    require(m['observer_environment'] == ENV, 'observer environment differs')
    require(set(m['configs']) == {'control', 'candidate'}, 'wrong configs')
    for role in ('control', 'candidate'):
        row = m['configs'][role]
        require(row['path'] == BASE + '/configs/' + role + '.json', 'wrong config path')
        cfg = load(bind(root, row))
        original = load(bind(root, {k: proposal['configuration']['base'][k] for k in ('path', 'sha256')}))
        expected_config = {**original, 'use_stdin': False, 'print_axioms': False,
                           'export_file_path': str(root / proposal[role]['path'])}
        require(cfg == expected_config, 'config changes science or input path')
    require([r['path'] for r in m['tooling_inputs']] == CODE, 'incomplete tooling binding')
    all_rows = list(m['fixed_inputs']) + list(m['configs'].values()) + m['tooling_inputs']
    all_rows += [m[k] for k in required] + [m['focused_test_receipt']]
    for row in all_rows:
        bind(root, row)
        if launch:
            committed(root, row['path'])
    test = load(bind(root, m['focused_test_receipt']))
    require(test['status'] == 'PASS' and test['tooling_inputs'] == m['tooling_inputs']
            and test['test_count'] >= 15 and test['real_process_launches'] == 0,
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
        from lib.survivor_let_payload import verify
        verify(root, require_commit=launch)
    if launch:
        gate(root)
        for p in (name, 'config/research-queue.json', 'docs/RESEARCH_STATUS.md',
                  'docs/research/SURVIVOR_LET_REUSE_PLAN.md'):
            committed(root, p)
    return m


def derive(events):
    require(events and events[0]['kind'] == 'START' and events[0]['run_id'] == RUN,
            'missing start')
    attempts, repairs = [], []
    for event in events[1:]:
        kind = event['kind']
        if kind == 'RESERVED':
            require(not attempts or 'terminal' in attempts[-1], 'unreconciled reservation')
            require(event['number'] == len(attempts) + 1, 'nonconsecutive reservation')
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
        return ('build', None)
    last = attempts[-1]
    if 'terminal' not in last:
        return ('PAUSED', None)
    if repairs and repairs[-1]['after_number'] == len(attempts):
        return (repairs[-1]['phase'], repairs[-1].get('cell'))
    r, t = last['reservation'], last['terminal']
    if t.get('engineering_pause') or not t.get('cleanup_completed'):
        return ('PAUSED', None)
    if r['phase'] == 'build':
        return ('checker', 0) if t['status'] == 'COMPLETE' and t.get('binary') else ('PAUSED', None)
    c = r['cell']
    if c < 2 and t['classification'] != 'ACCEPT':
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


def classify(cell, rec, stdout, stderr):
    if rec['status'] == 'TIMED_OUT':
        return 'TIMEOUT'
    if not rec.get('cleanup_completed') or rec.get('deadline_exceeded') or rec.get('error'):
        return 'INDETERMINATE'
    if rec['status'] == 'COMPLETE' and rec['returncode'] == 0 and stdout == SUCCESS and stderr == b'':
        return 'ACCEPT'
    # This source uses assert! as the rejection mechanism. Full backtrace must
    # locate BOTH the assertion and infer_let caller, not just a panic/exit code.
    if (cell == 'candidate-baseline' and rec['status'] == 'FAILED' and rec['returncode'] == 101
            and stdout == b'' and b'panicked at src/tc.rs:921:71:' in stderr
            and b'assertion failed: self.def_eq(u, v)' in stderr
            and b'::assert_def_eq' in stderr and b'::infer_let' in stderr
            and b'::check_declar_info' in stderr):
        return 'TYPECHECK_REFUSAL'
    lowered = stderr.lower()
    if any(token in lowered for token in (b'parse error', b'parser error', b'failed to parse', b'invalid json')):
        return 'PARSE_ERROR'
    if b'unsupported' in lowered:
        return 'UNSUPPORTED'
    if rec['returncode'] != 0 or b'panicked at' in stderr:
        return 'CRASH'
    return 'INDETERMINATE'


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
            path = root / 'external/survivor-let-reuse-0001-target/release/nanoda_bin'
            require(path.is_file() and not path.is_symlink(), 'missing selected build output')
            product = root / ('external/survivor-let-reuse-0001-products/build-' + str(reservation['number'])) / 'nanoda_bin'
            require(not product.exists(), 'immutable build product already exists')
            product.parent.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(path, product)
            product.chmod(0o555)
            require(sha(product) == sha(path), 'build product changed during copy')
            t['binary'] = binding(root, product)
            t['build_output_sha256'] = sha(path)
    else:
        cell = load(root / reservation['manifest']['path'])['matrix'][reservation['cell']]['id']
        t['classification'] = classify(cell, rec, (d / 'stdout').read_bytes(), (d / 'stderr').read_bytes())
        # Unknown output needs an audit repair, not a scientific negative.
        t['engineering_pause'] |= t['classification'] == 'INDETERMINATE'
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
            cell = m['matrix'][r['cell']]
            require(r['argv'][1:] == [str(root / m['configs'][cell['input']]['path'])]
                    and r['cwd'] == str(root) and r['env'] == m['observer_environment'], 'cell command drift')
            if cell['observer'] == 'baseline':
                expected_binary = load(root / PROPOSAL)['baseline']
            else:
                expected_binary = next(a['terminal']['binary'] for a in reversed(state['attempts'][:r['number'] - 1])
                                       if a.get('terminal', {}).get('binary'))
            require(r['argv'][0] == str(root / expected_binary['path']), 'wrong cell binary')
            # If tooling later changes, replay the original committed normalizer
            # in its own historical validation context; never reinterpret here.
            current_normalizer = next(x for x in m['tooling_inputs'] if x['path'] == 'lib/survivor_let_reuse.py')
            if sha(root / current_normalizer['path']) == current_normalizer['sha256']:
                require(t['classification'] == classify(cell['id'], raw, (d / 'stdout').read_bytes(),
                                                        (d / 'stderr').read_bytes()), 'normalized outcome drift')
            else:
                data = subprocess.check_output(['git', 'show', r['commit'] + ':lib/survivor_let_reuse.py'], cwd=root)
                namespace = {'__name__': 'historical_survivor_normalizer'}
                exec(compile(data, '<bound historical normalizer>', 'exec'), namespace)
                require(t['classification'] == namespace['classify'](cell['id'], raw, (d / 'stdout').read_bytes(),
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
        from lib.survivor_let_payload import verify
        payload = verify(root, require_commit=True)
        if action == 'build':
            b = payload['build']
            argv, cwd, env = b['argv'], b['cwd'], b['env']
        else:
            successful = [a for a in state['attempts'] if a['reservation']['phase'] == 'build'
                          and a.get('terminal', {}).get('binary')]
            require(successful, 'G5: no attributable successful build')
            selected = successful[-1]['terminal']['binary']
            bind(root, selected)
            proposal = load(root / PROPOSAL)
            baseline = {k: proposal['baseline'][k] for k in ('path', 'sha256')}
            bind(root, baseline)
            cell = m['matrix'][cell_index]
            binary = baseline if cell['observer'] == 'baseline' else selected
            argv = [str(root / binary['path']), str(root / m['configs'][cell['input']]['path'])]
            cwd, env = str(root), m['observer_environment']
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
    parser.add_argument('--evidence', action='store_true')
    parser.add_argument('--repair-record')
    parser.add_argument('--reconcile', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = evidence(root) if args.evidence else (validate_manifest(root, args.manifest)
             if validate else execute(root, args.manifest, args.repair_record, args.reconcile))
    print(json.dumps(result, indent=2))
    return 0
