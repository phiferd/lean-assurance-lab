"""Read-only closure validation for the bounded CVC-3 proof run.

This validator deliberately does not call the live research-queue gate.  That
gate is correct before a launch, but is no longer applicable after CVC-3 has
closed and the queue selects its outcome-dependent successor.  It launches no
Lean process and does not prescribe a result/report format.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

from lib import cvc_runner2 as runner
from lib.cvc_runner_audit import COMPARATORS
from lib.cvc_prep import read_events


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _json(path):
    return json.loads(Path(path).read_text())


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _receipt_map(rows):
    _require(isinstance(rows, list), 'raw receipts must be a list')
    result = {}
    for row in rows:
        _require(isinstance(row, dict) and isinstance(row.get('path'), str), 'invalid raw receipt')
        _require(row['path'] not in result, 'duplicate raw receipt: ' + row['path'])
        result[row['path']] = row
    return result


_AXIOM_REPORT = re.compile(
    r"^'([^\n]+)' (?:does not depend on any axioms|depends on axioms:\s*(\[[^\]]*\]))[ \t]*$", re.M)
_AXIOM_NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*")


def reported_axioms(stdout):
    """Parse independently printed axiom reports, including failed-attempt diagnostics."""
    reports = {}
    for match in _AXIOM_REPORT.finditer(stdout):
        name, listing = match.group(1), match.group(2)
        _require(name not in reports, 'duplicate axiom diagnostic: ' + name)
        values = [] if listing is None or listing == '[]' else [value.strip() for value in listing[1:-1].split(',')]
        _require(all(_AXIOM_NAME.fullmatch(value) for value in values), 'malformed axiom diagnostic: ' + name)
        _require(len(values) == len(set(values)), 'duplicate diagnostic axiom: ' + name)
        reports[name] = values
    return reports


def unlisted_comparator_axioms(stdout, assumptions):
    """Return only the unlisted axioms in the two mandatory comparator reports."""
    reports = reported_axioms(stdout)
    allowed = set(assumptions['conditional_axiom_policy']['standard_allowed']
                  + assumptions['conditional_axiom_policy']['source_helpers_allowed'])
    _require(set(COMPARATORS) <= set(reports), 'missing mandatory comparator diagnostic')
    return {name: sorted(set(reports[name]) - allowed) for name in COMPARATORS}


def _request(root, reservation, directory, receipts):
    path = directory / 'request.json'
    relative = str(path.relative_to(root))
    _require(relative in receipts, 'request receipt missing')
    runner.verify_receipt(root, receipts[relative])
    request = _json(path)
    digest = request.pop('request_sha256', None)
    _require(isinstance(digest, str) and hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() == digest,
             'request hash mismatch')
    for key in ('argv', 'cwd', 'env'):
        _require(request.get(key) == reservation[key], 'request differs from reservation: ' + key)
    _require(request.get('seconds') == reservation['reserved_seconds'], 'request duration differs from reservation')
    _require(request.get('deadline_monotonic') <= reservation['time']['monotonic'] + reservation['reserved_seconds'],
             'request deadline exceeds reservation')
    return digest


def _supervisor(root, terminal, directory, receipts, request_sha256):
    path = directory / 'supervisor.json'
    relative = str(path.relative_to(root))
    _require(relative in receipts and terminal.get('supervisor_receipt') == receipts[relative],
             'supervisor receipt missing or differs from raw receipt')
    runner.verify_receipt(root, receipts[relative])
    value = _json(path)
    _require(value.get('request_sha256') == request_sha256, 'supervisor request differs')
    for key in ('status', 'returncode', 'charged_seconds', 'cleanup_completed', 'deadline_exceeded'):
        _require(value.get(key) == terminal.get(key), 'supervisor terminal differs: ' + key)
    for stream in ('stdout', 'stderr'):
        stream_path = str((directory / stream).relative_to(root))
        _require(stream_path in receipts, stream + ' receipt missing')
        runner.verify_receipt(root, receipts[stream_path])
        _require(value.get(stream + '_sha256') == receipts[stream_path]['sha256'],
                 'supervisor ' + stream + ' digest differs')


def _attempt(root, manifest, row, require_payloads):
    reservation, terminal = row['reservation'], row['terminal']
    number = reservation['number']
    _require(reservation.get('manifest_sha256') == runner.sha(root / runner.MANIFEST), 'attempt manifest differs')
    _require(reservation.get('argv') == manifest['commands'][number - 1], 'attempt argv differs')
    workspace = manifest['environment']['LEAN_PATH'].split(':')[0]
    _require(reservation.get('cwd') == workspace, 'attempt cwd differs')
    _require(reservation.get('env') == manifest['environment'], 'attempt environment differs')
    directory = root / runner.OUT / 'attempts' / f'{number:02d}'
    _require(directory.is_dir() and not directory.is_symlink(), 'missing attempt directory')
    receipts = _receipt_map(terminal.get('raw_files'))
    for receipt in receipts.values():
        runner.verify_receipt(root, receipt)
    source_name = 'Contract.lean' if number == 1 else 'CVC2Proof.lean'
    for name, expected in (('implementation.lean', reservation['source_sha256']),
                           (source_name, reservation['input_sha256'])):
        relative = str((directory / name).relative_to(root))
        _require(relative in receipts, 'source receipt missing: ' + relative)
        runner.verify_receipt(root, receipts[relative])
        _require(receipts[relative]['sha256'] == expected, 'reserved source digest differs: ' + name)
    request_sha256 = _request(root, reservation, directory, receipts)
    _supervisor(root, terminal, directory, receipts, request_sha256)

    if require_payloads:
        for receipt in terminal.get('outputs', []):
            runner.verify_receipt(root, receipt)
    elif terminal.get('outputs') is not None:
        _require(isinstance(terminal['outputs'], list), 'outputs must be a list')

    if number == 1:
        _require('sorry' not in ((directory / 'stdout').read_text() + (directory / 'stderr').read_text()).lower(),
                 'signature output reports sorry')
        return None
    source = (directory / 'implementation.lean').read_text()
    generated = runner.generate(source, reservation['mode'])
    _require(generated == (directory / source_name).read_bytes(), 'generated proof audit differs')
    if terminal['status'] != 'COMPLETE':
        return {'failed_reports': reported_axioms((directory / 'stdout').read_text())}
    audit = runner.audit((directory / 'stdout').read_text(), (directory / 'stderr').read_text(),
                         runner.load(root / runner.ASSUMPTIONS), reservation['mode'])
    _require(terminal.get('axiom_audit') == audit, 'stored axiom audit differs')
    if terminal.get('result'):
        expected = 'SUCCESS' if reservation['mode'] == 'proof' else 'NEGATIVE'
        _require(terminal['result'] == expected, 'terminal result differs from result mode')
    return {'source_sha256': reservation['source_sha256'], 'declarations': audit['declarations'],
            'axioms': audit['transitive_axioms'], 'mode': reservation['mode']}


def _recorded_manifest(root):
    """Validate the committed entry-reviewed manifest without rebuilding local runtime state."""
    manifest = runner.load(root / runner.MANIFEST)
    _require(manifest.get('schema_version') == 1 and manifest.get('run_id') == runner.RUN
             and manifest.get('item_id') == runner.ITEM and manifest.get('limits') == runner.LIMITS,
             'invalid fixed run manifest')
    _require(isinstance(manifest.get('fixed_inputs'), list) and isinstance(manifest.get('controller_inputs'), list),
             'manifest bindings missing')
    review = runner.load(root / runner.ENTRY_REVIEW)
    _require(review.get('item_id') == runner.ITEM and review.get('decision') == 'PROMOTE'
             and review.get('run_id') == runner.RUN and review.get('manifest') == runner.binding(root, runner.MANIFEST),
             'entry review does not bind manifest')
    checkpoint = review.get('implementation_checkpoint')
    _require(isinstance(checkpoint, str) and re.fullmatch(r'[0-9a-f]{40}', checkpoint), 'invalid entry checkpoint')
    recorded = subprocess.check_output(['git', 'show', checkpoint + ':' + runner.MANIFEST], cwd=root)
    _require(recorded == (root / runner.MANIFEST).read_bytes(), 'manifest differs from entry checkpoint')
    for row in manifest['fixed_inputs'] + manifest['controller_inputs']:
        runner.bind(root, row)
        runner.committed(root, row['path'])
        historical = subprocess.check_output(['git', 'show', checkpoint + ':' + row['path']], cwd=root)
        _require(historical == (root / row['path']).read_bytes(), 'entry checkpoint differs: ' + row['path'])
    runner.committed(root, runner.MANIFEST)
    runner.committed(root, runner.ENTRY_REVIEW)
    _require(isinstance(manifest.get('commands'), list) and len(manifest['commands']) == 12,
             'manifest commands missing')
    for number, command in enumerate(manifest['commands'], 1):
        _require(isinstance(command, list) and len(command) == 4 and command[0] == manifest['compiler']
                 and command[1] == '-o' and command[3] == ('Contract.lean' if number == 1 else 'CVC2Proof.lean'),
                 'manifest command differs')
    return manifest


def validate_run(root, require_payloads=False):
    """Validate a closed CVC3-U1-PROOF-0001 run without starting any process.

    Default mode validates committed controller/fixed inputs and all recorded
    source/log evidence.  ``require_payloads`` additionally requires every
    compiled-output receipt, its normal mode for a full local payload check.
    """
    root = Path(root).resolve()
    _require(type(require_payloads) is bool, 'require_payloads must be boolean')
    manifest = _recorded_manifest(root)
    ledger = runner.Ledger(root / runner.OUT / 'execution')
    events = read_events(ledger.path)
    snapshot = _json(ledger.snapshot)
    state = runner.derive(events)
    _require(snapshot == {'count': len(events), 'tail': events[-1]['event_sha256'], 'state': state},
             'ledger snapshot differs from exact event chain')
    start = _json(root / runner.OUT / 'start.json')
    _require(events[0].get('kind') == 'START' and all(events[0].get(key) == value for key, value in start.items()),
             'start marker differs from ledger')
    _require(start.get('run_id') == runner.RUN and start.get('manifest_sha256') == runner.sha(root / runner.MANIFEST),
             'run identity differs from fixed manifest')
    _require(state['sessions'] and all('end' in session for session in state['sessions']),
             'closure requires all design sessions closed')
    active = sum(session['charged_seconds'] for session in state['sessions'])
    _require(_finite(active) and len(state['sessions']) <= 4 and active <= 21600, 'session cap exceeded')
    _require(all(_finite(session['charged_seconds']) and session['charged_seconds'] <= 5400
                 for session in state['sessions']), 'individual session cap exceeded')
    _require(len(state['attempts']) <= 12 and all('terminal' in row for row in state['attempts']),
             'closure has unfinished attempts')
    process_seconds = 0.
    final, failed_reports = None, []
    for row in state['attempts']:
        terminal = row['terminal']
        _require(_finite(terminal['charged_seconds']) and terminal['charged_seconds'] <= row['reservation']['reserved_seconds'],
                 'terminal charge exceeds reservation')
        process_seconds += terminal['charged_seconds']
        inspected = _attempt(root, manifest, row, require_payloads)
        if inspected is not None:
            if 'failed_reports' in inspected:
                failed_reports.append({'attempt': row['reservation']['number'], 'reports': inspected['failed_reports']})
            else:
                final = inspected
    outcome = state['outcome']
    _require(outcome in {'SUCCESS', 'NEGATIVE', 'BOUNDED_UNRESOLVED'}, 'closure has no terminal outcome')
    if outcome in {'SUCCESS', 'NEGATIVE'}:
        _require(state['control_stop'] is None and final is not None, 'successful/negative closure lacks final audited proof')
        _require(final['mode'] == ('proof' if outcome == 'SUCCESS' else 'counterexample'),
                 'outcome differs from final result mode')
        expected = runner.TARGETS if outcome == 'SUCCESS' else runner.NEGATIVE
        _require(final['declarations'] == [{'name': name, 'type': typ} for name, typ in expected],
                 'final declarations differ from fixed result mode')
    if require_payloads:
        runner.validate_manifest(root, require_commit=True)
        runner.verify_payloads(root, manifest)
        runner.verify_attempts(root, state)
    return {'run_id': runner.RUN, 'outcome': outcome, 'sessions': len(state['sessions']),
            'active_seconds': active, 'attempts': len(state['attempts']),
            'process_seconds': process_seconds, 'control_stop': state['control_stop'],
            'final_source_sha256': None if final is None else final['source_sha256'],
            'final_declarations': [] if final is None else final['declarations'],
            'final_axioms': {} if final is None else final['axioms'],
            'failed_axiom_reports': failed_reports,
            'manifest_sha256': runner.sha(root / runner.MANIFEST),
            'payloads_verified': require_payloads, 'compiler': manifest['compiler']}


def _file_receipt(root, row):
    _require(set(row) == {'path', 'sha256', 'bytes'}, 'invalid closure file receipt')
    runner.verify_receipt(root, row)
    return row['path']


def validate_closure(root, require_payloads=False):
    """Validate the closed run plus its result, work record and evidence manifest."""
    root = Path(root).resolve()
    summary = validate_run(root, require_payloads=require_payloads)
    base = root / 'results/research/conditional-validation-contracts/cvc-3'
    result, work, diagnostic = (_json(base / name) for name in ('result.json', 'work-record.json', 'stop-diagnostic.json'))
    for value, label in ((result, 'result'), (work, 'work record'), (diagnostic, 'stop diagnostic')):
        _require(value.get('schema_version') == 1 and value.get('item_id') == runner.ITEM, 'invalid ' + label + ' identity')
        _require(value.get('outcome') == summary['outcome'], label + ' outcome differs from ledger')
    _require(result.get('run_id') == runner.RUN and work.get('run_id') == runner.RUN, 'run ID differs from ledger')
    for key, summary_key in (('sessions', 'sessions'), ('active_seconds', 'active_seconds'), ('attempts', 'attempts'),
                             ('compilation_seconds', 'process_seconds')):
        _require(result.get(key) == summary[summary_key], 'result accounting differs: ' + key)
    _require(result.get('manifest', {}).get('sha256') == summary['manifest_sha256'], 'result manifest differs')
    attempts = runner.derive(read_events(root / runner.OUT / 'execution' / 'events.jsonl'))['attempts']
    signature_count = sum(row['reservation']['phase'] == 'signature' for row in attempts)
    proof_rows = [row for row in attempts if row['reservation']['phase'] == 'proof']
    _require(result.get('signature_elaborations') == signature_count and result.get('proof_builds') == len(proof_rows)
             and result.get('successful_proof_builds') == sum(row['terminal']['status'] == 'COMPLETE' for row in proof_rows)
             and result.get('remaining_attempts_unspent') == 12 - summary['attempts'],
             'result attempt accounting differs')
    prior = result.get('prior_costs')
    _require(isinstance(prior, dict) and isinstance(prior.get('result'), dict), 'prior costs missing')
    runner.verify_receipt(root, prior['result'])
    previous = _json(root / prior['result']['path'])
    prior_active = previous.get('aggregate_preparation_and_runner_active_seconds')
    prior_compilation = previous.get('prior_costs_unchanged', {}).get('preparation_compilation_seconds')
    _require(prior.get('preparation_and_runner_active_seconds') == prior_active
             and prior.get('preparation_compilation_seconds') == prior_compilation
             and result.get('aggregate_active_seconds') == prior_active + summary['active_seconds']
             and result.get('aggregate_compilation_seconds') == prior_compilation + summary['process_seconds'],
             'aggregate costs differ from bound predecessor')
    _require(work.get('status') == 'COMPLETE' and work.get('active_seconds') == summary['active_seconds']
             and work.get('attempts_consumed') == summary['attempts'], 'work record accounting differs')
    _require(work.get('compilation_seconds') == summary['process_seconds'], 'work record process charge differs')
    sessions = runner.derive(read_events(root / runner.OUT / 'execution' / 'events.jsonl'))['sessions']
    _require(work.get('sessions') == sessions, 'work record session ledger differs')
    _require(work.get('remaining_attempts_unspent') == 12 - summary['attempts'], 'work record remaining attempts differs')

    stdout = diagnostic.get('stdout')
    _require(isinstance(stdout, dict), 'diagnostic stdout receipt missing')
    runner.verify_receipt(root, stdout)
    assumptions = runner.load(root / runner.ASSUMPTIONS)
    actual = unlisted_comparator_axioms((root / stdout['path']).read_text(), assumptions)
    unlisted = sorted({axiom for values in actual.values() for axiom in values})
    _require(diagnostic.get('mandatory_comparator_reports') == {
        name: reported_axioms((root / stdout['path']).read_text())[name] for name in COMPARATORS
    }, 'diagnostic comparator reports differ')
    _require(diagnostic.get('unlisted_axioms') == unlisted and result.get('unlisted_axioms') == unlisted,
             'unlisted axiom conclusion differs from raw reports')
    _require(summary['outcome'] != 'BOUNDED_UNRESOLVED' or summary['control_stop'],
             'bounded closure lacks control stop')
    source = diagnostic.get('source_binding')
    _require(isinstance(source, dict) and set(source) == {'path', 'sha256', 'bytes'}, 'diagnostic source binding missing')
    source_path = root / source['path']
    if require_payloads or source_path.is_file():
        runner.verify_receipt(root, source)
    closure = runner.load(root / runner.CLOSURE)
    modules = [row for row in closure['closure']['modules'] if row.get('module') == 'Lean4Lean.Verify.Axioms']
    _require(len(modules) == 1 and modules[0].get('source', {}).get('sha256') == source['sha256']
             and modules[0]['source'].get('bytes') == source['bytes'], 'diagnostic source differs from fixed closure')

    manifest = _json(base / 'evidence-manifest.json')
    _require(manifest.get('schema_version') == 1 and manifest.get('item_id') == runner.ITEM
             and isinstance(manifest.get('files'), list), 'invalid CVC-3 evidence manifest')
    paths = [_file_receipt(root, row) for row in manifest['files']]
    manifest_path = str((base / 'evidence-manifest.json').relative_to(root))
    _require(paths and len(paths) == len(set(paths)) and manifest_path not in paths,
             'evidence manifest is empty, duplicate, or self-referential')
    expected = {
        str((base / name).relative_to(root)) for name in ('result.json', 'work-record.json', 'stop-diagnostic.json')
    } | {str((root / runner.OUT / name).relative_to(root)) for name in ('start.json', 'execution/events.jsonl', 'execution/state.json')}
    for row in runner.derive(read_events(root / runner.OUT / 'execution' / 'events.jsonl'))['attempts']:
        expected.update(receipt['path'] for receipt in row['terminal']['raw_files'])
    _require(expected <= set(paths), 'evidence manifest omits core run receipts')
    return {**summary, 'unlisted_axioms': unlisted, 'evidence_files': len(paths)}
