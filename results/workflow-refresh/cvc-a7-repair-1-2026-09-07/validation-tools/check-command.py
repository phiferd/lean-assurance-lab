"""Retain closure checks with one shared source manifest and bounded fixtures."""
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
from lib.cvc_a7_repair_runner import FIXED

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def receipt(path):
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

label, command = sys.argv[1], sys.argv[2:]
record, log = base / (label + '.json'), base / (label + '.log')
if record.exists() or log.exists():
    raise SystemExit('Cannot overwrite a check')
bindings = base / 'code-bindings.json'
if not bindings.exists():
    paths = {p for folder in ('lib', 'scripts', 'tests', 'research/conditional-validation-contracts/cvc-a7-repair')
             for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    paths |= {root / p for p in FIXED} | {Path(__file__).resolve()}
    dump(bindings, [receipt(p) for p in sorted(paths)])
source = json.loads(bindings.read_text())
if any(receipt(root / row['path']) != row for row in source):
    raise SystemExit('Closure code changed; retain old binding and create a new explicit batch')
stamp = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
env = dict(os.environ)
start, tick = stamp(), time.monotonic()
dump(base / (label + '-start.json'), {'command': command, 'at': start, 'monotonic': tick,
     'source_manifest': receipt(bindings)})
if command[0] == 'scripts/run-unit-tests':
    prior = [json.loads(p.read_text()) for p in base.glob('*-fixture-reservation.json')]
    if sum(p['reserved_launches'] for p in prior) + 23 > 46:
        raise SystemExit('Closure fixture launch cap exhausted')
    if sum(p['reserved_seconds'] for p in prior) + 115 > 230:
        raise SystemExit('Closure fixture time cap exhausted')
    for p in prior:
        done = base / (p['label'] + '.json')
        if not done.exists() or not json.loads(done.read_text()).get('fixtures_reconciled'):
            raise SystemExit('Prior fixture accounting needs reconciliation')
    directory = base / (label + '-fixtures')
    directory.mkdir(exist_ok=False)
    env['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
    env['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
    dump(base / (label + '-fixture-reservation.json'), {
        'item_id': 'CVC-A7-REPAIR-1', 'label': label, 'reserved_launches': 23,
        'reserved_seconds': 115, 'seconds_per_process': 5, 'at': stamp(),
        'ledger_directory': str(directory.relative_to(root)), 'source_manifest': receipt(bindings)})
with log.open('wb') as stream:
    process = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
unchanged = all(receipt(root / row['path']) == row for row in source)
result = {'command': command, 'returncode': process.returncode, 'started_at': start,
          'ended_at': stamp(), 'elapsed_seconds': time.monotonic() - tick, 'log': receipt(log),
          'source_manifest': receipt(bindings), 'tested_inputs_unchanged': unchanged,
          'status': 'PASS' if process.returncode == 0 and unchanged else 'FAIL'}
if command[0] == 'scripts/run-unit-tests':
    from lib.cvc_fixture_budget import totals
    from lib.cvc_prep import read_events
    from lib.cvc_runner2_evidence import _legacy
    try:
        count, charged = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
        count2, charged2 = _legacy(directory / 'preparation.jsonl')
        result.update(fixtures_reconciled=count + count2 == 23 and charged + charged2 <= 115 and unchanged,
                      fixture_launches=count + count2, fixture_charged_seconds=charged + charged2)
    except (ValueError, OSError) as error:
        result.update(fixtures_reconciled=False, reconciliation_error=str(error))
dump(record, result)
print(json.dumps(result))
raise SystemExit(0 if result['status'] == 'PASS' and result.get('fixtures_reconciled', True) else 1)
