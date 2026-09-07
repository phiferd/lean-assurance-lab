"""One bounded original timeout test, logging group-signal behavior unchanged."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import unittest
from unittest.mock import patch

root = Path(__file__).resolve().parents[4]
base = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(root), str(root / 'tests')]
from lib.cvc_prep import read_events
from lib.cvc_fixture_budget import totals

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def receipt(path):
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

allocation = json.loads((base / 'additional-validation-allocation.json').read_text())
assert allocation['diagnostic_launches_max'] == 9
number = int(sys.argv[1]); assert number in (1, 2, 3)
directory = base / ('signal-diagnostic-' + str(number))
assert not directory.exists(); directory.mkdir()
prior = [p for p in base.glob('signal-diagnostic-*') if p != directory]
assert len(prior) == number - 1
for path in prior:
    assert json.loads((path / 'result.json').read_text())['status'] == 'PASS'
sources = json.loads((base / 'code-bindings.json').read_text())
assert all(receipt(root / row['path']) == row for row in sources)
dump(directory / 'reservation.json', {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'fixture_launches': 3, 'reserved_seconds': 15, 'number': number,
    'source_manifest': receipt(base / 'code-bindings.json'), 'diagnostic_source': receipt(Path(__file__).resolve()),
    'allocation': receipt(base / 'additional-validation-allocation.json'),
    'purpose': 'Run exact unchanged timeout assertion; only log os.killpg entry/return/error, never suppress or replace its behavior.'})
ledger = directory / 'fixture-ledger.jsonl'
os.environ['CVC_RUNNER2_FIXTURE_LEDGER'] = str(ledger)
os.environ.pop('CVC_PREP_FIXTURE_LEDGER', None)
trace = directory / 'signals.jsonl'
original = os.killpg

def traced(pgid, sig):
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'sender_pid': os.getpid(), 'uid': os.getuid(), 'pgid': pgid, 'signal': int(sig)}
    try:
        value = original(pgid, sig)
        row['result'] = 'RETURNED'
        return value
    except OSError as error:
        row.update(result='ERROR', errno=error.errno, message=str(error))
        try:
            row['leader_group'] = os.getpgid(pgid)
        except OSError as lookup:
            row['leader_lookup_errno'] = lookup.errno
        raise
    finally:
        with trace.open('a') as stream:
            stream.write(json.dumps(row) + '\n'); stream.flush(); os.fsync(stream.fileno())

suite = unittest.defaultTestLoader.loadTestsFromName('test_cvc_process.ProcessTests.test_timeout_terminates_descendant_group')
with (directory / 'test.log').open('w') as log, patch('os.killpg', traced):
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
count, charged = totals(read_events(ledger))
assert count == 3
unchanged = all(receipt(root / row['path']) == row for row in sources)
value = {'status': 'PASS' if result.wasSuccessful() and unchanged else 'FAIL',
    'fixture_launches': count, 'charged_seconds': charged, 'source_bindings_unchanged': unchanged,
    'test_log': receipt(directory / 'test.log'), 'signal_trace': receipt(trace)}
dump(directory / 'result.json', value)
print(json.dumps(value)); print(trace.read_text())
raise SystemExit(0 if value['status'] == 'PASS' else 1)
