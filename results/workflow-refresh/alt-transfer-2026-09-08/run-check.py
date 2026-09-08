#!/usr/bin/env python3
"""Record bounded administrative checks for ALT-TRANSFER, preserving failures."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PACKAGE = ROOT / 'results/research/alt-transfer-2026-09-08'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def binding(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    label, *command = sys.argv[1:]
    if not command or not label.replace('-', '').isalnum():
        raise SystemExit('expected unique label and exact command')
    receipt, log = HERE / (label + '.json'), HERE / (label + '.log')
    if receipt.exists() or log.exists():
        raise SystemExit('never overwrite a validation attempt')
    work = json.loads((PACKAGE / 'work-record.json').read_text())
    started = time.monotonic()
    remaining = 5400 - work['entry_overhead_conservative_seconds'] - (
        started - work['intervals'][0]['started_monotonic'])
    if remaining <= 0:
        raise SystemExit('cumulative ALT-TRANSFER cap exhausted')
    timeout = min(1200, remaining)
    sources = [PACKAGE / 'evidence-manifest.json', PACKAGE / 'work-record.json',
               ROOT / 'config/research-queue.json', ROOT / 'docs/RESEARCH_STATUS.md',
               Path(__file__).resolve()]
    record = {'schema_version': 1, 'item_id': 'ALT-TRANSFER',
              'command': command, 'started_at': now(), 'started_monotonic': started,
              'status': 'RUNNING', 'timeout_seconds': timeout,
              'inputs': [binding(p) for p in sources],
              'repository_commit': subprocess.check_output(
                  ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    environment = os.environ.copy()
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    environment['CVC_PREP_FIXTURE_LEDGER'] = str(HERE / 'prep-fixture-ledger.jsonl')
    environment['CVC_RUNNER2_FIXTURE_LEDGER'] = str(HERE / 'runner-fixture-ledger.jsonl')
    try:
        with log.open('wb') as stream:
            process = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream,
                                     stderr=subprocess.STDOUT, timeout=timeout, check=False)
        code = process.returncode
        record.update(returncode=code, status='PASS' if code == 0 else 'FAIL')
    except subprocess.TimeoutExpired:
        code = 124
        record.update(returncode=code, status='TIMEOUT_REQUIRES_PROCESS_RECONCILIATION')
    ended = time.monotonic()
    record.update(ended_at=now(), ended_monotonic=ended, elapsed_seconds=ended-started,
                  log=binding(log), inputs_unchanged=record['inputs'] == [binding(p) for p in sources])
    if not record['inputs_unchanged']:
        record['status'] = 'INPUT_DRIFT'
        code = 1
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'label': label, 'status': record['status'], 'returncode': code,
                      'elapsed_seconds': record['elapsed_seconds']}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
