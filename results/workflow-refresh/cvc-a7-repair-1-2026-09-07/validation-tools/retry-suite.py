"""Reconcile the retained sandbox fixture failure, then retry unchanged tests."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[4]
base = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from lib.cvc_fixture_budget import totals
from lib.cvc_prep import read_events
from lib.cvc_runner2_evidence import _legacy

def load(path):
    return json.loads(path.read_text())

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def receipt(path):
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

source_file = base / 'code-bindings.json'
sources = load(source_file)
assert all(receipt(root / row['path']) == row for row in sources)
failed = load(base / '06-full-tests.json')
assert failed['returncode'] == 1 and failed['status'] == 'FAIL' and failed['tested_inputs_unchanged']
text = (base / '06-full-tests.log').read_text()
assert text.count('ERROR: ') == 1 and 'ERROR: test_real_timeout_kills_process_group (test_cvc_prep.ProcessTests)' in text
assert 'PermissionError: [Errno 1] Operation not permitted' in text
cleanup = load(base / 'fixture-cleanup-inspection.json')
assert cleanup['matching_processes'] == [] and cleanup['historical_actual_seconds'] is None
legacy = base / '06-full-tests-fixtures/preparation.jsonl'
rows = [json.loads(line) for line in legacy.read_text().splitlines()]
reservations = [row for row in rows if row['kind'] == 'RESERVED']
assert sum(row['reserved_launches'] for row in reservations) == 8
pending, missing, known = None, [], 0.
for row in rows:
    if row['kind'] == 'RESERVED':
        if pending:
            missing.append(pending)
        pending = row
    else:
        assert row['kind'] == 'TERMINAL' and pending and row['test'] == pending['test']
        assert 0 <= row['charged_seconds'] <= pending['reserved_seconds']
        known += row['charged_seconds']; pending = None
if pending:
    missing.append(pending)
assert len(missing) == 1 and missing[0]['test'] == 'test_cvc_prep.ProcessTests.test_real_timeout_kills_process_group'
assert missing[0]['reserved_launches'] == 2 and missing[0]['reserved_seconds'] == 10
count, charge = totals(read_events(base / '06-full-tests-fixtures/runner/fixture-ledger.jsonl'))
assert count == 15
prior_count = count + sum(row['reserved_launches'] for row in reservations)
conservative = charge + known + 10
assert prior_count == 23 and conservative <= 115
reconciliation = {'schema_version': 1, 'status': 'RECONCILED_FOR_CONTINUATION',
    'failed_batch': receipt(base / '06-full-tests.json'), 'raw_legacy_ledger': receipt(legacy),
    'cleanup_inspection': receipt(base / 'fixture-cleanup-inspection.json'),
    'reserved_launches': prior_count, 'reserved_seconds': 115,
    'known_actual_seconds': charge + known, 'unknown_actual_seconds': None,
    'unknown_reservations': missing, 'conservative_charged_seconds': conservative,
    'original_duration_cap_compliance': 'NOT_ESTABLISHED',
    'cause': 'Sandbox denied legacy timeout fixture killpg(SIGKILL). Original ledger has no terminal receipt for that reservation. The unchanged suite continued before the owner observed the buffered failure; preserve this limitation.',
    'repair': 'Current matching processes are absent. Preserve the unknown original duration and charge its complete reservation. Retry the same source-bound suite with process-control permissions; do not alter the legacy test/controller or raw evidence.'}
reconciled_path = base / 'fixture-reconciliation.json'
assert not reconciled_path.exists(); dump(reconciled_path, reconciliation)
label = '12-full-tests-retry'
record, log = base / (label + '.json'), base / (label + '.log')
assert not record.exists() and not log.exists()
all_batches = [load(p) for p in base.glob('*-fixture-reservation.json')]
assert sum(p['reserved_launches'] for p in all_batches) + 23 <= 46
assert sum(p['reserved_seconds'] for p in all_batches) + 115 <= 230
directory = base / (label + '-fixtures'); directory.mkdir(exist_ok=False)
env = dict(os.environ)
env['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
env['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
start, tick = datetime.datetime.now(datetime.timezone.utc).isoformat(), time.monotonic()
command = ['scripts/run-unit-tests', '--require-full-payload']
dump(base / (label + '-fixture-reservation.json'), {'item_id': 'CVC-A7-REPAIR-1', 'label': label,
    'reserved_launches': 23, 'reserved_seconds': 115, 'seconds_per_process': 5, 'at': start,
    'ledger_directory': str(directory.relative_to(root)), 'source_manifest': receipt(source_file),
    'prior_reconciliation': receipt(reconciled_path), 'permissions': 'unsandboxed process control for inert fixtures'})
with log.open('wb') as stream:
    process = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
unchanged = all(receipt(root / row['path']) == row for row in sources)
value = {'command': command, 'returncode': process.returncode, 'started_at': start,
    'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-tick,
    'log': receipt(log), 'source_manifest': receipt(source_file), 'tested_inputs_unchanged': unchanged,
    'status': 'PASS' if process.returncode == 0 and unchanged else 'FAIL'}
try:
    n, a = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
    n2, a2 = _legacy(directory / 'preparation.jsonl')
    value.update(fixtures_reconciled=n+n2 == 23 and a+a2 <= 115 and unchanged,
                 fixture_launches=n+n2, fixture_charged_seconds=a+a2)
except (ValueError, OSError) as error:
    value.update(fixtures_reconciled=False, reconciliation_error=str(error))
dump(record, value); print(json.dumps(value))
raise SystemExit(0 if value['status'] == 'PASS' and value['fixtures_reconciled'] else 1)
