"""Bind the diagnostic-only same-item revision; never rewrite run 1."""
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from lib.cvc4_artifacts import receipt
from lib import cvc4_runner as old
from lib import cvc4_runner2 as new

base = ROOT / 'results/research/conditional-validation-contracts/cvc-4-conditional'
rev = base / 'revision-02'
assert not (ROOT / new.OUT / 'events.jsonl').exists(), 'Cannot regenerate a launched revision'
prior = json.loads((ROOT / old.MANIFEST).read_text())
fixed = {ROOT / r['path'] for r in prior['fixed_inputs']}
fixed |= {ROOT / old.MANIFEST, ROOT / prior['validation_record']['path'], ROOT / prior['work_baseline']['path']}
fixed |= {p for p in (base / 'run-0001').rglob('*') if p.is_file() and not p.name.endswith('.lock')}
fixed |= {rev / 'repair-diagnostic.json', rev / 'protocol.json', rev / 'nanoda-pretty-printer.rs', Path(__file__).resolve()}
fixed |= set((rev / 'configurations').glob('*.json'))
fixed -= {ROOT / p for p in new.CODE}
cells = deepcopy(prior['cells'])
for cell in cells:
    if cell['implementation'] == 'nanoda':
        cell['argv'][1] = str(rev / 'configurations' / Path(cell['argv'][1]).name)
baseline = rev / 'work-baseline.json'
if not baseline.exists():
    baseline.write_bytes((ROOT / new.WORK).read_bytes())
manifest = {**prior, 'run_id': new.RUN, 'run_directory': new.OUT,
            'fixed_inputs': [receipt(ROOT, p) for p in sorted(fixed)],
            'tooling_inputs': [receipt(ROOT, ROOT / p) for p in new.CODE],
            'work_baseline': receipt(ROOT, baseline), 'validation_record': receipt(ROOT, rev / 'prelaunch-tests.json'),
            'predecessor': receipt(ROOT, rev / 'predecessor.json'), 'cells': cells}
target = ROOT / new.MANIFEST
assert not target.exists() or json.loads(target.read_text()) == manifest, 'Existing revision binding differs'
target.write_text(json.dumps(manifest, indent=2) + '\n')
print('Bound same-item revision: two retained launches plus twelve fresh cells, cap sixteen.')
