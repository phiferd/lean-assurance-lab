"""Read-only current/historical transition check for this one-item closure."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'results/research/conditional-validation-contracts/cvc-axioms-1'
VALIDATION = ROOT / 'results/workflow-refresh/cvc-axioms-1-2026-09-06'


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


work = load(BASE / 'work-record.json')
checkpoint = work['input_commit']
for row in work['authority']:
    data = subprocess.check_output(['git', 'show', checkpoint + ':' + row['path']], cwd=ROOT)
    assert hashlib.sha256(data).hexdigest() == row['sha256']
    assert len(data) == row['bytes']
for row in work['inputs']:
    assert sha(ROOT / row['path']) == row['sha256']

before = json.loads(subprocess.check_output(['git', 'show', checkpoint + ':config/research-queue.json'], cwd=ROOT))
after = load(ROOT / 'config/research-queue.json')
old = {row['id']: row for row in before['items']}
current = {row['id']: row for row in after['items']}
newly_completed = [key for key, row in current.items()
                   if row['status'] == 'COMPLETE'
                   and (key not in old or old[key]['status'] != 'COMPLETE')]
assert newly_completed == ['CVC-AXIOMS-1']
assert after['selected_item'] == 'CVC-CONDITIONAL-1'
assert current['CVC-CONDITIONAL-1']['status'] == 'READY'
assert current['CVC-3-CONDITIONAL']['status'] == 'PLANNED'
assert current['CVC-4']['status'] == current['CVC-5']['status'] == 'PLANNED'
assert current['CVC-4']['depends_on'] == ['CVC-3']
assert current['CVC-3']['closure']['outcome'] == 'BOUNDED_UNRESOLVED'
assert not any(row['status'] == 'ACTIVE' for row in current.values())
for name in ('cvc-conditional-1', 'cvc-3-conditional'):
    assert not (BASE.parent / name).exists(), 'next item has started'
assert not (ROOT / 'external/cvc3-u1-a7-proof-0001').exists()
assert not (ROOT / 'config/cvc-u1-a7-proof-0001.json').exists()

review = load(ROOT / 'results/research/queue-reviews/2026-09-06-cvc-axioms-1.json')
assert review['before']['ordering'] == [r['id'] for r in before['items']]
assert review['after']['ordering'] == [r['id'] for r in after['items']]
assert review['after']['selected_item'] == after['selected_item']

# Every old tracked contract artifact and old runner remains byte-for-byte intact.
protected = [str(p.relative_to(ROOT)) for p in BASE.parent.iterdir()
             if p.is_dir() and p != BASE]
protected += ['research/conditional-validation-contracts/cvc2',
              'config/cvc-u1-proof-0001.json', 'lib/cvc_runner2.py',
              'lib/cvc_runner.py', 'lib/cvc_process.py', 'lib/cvc_runner_audit.py',
              'config/declaration-validation-catalog.json',
              'config/declaration-validation-approved-authority-sources.json']
assert not subprocess.check_output(['git', 'diff', '--name-only', checkpoint, '--', *protected], cwd=ROOT).strip()

# Required regression batch ran on exactly the source/test bytes bound before launch.
sources = load(VALIDATION / '11-full-tests-source-bindings.json')
for row in sources:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']

print(json.dumps(dict(status='PASS', newly_completed=newly_completed,
    selected_next='CVC-CONDITIONAL-1', next_started=False,
    historical_inputs_unchanged=True, test_source_bindings_verified=len(sources))))
