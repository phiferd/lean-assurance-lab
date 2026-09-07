"""Prepare the finite observer input manifest before any feedback or launch."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.cvc4_artifacts import BASE, build, receipt
from lib.cvc4_runner import CODE, LIMITS, MANIFEST, OUT, WORK

base = ROOT / BASE
if (ROOT / OUT / 'events.jsonl').exists():
    raise SystemExit('Run exists; frozen manifest cannot be regenerated')
cases = build(ROOT)['cases']
mapping = json.loads((base / 'mapping/mapping.json').read_text())
binary = {r['observer'].lower(): r['executable'] for r in mapping['observers']}


def hypothesis(case, impl):
    if case['role'] == 'control' or (case['id'] == 'E-POS' and impl == 'nanoda'):
        message = 'Accepted 1 declarations.\n' if impl == 'official' else 'Checked 1 declarations with no errors\n'
        return {'returncode': 0, 'stdout_pattern': re.escape(message), 'stderr_pattern': ''}
    if impl == 'nanoda':
        line, assertion = ('520:13', 'self.ctx.all_uparams_defined(l, declar_info.uparams)') if case['id'] == 'E-UNOWNED' else ('921:71', 'self.def_eq(u, v)')
        pattern = (r"\nthread 'thread_[0-3]' \([0-9]+\) panicked at src/tc\.rs:" + re.escape(line) + ':\n' +
                   re.escape('assertion failed: ' + assertion + '\n') +
                   re.escape('note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace\n\n') +
                   r"thread 'main' \([0-9]+\) panicked at src/tc\.rs:139:26:\n" +
                   re.escape('A thread in `check_all_declars` panicked while being joined: Any { .. }\n'))
        return {'returncode': 101, 'stdout_pattern': '', 'stderr_pattern': pattern}
    name = case['artifact']['name']
    prefix = f"uncaught exception: while replaying declaration '{name}':\n(kernel) "
    if case['id'] == 'E-UNOWNED':
        pattern = re.escape(prefix + "invalid reference to undefined universe level parameter 'u'\n")
    else:
        pattern = (re.escape(prefix + f"declaration type mismatch, '{name}' has type\n  ") +
                   r'[^\n]+' + re.escape('\nbut it is expected to have type\n  ') + r'[^\n]+\n')
    return {'returncode': 1, 'stdout_pattern': '', 'stderr_pattern': pattern}


cells = []
for case in cases:
    for impl in ['official', 'nanoda']:
        arg = ROOT / case['input']['path'] if impl == 'official' else base / 'configurations' / (case['id'].lower() + '.json')
        cells.append({'id': case['id'] + '-' + impl, 'pair_id': case['pair_id'], 'role': case['role'],
                      'implementation': impl, 'argv': [str(ROOT / binary[impl]['path']), str(arg)],
                      'cwd': str(ROOT), 'env': {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'RUST_BACKTRACE': '0'},
                      'expected': hypothesis(case, impl)})
fixed = {base / 'cases.json', base / 'execution-protocol.json', base / 'prepare-manifest.py',
         ROOT / 'lib/cvc4_artifacts.py', ROOT / 'tests/test_cvc4_artifacts.py', ROOT / 'scripts/build-cvc4-artifacts'}
fixed |= {ROOT / r['input']['path'] for r in cases}
fixed |= set((base / 'configurations').glob('*.json'))
fixed |= {p for p in (base / 'mapping').rglob('*') if p.is_file()}
fixed |= {ROOT / r['path'] for r in mapping['bindings'] + mapping['prior_observations']}
fixed |= {ROOT / 'lib/cvc2_artifact.py', ROOT / 'results/workflow-refresh/cvc-a7-repair-1-2026-09-07/14-full-tests-repaired.json'}
baseline = base / 'work-baseline.json'
if not baseline.exists():
    baseline.write_bytes((ROOT / WORK).read_bytes())
manifest = {'schema_version': 1, 'item_id': 'CVC-4-CONDITIONAL', 'run_id': 'CVC4-U1-A7-0001',
            'run_directory': OUT, 'work_record': WORK, 'limits': LIMITS,
            'fixed_inputs': [receipt(ROOT, p) for p in sorted(fixed)],
            'payloads': [{'path': str(ROOT / r['path']), 'sha256': r['sha256']} for r in binary.values()],
            'tooling_inputs': [receipt(ROOT, ROOT / rel) for rel in CODE],
            'validation_record': receipt(ROOT, base / 'prelaunch-tests-02.json'),
            'work_baseline': receipt(ROOT, baseline), 'cells': cells}
target = ROOT / MANIFEST
if target.exists() and json.loads(target.read_text()) != manifest:
    raise SystemExit('Refuse changed manifest; retain and use an explicit revision after launch')
target.write_text(json.dumps(manifest, indent=2) + '\n')
print('Prepared 12 fixed cells; not launched.')
