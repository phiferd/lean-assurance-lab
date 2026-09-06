#!/usr/bin/env python3
"""Check the recorded failed-preflight closure offline; never query GitHub."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/research/ops-upstream-1'


def load(path):
    return json.loads(path.read_text())


def check_binding(binding, data):
    assert hashlib.sha256(data).hexdigest() == binding['sha256'], binding['path']
    if 'bytes' in binding:
        assert len(data) == binding['bytes'], binding['path']


def main():
    work = load(OUT / 'work-record.json')
    packet = load(OUT / 'status-packet.json')
    assert work['item_id'] == packet['item_id'] == 'OPS-UPSTREAM-1'
    assert work['status'] == 'COMPLETE'
    assert work['outcome'] == packet['outcome'] == 'BOUNDED_UNRESOLVED'
    assert packet['scientific_status'] == 'NO_NEW_UPSTREAM_OR_SEMANTIC_EVIDENCE'
    assert packet['upstream_change_assessment'] == 'UNKNOWN'
    assert len(work['sessions']) == work['consumed']['sessions'] == 1
    elapsed = (datetime.fromisoformat(work['ended_at']) -
               datetime.fromisoformat(work['started_at'])).total_seconds() / 60
    assert 0 <= elapsed <= work['budget']['session_minutes'] == 90
    assert abs(elapsed - work['active_minutes']) < 0.000001
    assert work['sessions'] == [{'started_at': work['started_at'], 'ended_at': work['ended_at']}]
    assert work['requests'] == []
    assert work['remaining_get_requests'] == work['budget']['max_get_requests_after_preflight'] == 6
    for key in ('get_requests_after_preflight', 'builds', 'checker_launches', 'external_messages'):
        assert work['consumed'][key] == 0, key
    assert packet['get_requests_after_preflight'] == 0
    assert work['preflight'] == packet['preflight']
    preflight = work['preflight']
    assert preflight['command'] == ['scripts/github-cli-preflight', 'leanprover/lean-kernel-arena']
    assert preflight['status'] == 'FAIL' and preflight['returncode'] == 1
    log = (ROOT / preflight['log']).read_bytes()
    check_binding({'path': preflight['log'], 'sha256': preflight['sha256']}, log)
    assert log == (b'FAIL: GitHub CLI authentication is unavailable for github.com\n'
                   b'Repair with: gh auth login -h github.com --web\n')
    for binding in work['inputs']:
        committed = subprocess.check_output(
            ['git', 'show', work['input_commit'] + ':' + binding['path']], cwd=ROOT)
        check_binding(binding, committed)
    for binding in (packet['work_record'], packet['last_known_record']['binding']):
        check_binding(binding, (ROOT / binding['path']).read_bytes())
    previous = load(ROOT / packet['last_known_record']['binding']['path'])
    for key in ('recorded_at', 'decisions', 'duplicate_preflight'):
        assert packet['last_known_record'][key] == previous[key], key
    assert previous['decisions']['kiota_contract_clarification']['decision'] == 'DEFERRED'
    for finding in packet['findings'][:3]:
        assert finding['change_since_last_record'] == 'UNKNOWN'
    assert packet['recommendations'][0]['repair_command'] == 'gh auth login -h github.com --web'
    print('PASS: exact preflight bytes, committed inputs, bounded accounting, and preserved baseline; no fresh disposition claim')


if __name__ == '__main__':
    main()
