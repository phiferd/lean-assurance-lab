"""Run one immutable closure check and retain exact logs and fixture costs."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib.cvc_prep import read_events
from lib.cvc_fixture_budget import totals
from lib.cvc_runner2_evidence import _legacy


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def receipt(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


label, command = sys.argv[1], sys.argv[2:]
assert command and '/' not in label
record, log = BASE / (label + '.json'), BASE / (label + '.log')
assert not record.exists() and not log.exists(), 'retain old command result'
source = json.loads((BASE / 'closure-code-bindings.json').read_text())
decisions = json.loads((BASE / 'closure-decision-bindings.json').read_text())
assert all(receipt(ROOT / row['path']) == row for row in source), 'closure code changed before check'
assert all(receipt(ROOT / row['path']) == row for row in decisions), 'closure decisions changed before check'
stamp = lambda: datetime.now(timezone.utc).isoformat()
environment = dict(os.environ)
started_at, started = stamp(), time.monotonic()
dump(BASE / (label + '-start.json'), {'command': command, 'at': started_at,
     'monotonic': started, 'code_bindings': receipt(BASE / 'closure-code-bindings.json'),
     'decision_bindings': receipt(BASE / 'closure-decision-bindings.json')})
full = command[0] == 'scripts/run-unit-tests-with-signal-retry'
if full:
    allocation = json.loads((BASE / 'administrative-fixture-allocation.json').read_text())
    prior = [json.loads(path.read_text()) for path in BASE.glob('*-fixture-reservation.json')]
    assert sum(row['reserved_launches'] for row in prior) + 23 <= allocation['max_reserved_launches']
    assert sum(row['reserved_seconds'] for row in prior) + 115 <= allocation['max_reserved_seconds']
    directory = BASE / (label + '-fixtures')
    directory.mkdir()
    environment['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
    environment['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
    dump(BASE / (label + '-fixture-reservation.json'), {
        'item_id': 'SURVIVOR-LET-REUSE-1', 'label': label, 'at': started_at,
        'reserved_launches': 23, 'reserved_seconds': 115, 'seconds_per_process': 5,
        'ledger_directory': str(directory.relative_to(ROOT))})
with log.open('wb') as output:
    process = subprocess.run(command, cwd=ROOT, env=environment,
                             stdout=output, stderr=subprocess.STDOUT)
unchanged = all(receipt(ROOT / row['path']) == row for row in source + decisions)
result = {'command': command, 'returncode': process.returncode, 'started_at': started_at,
          'ended_at': stamp(), 'elapsed_seconds': time.monotonic() - started,
          'log': receipt(log), 'tested_inputs_unchanged': unchanged,
          'status': 'PASS' if process.returncode == 0 and unchanged else 'FAIL'}
if full:
    try:
        count, actual = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
        count2, actual2 = _legacy(directory / 'preparation.jsonl')
        result.update(fixtures_reconciled=count + count2 == 23 and actual + actual2 <= 115,
                      reserved_launches=count + count2,
                      known_instrumented_charge_seconds=actual + actual2)
    except (OSError, ValueError) as error:
        result.update(fixtures_reconciled=False, reconciliation_error=str(error))
dump(record, result)
print(json.dumps(result))
raise SystemExit(0 if result['status'] == 'PASS' and result.get('fixtures_reconciled', True) else 1)
