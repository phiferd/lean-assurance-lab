"""Replay completed evidence in a clean local clone without ignored payloads."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

root = Path(__file__).resolve().parents[4]
base = Path(__file__).resolve().parents[1]
record, log = base / '11-portable.json', base / '11-portable.log'
assert not record.exists() and not log.exists()
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=root)
checkpoint = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
start, tick = datetime.datetime.now(datetime.timezone.utc).isoformat(), time.monotonic()
with tempfile.TemporaryDirectory(prefix='cvc-a7-repair-portable-') as temporary, log.open('wb') as stream:
    clone = Path(temporary) / 'repo'
    command = ['git', 'clone', '--no-hardlinks', str(root), str(clone)]
    subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True)
    assert not (clone / 'external').exists()
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=clone, text=True).strip()
    assert actual == checkpoint
    check = ['scripts/validate-cvc-a7-repair', '--closure']
    subprocess.run(check, cwd=clone, stdout=stream, stderr=subprocess.STDOUT, check=True)
    subprocess.run(['python3', 'results/workflow-refresh/cvc-a7-repair-1-2026-09-07/validation-tools/bind-evidence.py', '--check'],
                   cwd=clone, stdout=stream, stderr=subprocess.STDOUT, check=True)
value = {'schema_version': 1, 'status': 'PASS', 'checkpoint': checkpoint,
         'started_at': start, 'elapsed_seconds': time.monotonic() - tick,
         'command': command, 'validation_command': check,
         'clean_clone': True, 'ignored_external_payloads_absent': True,
         'research_launches': 0, 'network_requests': 0,
         'log': {'path': str(log.relative_to(root)), 'bytes': log.stat().st_size,
                 'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}}
record.write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(value))
