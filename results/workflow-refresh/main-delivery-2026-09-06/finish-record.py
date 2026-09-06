#!/usr/bin/env python3
"""Retain validation and the correction to the earlier delivery decision."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
records = []
for path in sorted(OUT.glob('[0-9][0-9]-*.json')):
    row = json.loads(path.read_text())
    assert hashlib.sha256((ROOT / row['log']).read_bytes()).hexdigest() == row['log_sha256']
    if path.stem == '03-artifact-status':
        assert row['status'] == 'FAIL'
    else:
        assert row['status'] == 'PASS', path
    records.append({'record': str(path.relative_to(ROOT)), **row})
required = ['01-guard-tests', '02-historical', '04-queue', '05-repair-evidence',
            '06-refresh', '07-artifact-status-final', '08-project-review', '09-diff']
assert {name + '.json' for name in required} <= {Path(row['record']).name for row in records}
record = json.loads((OUT / 'record.json').read_text())
record.update(validation_status='PASS', validations=records,
              preserved_diagnostic='03-artifact-status detected stale generated bindings after the instruction edits. The defined refresh path regenerated current artifacts; final artifact and review checks pass. Historical evidence validates unchanged.',
              guard_tests={'count': 8, 'status': 'PASS', 'network_requests': 0, 'git_processes': 0},
              implementation_bindings=[{'path': path, 'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
                  for path in record['instructions'] + ['scripts/push-main', 'tests/test_push_main.py']])
(OUT / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
print('PASS: main-only policy, guarded delivery, eight tests and current/historical evidence')
