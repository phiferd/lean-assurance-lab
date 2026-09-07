"""Pure evidence validation for the CVC-RUNNER-2 engineering successor."""
from datetime import datetime
import json
import math
from pathlib import Path

from lib.cvc_fixture_budget import totals
from lib.cvc_prep import read_events, require, safe, sha
from lib.cvc_runner2 import CODE, FIXED, MANIFEST as PROOF_MANIFEST

BASE = 'results/research/conditional-validation-contracts/cvc-runner-2'
MANIFEST = BASE + '/evidence-manifest.json'
RESULT = BASE + '/result.json'
WORK = BASE + '/work-record.json'
LEDGER = BASE + '/fixture-ledger.jsonl'
LEGACY = BASE + '/validation-fixture-ledger.jsonl'
FIXTURE_SOURCES = {
    'lib/cvc_runner2.py', 'lib/cvc_process.py', 'lib/cvc_runner_audit.py',
    'lib/cvc_fixture_budget.py', 'tests/test_cvc_runner2.py',
    'tests/test_cvc_process.py', 'tests/cvc_runner2_fixture.py',
}
SOURCES = FIXTURE_SOURCES | {
    'scripts/run-cvc-u1-proof-successor', 'scripts/bind-cvc-u1-proof',
    'lib/cvc_runner2_evidence.py', 'scripts/validate-cvc-runner2',
    'tests/test_cvc_runner2_evidence.py',
} | set(CODE)
REQUIRED = {
    'results/research/conditional-validation-contracts/cvc-2/execution-protocol.json',
    'results/research/conditional-validation-contracts/cvc-2/assumptions.json',
    'results/research/conditional-validation-contracts/cvc-prep-2/result.json',
    'results/research/conditional-validation-contracts/cvc-runner-1/evidence-manifest.json',
    'results/research/conditional-validation-contracts/cvc-runner-1/result.json',
    'results/research/conditional-validation-contracts/cvc-runner-1/work-record.json',
    RESULT, WORK, LEDGER, LEGACY, PROOF_MANIFEST,
    BASE + '/fixture-ledger.identity.json', BASE + '/fixture-ledger.state.json',
    BASE + '/initial-work-record.json', BASE + '/fixture-identity-adoption.json',
} | SOURCES | set(FIXED)


def _json(path):
    return json.loads(Path(path).read_text())


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _binding(root, row, current=False):
    require(set(row) == {'path', 'sha256'}, 'invalid binding shape')
    require(isinstance(row['path'], str) and isinstance(row['sha256'], str)
            and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256']),
            'invalid binding value')
    path = safe(root, row['path'])
    if current:
        require(sha(path) == row['sha256'], 'current binding changed: ' + row['path'])
    return row['path']


def _receipt(root, base, row):
    require(set(row) == {'path', 'sha256'} and isinstance(row['path'], str), 'invalid raw file receipt')
    require(len(row['sha256']) == 64, 'invalid raw file digest')
    path = safe(base, row['path'])
    require(path.is_file() and sha(path) == row['sha256'], 'fixture raw receipt changed: ' + row['path'])


def _legacy(path):
    pending, count, charged = None, 0, 0.
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        if row.get('kind') == 'RESERVED':
            require(pending is None and type(row.get('reserved_launches')) is int
                    and 0 < row['reserved_launches'] <= 80 and row.get('reserved_seconds') == row['reserved_launches'] * 5,
                    'invalid legacy fixture reservation')
            pending = row; count += row['reserved_launches']
        elif row.get('kind') == 'TERMINAL':
            require(pending is not None and _finite(row.get('charged_seconds'))
                    and row['charged_seconds'] <= pending['reserved_seconds'], 'invalid legacy fixture terminal')
            charged += row['charged_seconds']; pending = None
        else:
            raise ValueError('unknown legacy fixture event')
    require(pending is None, 'legacy fixture reservation lacks terminal receipt')
    return count, charged


def _sessions(work):
    sessions = work.get('sessions')
    require(isinstance(sessions, list) and 0 < len(sessions) <= 2, 'invalid session count')
    total = 0.
    for number, row in enumerate(sessions, 1):
        require(row.get('number') == number, 'session number reset')
        start, end = datetime.fromisoformat(row['started_at']), datetime.fromisoformat(row['ended_at'])
        seconds = (end - start).total_seconds()
        require(start.tzinfo and end.tzinfo and _finite(seconds) and seconds <= 5400, 'invalid session duration')
        total += seconds
    require(total <= 10800, 'active-session cap exceeded')
    return total


