"""Bind the exact tested ownership-input successor before observer feedback."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import cvc4_ownership_runner as new
from lib import cvc4_runner2 as old
from lib.cvc4_ownership_inputs import build, PROPOSAL

BASE = ROOT / 'results/research/conditional-validation-contracts/cvc-4-ownership-1'


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def receipt(path):
    return {**binding(path), 'bytes': path.stat().st_size}


assert not (ROOT / new.OUT / 'start.json').exists(), 'launched input binding cannot be regenerated'
assert not (ROOT / new.MANIFEST).exists(), 'preserve prior manifest revisions'
cases = build(ROOT)['cases']
prior = json.loads((ROOT / old.MANIFEST).read_text())
previous = old.validate_run(ROOT)
assert previous['combined_launch_count'] == 12
assert previous['combined_process_seconds'] == new.INHERITED_PROCESS_SECONDS
test_command = ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_cvc4*.py']
log = BASE / 'prelaunch-tests.log'
assert not log.exists(), 'retain previous test evidence'
sources = [binding(ROOT / p) for p in new.CODE]
started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
with log.open('wb') as output:
    tested = subprocess.run(test_command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
assert sources == [binding(ROOT / p) for p in new.CODE], 'tooling changed during pure tests'
dump(BASE / 'prelaunch-tests.json', {'status': 'PASS' if tested.returncode == 0 else 'FAIL',
     'returncode': tested.returncode, 'command': test_command, 'started_at': started,
     'elapsed_seconds': time.monotonic() - tick, 'source_bindings': sources, 'log': receipt(log),
     'scope': 'Pure and mocked artifact/controller tests; no observer or inert-fixture process.'})
assert tested.returncode == 0, 'repair within same item; retain test evidence'
pred = {'schema_version': 1, 'item_id': old.ITEM, 'run_id': old.RUN,
        'checkpoint': previous['checkpoint'], 'manifest': binding(ROOT / old.MANIFEST),
        'launches': 12, 'known_process_seconds': new.INHERITED_PROCESS_SECONDS,
        'start': receipt(ROOT / old.OUT / 'start.json'),
        'events': receipt(ROOT / old.OUT / 'events.jsonl'),
        'snapshot': receipt(ROOT / old.OUT / 'state.json')}
dump(BASE / 'predecessor.json', pred)
baseline = BASE / 'work-baseline.json'
assert not baseline.exists(), 'work baseline already fixed'
baseline.write_bytes((ROOT / new.WORK).read_bytes())
cells = deepcopy(prior['cells'][-4:])
for cell in cells:
    cell['id'] += '-PARAM-RECORD'
    case = next(c for c in cases if c['role'] == cell['role'])
    cell['argv'][1] = str(ROOT / case['input']['path']) if cell['implementation'] == 'official' else str(BASE / 'configurations' / (case['id'].lower() + '.json'))
fixed = {ROOT / r['path'] for r in prior['fixed_inputs'] + prior['tooling_inputs']}
fixed |= {ROOT / old.MANIFEST, ROOT / prior['validation_record']['path'], ROOT / prior['work_baseline']['path'], ROOT / prior['predecessor']['path']}
fixed |= {p for p in (ROOT / old.OUT).rglob('*') if p.is_file() and not p.name.endswith('.lock')}
fixed |= {ROOT / PROPOSAL, BASE / 'cases.json', BASE / 'source-mapping.json', BASE / 'protocol.json',
          BASE / 'independent-input-review.json', BASE / 'entry-review.json', Path(__file__).resolve()}
fixed |= set((BASE / 'inputs').glob('*.ndjson')) | set((BASE / 'configurations').glob('*.json'))
fixed |= {ROOT / 'results/research/conditional-validation-contracts/cvc-4-adapter-review/evidence-manifest.json',
          ROOT / 'results/research/conditional-validation-contracts/cvc-4-conditional/result.json',
          ROOT / 'results/research/conditional-validation-contracts/cvc-4-conditional/work-record.json',
          ROOT / 'results/workflow-refresh/cvc-4-adapter-review-2026-09-08/validation.json'}
fixed -= {ROOT / p for p in new.CODE}
manifest = {'schema_version': 1, 'item_id': new.ITEM, 'run_id': new.RUN,
            'run_directory': new.OUT, 'work_record': new.WORK, 'limits': new.LIMITS,
            'fixed_inputs': [binding(p) for p in sorted(fixed)], 'payloads': prior['payloads'],
            'tooling_inputs': sources, 'validation_record': binding(BASE / 'prelaunch-tests.json'),
            'work_baseline': binding(baseline), 'predecessor': binding(BASE / 'predecessor.json'), 'cells': cells}
dump(ROOT / new.MANIFEST, manifest)
new.validate_manifest(ROOT)
print('PASS: exact ownership successor bound; commit and committed preflight still required; zero observer launches.')
