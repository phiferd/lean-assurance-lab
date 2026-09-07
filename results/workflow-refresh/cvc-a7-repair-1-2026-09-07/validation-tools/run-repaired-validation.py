"""Use the remaining explicit allocation for focused repair and complete suite."""
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
from lib.cvc_prep import read_events, committed
from lib.cvc_runner2_evidence import _legacy

def load(path):
    return json.loads(path.read_text())

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def receipt(path):
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

mode = sys.argv[1]; assert mode in ('focused', 'full')
bindings_file = base / 'signal-repair-bindings.json'
bindings = load(bindings_file)
assert all(receipt(root / row['path']) == row for row in bindings)
for path in ('lib/cvc_signal_retry.py', 'tests/test_cvc_signal_retry.py', 'scripts/run-unit-tests-with-signal-retry'):
    committed(root, path)
plan = load(base / 'signal-repair-validation-plan.json')
assert plan['status'] == 'READY' and plan['max_total_launches'] == 78 and plan['max_total_reserved_seconds'] == 390
assert load(base / 'signal-diagnostic-2/reconciliation.json')['current_pids']
assert all(p['status'] == 'ABSENT' for p in load(base / 'signal-diagnostic-2/reconciliation.json')['current_pids'])
prior = [load(p) for p in base.glob('*-fixture-reservation.json')]
used = sum(p['reserved_launches'] for p in prior) + 6
seconds_used = sum(p['reserved_seconds'] for p in prior) + 30
expected = 3 if mode == 'focused' else 23
assert used + expected <= 78 and seconds_used + expected*5 <= 390
label = '13-signal-repair' if mode == 'focused' else '14-full-tests-repaired'
record, log = base / (label + '.json'), base / (label + '.log')
assert not record.exists() and not log.exists()
if mode == 'full':
    focus = load(base / '13-signal-repair.json')
    assert focus['status'] == 'PASS' and focus['fixtures_reconciled']
    assert load(base / '13-signal-repair-fixtures/runner/fixtures/01/supervisor.json')['cleanup_completed'] is True
    command = ['scripts/run-unit-tests-with-signal-retry', '--require-full-payload']
else:
    command = ['python3', '-c', "import sys,unittest; sys.path.insert(0,'tests'); from lib.cvc_signal_retry import signal_retry; suite=unittest.defaultTestLoader.loadTestsFromName('test_cvc_process.ProcessTests.test_timeout_terminates_descendant_group');\nwith signal_retry(): result=unittest.TextTestRunner(verbosity=2).run(suite)\nsys.exit(not result.wasSuccessful())"]
directory = base / (label + '-fixtures'); directory.mkdir(exist_ok=False)
env = dict(os.environ)
env['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
if mode == 'full':
    env['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
else:
    env.pop('CVC_PREP_FIXTURE_LEDGER', None)
start, tick = datetime.datetime.now(datetime.timezone.utc).isoformat(), time.monotonic()
dump(base / (label + '-fixture-reservation.json'), {'item_id': 'CVC-A7-REPAIR-1', 'label': label,
    'reserved_launches': expected, 'reserved_seconds': expected*5, 'seconds_per_process': 5, 'at': start,
    'aggregate_reserved_launches_after': used+expected, 'aggregate_reserved_seconds_after': seconds_used+expected*5,
    'ledger_directory': str(directory.relative_to(root)), 'source_manifest': receipt(bindings_file),
    'plan': receipt(base / 'signal-repair-validation-plan.json'),
    'checkpoint': subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()})
with log.open('wb') as stream:
    process = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
unchanged = all(receipt(root / row['path']) == row for row in bindings)
value = {'command': command, 'returncode': process.returncode, 'started_at': start,
    'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-tick,
    'log': receipt(log), 'source_manifest': receipt(bindings_file), 'tested_inputs_unchanged': unchanged,
    'status': 'PASS' if process.returncode == 0 and unchanged else 'FAIL'}
try:
    n,a = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
    n2,a2 = _legacy(directory / 'preparation.jsonl') if mode == 'full' else (0,0.)
    value.update(fixtures_reconciled=n+n2 == expected and a+a2 <= expected*5 and unchanged,
                 fixture_launches=n+n2, fixture_charged_seconds=a+a2)
except (OSError,ValueError) as error:
    value.update(fixtures_reconciled=False,reconciliation_error=str(error))
dump(record,value);print(json.dumps(value))
raise SystemExit(0 if value['status']=='PASS' and value['fixtures_reconciled'] else 1)
