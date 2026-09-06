#!/usr/bin/env python3
"""Verify the single completed repair and an unstarted selected successor."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]

def load(rel):
    return json.loads((ROOT / rel).read_text())

q = load('config/research-queue.json')
by = {r['id']: r for r in q['items']}
out = 'results/research/conditional-validation-contracts/cvc-prep-2/'
r = load(out + 'result.json')
review = load('results/research/queue-reviews/2026-09-06-cvc-prep-2.json')
assert q['selected_item'] == 'CVC-RUNNER-1' and by['CVC-RUNNER-1']['status'] == 'READY'
assert by['CVC-PREP-2']['status'] == 'COMPLETE' and by['CVC-PREP-2']['closure']['outcome'] == r['outcome'] == 'SUCCESS'
assert by['CVC-PREP-1']['closure']['outcome'] == r['predecessor']['outcome'] == 'BOUNDED_UNRESOLVED'
assert r['completed_modules'] == 37 and r['compilation_attempts'] == 10 and len(r['outputs']) == 141
assert all(row['status'] == 'COMPLETE' for row in r['attempts'])
assert r['costs']['aggregate_compilation_attempts'] == 37
assert review['stopped_item'] == 'CVC-PREP-2' and review['after']['selected_item'] == q['selected_item']
assert review['after']['ordering'] == [row['id'] for row in sorted(q['items'], key=lambda row: row['priority'])]
assert by['CVC-RUNNER-1']['depends_on'] == ['CVC-PREP-2']
assert by['CVC-3']['depends_on'] == ['CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-1']
for item in ['CVC-3', 'CVC-4', 'CVC-5']:
    assert by[item]['status'] == 'PLANNED'
for rel in ['external/cvc3-u1-proof-0001', 'results/research/conditional-validation-contracts/cvc-3/run-0001',
            'results/research/conditional-validation-contracts/cvc-runner-1/work-record.json']:
    assert not (ROOT / rel).exists(), rel
m = load('config/cvc-u1-dependencies-0002.json')
for row in [m[k] for k in ['source_closure', 'runtime_manifest', 'work_record', 'controller', 'tests', 'predecessor', 'commands']] + m['immutable_bindings']:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
for rel in ['config/cvc-u1-dependencies-0002.json', 'lib/cvc_prep2.py', 'tests/test_cvc_prep2.py']:
    assert (ROOT / rel).read_bytes() == subprocess.check_output(['git', 'show', r['checkpoint_commit'] + ':' + rel], cwd=ROOT)
work = load(out + 'work-record.json')
for key in ['lab_elaborations', 'proof_attempts', 'checker_launches', 'lake_executions', 'native_compiler_invocations', 'network_requests', 'toolchain_installs']:
    assert work[key] == 0
assert hashlib.sha256((ROOT / 'research/conditional-validation-contracts/cvc2/Contract.lean').read_bytes()).hexdigest() == '20f3c65a3bfcd3a491f58a9562d203eeb91084f88c728206a725e252e533e5d3'
print('PASS: one completed controller repair; exact37-module bundle; immutable predecessor; CVC-RUNNER-1 selected but unstarted')
