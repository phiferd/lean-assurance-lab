"""Offline closure audit for the terminal CVC3-U1-A7-PROOF-0001 baseline failure.

The frozen runner remains authoritative for the failed audit.  This successor
replays that failure; it does not repair the parser or promote its transcript
to a successful baseline.  Git reads are the only subprocess operations.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

from lib import cvc_a7_runner as runner
from lib.cvc_prep import read_events, require, safe


BASE = 'results/research/conditional-validation-contracts/cvc-3-conditional'
REVIEW = 'results/research/queue-reviews/2026-09-07-cvc-3-conditional.json'
PREP_EVIDENCE = 'results/research/conditional-validation-contracts/cvc-conditional-1/evidence-manifest.json'
STOP = 'fixed imported type or A7 assumption baseline mismatch'
OUTCOME = 'BOUNDED_UNRESOLVED'


def load(path):
    return json.loads(Path(path).read_text())


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _git(root, checkpoint, path):
    require(isinstance(checkpoint, str) and re.fullmatch('[0-9a-f]{40}', checkpoint),
            'invalid committed checkpoint')
    return subprocess.check_output(['git', 'show', checkpoint + ':' + path], cwd=root)


def _recorded_manifest(root):
    """Use recorded absolute command paths, so evidence works in another clone."""
    manifest = load(root / runner.MANIFEST)
    review = load(root / runner.ENTRY_REVIEW)
    require(manifest.get('schema_version') == 1 and manifest.get('run_id') == runner.RUN
            and manifest.get('item_id') == runner.ITEM and manifest.get('limits') == runner.LIMITS,
            'manifest identity or limits differ')
    require(review.get('item_id') == runner.ITEM and review.get('run_id') == runner.RUN
            and review.get('decision') == 'PROMOTE'
            and review.get('manifest') == runner.binding(root, runner.MANIFEST),
            'entry review does not bind manifest')
    checkpoint = review.get('implementation_checkpoint')
    require(_git(root, checkpoint, runner.MANIFEST) == (root / runner.MANIFEST).read_bytes(),
            'manifest differs from entry checkpoint')
    require(manifest.get('fixed_inputs') == [
        {'path': path, 'sha256': digest} for path, digest in sorted(runner.FIXED.items())],
        'fixed input set differs')
    require([row.get('path') for row in manifest.get('controller_inputs', [])] == runner.CODE,
            'controller input set differs')
    for row in manifest['fixed_inputs'] + manifest['controller_inputs']:
        runner.bind(root, row)
        runner.committed(root, row['path'])
        require(_git(root, checkpoint, row['path']) == (root / row['path']).read_bytes(),
                'input differs from entry checkpoint: ' + row['path'])
    runner.committed(root, runner.MANIFEST)
    runner.committed(root, runner.ENTRY_REVIEW)
    workspace = Path(manifest['environment']['LEAN_PATH'].split(':')[0])
    require(workspace.is_absolute() and workspace.parts[-2:] == tuple(Path(runner.BASE).parts),
            'recorded workspace differs')
    original_root = workspace.parent.parent
    commands = []
    for number in range(1, 7):
        stages = ('signature',) if number == 1 else ('baseline',) if number == 2 else ('baseline', 'proof')
        commands.append({'number': number, 'stages': {
            stage: runner.commands(original_root, manifest['compiler'], number, stage) for stage in stages}})
    require(manifest.get('commands') == commands, 'recorded command schedule differs')
    require(manifest['environment'] == runner.environment(original_root, manifest['environment']['LEAN_SYSROOT']),
            'recorded environment differs')
    return manifest


def _activation(root, start):
    """Check authorization at launch, independently of the later queue selection."""
    checkpoint = start.get('checkpoint')
    for path in (runner.MANIFEST, runner.ENTRY_REVIEW):
        require(_git(root, checkpoint, path) == (root / path).read_bytes(),
                'launch checkpoint input differs: ' + path)
    queue = json.loads(_git(root, checkpoint, 'config/research-queue.json'))
    rows = {row['id']: row for row in queue['items']}
    require(queue.get('frontier_id') == 'F-CONDITIONAL-VALIDATION-CONTRACTS'
            and queue.get('selected_item') == runner.ITEM
            and rows[runner.ITEM]['status'] in {'READY', 'ACTIVE'},
            'launch checkpoint did not authorize this item')
    for name in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2', 'CVC-AXIOMS-1', 'CVC-CONDITIONAL-1'):
        require(rows[name]['status'] == 'COMPLETE' and rows[name]['closure']['outcome'] == 'SUCCESS',
                'launch checkpoint prerequisite differs: ' + name)


def _preserved_preparation(root, start):
    """Preserve prior closure bytes without applying its historical unstarted gate."""
    require(_git(root, start['checkpoint'], PREP_EVIDENCE) == (root / PREP_EVIDENCE).read_bytes(),
            'preparation evidence manifest differs from launch checkpoint')
    evidence = load(root / PREP_EVIDENCE)
    require(evidence.get('schema_version') == 1 and evidence.get('item_id') == 'CVC-CONDITIONAL-1'
            and evidence.get('outcome') == 'SUCCESS' and isinstance(evidence.get('files'), list),
            'invalid predecessor evidence manifest')
    paths = []
    for row in evidence['files']:
        require(isinstance(row, dict) and set(row) in ({'path', 'sha256'}, {'path', 'sha256', 'bytes'}),
                'invalid predecessor binding')
        runner.bind(root, {key: row[key] for key in ('path', 'sha256')})
        if 'bytes' in row:
            _receipt(root, row)
        paths.append(row['path'])
    require(paths and len(paths) == len(set(paths)), 'duplicate or empty predecessor bindings')


def _receipt(root, row, required=True):
    require(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'}
            and type(row['bytes']) is int and row['bytes'] >= 0
            and isinstance(row['sha256'], str) and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid file receipt')
    path = safe(root, row['path'], exists=required)
    if required or path.exists():
        runner.verify_receipt(root, row)
    return row['path']


def _baseline_failure(stdout, stderr, terminal):
    """A process success may be downgraded only by the exact frozen audit."""
    try:
        runner.audit_baseline(stdout, stderr)
    except ValueError as error:
        message = str(error)
    else:
        raise ValueError('recorded failed baseline now passes its frozen audit')
    require(terminal.get('status') == 'FAILED' and terminal.get('baseline_mismatch') is True
            and terminal.get('error') == message and not terminal.get('baseline_audit')
            and not terminal.get('result') and not terminal.get('axiom_audit'),
            'baseline downgrade differs from replayed frozen audit')
    return message


def _attempt(root, manifest, row, full):
    reservation, terminal = row['reservation'], row['terminal']
    number, phase = reservation['number'], reservation['phase']
    stem = runner.stem_for(phase)
    directory = root / runner.OUT / 'attempts' / f'{number:02d}'
    require(directory.is_dir() and not directory.is_symlink(), 'missing attempt directory')
    require(reservation.get('argv') == manifest['commands'][number - 1]['stages'][phase],
            'attempt command differs')
    require(reservation.get('env') == manifest['environment'] and
            reservation.get('cwd') == manifest['environment']['LEAN_PATH'].split(':')[0],
            'attempt environment or cwd differs')
    require(reservation.get('manifest_sha256') == runner.sha(root / runner.MANIFEST),
            'attempt manifest differs')
    expected_digest = runner.FIXED[runner.SIGNATURE if phase == 'signature' else runner.BASELINE]
    require(reservation.get('source_sha256') == reservation.get('input_sha256') == expected_digest,
            'reserved fixed source differs')
    raw = terminal.get('raw_files')
    require(isinstance(raw, list), 'raw receipts missing')
    receipts = {_receipt(root, receipt): receipt for receipt in raw}
    require(len(receipts) == len(raw), 'duplicate raw receipt')
    required = {str((directory / name).relative_to(root)) for name in
                ('implementation.lean', stem + '.lean', 'stdout', 'stderr',
                 'request.json', 'supervisor.json', 'process.json')}
    require(required <= set(receipts), 'required source/process receipt missing')
    for name in ('implementation.lean', stem + '.lean'):
        require(receipts[str((directory / name).relative_to(root))]['sha256'] == expected_digest,
                'raw fixed source differs')
    outputs = terminal.get('outputs')
    require(isinstance(outputs, list) and outputs, 'compiler output receipts missing')
    output_paths = [_receipt(root, output, required=full) for output in outputs]
    expected_output = runner.BASE + '/Contract.olean' if phase == 'signature' else str(
        (directory / (stem + '.olean')).relative_to(root))
    require(len(output_paths) == len(set(output_paths)) and expected_output in output_paths,
            'required compiled output receipt missing')
    require(all(Path(path).parent == Path(expected_output).parent and
                Path(path).name.startswith(stem + '.') and Path(path).suffix != '.lean'
                for path in output_paths), 'unexpected compiler output path')
    require(set(receipts) <= required | set(output_paths), 'unrecognized raw receipt')
    for output in outputs:
        if output['path'] in receipts:
            require(output == receipts[output['path']], 'raw/compiler product receipts differ')
    request = load(directory / 'request.json')
    request_hash = request.pop('request_sha256', None)
    require(hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() == request_hash,
            'request hash differs')
    require(all(request.get(key) == reservation[key] for key in ('argv', 'cwd', 'env'))
            and request.get('seconds') == reservation['reserved_seconds'], 'request differs from reservation')
    require(_finite(request.get('deadline_monotonic')) and _finite(request.get('monotonic_started'))
            and reservation['time']['monotonic'] <= request['monotonic_started']
            < request['deadline_monotonic'] <= reservation['time']['monotonic'] + reservation['reserved_seconds'],
            'request deadline differs from reservation')
    supervisor = load(directory / 'supervisor.json')
    require(terminal.get('supervisor_receipt') == receipts[str((directory / 'supervisor.json').relative_to(root))],
            'supervisor receipt differs')
    require(supervisor.get('request_sha256') == request_hash
            and supervisor.get('status') == 'COMPLETE' and supervisor.get('returncode') == 0
            and supervisor.get('cleanup_completed') is True and supervisor.get('deadline_exceeded') is False,
            'compiler process did not complete with verified cleanup')
    for key, value in supervisor.items():
        if key not in {'status', 'error'}:
            require(terminal.get(key) == value, 'terminal differs from supervisor: ' + key)
    require(supervisor.get('started_at') == request['started_at']
            and supervisor.get('monotonic_started') == request['monotonic_started'],
            'supervisor start differs from request')
    require(_finite(supervisor.get('monotonic_ended'))
            and supervisor['monotonic_started'] <= supervisor['monotonic_ended'] <= request['deadline_monotonic']
            and _finite(supervisor.get('charged_seconds'))
            and supervisor['charged_seconds'] <= supervisor['monotonic_ended'] - supervisor['monotonic_started'],
            'invalid supervisor timing')
    for stream in ('stdout', 'stderr'):
        require(supervisor.get(stream + '_sha256') == receipts[str((directory / stream).relative_to(root))]['sha256'],
                'supervisor stream digest differs: ' + stream)
    process = load(directory / 'process.json')
    require(process.get('request_sha256') == request_hash
            and all(type(process.get(key)) is int and process[key] > 0 for key in ('pid', 'supervisor_pid')),
            'process identity differs')
    stdout, stderr = (directory / 'stdout').read_text(), (directory / 'stderr').read_text()
    if phase == 'signature':
        require(terminal.get('status') == 'COMPLETE' and 'sorry' not in (stdout + stderr).lower()
                and not any(terminal.get(key) for key in ('error', 'baseline_mismatch', 'baseline_audit', 'result', 'axiom_audit')),
                'signature did not complete without a scientific result')
        return None
    return _baseline_failure(stdout, stderr, terminal)


def validate_run(root, require_full_payload=False):
    root = Path(root).resolve()
    require(type(require_full_payload) is bool, 'full-payload option must be boolean')
    manifest = _recorded_manifest(root)
    directory = root / runner.OUT
    events = read_events(directory / 'execution/events.jsonl')
    state = runner.derive(events)
    require(load(directory / 'execution/state.json') == {
        'count': len(events), 'tail': events[-1]['event_sha256'], 'state': state},
        'snapshot differs from complete event chain')
    start = load(directory / 'start.json')
    require(start.get('run_id') == runner.RUN and start.get('manifest_sha256') == runner.sha(root / runner.MANIFEST)
            and all(events[0].get(key) == value for key, value in start.items()), 'run start identity differs')
    _activation(root, start)
    _preserved_preparation(root, start)
    sessions = state['sessions']
    require(0 < len(sessions) <= 2 and all('end' in session for session in sessions),
            'closure requires closed sessions within cap')
    require(all(_finite(session['charged_seconds']) and session['charged_seconds'] <= 3600 for session in sessions),
            'individual session cap exceeded')
    active = sum(session['charged_seconds'] for session in sessions)
    require(active <= 7200, 'total session cap exceeded')
    attempts = state['attempts']
    require([row['reservation']['phase'] for row in attempts] == ['signature', 'baseline']
            and all('terminal' in row for row in attempts), 'expected terminal two-stage baseline failure')
    require(state['outcome'] == OUTCOME and state['control_stop'] == STOP, 'terminal immutable stop differs')
    require({p.name for p in (directory / 'attempts').iterdir()} == {'01', '02'}, 'unexpected attempt directory')
    for index, event in enumerate(events[1:], 1):
        before = runner.derive(events[:index])
        if event['kind'] == 'RESERVED':
            require(event.get('active_seconds_before') == runner.active_seconds(before, event['time'])
                    and event.get('remaining_attempts_after_reservation') == 6 - event['number'],
                    'reservation counters differ')
        elif event['kind'] == 'TERMINAL':
            require(event.get('remaining_attempts') == 6 - event['number']
                    and event.get('remaining_active_seconds') == max(0, 7200 - runner.active_seconds(before, event['time'])),
                    'terminal counters differ')
            require(_finite(event['charged_seconds']) and
                    event['charged_seconds'] <= before['attempts'][-1]['reservation']['reserved_seconds'],
                    'terminal process charge exceeds reservation')
    failures = [_attempt(root, manifest, row, require_full_payload) for row in attempts]
    if require_full_payload:
        runner.validate_manifest(root, require_commit=True)
        runner.verify_payloads(root, manifest)
        runner.verify_attempts(root, state)
    return {'run_id': runner.RUN, 'item_id': runner.ITEM, 'outcome': OUTCOME,
            'scientific_status': 'NO_CHECKED_LAB_RESULT', 'sessions': len(sessions), 'active_seconds': active,
            'attempts': len(attempts), 'signature_elaborations': 1, 'baseline_builds': 1,
            'successful_baselines': 0, 'proof_builds': 0, 'successful_proof_builds': 0,
            'compilation_seconds': sum(row['terminal']['charged_seconds'] for row in attempts),
            'remaining_attempts_unspent': 6 - len(attempts), 'control_stop': STOP,
            'baseline_audit_error': failures[-1], 'failed_attempt': 2,
            'manifest_sha256': runner.sha(root / runner.MANIFEST), 'payloads_verified': require_full_payload}


def _costs_and_review(root, result, summary):
    """Bind prior cost scope and the successor ceiling without resetting history."""
    start = load(root / runner.OUT / 'start.json')
    entry = load(root / runner.ENTRY_REVIEW)
    require(result.get('input_checkpoint') == entry['implementation_checkpoint']
            and result.get('activation_checkpoint') == start['checkpoint'], 'result checkpoints differ')
    prior = result.get('prior_costs')
    require(isinstance(prior, dict), 'prior cost bindings missing')
    previous = {}
    for name, path in (
        ('original_proof_result', 'results/research/conditional-validation-contracts/cvc-3/result.json'),
        ('conditional_preparation_result', 'results/research/conditional-validation-contracts/cvc-conditional-1/result.json'),
    ):
        require(_receipt(root, prior.get(name)) == path, 'unexpected prior cost source')
        require(_git(root, start['checkpoint'], path) == (root / path).read_bytes(),
                'prior cost source differs from launch checkpoint')
        previous[name] = load(root / path)
    original, prepared = previous['original_proof_result'], previous['conditional_preparation_result']
    prior_active = prepared['combined_preparation_runner_proof_active_seconds']
    prior_compilation = original['aggregate_compilation_seconds']
    require(prior.get('preparation_runner_proof_active_seconds') == prior_active
            and prior.get('compilation_seconds') == prior_compilation
            and result.get('aggregate_active_seconds') == prior_active + summary['active_seconds']
            and result.get('aggregate_compilation_seconds') == prior_compilation + summary['compilation_seconds'],
            'aggregate costs differ from bound predecessors')
    require('prior_failed_fixture_actual_duration' in prior
            and prior['prior_failed_fixture_actual_duration'] == original['prior_costs']['prior_failed_fixture_actual_duration']
            and prior.get('prior_failed_fixture_cap_compliance') == original['prior_costs']['prior_failed_fixture_cap_compliance'],
            'prior unknown fixture costs were changed')
    review = load(root / REVIEW)
    require(review.get('schema_version') == 1 and review.get('stopped_item') == runner.ITEM
            and review.get('outcome') == OUTCOME and review.get('recommendation') == result['recommendation']
            and review.get('after', {}).get('selected_item') == result['recommendation'].get('next_item'),
            'stopping review differs from closed recommendation')
    carry = review.get('budget_carry_forward', {})
    expected = {
        'terminal_a7_attempts': summary['attempts'],
        'proposed_successor_attempts_max': summary['remaining_attempts_unspent'],
        'combined_a7_attempts_max': runner.LIMITS['attempts'],
        'original_cvc3_attempts': original['attempts'],
        'all_proof_phase_builds_max': original['attempts'] + runner.LIMITS['attempts'],
        'a7_active_seconds_consumed': summary['active_seconds'],
        'successor_active_seconds_max': (runner.LIMITS['sessions'] - summary['sessions']) * runner.LIMITS['session_seconds'],
        'counters_reused': False,
        'a7_sessions_consumed': summary['sessions'],
        'successor_sessions_max': runner.LIMITS['sessions'] - summary['sessions'],
        'combined_a7_sessions_max': runner.LIMITS['sessions'],
        'combined_a7_active_seconds_max': summary['active_seconds'] +
            (runner.LIMITS['sessions'] - summary['sessions']) * runner.LIMITS['session_seconds'],
    }
    require(carry == expected and carry.get('counters_reused') is False,
            'successor budget carry-forward differs from consumed counters')


def validate_closure(root, require_full_payload=False):
    root = Path(root).resolve()
    summary = validate_run(root, require_full_payload)
    base = root / BASE
    result, work, diagnostic = (load(base / name) for name in ('result.json', 'work-record.json', 'stop-diagnostic.json'))
    for value in (result, work, diagnostic):
        require(value.get('schema_version') == 1 and value.get('item_id') == runner.ITEM
                and value.get('run_id') == runner.RUN and value.get('outcome') == OUTCOME,
                'closure identity or outcome differs')
    for key in ('sessions', 'active_seconds', 'attempts', 'signature_elaborations', 'baseline_builds',
                'successful_baselines', 'proof_builds', 'successful_proof_builds', 'compilation_seconds',
                'remaining_attempts_unspent', 'scientific_status'):
        require(result.get(key) == summary[key], 'result differs from audited run: ' + key)
    require(result.get('manifest') == runner.receipt(root, root / runner.MANIFEST), 'result manifest differs')
    for key in ('checker_launches', 'dependency_compilations', 'research_network_requests'):
        require(type(result.get(key)) is int and result[key] == 0, 'forbidden research operation: ' + key)
    recommendation = result.get('recommendation', {})
    require(all(recommendation.get(key) for key in ('action', 'target', 'priority', 'prerequisites', 'evidence_refs')),
            'concrete recommendation missing')
    _costs_and_review(root, result, summary)
    state = runner.derive(read_events(root / runner.OUT / 'execution/events.jsonl'))
    require(work.get('status') == 'COMPLETE' and work.get('sessions') == state['sessions']
            and work.get('active_seconds') == summary['active_seconds']
            and work.get('attempts_consumed') == summary['attempts']
            and work.get('compilation_seconds') == summary['compilation_seconds']
            and work.get('remaining_attempts_unspent') == summary['remaining_attempts_unspent'],
            'work record differs from audited accounting')
    for key in ('failed_attempt', 'baseline_audit_error', 'control_stop'):
        require(diagnostic.get(key) == summary[key], 'stop diagnostic differs: ' + key)
    for stream in ('stdout', 'stderr'):
        path = root / runner.OUT / 'attempts/02' / stream
        require(diagnostic.get(stream) == runner.receipt(root, path), 'diagnostic stream binding differs')
    require(diagnostic.get('process_outcome') == {
        key: state['attempts'][-1]['terminal'][key] if key != 'status' else 'COMPLETE'
        for key in ('status', 'returncode', 'cleanup_completed', 'deadline_exceeded')}
        and diagnostic.get('runner_terminal_status') == state['attempts'][-1]['terminal']['status'],
        'diagnostic process/runner status distinction differs')
    evidence = load(base / 'evidence-manifest.json')
    require(evidence.get('schema_version') == 1 and evidence.get('item_id') == runner.ITEM
            and isinstance(evidence.get('files'), list), 'invalid evidence manifest')
    paths = [_receipt(root, receipt) for receipt in evidence['files']]
    require(len(paths) == len(set(paths)) and BASE + '/evidence-manifest.json' not in paths,
            'duplicate or self-referential evidence manifest')
    required = {BASE + '/' + name for name in ('result.json', 'work-record.json', 'stop-diagnostic.json', 'report.md')}
    required.add(REVIEW)
    required |= {runner.OUT + '/' + name for name in ('start.json', 'execution/events.jsonl', 'execution/state.json')}
    required |= {receipt['path'] for row in state['attempts'] for receipt in row['terminal']['raw_files']}
    require(required <= set(paths), 'evidence manifest omits required closure or raw receipts')
    return {**summary, 'evidence_files': len(paths)}
