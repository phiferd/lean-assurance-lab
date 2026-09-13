#!/usr/bin/env python3
"""Execute one committed, hash-bound Nat-dispatch test reservation."""
import fcntl
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.cvc_process import atomic, run_process
BASE = ROOT / 'results/research/nanoda-nat-dispatch-regression-1'
ITEM = 'NANODA-NAT-DISPATCH-REGRESSION-1'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(test, message):
    if not test:
        raise ValueError(message)


def main():
    require(len(sys.argv) == 2 and sys.argv[1] in tuple(f'{n:03d}-{kind}' for n in range(1, 4) for kind in ('focused', 'full')), 'fixed cell ID required')
    cell = sys.argv[1]
    manifest_path = BASE / 'execution' / (cell + '-manifest.json')
    raw = manifest_path.read_bytes()
    relative = str(manifest_path.relative_to(ROOT))
    require(subprocess.check_output(['git', 'show', 'HEAD:' + relative], cwd=ROOT) == raw, 'manifest must be committed')
    m = json.loads(raw)
    require(m['item_id'] == ITEM and m['cell_id'] == cell, 'wrong cell identity')
    for row in m['bindings']:
        path = Path(row['path'])
        if not path.is_absolute():
            path = ROOT / path
        require(digest(path.read_bytes()) == row['sha256'], 'binding mismatch: ' + str(path))
    for name in m.get('absent_paths', []):
        require(not Path(name).exists(), 'unbound Cargo configuration: ' + name)
    dependencies = json.loads((BASE / 'dependency-lock.json').read_text())
    for package in dependencies['packages']:
        expected = {row['path'] for row in package['files']}
        actual = {str(p) for p in Path(package['source_root']).rglob('*') if p.is_file()}
        require(actual == expected, 'dependency inventory mismatch')
        for row in package['files']:
            require(digest(Path(row['path']).read_bytes()) == row['sha256'], 'dependency source mismatch: ' + row['path'])
    source = Path(m['cwd'])
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source).decode().strip() == m['source_revision'], 'source revision')
    require(digest(subprocess.check_output(['git', 'diff', '--binary', 'HEAD'], cwd=source)) == m['patch_sha256'], 'exact source patch')
    require(not subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=source).strip(), 'unexpected untracked source')
    w = json.loads((BASE / 'work-record.json').read_text())
    elapsed = time.monotonic() - w['start_monotonic']
    utc_elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(w['started_at'])).total_seconds()
    require(elapsed >= 0 and abs(elapsed - utc_elapsed) <= 2, 'paired item clock disagreement')
    remaining = 5400 - elapsed
    require(remaining >= m['timeout_seconds'] and m['timeout_seconds'] == 120, 'remaining active time / process ceiling')
    account_path = BASE / 'execution/accounting.json'
    require(account_path.exists() or not any((BASE / 'execution').glob('*/supervisor.json')) and not any(p.is_dir() for p in (BASE / 'execution').iterdir()), 'missing accounting after reservation')
    account = json.loads(account_path.read_text()) if account_path.exists() else {'builds': 0, 'test_processes': 0, 'reservations': [], 'pending': None}
    require(account['builds'] == account['test_processes'] == len(account['reservations']), 'reservation count mismatch')
    require(account['pending'] is None and account['builds'] < 3 and account['test_processes'] < 4, 'unreconciled process or exhausted budget')
    require(not any(r['cell_id'] == cell for r in account['reservations']), 'cannot reuse a reservation')
    directory = BASE / 'execution' / cell
    directory.mkdir(exist_ok=False)
    reservation = {'cell_id': cell, 'manifest_sha256': digest(raw), 'build_number': account['builds'] + 1, 'test_number': account['test_processes'] + 1, 'active_seconds_at_reservation': 5400 - remaining, 'remaining_active_seconds': remaining, 'status': 'RESERVED'}
    account['builds'] += 1
    account['test_processes'] += 1
    account['reservations'].append(reservation)
    account['pending'] = cell
    atomic(account_path, account)
    receipt = run_process(m['argv'], source, m['environment'], directory, 120, deadline_monotonic=w['start_monotonic'] + 5400)
    reservation['receipt'] = str((directory / 'supervisor.json').relative_to(ROOT))
    reservation['status'] = receipt['status']
    if receipt['cleanup_completed'] and not receipt['deadline_exceeded'] and receipt['status'] in ('COMPLETE', 'FAILED'):
        account['pending'] = None
    atomic(account_path, account)
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt['status'] == 'COMPLETE' and receipt['returncode'] == 0 else 1


if __name__ == '__main__':
    with (BASE / 'execution/.launch.lock').open('a') as owner_lock:
        fcntl.flock(owner_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        raise SystemExit(main())