def _command(receipt):
    value = receipt.get('argv', receipt.get('command'))
    return ' '.join(value) if isinstance(value, list) else value if isinstance(value, str) else ''


def _validation_receipt(root, path, current_sources):
    receipt = _json(safe(root, path))
    require(receipt.get('outcome', receipt.get('status')) == 'PASS' and receipt.get('returncode') == 0,
            'required validation did not pass: ' + path)
    require(receipt.get('tested_input_bindings_unchanged') is True, 'tested bindings changed: ' + path)
    log = receipt.get('log')
    if isinstance(log, str):
        log = {'path': log, 'sha256': receipt.get('log_sha256')}
    require(isinstance(log, dict), 'missing validation log binding: ' + path)
    _binding(root, log, current=True)
    bindings = receipt.get('tested_input_bindings')
    require(isinstance(bindings, list), 'missing tested input bindings: ' + path)
    found = {_binding(root, row, current=current_sources) for row in bindings}
    if current_sources:
        require(SOURCES <= found, 'final validation lacks current source binding: ' + path)
    return _command(receipt)


def validate(root):
    root = Path(root).resolve()
    manifest, result, work = (_json(safe(root, p)) for p in (MANIFEST, RESULT, WORK))
    require(manifest.get('schema_version') == 1 and manifest.get('item_id') == 'CVC-RUNNER-2'
            and manifest.get('outcome') == 'SUCCESS' and isinstance(manifest.get('files'), list), 'bad evidence manifest')
    listed = {_binding(root, row, current=True) for row in manifest['files']}
    require(len(listed) == len(manifest['files']) and REQUIRED <= listed, 'evidence manifest missing required binding')

    events = read_events(safe(root, LEDGER))
    count, charged = totals(events)
    saved = _json(root / BASE / 'fixture-ledger.state.json')
    require(saved == {'count': len(events), 'tail': events[-1]['event_sha256']}, 'fixture snapshot reset or stale')
    fixture_base = root / BASE
    for event in events:
        if event['kind'] == 'RESERVED':
            bindings = event.get('bindings')
            require(isinstance(bindings, list) and {_binding(root, row) for row in bindings} == FIXTURE_SOURCES,
                    'invalid pre-batch source bindings')
        else:
            require(event.get('source_bindings_unchanged') is True, 'fixture source binding changed')
            require(isinstance(event.get('files'), list), 'missing fixture raw receipts')
            for row in event['files']:
                _receipt(root, fixture_base, row)
    legacy_count, legacy_charged = _legacy(safe(root, LEGACY))
    combined_count, combined_charged = count + legacy_count, charged + legacy_charged
    require(combined_count <= 80 and combined_charged <= 400, 'combined fixture cap exceeded')

    active = _sessions(work)
    require(result.get('item_id') == 'CVC-RUNNER-2' and result.get('outcome') == 'SUCCESS'
            and result.get('scientific_outcome') == 'NO_PROOF_ATTEMPTS', 'result identity/outcome disagreement')
    require(result.get('proof_attempts') == 0 and result.get('checker_launches') == 0, 'forbidden proof/checker launch')
    require(result.get('fixture_processes') == combined_count, 'fixture process count disagreement')
    require(result.get('fixture_process_seconds') == combined_charged, 'fixture process charge disagreement')
    require(result.get('active_seconds') == active, 'active-session charge disagreement')
    receipts = result.get('validation_receipts')
    final = result.get('final_source_validation_receipts')
    require(isinstance(receipts, list) and receipts and isinstance(final, list) and final, 'missing validation receipts')
    require(set(final) <= set(receipts), 'final validation receipts must be listed validation receipts')
    commands = [_validation_receipt(root, p, False) for p in receipts]
    final_commands = [_validation_receipt(root, p, True) for p in final]
    for required in ('scripts/validate-research-queue', 'scripts/close-declaration-validation-publication-study validate-historical',
                     'scripts/validate-publication-study-snapshot --require-full-payload',
                     'scripts/validate-contribution --check-catalog', 'scripts/refresh-current-state',
                     'scripts/build-project-review --check', 'scripts/artifact-status --require-current'):
        require(any(command == required or command.startswith(required + ' ') for command in commands),
                'missing required validation: ' + required)
    require(any('scripts/run-unit-tests' in command and '--require-full-payload' in command for command in final_commands),
            'final full run-unit-tests receipt required')
    return {'fixture_processes': combined_count, 'fixture_process_seconds': combined_charged,
            'active_seconds': active, 'validation_receipts': len(commands), 'final_receipts': len(final_commands)}
