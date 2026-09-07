"""Offline A7 repair evidence and logical closure audit; Git reads only.

Historical tooling remains immutable. Each attempt is replayed with its own
committed, archived audit module. Portable validation omits only absent ignored
compiler products, never committed source, transcript or process evidence.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from lib import cvc_a7_repair_runner as runner
from lib import cvc_a7_audit as frozen
from lib.cvc3_a7_evidence import _finite, _git, load
from lib.cvc_prep import read_events, require, safe

BASE = 'results/research/conditional-validation-contracts/cvc-a7-repair-1'
REVIEW = 'results/research/queue-reviews/2026-09-07-cvc-a7-repair-1.json'
PREDECESSOR = 'results/research/conditional-validation-contracts/cvc-3-conditional/result.json'
_PRODUCT = re.compile(r'^(?:Contract|Baseline|CVC2Proof)\.(?:olean(?:\.(?:private|server))?|ilean|c|o|bc)$')


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _ignored(root, relative):
    return subprocess.run(['git', 'check-ignore', '-q', '--', relative], cwd=root,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def _receipt(root, row, full=True):
    require(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'}
            and type(row['bytes']) is int and row['bytes'] >= 0
            and isinstance(row['sha256'], str) and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid file receipt')
    path = safe(root, row['path'], exists=False)
    if path.exists() or full:
        runner.verify_receipt(root, row)
    else:
        require(_PRODUCT.fullmatch(path.name) and _ignored(root, row['path']),
                'missing committed or non-product evidence: ' + row['path'])
    return row['path']


def _manifest(root, start):
    manifest = load(root / runner.MANIFEST)
    require(_git(root, start['checkpoint'], runner.MANIFEST) == (root / runner.MANIFEST).read_bytes(),
            'manifest differs from activation checkpoint')
    workspace = Path(manifest['environment']['LEAN_PATH'].split(':')[0])
    require(workspace.is_absolute() and workspace.parts[-2:] == tuple(Path(runner.BASE).parts),
            'recorded workspace differs')
    original_root = workspace.parent.parent
    compiler = load(root / runner.PREP_MANIFEST)['compiler']['path']
    runtime = load(root / runner.RUNTIME)['runtime_root']
    expected = {
        'schema_version': 1, 'run_id': runner.RUN, 'item_id': runner.ITEM,
        'workspace': runner.BASE, 'run_directory': runner.OUT, 'limits': runner.LIMITS,
        'fixed_inputs': [{'path': p, 'sha256': h} for p, h in sorted(runner.FIXED.items())],
        'controller_inputs': manifest['controller_inputs'], 'compiler': compiler,
        'environment': runner.environment(original_root, runtime),
        'commands': [{'number': n, 'stages': {stage: runner.commands(original_root, compiler, n, stage)
                     for stage in ('signature', 'baseline', 'proof')}} for n in range(1, 5)],
        'python': manifest['python'], 'work_record': runner.WORK, 'validation_record': runner.VALIDATION,
        'result_modes': {'proof': [{'name': n, 'type': t} for n, t in runner.TARGETS],
                         'counterexample': [{'name': n, 'type': t} for n, t in runner.NEGATIVE]},
    }
    require(manifest == expected, 'fixed manifest identity, commands, inputs or limits differ')
    require([r['path'] for r in manifest['controller_inputs']] == runner.CODE,
            'initial controller inventory differs')
    require(set(manifest['python']) == {'path', 'sha256'} and Path(manifest['python']['path']).is_absolute()
            and re.fullmatch('[0-9a-f]{64}', manifest['python']['sha256']), 'invalid bound Python identity')
    for row in manifest['fixed_inputs'] + manifest['controller_inputs']:
        require(_digest(_git(root, start['checkpoint'], row['path'])) == row['sha256'],
                'initial input differs from committed checkpoint: ' + row['path'])
        if row['path'] not in runner.REPAIRABLE:
            runner.bind(root, row)
    require(start.get('manifest_sha256') == runner.sha(root / runner.MANIFEST), 'run manifest digest differs')
    return manifest


def _activation(root, start):
    queue = json.loads(_git(root, start['checkpoint'], 'config/research-queue.json'))
    rows = {row['id']: row for row in queue['items']}
    require(queue['frontier_id'] == 'F-CONDITIONAL-VALIDATION-CONTRACTS'
            and queue['selected_item'] == runner.ITEM and rows[runner.ITEM]['status'] == 'ACTIVE',
            'activation checkpoint does not authorize selected ACTIVE repair')
    require(rows['CVC-3-CONDITIONAL']['status'] == 'COMPLETE'
            and rows['CVC-3-CONDITIONAL']['closure']['outcome'] == 'BOUNDED_UNRESOLVED',
            'historical predecessor is not preserved terminal')
    for item in ('CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2', 'CVC-AXIOMS-1', 'CVC-CONDITIONAL-1'):
        require(rows[item]['status'] == 'COMPLETE' and rows[item]['closure']['outcome'] == 'SUCCESS',
                'activation prerequisite differs: ' + item)
    work = json.loads(_git(root, start['checkpoint'], runner.WORK))
    require(work.get('item_id') == runner.ITEM and work.get('run_id') == runner.RUN
            and work.get('policy') == runner.POLICY and work.get('status') == 'ACTIVE'
            and start.get('work') == {'intervals': work['intervals']},
            'initial work interval differs from committed activation accounting')


def _revision(root, manifest, revision):
    runner.verify_revision(root, revision)
    directory = runner.OUT + '/tooling/' + f"{revision['number']:02d}"
    initial = {row['path']: row['sha256'] for row in manifest['controller_inputs']}
    for row in revision['inputs']:
        require(row['archive']['path'] == directory + '/files/' + row['path'],
                'tooling archive path differs')
        require(_git(root, revision['checkpoint'], row['path']) == (root / row['archive']['path']).read_bytes(),
                'archived tooling differs from Git checkpoint: ' + row['path'])
        if revision['number'] == 1 or row['path'] not in runner.REPAIRABLE:
            require(row['sha256'] == initial[row['path']], 'initial or immutable tooling changed')
    require(revision['validation']['path'] == directory + '/validation.json'
            and revision['log']['path'] == directory + '/validation.log', 'revision test archive paths differ')
    checked = load(root / revision['validation']['path'])
    require(_git(root, revision['checkpoint'], runner.VALIDATION) == (root / revision['validation']['path']).read_bytes()
            and _git(root, revision['checkpoint'], checked['log']['path']) == (root / revision['log']['path']).read_bytes(),
            'archived validation differs from committed check receipt')
    require(checked.get('schema_version') == 1 and isinstance(checked.get('command'), list)
            and checked['command'] and all(isinstance(x, str) and x for x in checked['command']),
            'invalid focused validation command')
    return runner.bound_audit(root, revision)


def _process(root, directory, reservation, terminal, receipts):
    request = load(directory / 'request.json')
    request_hash = request.pop('request_sha256', None)
    require(_digest(json.dumps(request, sort_keys=True).encode()) == request_hash, 'request hash differs')
    require(all(request.get(k) == reservation[k] for k in ('argv', 'cwd', 'env'))
            and request.get('seconds') == reservation['reserved_seconds'], 'request differs from reservation')
    require(_finite(request.get('monotonic_started')) and _finite(request.get('deadline_monotonic'))
            and reservation['time']['monotonic'] <= request['monotonic_started'] < request['deadline_monotonic']
            <= reservation['time']['monotonic'] + reservation['reserved_seconds'], 'request timing differs')
    supervisor = load(directory / 'supervisor.json')
    require(terminal.get('supervisor_receipt') == receipts[str((directory / 'supervisor.json').relative_to(root))],
            'supervisor receipt differs')
    require(supervisor.get('request_sha256') == request_hash
            and supervisor.get('started_at') == request['started_at']
            and supervisor.get('monotonic_started') == request['monotonic_started'], 'supervisor start/request differs')
    require(supervisor.get('status') in ('COMPLETE', 'FAILED', 'TIMED_OUT', 'INTERRUPTED')
            and type(supervisor.get('cleanup_completed')) is bool
            and type(supervisor.get('deadline_exceeded')) is bool, 'invalid supervisor disposition')
    require(_finite(supervisor.get('monotonic_ended')) and _finite(supervisor.get('charged_seconds'))
            and supervisor['monotonic_ended'] >= supervisor['monotonic_started']
            and supervisor['charged_seconds'] <= supervisor['monotonic_ended'] - supervisor['monotonic_started'],
            'invalid supervisor process timing')
    require((supervisor['monotonic_ended'] > request['deadline_monotonic']) == supervisor['deadline_exceeded'],
            'supervisor deadline evidence differs')
    if supervisor['status'] == 'COMPLETE':
        require(supervisor.get('returncode') == 0 and supervisor['cleanup_completed']
                and not supervisor['deadline_exceeded'], 'successful process lacks clean zero exit')
    for key, value in supervisor.items():
        if key not in ('status', 'error'):
            if terminal.get('orphan') and key == 'charged_seconds':
                require(terminal[key] >= max(value, reservation['reserved_seconds']), 'orphan charge was reset')
            elif not terminal.get('orphan'):
                require(terminal.get(key) == value, 'terminal differs from supervisor: ' + key)
    for stream in ('stdout', 'stderr'):
        require(supervisor.get(stream + '_sha256') == receipts[str((directory / stream).relative_to(root))]['sha256'],
                'supervisor stream digest differs: ' + stream)
    process = load(directory / 'process.json')
    require(process.get('request_sha256') == request_hash
            and all(type(process.get(k)) is int and process[k] > 0 for k in ('pid', 'supervisor_pid')),
            'process identity differs')
    runner.elapsed({'at': request['started_at'], 'monotonic': request['monotonic_started']},
                   {'at': supervisor['ended_at'], 'monotonic': supervisor['monotonic_ended']})
    require(terminal['time']['monotonic'] >= supervisor['monotonic_ended'], 'terminal predates process completion')
    return supervisor


def _replay(root, module, reservation, terminal, supervisor, directory):
    phase = reservation['phase']
    raw = (directory / 'implementation.lean').read_bytes()
    compiled = (directory / (runner.stem_for(phase) + '.lean')).read_bytes()
    require(_digest(raw) == reservation['source_sha256'] and _digest(compiled) == reservation['input_sha256'],
            'reserved source or compiler input changed')
    if phase == 'signature':
        require(raw == compiled == (root / runner.SIGNATURE).read_bytes(), 'fixed signature changed')
    elif phase == 'baseline':
        require(raw == compiled == module.baseline_source(load(root / runner.EXPECTATIONS)),
                'baseline differs from its bound generator and fixed expectations')
    else:
        require(runner.generate(raw.decode(), reservation['mode']) == compiled, 'fixed proof source generation differs')
    stdout, stderr = (directory / 'stdout').read_text(), (directory / 'stderr').read_text()
    if supervisor['status'] != 'COMPLETE' or terminal.get('orphan'):
        require(not any(terminal.get(k) for k in ('result', 'baseline_audit', 'axiom_audit', 'scientific_mismatch')),
                'failed compiler promoted to scientific result')
        return
    try:
        if phase == 'baseline':
            result = module.audit_baseline(stdout, stderr)
        elif phase == 'proof':
            result = module.audit(stdout, stderr, load(root / runner.ASSUMPTIONS), reservation['mode'])
        else:
            require('sorry' not in (stdout + stderr).lower(), 'signature sorry diagnostic')
            result = None
    except ValueError as error:
        require(terminal['status'] == 'FAILED' and terminal.get('error') == str(error)
                and not any(terminal.get(k) for k in ('result', 'baseline_audit', 'axiom_audit')),
                'recorded audit failure differs from bound replay')
        scientific = isinstance(error, module.ScientificMismatch)
        require(bool(terminal.get('scientific_mismatch')) == scientific
                and (scientific or terminal.get('repair_pause') == str(error)), 'audit failure classification differs')
        return
    require(not terminal.get('scientific_mismatch'), 'successful replay mislabeled scientific mismatch')
    if terminal['status'] != 'COMPLETE':
        require(terminal.get('cleanup_unverified') and terminal.get('error')
                and not any(terminal.get(k) for k in ('result', 'baseline_audit', 'axiom_audit')),
                'successful audit downgraded without retained integrity failure')
        return
    require(not terminal.get('repair_pause') and not terminal.get('cleanup_unverified'), 'successful attempt carries failure')
    if phase == 'signature':
        require(not any(terminal.get(k) for k in ('result', 'baseline_audit', 'axiom_audit')), 'signature claims result')
    elif phase == 'baseline':
        require(terminal.get('baseline_audit') == result and not terminal.get('result') and not terminal.get('axiom_audit'),
                'baseline audit differs from bound replay')
    else:
        require(terminal.get('axiom_audit') == result and terminal.get('result') ==
                ('SUCCESS' if reservation['mode'] == 'proof' else 'NEGATIVE'), 'proof audit differs from bound replay')
        expected = runner.TARGETS if reservation['mode'] == 'proof' else runner.NEGATIVE
        require(result['declarations'] == [{'name': n, 'type': t} for n, t in expected], 'fixed Lab result targets differ')
        _result_envelope(result, expected)


def _result_envelope(result, expected):
    """A tooling revision cannot broaden the fixed scientific result envelope."""
    reports = result.get('transitive_axioms', {})
    require(set(reports) == {n for n, _ in expected} | set(frozen.COMPARATORS),
            'required per-result axiom report inventory differs')
    for name, values in reports.items():
        require(isinstance(values, list) and all(isinstance(x, str) for x in values)
                and len(values) == len(set(values)), 'invalid or duplicate result axioms')
        require(set(values) == set(frozen.A7) if name in frozen.COMPARATORS else set(values) <= set(frozen.A7),
                'fixed A7 result envelope differs')
    require(result.get('assumptions') == list(frozen.A7) and result.get('model_id') == 'CVC-U1-A7'
            and result.get('conditional') is True, 'conditional result model differs')


def _attempt(root, manifest, state, row, modules, full):
    reservation, terminal = row['reservation'], row['terminal']
    number, phase = reservation['number'], reservation['phase']
    directory = safe(root, runner.OUT + '/attempts/' + f'{number:02d}')
    require(reservation.get('argv') == manifest['commands'][number - 1]['stages'][phase]
            and reservation.get('env') == manifest['environment']
            and reservation.get('cwd') == manifest['environment']['LEAN_PATH'].split(':')[0], 'attempt invocation differs')
    require(reservation['manifest_sha256'] == runner.sha(root / runner.MANIFEST)
            and reservation['tooling_checkpoint'] == state['revisions'][reservation['tooling_revision'] - 1]['checkpoint'],
            'attempt manifest or tooling checkpoint differs')
    raw, outputs = terminal.get('raw_files'), terminal.get('outputs')
    require(isinstance(raw, list) and isinstance(outputs, list), 'missing attempt receipt lists')
    receipts = {_receipt(root, r, full): r for r in raw}
    output_paths = [_receipt(root, r, full) for r in outputs]
    require(len(receipts) == len(raw) and len(output_paths) == len(set(output_paths)), 'duplicate attempt receipt')
    stem = runner.stem_for(phase)
    required = {str((directory / name).relative_to(root)) for name in
                ('implementation.lean', stem + '.lean', 'stdout', 'stderr', 'request.json', 'supervisor.json', 'process.json')}
    require(required <= set(receipts) and set(receipts) <= required | set(output_paths), 'missing or unknown raw receipt')
    require(all(Path(p).parent == directory.relative_to(root) and Path(p).name.startswith(stem + '.')
                and _PRODUCT.fullmatch(Path(p).name) for p in output_paths), 'unexpected compiler product')
    for output in outputs:
        require(receipts.get(output['path']) == output, 'compiler product absent or different in raw receipts')
    if terminal['status'] == 'COMPLETE':
        require(str((directory / (stem + '.olean')).relative_to(root)) in output_paths, 'successful attempt lacks olean')
    supervisor = _process(root, directory, reservation, terminal, receipts)
    _replay(root, modules[reservation['tooling_revision']], reservation, terminal, supervisor, directory)
    materialized = terminal.get('signature_materialization', [])
    require(isinstance(materialized, list), 'invalid signature materialization')
    if phase == 'signature' and terminal['status'] == 'COMPLETE':
        require(len(materialized) == len(outputs), 'signature materialization incomplete')
        for product, source in zip(materialized, outputs):
            require(product == {**source, 'path': runner.BASE + '/' + Path(source['path']).name},
                    'signature materialization differs from compiled product')
            _receipt(root, product, full)
    else:
        require(not materialized, 'unexpected signature materialization')


def validate_run(root, require_full_payload=False):
    root = Path(root).resolve()
    require(type(require_full_payload) is bool, 'full-payload flag must be boolean')
    directory = root / runner.OUT
    events = read_events(directory / 'execution/events.jsonl')
    state = runner.derive(events)
    require(load(directory / 'execution/state.json') ==
            {'count': len(events), 'tail': events[-1]['event_sha256'], 'state': state}, 'snapshot differs from complete event chain')
    start = load(directory / 'start.json')
    require(start.get('run_id') == runner.RUN and all(events[0].get(k) == v for k, v in start.items()), 'run start identity differs')
    manifest = _manifest(root, start)
    _activation(root, start)
    require(state['revisions'], 'missing bound tooling revision')
    modules = {r['number']: _revision(root, manifest, r) for r in state['revisions']}
    attempts = state['attempts']
    require(all('terminal' in row for row in attempts), 'unreconciled pending reservation')
    expected = {f"{r['reservation']['number']:02d}" for r in attempts}
    attempt_dir = directory / 'attempts'
    require((not attempt_dir.exists() and not expected) or
            (attempt_dir.is_dir() and {p.name for p in attempt_dir.iterdir()} == expected), 'unrecorded/missing attempt directory')
    for index, event in enumerate(events[1:], 1):
        if event['kind'] == 'RESERVED':
            require(event['active_seconds_before'] == runner.work_total(event['work'], event['time'])
                    and event['remaining_attempts_after_reservation'] == 4 - event['number'], 'reservation counters differ')
        elif event['kind'] == 'TERMINAL':
            require(event['remaining_attempts'] == 4 - event['number']
                    and event['remaining_active_seconds'] == max(0, runner.LIMITS['active_seconds'] -
                                                                 runner.work_total(event['work'], event['time'])),
                    'terminal counters differ')
    for row in attempts:
        _attempt(root, manifest, state, row, modules, require_full_payload)
    for event in state.get('reconciliations', []):
        for receipt in [event['supervisor_receipt'], event['request_receipt'], *event['raw_files']]:
            _receipt(root, receipt)
        proc = load(root / event['supervisor_receipt']['path'])
        require(proc['cleanup_completed'] is True and event['known_actual_seconds'] == proc['charged_seconds'],
                'control reconciliation changes actual cost or cleanup')
    work = load(root / runner.WORK)
    require(work.get('item_id') == runner.ITEM and work.get('run_id') == runner.RUN and work.get('policy') == runner.POLICY,
            'work identity differs')
    current = work['intervals'][-1].get('end', events[-1]['time'])
    # Existing event snapshots bind every earlier interval start and closed end.
    runner.work_continuation(state['work'], {'intervals': work['intervals']}, state['accounted_at'], current)
    active = runner.work_total({'intervals': work['intervals']}, current)
    require(work['active_seconds_closed'] == sum(r['charged_seconds'] for r in work['intervals'] if 'end' in r),
            'closed work total differs')
    policy, prior = load(root / runner.POLICY), load(root / PREDECESSOR)
    require(policy['consumed']['builds'] == prior['attempts'] == 2
            and policy['consumed']['active_seconds'] == prior['active_seconds']
            and policy['remaining']['builds'] == 4
            and policy['remaining']['active_seconds'] == runner.LIMITS['active_seconds'], 'policy carry-forward differs')
    if require_full_payload:
        runner.verify_payloads(root, manifest)
    count = lambda phase: sum(r['reservation']['phase'] == phase for r in attempts)
    success = lambda phase: sum(r['reservation']['phase'] == phase and r['terminal']['status'] == 'COMPLETE' for r in attempts)
    scientific = {'SUCCESS': 'CHECKED_CONDITIONAL_LAB_PROOF', 'NEGATIVE': 'CHECKED_CONDITIONAL_COUNTEREXAMPLE'}
    return {'item_id': runner.ITEM, 'run_id': runner.RUN, 'run_outcome': state['outcome'],
            'scientific_status': scientific.get(state['outcome'], 'NO_CHECKED_LAB_RESULT'),
            'attempts': len(attempts), 'signature_builds': count('signature'), 'baseline_builds': count('baseline'),
            'proof_builds': count('proof'), 'successful_signatures': success('signature'),
            'successful_baselines': success('baseline'), 'successful_proof_builds': success('proof'),
            'tooling_revisions': len(state['revisions']), 'active_seconds': active,
            'compilation_seconds': sum(r['terminal']['charged_seconds'] for r in attempts),
            'remaining_attempts_unspent': 4 - len(attempts),
            'combined_a7_attempts': prior['attempts'] + len(attempts),
            'combined_a7_active_seconds': prior['active_seconds'] + active,
            'repair_pause': state['repair_pause'], 'control_stop': state['control_stop'],
            'payloads_verified': require_full_payload}


def _closure_stop(root, result, summary, state):
    stop = result.get('stop', {})
    kind = stop.get('kind')
    require(kind in ('completed_proof', 'checked_counterexample', 'build_cap', 'active_time_cap',
                     'scientific_mismatch', 'unrepairable_gap') and isinstance(stop.get('reason'), str) and stop['reason'],
            'missing concrete closure boundary')
    require(isinstance(stop.get('evidence'), list) and stop['evidence'], 'closure boundary lacks evidence')
    for receipt in stop['evidence']:
        _receipt(root, receipt)
    if kind in ('completed_proof', 'checked_counterexample'):
        expected = 'SUCCESS' if kind == 'completed_proof' else 'NEGATIVE'
        require(result['outcome'] == summary['run_outcome'] == expected and not summary['control_stop'],
                'checked closure outcome differs from audited result')
        return
    require(result['outcome'] == 'BOUNDED_UNRESOLVED' and summary['run_outcome'] not in ('SUCCESS', 'NEGATIVE'),
            'unresolved closure mislabels a checked result')
    if kind == 'build_cap':
        require(summary['attempts'] == 4, 'build cap is not exhausted')
    elif kind == 'active_time_cap':
        require(summary['active_seconds'] >= runner.LIMITS['active_seconds'], 'cumulative active cap is not exhausted')
    elif kind == 'scientific_mismatch':
        require(any(r['terminal'].get('scientific_mismatch') for r in state['attempts']),
                'scientific mismatch lacks bound replay evidence')
    else:
        for key in ('attempted_repairs', 'remaining_options_blocked'):
            require(isinstance(stop.get(key), list) and stop[key]
                    and all(isinstance(x, str) and x.strip() for x in stop[key]), 'unrepairable gap lacks ' + key)
        require(stop.get('no_feasible_authorized_repair') is True,
                'engineering failure alone cannot close an active item')


def _success_limits(work, summary):
    runner.work_total({'intervals': work['intervals']}, work['intervals'][-1]['end'], enforce_limits=True)
    require(summary['attempts'] <= 4 and summary['combined_a7_attempts'] <= 6
            and summary['combined_a7_active_seconds'] <= 7200,
            'successful closure exceeds cumulative A7 policy caps')


def validate_closure(root, require_full_payload=False):
    root = Path(root).resolve()
    summary = validate_run(root, require_full_payload)
    result, work = load(root / BASE / 'result.json'), load(root / runner.WORK)
    require(result.get('schema_version') == 1 and result.get('item_id') == runner.ITEM
            and result.get('run_id') == runner.RUN and result.get('contract_id') == 'CVC-U1-A7', 'closure identity differs')
    require(result.get('summary') == {k: v for k, v in summary.items() if k != 'payloads_verified'},
            'result summary differs from audited run')
    require(result.get('scientific_status') == summary['scientific_status'], 'scientific status differs')
    for field, path in (('protocol', runner.MANIFEST), ('execution_protocol', BASE + '/execution-protocol.json'),
                        ('predecessor_result', PREDECESSOR), ('work_record', runner.WORK)):
        require(result.get(field) == runner.receipt(root, root / path), 'closure binding differs: ' + field)
    require(work.get('status') == 'CLOSED' and work.get('outcome') == result['outcome']
            and all('end' in row for row in work['intervals'])
            and work['active_seconds_closed'] == summary['active_seconds'] and work.get('closure_started'),
            'logical closure requires completed cumulative work accounting')
    require(work.get('research_operations') == {'signature_builds': summary['signature_builds'],
            'baseline_builds': summary['baseline_builds'], 'proof_builds': summary['proof_builds'],
            'dependency_builds': 0, 'observer_launches': 0, 'network_requests': 0}, 'work research operation counts differ')
    state = runner.derive(read_events(root / runner.OUT / 'execution/events.jsonl'))
    _closure_stop(root, result, summary, state)
    if result['outcome'] in ('SUCCESS', 'NEGATIVE'):
        _success_limits(work, summary)
    successful = [r['terminal']['axiom_audit']['declarations'] for r in state['attempts'] if r['terminal'].get('result')]
    require(result.get('result_declarations') == (successful[-1] if successful else []), 'result declarations differ')
    reports = [r['terminal']['axiom_audit']['transitive_axioms'] for r in state['attempts'] if r['terminal'].get('result')]
    require(result.get('transitive_axioms') == (reports[-1] if reports else {}), 'result transitive axioms differ')
    require(isinstance(result.get('nonclaims'), list) and result['nonclaims']
            and all(isinstance(x, str) and x.strip() for x in result['nonclaims']), 'scoped result nonclaims missing')
    return {**summary, 'outcome': result['outcome'], 'closure_verified': True}
