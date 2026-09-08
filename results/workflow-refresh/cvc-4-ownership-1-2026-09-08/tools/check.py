"""Retain exact validation inputs/logs and separately bounded inert fixtures."""
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
bindings = BASE / 'closure-code-bindings.json'
if not bindings.exists():
    paths = {p for folder in ('lib', 'scripts', 'tests') for p in (ROOT / folder).rglob('*')
             if p.is_file() and '__pycache__' not in p.parts}
    paths |= set((BASE / 'tools').glob('*.py'))
    dump(bindings, [receipt(p) for p in sorted(paths)])
source = json.loads(bindings.read_text())
decisions = json.loads((BASE / 'closure-decision-bindings.json').read_text())
assert all(receipt(ROOT / r['path']) == r for r in decisions), 'decision inputs changed before check'
assert all(receipt(ROOT / r['path']) == r for r in source), 'code changed; explicit new validation batch required'
stamp = lambda: datetime.now(timezone.utc).isoformat()
env = dict(os.environ)
start, tick = stamp(), time.monotonic()
dump(BASE / (label + '-start.json'), {'command': command, 'at': start, 'monotonic': tick,
                                     'source_manifest': receipt(bindings)})
is_full = command[0] == 'scripts/run-unit-tests-with-signal-retry'
if is_full:
    protocol = BASE / 'administrative-fixture-allocation.json'
    plan = json.loads(protocol.read_text())
    prior = [json.loads(p.read_text()) for p in BASE.glob('*-fixture-reservation.json')]
    assert sum(r['reserved_launches'] for r in prior) + 23 <= plan['max_reserved_launches']
    assert sum(r['reserved_seconds'] for r in prior) + 115 <= plan['max_reserved_seconds']
    for r in prior:
        assert json.loads((BASE / (r['label'] + '.json')).read_text())['fixtures_reconciled']
    directory = BASE / (label + '-fixtures')
    directory.mkdir()
    env['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
    env['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
    dump(BASE / (label + '-fixture-reservation.json'), {'item_id': 'CVC-4-OWNERSHIP-1', 'label': label,
         'at': start, 'reserved_launches': 23, 'reserved_seconds': 115, 'seconds_per_process': 5,
         'source_manifest': receipt(bindings), 'protocol': receipt(protocol),
         'ledger_directory': str(directory.relative_to(ROOT))})
with log.open('wb') as output:
    process = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
unchanged = all(receipt(ROOT / r['path']) == r for r in source + decisions)
result = {'command': command, 'returncode': process.returncode, 'started_at': start, 'ended_at': stamp(),
          'elapsed_seconds': time.monotonic() - tick, 'source_manifest': receipt(bindings), 'log': receipt(log),
          'tested_inputs_unchanged': unchanged, 'status': 'PASS' if process.returncode == 0 and unchanged else 'FAIL'}
if is_full:
    try:
        n, actual = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
        n2, actual2 = _legacy(directory / 'preparation.jsonl')
        result.update(fixtures_reconciled=n+n2 == 23 and actual+actual2 <= 115 and unchanged,
                      reserved_launches=n+n2, known_instrumented_charge_seconds=actual+actual2)
    except (OSError, ValueError) as error:
        result.update(fixtures_reconciled=False, reconciliation_error=str(error))
dump(record, result)
print(json.dumps(result))
raise SystemExit(0 if result['status'] == 'PASS' and result.get('fixtures_reconciled', True) else 1)
