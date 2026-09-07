"""Administrative validation receipts; reuse existing fixture instrumentation."""
import datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parents[4]
base = Path(__file__).resolve().parents[1]
label, cmd = sys.argv[1], sys.argv[2:]
record, log = base / (label + '.json'), base / (label + '.log')
if record.exists() or log.exists():
    raise SystemExit('Refuse to overwrite validation receipt')
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
hashfile = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [p for folder in ('lib', 'scripts', 'tests', 'research/conditional-validation-contracts/cvc-a7')
          for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
sys.path.insert(0, str(root))
from lib.cvc_a7_runner import FIXED
inputs = sorted(set(inputs) | {Path(__file__).resolve()} | {root / p for p in FIXED})
source = [{'path': str(p.relative_to(root)), 'sha256': hashfile(p)} for p in sorted(inputs)]
start, tick, env = now(), time.monotonic(), dict(os.environ)
start_record = {'command': cmd, 'started_at': start, 'monotonic': tick, 'source_bindings': source}
(base / (label + '-start.json')).write_text(json.dumps(start_record, indent=2) + '\n')
if cmd[0] == 'scripts/run-unit-tests':
    prior = [json.loads(p.read_text()) for p in base.glob('*-fixture-reservation.json')]
    if sum(p['reserved_launches'] for p in prior) + 23 > 46 or sum(p['reserved_seconds'] for p in prior) + 115 > 230:
        raise SystemExit('A7 aggregate fixture reservation cap exhausted')
    # An unfinished earlier batch must be reconciled before any new fixture launch.
    for p in prior:
        receipt = base / (p['label'] + '.json')
        if not receipt.exists() or not json.loads(receipt.read_text()).get('fixtures_reconciled'):
            raise SystemExit('Unreconciled fixture batch; pause launches and repair locally')
    directory = base / (label + '-fixtures')
    directory.mkdir(exist_ok=False)
    env['CVC_RUNNER2_FIXTURE_LEDGER'] = str(directory / 'runner/fixture-ledger.jsonl')
    env['CVC_PREP_FIXTURE_LEDGER'] = str(directory / 'preparation.jsonl')
    reservation = {'item_id': 'CVC-3-CONDITIONAL', 'label': label, 'reserved_launches': 23,
                   'reserved_seconds': 115, 'seconds_per_process': 5, 'at': now(),
                   'ledger_directory': str(directory.relative_to(root)), 'source_bindings': source}
    (base / (label + '-fixture-reservation.json')).write_text(json.dumps(reservation, indent=2) + '\n')
with log.open('wb') as f:
    r = subprocess.run(cmd, cwd=root, env=env, stdout=f, stderr=subprocess.STDOUT)
unchanged = all(hashfile(root / b['path']) == b['sha256'] for b in source)
d = {'command': cmd, 'returncode': r.returncode, 'started_at': start, 'ended_at': now(),
     'elapsed_seconds': time.monotonic() - tick, 'log': str(log.relative_to(root)),
     'log_sha256': hashfile(log), 'tested_input_bindings_unchanged': unchanged,
     'status': 'PASS' if r.returncode == 0 and unchanged else 'FAIL'}
if cmd[0] == 'scripts/run-unit-tests':
    sys.path.insert(0, str(root))
    from lib.cvc_fixture_budget import totals
    from lib.cvc_prep import read_events
    from lib.cvc_runner2_evidence import _legacy
    try:
        count, charged = totals(read_events(directory / 'runner/fixture-ledger.jsonl'))
        count2, charged2 = _legacy(directory / 'preparation.jsonl')
        d['fixtures_reconciled'] = count + count2 == 23 and charged + charged2 <= 115 and unchanged
        d['fixture_launches'] = count + count2
        d['fixture_charged_seconds'] = charged + charged2
    except (ValueError, OSError) as error:
        d['fixtures_reconciled'] = False
        d['reconciliation_error'] = str(error)
record.write_text(json.dumps(d, indent=2) + '\n')
print(json.dumps(d))
raise SystemExit(r.returncode if r.returncode else 0 if unchanged and d.get('fixtures_reconciled', True) else 1)
